"""
Agent Controller - FastAPI routes for the MCP Agent
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
import io
import json
import logging
import traceback
from datetime import datetime

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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Router instance
router = APIRouter()

# Global service instance (will be injected)
mcp_service: MCPService = None


def set_mcp_service(service: MCPService):
    """Set the MCP service instance"""
    global mcp_service
    logger.info(f"Setting MCP service: {type(service).__name__}")
    logger.debug(f"Service instance: {service}")
    mcp_service = service
    logger.info("MCP service set successfully")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    try:
        mcp_connected = False
        if mcp_service:
            logger.debug("Checking MCP service connection")
            mcp_connected = mcp_service.is_connected()
            logger.debug(f"MCP service connected: {mcp_connected}")
        else:
            logger.warning("MCP service is None")
        
        response = HealthResponse(
            status="healthy",
            message="MCP Agent is running",
            mcp_connected=mcp_connected
        )
        logger.info(f"Health check response: {response}")
        return response
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/status", response_model=AgentStatusResponse)
async def get_status():
    """Get detailed agent status"""
    logger.info("Status check requested")
    try:
        if not mcp_service:
            logger.error("MCP service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not initialized"
            )
        
        logger.debug("Checking MCP service status...")
        agent_initialized = mcp_service.is_initialized()
        mcp_connected = mcp_service.is_connected()
        available_tools = mcp_service.get_available_tools()
        google_credentials_loaded = mcp_service.has_google_credentials()
        
        logger.debug(f"Agent initialized: {agent_initialized}")
        logger.debug(f"MCP connected: {mcp_connected}")
        logger.debug(f"Available tools: {available_tools}")
        logger.debug(f"Google credentials loaded: {google_credentials_loaded}")
        
        response = AgentStatusResponse(
            agent_initialized=agent_initialized,
            mcp_connected=mcp_connected,
            available_tools=available_tools,
            google_credentials_loaded=google_credentials_loaded
        )
        logger.info(f"Status response: {response}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )


@router.post("/mcp/tool", response_model=MCPToolResponse)
async def call_mcp_tool(request: MCPToolRequest):
    """Call an MCP tool"""
    logger.info(f"MCP tool call requested: {request.tool_name}")
    logger.debug(f"Tool arguments: {request.arguments}")
    
    try:
        if not mcp_service:
            logger.error("MCP service is None")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not initialized"
            )
        
        if not mcp_service.is_connected():
            logger.error("MCP service not connected")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not connected"
            )
        
        logger.debug(f"Calling MCP tool: {request.tool_name} with args: {request.arguments}")
        result = await mcp_service.call_mcp_tool(request.tool_name, request.arguments)
        logger.debug(f"MCP tool result: {result}")
        
        response = MCPToolResponse(
            success=True,
            result=result
        )
        logger.info(f"MCP tool call successful: {request.tool_name}")
        return response
        
    except ValueError as e:
        logger.error(f"MCP tool validation error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP tool call failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return MCPToolResponse(
            success=False,
            error=str(e)
        )


@router.get("/notebooks")
async def list_notebooks():
    """List all saved notebooks"""
    logger.info("List notebooks requested")
    
    try:
        if not mcp_service:
            logger.error("MCP service is None")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not initialized"
            )
        
        if not mcp_service.is_connected():
            logger.error("MCP service not connected")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not connected"
            )
        
        logger.debug("Calling list_notebooks on MCP service")
        result = await mcp_service.list_notebooks()
        logger.debug(f"List notebooks result: {result}")
        
        # Extract the notebooks list from the MCP service response
        if isinstance(result, dict) and "notebooks" in result:
            notebooks_list = result["notebooks"]
            success = result.get("success", True)
            message = result.get("message", "Notebooks retrieved successfully")
        else:
            # Fallback: assume result is already a list
            notebooks_list = result if isinstance(result, list) else []
            success = True
            message = f"Found {len(notebooks_list)} notebooks"
        
        response = {
            "notebooks": notebooks_list,
            "success": success,
            "count": len(notebooks_list) if isinstance(notebooks_list, list) else 0,
            "message": message
        }
        logger.info(f"List notebooks successful, found {len(notebooks_list) if isinstance(notebooks_list, list) else 'unknown'} notebooks")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list notebooks: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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
    logger.info(f"Agent task requested: {request.task[:100]}..." if len(request.task) > 100 else f"Agent task requested: {request.task}")
    logger.debug(f"Full request: {request}")
    
    try:
        if not mcp_service:
            logger.error("MCP service is None")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not initialized"
            )
        
        if not mcp_service.is_connected():
            logger.error("MCP service not connected")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not connected"
            )
        
        logger.info("Starting agent execution...")
        start_time = datetime.now()
        
        # Run the agent
        logger.debug("Calling run_agent function")
        result = await run_agent(request.task, mcp_service)
        logger.debug(f"Agent execution result: {result}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Agent execution completed in {execution_time:.2f} seconds")
        
        # Optionally save notebook if requested
        if request.save_notebook:
            filename = request.notebook_filename or f"agent_task_{hash(request.task) % 10000}.ipynb"
            logger.info(f"Saving notebook as: {filename}")
            try:
                save_result = await mcp_service.call_mcp_tool("saveNotebook", {"filename": filename})
                result["notebook_saved"] = save_result
                logger.info(f"Notebook saved successfully: {save_result}")
            except Exception as save_error:
                logger.error(f"Failed to save notebook: {str(save_error)}")
                logger.error(f"Save error traceback: {traceback.format_exc()}")
                result["notebook_save_error"] = str(save_error)
        
        response = AgentTaskResponse(
            success=result["success"],
            task=result["task"],
            outputs=result["outputs"],
            attempts=result["attempts"],
            notebook_data=result.get("notebook_data")
        )
        logger.info(f"Agent task completed successfully with {result['attempts']} attempts")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent task failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return AgentTaskResponse(
            success=False,
            task=request.task,
            outputs=[f"Error: {str(e)}"],
            attempts=0,
            error=str(e)
        )


@router.get("/agent/download/{filename}")
async def download_notebook(filename: str):
    """Download a notebook file"""
    logger.info(f"Download notebook requested: {filename}")
    
    try:
        if not mcp_service:
            logger.error("MCP service is None")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not initialized"
            )
        
        if not mcp_service.is_connected():
            logger.error("MCP service not connected")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not connected"
            )
        
        logger.debug(f"Loading notebook: {filename}")
        # Load the notebook
        notebook_result = await mcp_service.load_notebook(filename)
        logger.debug(f"Load notebook result: {notebook_result}")
        
        if not notebook_result or not notebook_result.get("loaded"):
            logger.warning(f"Notebook not found or failed to load: {filename}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notebook not found: {filename}"
            )
        
        logger.debug(f"Exporting notebook: {filename}")
        # Get the notebook content 
        # Since we don't have direct access to the notebook content from load_notebook,
        # we'll need to get it through the exportNotebook tool
        export_result = await mcp_service.call_mcp_tool("exportNotebook", {
            "filename": filename,
            "format": "json"
        })
        logger.debug(f"Export result: {export_result}")
        
        if not export_result.get("exported"):
            logger.error(f"Failed to export notebook: {filename}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to export notebook"
            )
        
        # Create a JSON response for download
        logger.debug("Creating JSON response for download")
        notebook_json = json.dumps(export_result, indent=2)
        
        # Create streaming response for download
        logger.info(f"Sending notebook download: {filename} ({len(notebook_json)} bytes)")
        return StreamingResponse(
            io.BytesIO(notebook_json.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download notebook {filename}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
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