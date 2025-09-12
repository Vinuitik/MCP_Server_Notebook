from services.mcp_client import MCPClient
from services.ai_service import AIService
from services.notebook_service import NotebookService
from services.improved_notebook_service import SimpleMCPNotebookService
import logging

logger = logging.getLogger(__name__)

# Global instances
_mcp_client = None
_ai_service = None
_notebook_service = None
_simple_mcp_service = None

def get_mcp_client() -> MCPClient:
    """Get MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        logger.info("MCP Client initialized")
    return _mcp_client

def get_ai_service() -> AIService:
    """Get AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
        logger.info("AI Service initialized")
    return _ai_service

def get_notebook_service() -> NotebookService:
    """Get legacy notebook service instance"""
    global _notebook_service
    if _notebook_service is None:
        mcp_client = get_mcp_client()
        ai_service = get_ai_service()
        _notebook_service = NotebookService(mcp_client, ai_service)
        logger.info("Legacy Notebook Service initialized")
    return _notebook_service

async def get_simple_mcp_service() -> SimpleMCPNotebookService:
    """Get simple MCP notebook service instance with proper LangChain integration"""
    global _simple_mcp_service
    if _simple_mcp_service is None:
        _simple_mcp_service = SimpleMCPNotebookService()
        await _simple_mcp_service.initialize()
        logger.info("Simple MCP Notebook Service with proper LangChain integration initialized")
    return _simple_mcp_service
