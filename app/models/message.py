from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum

class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class AgentType(enum.Enum):
    SUPPORT = "support"
    SALES = "sales"
    TECHNICAL = "technical"
    GENERAL = "general"
    ORCHESTRATOR = "orchestrator"

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key linking back to the conversation
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    
    # Role of the sender (user, assistant, or system)
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # Which specific AI agent handled this message
    agent_type = Column(SQLEnum(AgentType), nullable=True)
    
    # Analytics data for the LLM call
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    
    # JSON array storing the IDs of the documents used as context
    context_sources = Column(Text, nullable=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Link back to the parent conversation
    conversation = relationship("Conversation", back_populates="messages")