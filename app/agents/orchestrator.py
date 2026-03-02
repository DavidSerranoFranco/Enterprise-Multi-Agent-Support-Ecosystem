from typing import List, Dict, Any, Tuple
from app.agents.specialized import SupportAgent, SalesAgent, TechnicalAgent
from app.agents.llm_service import llm_service
from app.schemas.chat import AgentType
import json
import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        # Initialize our specialized agents
        self.agents = {
            AgentType.SUPPORT: SupportAgent(),
            AgentType.SALES: SalesAgent(),
            AgentType.TECHNICAL: TechnicalAgent(),
        }

    async def classify_intent(self, message: str) -> AgentType:
        """
        Uses the LLM to analyze the user's message and decide which agent is best suited.
        """
        system_prompt = """You are a highly efficient Router Agent. 
Your ONLY job is to classify the user's message into one of the following categories:
- "support": For account issues, billing, password resets, or general help.
- "sales": For pricing, buying, upgrading, or asking about features.
- "technical": For bugs, API issues, coding, or system errors.

Respond ONLY with a JSON object in this format: {"category": "support|sales|technical"}"""

        try:
            response = await llm_service.generate_response(
                system_prompt=system_prompt,
                user_message=message
            )
            
            # Parse the JSON response
            content = response["content"].strip().lower()
            # Clean up potential markdown formatting (e.g., ```json ... ```)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            result = json.loads(content)
            category = result.get("category", "support")
            
            # Map string to Enum
            if category == "sales":
                return AgentType.SALES
            elif category == "technical":
                return AgentType.TECHNICAL
            else:
                return AgentType.SUPPORT
                
        except Exception as e:
            logger.error(f"Error classifying intent: {e}. Defaulting to SUPPORT.")
            return AgentType.SUPPORT # Default fallback

    async def route_message(
        self, 
        message: str, 
        chat_history: List[Dict[str, str]] = None,
        preferred_agent: AgentType = None
    ) -> Tuple[Dict[str, Any], List[Dict], AgentType]:
        """
        Routes the message to the correct agent and returns the response.
        """
        # Determine which agent to use
        selected_agent_type = preferred_agent
        
        if not selected_agent_type:
            logger.info("Classifying user intent...")
            selected_agent_type = await self.classify_intent(message)
            
        logger.info(f"Routing message to: {selected_agent_type.value.upper()} agent")
        
        # Get the specific agent instance
        agent = self.agents.get(selected_agent_type, self.agents[AgentType.SUPPORT])
        
        # Process the message with the selected agent
        llm_response, rag_sources = await agent.process_message(
            message=message,
            chat_history=chat_history
        )
        
        return llm_response, rag_sources, selected_agent_type

# Global instance
orchestrator = AgentOrchestrator()