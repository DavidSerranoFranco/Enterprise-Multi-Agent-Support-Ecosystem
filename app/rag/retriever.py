from app.rag.vectorstore import vectorstore_service
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RAGRetriever:
    def __init__(self):
        self.vectorstore = vectorstore_service

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        doc_type: Optional[str] = None,
        min_relevance: float = 0.0
    ) -> List[Dict]:
        """
        Retrieves relevant context for a given query
        """
        # Build filters
        filters = {}
        if category:
            filters["category"] = category
        if doc_type:
            filters["doc_type"] = doc_type

        filter_param = filters if filters else None

        # Search in vectorstore
        results = await self.vectorstore.search(
            query=query,
            n_results=top_k,
            filter_metadata=filter_param
        )

        # Filter by minimum relevance
        filtered_results = [
            r for r in results
            if r["relevance_score"] >= min_relevance
        ]

        logger.info(f"Retrieved {len(filtered_results)} relevant documents for: '{query[:50]}...'")

        return filtered_results

    def format_context(self, results: List[Dict]) -> str:
        """
        Formats the results into context for the LLM
        """
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}] (Relevance: {result['relevance_score']:.2f})\n"
                f"{result['content']}\n"
            )

        return "\n---\n".join(context_parts)

# Global instance
rag_retriever = RAGRetriever()