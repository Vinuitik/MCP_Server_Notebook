from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatMessage, ChatResponse
from services.notebook_service import NotebookService
from dependencies.deps import get_notebook_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    chat_message: ChatMessage,
    notebook_service: NotebookService = Depends(get_notebook_service)
):
    """Main chat endpoint for interacting with the notebook AI"""
    try:
        response = await notebook_service.process_message(chat_message.message)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/health")
async def chat_health():
    """Health check for chat service"""
    return {"status": "healthy", "service": "chat"}
