from langchain_groq import ChatGroq # <--- Cambio aquí
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.core.config import get_settings
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging
import time
import os

load_dotenv()
settings = get_settings()
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        """
        Initializes the Groq LLM (Llama 3) for high speed and reliability.
        """
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables")

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=settings.temperature,
        )

    async def generate_response(
        self, 
        system_prompt: str, 
        user_message: str, 
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        messages = [SystemMessage(content=system_prompt)]
        
        if chat_history:
            for msg in chat_history:
                role = str(msg["role"]).lower()
                content = msg["content"]
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role in ["assistant", "ai", "model"]:
                    messages.append(AIMessage(content=content))
        
        messages.append(HumanMessage(content=user_message))
        
        try:
            response = await self.llm.ainvoke(messages)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            tokens_used = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens_used = response.usage_metadata.get("total_tokens", 0)
            
            return {
                "content": response.content,
                "latency_ms": latency_ms,
                "tokens_used": tokens_used
            }

        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "latency_ms": 0,
                "tokens_used": 0
            }

llm_service = LLMService()