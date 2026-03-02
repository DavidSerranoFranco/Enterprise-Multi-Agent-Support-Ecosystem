from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from app.rag.retriever import rag_retriever
from app.agents.llm_service import llm_service

class BaseAgent(ABC):
    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description

    @abstractmethod
    def get_system_prompt(self, context: str = "") -> str:
        """Returns the specific system prompt for this agent"""
        pass

    async def process_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, str]] = None
    ) -> Tuple[Dict[str, Any], List[Dict]]:
        """
        Main method to process a user message:
        1. Retrieves context from RAG.
        2. Builds the prompt.
        3. Calls the LLM.
        """
        # 1. Retrieve relevant documents from vector database
        rag_results = await rag_retriever.retrieve(query=message)
        context_text = rag_retriever.format_context(rag_results)
        
        # 2. Get the specialized prompt
        system_prompt = self.get_system_prompt(context=context_text)
        
        # 3. Generate response via LLM
        llm_response = await llm_service.generate_response(
            system_prompt=system_prompt,
            user_message=message,
            chat_history=chat_history
        )
        
        return llm_response, rag_results