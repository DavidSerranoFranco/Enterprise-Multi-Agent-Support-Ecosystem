from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid
import json

from app.db.database import get_db
from app.models.message import Message, MessageRole, AgentType
from app.models.conversation import Conversation
from app.agents.orchestrator import orchestrator
from app.schemas.chat import ChatRequest, ChatResponse, SourceReference

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_db)
):
    try:
        # 1. Handle Conversation ID
        conv_id = request.conversation_id
        if not conv_id:
            conv_id = str(uuid.uuid4())
            new_conv = Conversation(
                id=conv_id,
                session_id=request.session_id,
                user_id=request.user_id,
                title=request.message[:50] + "..."
            )
            db.add(new_conv)
            await db.flush() # Use flush instead of commit to keep transaction open

        # 2. Save User Message
        user_msg_id = str(uuid.uuid4())
        user_message_db = Message(
            id=user_msg_id,
            conversation_id=conv_id,
            role=MessageRole.USER,
            content=request.message,
            # Explicitly set agent_type to None for users if your model allows
            agent_type=None 
        )
        db.add(user_message_db)
        await db.flush()

        # 3. Retrieve chat history (Last 10 messages)
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
            .limit(10)
        )
        history_db = result.scalars().all()
        
        # Format history: Ensure roles are strings for the LLM
        chat_history = [{"role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role), "content": msg.content} for msg in history_db[:-1]]

        # 4. Orchestrator Processing
        llm_response, rag_sources, agent_type = await orchestrator.route_message(
            message=request.message,
            chat_history=chat_history,
            preferred_agent=request.preferred_agent
        )

        # 5. Format RAG sources
        formatted_sources = []
        source_ids = []
        for src in rag_sources:
            doc_id = src["metadata"].get("document_id", "unknown")
            source_ids.append(doc_id)
            formatted_sources.append(
                SourceReference(
                    document_id=doc_id,
                    title=src["metadata"].get("title", "Untitled Document"),
                    relevance_score=src["relevance_score"],
                    snippet=src["content"][:200] + "..."
                )
            )

        # 6. Save AI Response
        # CRITICAL FIX: Ensure agent_type is passed as the Enum member, not a string
        ai_msg_id = str(uuid.uuid4())
        
        # If agent_type comes as a string "support", convert to Enum AgentType.SUPPORT
        if isinstance(agent_type, str):
            db_agent_type = AgentType[agent_type.upper()]
        else:
            db_agent_type = agent_type

        ai_message_db = Message(
            id=ai_msg_id,
            conversation_id=conv_id,
            role=MessageRole.ASSISTANT,
            content=llm_response["content"],
            agent_type=db_agent_type, # Fixed Enum reference
            tokens_used=llm_response.get("tokens_used", 0),
            latency_ms=llm_response.get("latency_ms", 0.0),
            context_sources=json.dumps(source_ids)
        )
        
        db.add(ai_message_db)
        await db.commit() # Final commit for everything

        return ChatResponse(
            response=llm_response["content"],
            conversation_id=conv_id,
            message_id=ai_msg_id,
            agent_type=db_agent_type.value if hasattr(db_agent_type, 'value') else db_agent_type,
            sources=formatted_sources,
            tokens_used=llm_response.get("tokens_used", 0),
            latency_ms=llm_response.get("latency_ms", 0.0)
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database or LLM Error: {str(e)}")