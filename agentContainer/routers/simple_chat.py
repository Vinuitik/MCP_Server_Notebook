"""
Simple chat router using proper MCP LangChain integration
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatMessage, ChatResponse
from services.improved_notebook_service import SimpleMCPNotebookService
from dependencies.deps import get_simple_mcp_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2/chat", tags=["chat-v2"])


@router.post("/", response_model=ChatResponse)
async def simple_mcp_chat(
    chat_message: ChatMessage,
    notebook_service: SimpleMCPNotebookService = Depends(get_simple_mcp_service)
):
    """
    Chat endpoint using proper MCP LangChain integration
    """
    try:
        logger.info(f"Received chat message: {chat_message.message[:100]}...")
        
        response = await notebook_service.process_message(chat_message.message)
        
        logger.info("Chat response generated successfully")
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"Error in simple MCP chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/tools")
async def get_available_tools(
    notebook_service: SimpleMCPNotebookService = Depends(get_simple_mcp_service)
):
    """Get available MCP tools"""
    try:
        tools = notebook_service.get_available_tools()
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tools: {str(e)}")


@router.get("/status")
async def get_service_status(
    notebook_service: SimpleMCPNotebookService = Depends(get_simple_mcp_service)
):
    """Get service status"""
    try:
        status = notebook_service.get_service_status()
        return status
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/health")
async def chat_health():
    """Health check for simple MCP chat service"""
    return {
        "status": "healthy", 
        "service": "simple-mcp-chat",
        "version": "2.0",
        "agent": "langchain-mcp-adapters"
    }