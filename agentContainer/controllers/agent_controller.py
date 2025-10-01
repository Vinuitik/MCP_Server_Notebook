"""
Agent Controller - FastAPI routes for the MCP Agent
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
import io
import json

from models.schemas import (
    HealthResponse, 
    MCPToolRequest, 
    MCPToolResponse,
    NotebookRequest,
    AgentStatusResponse,
    ChatMessage,
    ChatResponse,
    AgentTaskRequest,
    AgentTaskResponse,
    NotebookDownloadResponse
)
from services.mcp_service import MCPService
from agent import run_agent

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


@router.post("/agent/run", response_model=AgentTaskResponse)
async def run_agent_task(request: AgentTaskRequest):
    """Run an agent task with MCP tools"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        # Run the agent
        result = await run_agent(request.task, mcp_service)
        
        # Optionally save notebook if requested
        if request.save_notebook:
            filename = request.notebook_filename or f"agent_task_{hash(request.task) % 10000}.ipynb"
            try:
                save_result = await mcp_service.call_mcp_tool("saveNotebook", {"filename": filename})
                result["notebook_saved"] = save_result
            except Exception as save_error:
                result["notebook_save_error"] = str(save_error)
        
        return AgentTaskResponse(
            success=result["success"],
            task=result["task"],
            outputs=result["outputs"],
            attempts=result["attempts"],
            notebook_data=result.get("notebook_data")
        )
        
    except Exception as e:
        return AgentTaskResponse(
            success=False,
            task=request.task,
            outputs=[],
            attempts=0,
            error=str(e)
        )


@router.get("/agent/download/{filename}")
async def download_notebook(filename: str):
    """Download a notebook file"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        # Load the notebook
        notebook_result = await mcp_service.load_notebook(filename)
        
        if not notebook_result or not notebook_result.get("loaded"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notebook not found: {filename}"
            )
        
        # Get the notebook content 
        # Since we don't have direct access to the notebook content from load_notebook,
        # we'll need to get it through the exportNotebook tool
        export_result = await mcp_service.call_mcp_tool("exportNotebook", {
            "filename": filename,
            "format": "json"
        })
        
        if not export_result.get("exported"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export notebook"
            )
        
        # Create a JSON response for download
        notebook_json = json.dumps(export_result, indent=2)
        
        # Create streaming response for download
        file_like = io.BytesIO(notebook_json.encode('utf-8'))
        
        return StreamingResponse(
            io.BytesIO(notebook_json.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download notebook: {str(e)}"
        )


@router.get("/agent/notebook/{filename}", response_model=NotebookDownloadResponse)
async def get_notebook_info(filename: str):
    """Get notebook information and download URL"""
    if not mcp_service or not mcp_service.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP service not connected"
        )
    
    try:
        # Check if notebook exists
        notebooks = await mcp_service.list_notebooks()
        
        if filename not in notebooks.get("notebooks", []):
            return NotebookDownloadResponse(
                success=False,
                filename=filename,
                error="Notebook not found"
            )
        
        return NotebookDownloadResponse(
            success=True,
            filename=filename,
            download_url=f"/api/v1/agent/download/{filename}"
        )
        
    except Exception as e:
        return NotebookDownloadResponse(
            success=False,
            filename=filename,
            error=str(e)
        )