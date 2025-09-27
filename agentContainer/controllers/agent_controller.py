"""
Agent Controller - FastAPI routes for the MCP Agent
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from models.schemas import (
    HealthResponse, 
    MCPToolRequest, 
    MCPToolResponse,
    NotebookRequest,
    AgentStatusResponse,
    ChatMessage,
    ChatResponse
)
from services.mcp_service import MCPService

# Router instance
router = APIRouter()

# Global service instance (will be injected)
mcp_service: MCPService = None


def set_mcp_service(service: MCPService):
    """Set the MCP service instance"""
    global mcp_service
    mcp_service = service


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="MCP Agent is running",
        mcp_connected=mcp_service.is_connected() if mcp_service else False
    )


@router.get("/status", response_model=AgentStatusResponse)
async def get_status():
    """Get detailed agent status"""
    if not mcp_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not initialized"
        )
    
    return AgentStatusResponse(
        agent_initialized=mcp_service.is_initialized(),
        mcp_connected=mcp_service.is_connected(),
        available_tools=mcp_service.get_available_tools(),
        google_credentials_loaded=mcp_service.has_google_credentials()
    )


@router.post("/mcp/tool", response_model=MCPToolResponse)
async def call_mcp_tool(request: MCPToolRequest):
    """Call an MCP tool"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        result = await mcp_service.call_mcp_tool(request.tool_name, request.arguments)
        return MCPToolResponse(
            success=True,
            result=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        return MCPToolResponse(
            success=False,
            error=str(e)
        )


@router.get("/notebooks")
async def list_notebooks():
    """List all saved notebooks"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        result = await mcp_service.list_notebooks()
        return {"notebooks": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list notebooks: {str(e)}"
        )


@router.post("/notebooks")
async def save_notebook(request: NotebookRequest):
    """Save a notebook"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        result = await mcp_service.save_notebook(request.name, request.content or {})
        return {"message": "Notebook saved successfully", "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save notebook: {str(e)}"
        )


@router.get("/notebooks/{name}")
async def load_notebook(name: str):
    """Load a specific notebook"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        result = await mcp_service.load_notebook(name)
        return {"notebook": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load notebook: {str(e)}"
        )


@router.delete("/notebooks/{name}")
async def delete_notebook(name: str):
    """Delete a specific notebook"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        result = await mcp_service.delete_notebook(name)
        return {"message": "Notebook deleted successfully", "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notebook: {str(e)}"
        )