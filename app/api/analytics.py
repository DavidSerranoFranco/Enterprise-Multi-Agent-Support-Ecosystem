from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import Dict, Any

from app.db.database import get_db
from app.models.message import Message
from app.models.conversation import Conversation

router = APIRouter()

@router.get("/summary", response_model=Dict[str, Any])
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns a high-level summary of the system's usage and performance.
    """
    try:
        # 1. Total conversations
        total_convs = await db.scalar(select(func.count(Conversation.id)))
        
        # 2. Total messages sent by AI
        total_ai_messages = await db.scalar(
            select(func.count(Message.id)).where(Message.role == 'assistant')
        )
        
        # 3. Total tokens used across all AI responses
        total_tokens = await db.scalar(
            select(func.sum(Message.tokens_used)).where(Message.tokens_used.is_not(None))
        )
        
        # 4. Average latency (response time)
        avg_latency = await db.scalar(
            select(func.avg(Message.latency_ms)).where(Message.latency_ms.is_not(None))
        )

        return {
            "total_conversations": total_convs or 0,
            "total_ai_messages": total_ai_messages or 0,
            "total_tokens_used": total_tokens or 0,
            "average_latency_ms": round(avg_latency or 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily", response_model=Dict[str, Any])
async def get_daily_statistics(db: AsyncSession = Depends(get_db)):
    """
    Returns statistics grouped by Agent Type (to see which agent is the busiest).
    Note: In a production environment, this would be grouped by date truncations.
    """
    try:
        # Group by agent_type and count messages
        result = await db.execute(
            select(
                Message.agent_type, 
                func.count(Message.id).label('message_count')
            )
            .where(Message.agent_type.is_not(None))
            .group_by(Message.agent_type)
        )
        
        agent_stats = result.all()
        
        distribution = {}
        for agent_type, count in agent_stats:
            # agent_type is an Enum, we extract the string value
            distribution[agent_type.value] = count

        return {
            "agent_distribution": distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))