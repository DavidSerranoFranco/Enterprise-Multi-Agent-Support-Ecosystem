from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any

from app.db.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    """
    Retrieves all conversations, ordered by the most recently updated.
    """
    try:
        result = await db.execute(
            select(Conversation).order_by(Conversation.updated_at.desc())
        )
        conversations = result.scalars().all()
        
        return [
            {
                "id": conv.id,
                "session_id": conv.session_id,
                "title": conv.title,
                "status": conv.status.value,
                "created_at": conv.created_at,
            }
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_history(
    conversation_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a specific conversation and all its messages.
    """
    try:
        # Load conversation and its messages using selectinload to avoid N+1 query issues
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Sort messages by creation time
        messages = sorted(conversation.messages, key=lambda m: m.created_at)

        return {
            "conversation_id": conversation.id,
            "title": conversation.title,
            "status": conversation.status.value,
            "created_at": conversation.created_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "agent_type": msg.agent_type.value if msg.agent_type else None,
                    "created_at": msg.created_at
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))