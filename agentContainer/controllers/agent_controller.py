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
import httpx
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

# Set up logging - INFO level to reduce noise
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

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
    try:
        mcp_connected = False
        if mcp_service:
            mcp_connected = mcp_service.is_connected()
        else:
            logger.error("❌ MCP service is None")
        
        response = HealthResponse(
            status="healthy",
            message="MCP Agent is running",
            mcp_connected=mcp_connected
        )
        return response
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/status", response_model=AgentStatusResponse)
async def get_status():
    """Get detailed agent status with real-time connection check"""
    try:
        if not mcp_service:
            logger.error("MCP service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not initialized"
            )
        
        agent_initialized = mcp_service.is_initialized()
        
        # Do real-time connection check
        mcp_connected = await mcp_service.check_connection_status()
        
        available_tools = mcp_service.get_available_tools()
        anthropic_api_key_loaded = mcp_service.has_api_key()
        
        response = AgentStatusResponse(
            agent_initialized=agent_initialized,
            mcp_connected=mcp_connected,
            available_tools=available_tools,
            anthropic_api_key_loaded=anthropic_api_key_loaded
        )
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


@router.get("/notebooks")
async def list_notebooks():
    """List all saved notebooks"""
    try:
        if not mcp_service:
            logger.error("MCP service is None")
            # Return empty list instead of error
            return {
                "notebooks": [],
                "success": False,
                "count": 0,
                "message": "MCP service not initialized",
                "error": "MCP service not initialized"
            }
        
        # Do real-time connection check
        try:
            mcp_connected = await mcp_service.check_connection_status()
        except Exception as conn_error:
            logger.error(f"Connection check failed: {conn_error}")
            mcp_connected = False
        
        if not mcp_connected:
            logger.error("MCP service not connected (real-time check failed)")
            # Return empty list instead of HTTP error
            return {
                "notebooks": [],
                "success": False,
                "count": 0,
                "message": "MCP service not connected - try refreshing status",
                "error": "MCP service not connected"
            }
        
        try:
            result = await mcp_service.list_notebooks()
        except Exception as list_error:
            logger.error(f"Failed to call list_notebooks: {list_error}")
            # Return empty list with error info
            return {
                "notebooks": [],
                "success": False,
                "count": 0,
                "message": f"Failed to retrieve notebooks: {str(list_error)}",
                "error": str(list_error)
            }
        
        # Extract the notebooks list from the MCP service response
        if isinstance(result, dict) and "notebooks" in result:
            notebooks_list = result["notebooks"]
            success = result.get("success", True)
            message = result.get("message", "Notebooks retrieved successfully")
        elif isinstance(result, list):
            # If result is directly a list
            notebooks_list = result
            success = True
            message = f"Found {len(notebooks_list)} notebooks"
        elif isinstance(result, str):
            # If result is a string, try to parse or treat as single item
            try:
                import json as json_parser
                parsed_result = json_parser.loads(result)
                if isinstance(parsed_result, list):
                    notebooks_list = parsed_result
                else:
                    notebooks_list = [result] if result.strip() else []
            except:
                notebooks_list = [result] if result.strip() else []
            success = True
            message = f"Found {len(notebooks_list)} notebooks"
        else:
            # Fallback: treat as empty
            notebooks_list = []
            success = False
            message = "No notebooks found or unexpected response format"
        
        # Ensure notebooks_list is always a list of strings
        if not isinstance(notebooks_list, list):
            notebooks_list = []
        
        # Filter and clean notebook names
        clean_notebooks = []
        for notebook in notebooks_list:
            if isinstance(notebook, str) and notebook.strip():
                clean_notebooks.append(notebook.strip())
            elif notebook:  # Convert to string if not None/empty
                clean_notebooks.append(str(notebook).strip())
        
        response = {
            "notebooks": clean_notebooks,
            "success": success,
            "count": len(clean_notebooks),
            "message": message
        }
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in list_notebooks: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return error response instead of raising HTTP exception
        return {
            "notebooks": [],
            "success": False,
            "count": 0,
            "message": f"Error retrieving notebooks: {str(e)}",
            "error": str(e)
        }


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
        
        # Do real-time connection check
        logger.debug("Performing real-time MCP connection check before task execution...")
        mcp_connected = await mcp_service.check_connection_status()
        
        if not mcp_connected:
            logger.error("MCP service not connected (real-time check failed)")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not connected"
            )
        
        logger.info("🚀 Starting agent execution...")
        start_time = datetime.now()
        
        # Run the agent
        result = await run_agent(request.task, mcp_service)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Agent execution completed in {execution_time:.2f} seconds")
        
        # Optionally save notebook if requested
        if request.save_notebook:
            filename = request.notebook_filename or f"agent_task_{hash(request.task) % 10000}.ipynb"
            logger.info(f"💾 Saving notebook as: {filename}")
            try:
                save_result = await mcp_service.call_mcp_tool("saveNotebook", {"filename": filename})
                result["notebook_saved"] = save_result
                logger.info(f"✅ Notebook saved successfully")
            except Exception as save_error:
                logger.error(f"❌ Failed to save notebook: {str(save_error)}")
                logger.error(f"Save error traceback: {traceback.format_exc()}")
                result["notebook_save_error"] = str(save_error)
        
        # Ensure outputs are properly formatted as strings
        formatted_outputs = []
        for output in result.get("outputs", []):
            if isinstance(output, dict):
                # Extract text from dict if it has a text field
                if "text" in output:
                    formatted_outputs.append(str(output["text"]))
                else:
                    formatted_outputs.append(str(output))
            elif isinstance(output, list):
                # Convert list to string representation
                formatted_outputs.append(str(output))
            else:
                # Ensure it's a string
                formatted_outputs.append(str(output))
        
        response = AgentTaskResponse(
            success=result["success"],
            task=result["task"],
            outputs=formatted_outputs,
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
        # Ensure filename has .ipynb extension
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'
        
        logger.debug(f"Fetching notebook file from FastAPI server: {filename}")
        
        # Use the new FastAPI endpoint (port 8003) for file download
        fastapi_download_url = f"http://localhost:8003/notebooks/{filename}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(fastapi_download_url)
            
            if response.status_code == 404:
                logger.warning(f"Notebook file not found: {filename}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Notebook not found: {filename}"
                )
            elif response.status_code != 200:
                logger.error(f"FastAPI server returned error: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch notebook from server"
                )
            
            # Get the notebook content
            notebook_content = response.content
            
            logger.info(f"Successfully fetched notebook: {filename} ({len(notebook_content)} bytes)")
            
            # Create streaming response for download with proper headers
            return StreamingResponse(
                io.BytesIO(notebook_content),
                media_type="application/x-ipynb+json",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                    "Content-Type": "application/x-ipynb+json",
                    "Content-Length": str(len(notebook_content)),
                    "Cache-Control": "no-cache"
                }
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