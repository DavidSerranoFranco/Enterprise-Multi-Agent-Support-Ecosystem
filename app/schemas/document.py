from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentCreate(BaseModel):
    """Schema used when uploading or creating a new document"""
    title: str = Field(..., max_length=500)
    content: str
    source: Optional[str] = None
    doc_type: str = Field(..., max_length=50)
    category: Optional[str] = None

class DocumentUpdate(BaseModel):
    """Schema used when modifying an existing document"""
    title: Optional[str] = None
    content: Optional[str] = None
    doc_type: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class DocumentResponse(BaseModel):
    """Schema representing the document data returned by the API"""
    id: str
    title: str
    doc_type: str
    category: Optional[str]
    is_active: bool
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    """Schema for the response after a successful document upload and processing"""
    document_id: str
    chunks_created: int
    message: str