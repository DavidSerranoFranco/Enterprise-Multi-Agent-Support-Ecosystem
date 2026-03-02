from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class AgentType(str, Enum):
    SUPPORT = "support"
    SALES = "sales"
    TECHNICAL = "technical"
    GENERAL = "general"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    # The message must not be empty and cannot exceed 10,000 characters
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    session_id: str
    user_id: Optional[str] = None
    preferred_agent: Optional[AgentType] = None

class SourceReference(BaseModel):
    """Schema representing a document snippet used by the RAG system"""
    document_id: str
    title: str
    relevance_score: float
    snippet: str

class ChatResponse(BaseModel):
    """Schema for the API response returned to the frontend"""
    response: str
    conversation_id: str
    message_id: str
    agent_type: AgentType
    sources: List[SourceReference] = []
    tokens_used: int
    latency_ms: float

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    status: str