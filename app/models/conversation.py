from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum

class ConversationStatus(enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"

class Conversation(Base):
    __tablename__ = "conversations"

    # Unique identifier for the conversation
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    session_id = Column(String(100), nullable=False)
    
    # Current status of the conversation
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    title = Column(String(255), nullable=True)
    
    # JSON string to store any additional metadata
    metadata_ = Column(Text, nullable=True)  
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to link conversation with its messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")