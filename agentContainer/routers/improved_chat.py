"""
Improved chat router using LangChain-based agent service
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatMessage, ChatResponse
from services.improved_notebook_service import ImprovedNotebookService
from dependencies.deps import get_improved_notebook_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2/chat", tags=["chat-v2"])


@router.post("/", response_model=ChatResponse)
async def improved_chat_endpoint(
    chat_message: ChatMessage,
    notebook_service: ImprovedNotebookService = Depends(get_improved_notebook_service)
):
    """
    Improved chat endpoint using LangChain agent for intelligent tool selection
    """
    try:
        logger.info(f"Received chat message: {chat_message.message[:100]}...")
        
        response = await notebook_service.process_message(chat_message.message)
        
        logger.info("Chat response generated successfully")
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"Error in improved chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/history")
async def get_conversation_history(
    notebook_service: ImprovedNotebookService = Depends(get_improved_notebook_service)
):
    """Get the current conversation history"""
    try:
        history = notebook_service.get_conversation_history()
        return {"history": [msg.dict() if hasattr(msg, 'dict') else str(msg) for msg in history]}
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


@router.delete("/history")
async def clear_conversation_history(
    notebook_service: ImprovedNotebookService = Depends(get_improved_notebook_service)
):
    """Clear the conversation history"""
    try:
        result = notebook_service.clear_conversation_history()
        return {"message": result}
    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


@router.get("/status")
async def get_chat_status(
    notebook_service: ImprovedNotebookService = Depends(get_improved_notebook_service)
):
    """Get the status of chat service and MCP server connection"""
    try:
        mcp_status = notebook_service.get_mcp_server_status()
        return {
            "chat_service": "healthy",
            "mcp_server": mcp_status,
            "agent_type": "langchain"
        }
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        return {
            "chat_service": "error",
            "error": str(e),
            "agent_type": "langchain"
        }


@router.get("/health")
async def chat_health():
    """Health check for improved chat service"""
    return {
        "status": "healthy", 
        "service": "improved-chat",
        "version": "2.0",
        "agent": "langchain"
    }