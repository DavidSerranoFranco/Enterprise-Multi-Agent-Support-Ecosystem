import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.rag.embeddings import embedding_service
from typing import List, Dict, Optional
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        self.client = None
        self.collection = None
        # Split documents into smaller 1000-character chunks with a 200-character overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    async def initialize(self):
        """Initializes ChromaDB"""
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"VectorStore initialized with {self.collection.count()} documents")

    async def add_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict
    ) -> int:
        """Adds a document to the vectorstore"""
        # Split into chunks
        chunks = self.text_splitter.split_text(content)

        # Generate embeddings
        embeddings = await embedding_service.embed_documents(chunks)

        # Create unique IDs for each chunk
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

        # Prepare metadata for each chunk
        metadatas = [
            {**metadata, "chunk_index": i, "document_id": document_id}
            for i in range(len(chunks))
        ]

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

        logger.info(f"Document {document_id} added with {len(chunks)} chunks")
        return len(chunks)

    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Searches for relevant documents"""
        query_embedding = await embedding_service.embed_text(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "relevance_score": 1 - results["distances"][0][i]  # Convert distance to similarity
                })

        return formatted_results

    async def delete_document(self, document_id: str):
        """Deletes a document from the vectorstore"""
        # Find all chunks of the document
        results = self.collection.get(
            where={"document_id": document_id}
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.info(f"Document {document_id} deleted ({len(results['ids'])} chunks)")

    async def update_document(
        self,
        document_id: str,
        content: str,
        metadata: Dict
    ) -> int:
        """Updates a document (deletes and re-adds)"""
        await self.delete_document(document_id)
        return await self.add_document(document_id, content, metadata)

# Global instance
vectorstore_service = VectorStoreService()

async def init_vectorstore():
    await vectorstore_service.initialize()