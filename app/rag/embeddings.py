from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.core.config import get_settings
from typing import List
import numpy as np

settings = get_settings()

class EmbeddingService:
    def __init__(self, model_type: str = "openai"):
        if model_type == "openai":
            self.embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

    async def embed_text(self, text: str) -> List[float]:
        """Generates embedding for a single text string"""
        return await self.embeddings.aembed_query(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for multiple documents"""
        return await self.embeddings.aembed_documents(texts)

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculates cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Global instance
# embedding_service = EmbeddingService()
embedding_service = EmbeddingService(model_type="huggingface")