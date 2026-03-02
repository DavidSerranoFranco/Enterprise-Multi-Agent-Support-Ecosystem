from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    
    # URL or file path where the original document is located
    source = Column(String(255), nullable=True)  
    
    # E.g., 'faq', 'manual', 'policy', etc.
    doc_type = Column(String(50), nullable=False)  
    category = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
    chunk_count = Column(Integer, default=0)
    
    # JSON string to store extra metadata required for ChromaDB
    metadata_ = Column(Text, nullable=True)  
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())