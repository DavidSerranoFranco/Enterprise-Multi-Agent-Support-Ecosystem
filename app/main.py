
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import get_settings
from app.db.database import init_db
# Imports commented out until we create the routers and RAG implementation
from app.api import chat, documents, conversations, analytics
# from app.api.routes import chat, documents, conversations, analytics
from app.rag.vectorstore import init_vectorstore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Starting Multi-Agent Support API...")
    await init_db()
    await init_vectorstore()
    logger.info("Application started successfully")
    yield
    # Shutdown tasks
    logger.info("Shutting down application...")

app = FastAPI(
    title="Multi-Agent Support API",
    description="AI agent system for customer support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers (We will uncomment these as we build them)
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    return {"message": "Multi-Agent Support API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}