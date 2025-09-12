"""
Simple notebook service using the proper MCP Agent Service.
"""

import logging
from services.langchain_agent_service import ProperMCPAgentService

logger = logging.getLogger(__name__)


class SimpleMCPNotebookService:
    """
    Simple notebook service that uses the proper MCP agent
    """
    
    def __init__(self):
        self.agent_service = ProperMCPAgentService()
        self._initialized = False
        logger.info("Initialized SimpleMCPNotebookService")
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if not self._initialized:
            await self.agent_service.initialize()
            self._initialized = True
    
    async def process_message(self, user_message: str) -> str:
        """
        Process user message using the proper MCP agent
        
        Args:
            user_message: The user's input message
            
        Returns:
            The agent's response
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            logger.info(f"Processing message: {user_message[:100]}...")
            
            # Use the proper MCP agent to process the message
            response = await self.agent_service.process_message(user_message)
            
            logger.info("Message processed successfully by MCP agent")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def get_available_tools(self) -> list:
        """Get list of available tool names"""
        if self.agent_service.is_initialized:
            return self.agent_service.list_available_tools()
        return []
    
    def get_service_status(self) -> dict:
        """Get service status"""
        return {
            "status": "healthy" if self._initialized else "not_initialized",
            "agent_initialized": self.agent_service.is_initialized,
            "available_tools": self.get_available_tools()
        }