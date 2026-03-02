from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
import json

from app.db.database import get_db
from app.schemas.document import DocumentUploadResponse, DocumentResponse
from app.models.document import Document
from app.rag.document_processor import document_processor
from app.rag.vectorstore import vectorstore_service

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    category: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to upload a file, process its text, and index it into ChromaDB for RAG.
    """
    try:
        # 1. Read file content
        content_bytes = await file.read()
        
        # Extract file extension
        filename = file.filename
        file_ext = filename.split(".")[-1].lower() if "." in filename else "text"
        
        # 2. Extract text using the DocumentProcessor
        extracted_text = await document_processor.process(
            content=content_bytes, 
            file_type=file_ext
        )
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Could not extract text from file")

        # 3. Create document record in PostgreSQL
        doc_id = str(uuid.uuid4())
        new_doc = Document(
            id=doc_id,
            title=filename,
            content=extracted_text, # Keeping full text in DB as backup
            doc_type=doc_type,
            category=category,
            source=filename
        )
        
        # Prepare metadata for ChromaDB
        metadata = {
            "title": filename,
            "doc_type": doc_type,
            "category": category if category else "general"
        }

        # 4. Add to Vector Database (ChromaDB)
        chunks_created = await vectorstore_service.add_document(
            document_id=doc_id,
            content=extracted_text,
            metadata=metadata
        )

        # Update chunk count in SQL database
        new_doc.chunk_count = chunks_created
        db.add(new_doc)
        await db.commit()

        return DocumentUploadResponse(
            document_id=doc_id,
            chunks_created=chunks_created,
            message="Document processed and indexed successfully"
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    """
    Retrieves a list of all indexed documents from PostgreSQL.
    """
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    documents = result.scalars().all()
    return documents