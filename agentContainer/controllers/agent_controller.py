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


@router.get("/debug/mcp")
async def debug_mcp_connection():
    """Debug MCP connection status and try different endpoints"""
    logger.info("MCP debug requested")
    
    debug_info = {
        "mcp_service_exists": mcp_service is not None,
        "connection_tests": [],
        "available_tools": [],
        "server_url": None
    }
    
    if not mcp_service:
        return debug_info
    
    debug_info["server_url"] = mcp_service.mcp_server_url
    debug_info["available_tools"] = mcp_service.get_available_tools()
    
    # Test various endpoints
    test_endpoints = [
        "/health",
        "/noteBooks/",
        "/noteBooks/info",
        "/noteBooks/tools",
        "/tools",
        "/info"
    ]
    
    import httpx
    for endpoint in test_endpoints:
        url = f"{mcp_service.mcp_server_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                debug_info["connection_tests"].append({
                    "url": url,
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "response_size": len(response.text),
                    "content_type": response.headers.get("content-type", "unknown")
                })
        except Exception as e:
            debug_info["connection_tests"].append({
                "url": url,
                "status": "error",
                "success": False,
                "error": str(e)
            })
    
    return debug_info


@router.get("/status", response_model=AgentStatusResponse)
async def get_status():
    """Get detailed agent status with real-time connection check"""
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
        
        # Do real-time connection check
        logger.debug("Performing real-time MCP connection check...")
        mcp_connected = await mcp_service.check_connection_status()
        
        available_tools = mcp_service.get_available_tools()
        anthropic_api_key_loaded = mcp_service.has_api_key()
        
        logger.debug(f"Agent initialized: {agent_initialized}")
        logger.debug(f"MCP connected (real-time): {mcp_connected}")
        logger.debug(f"Available tools: {available_tools}")
        logger.debug(f"Anthropic API key loaded: {anthropic_api_key_loaded}")
        
        response = AgentStatusResponse(
            agent_initialized=agent_initialized,
            mcp_connected=mcp_connected,
            available_tools=available_tools,
            anthropic_api_key_loaded=anthropic_api_key_loaded
        )
        logger.info(f"Status response: agent_initialized={agent_initialized} mcp_connected={mcp_connected} available_tools={available_tools} anthropic_api_key_loaded={anthropic_api_key_loaded}")
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
            # Return empty list instead of error
            return {
                "notebooks": [],
                "success": False,
                "count": 0,
                "message": "MCP service not initialized",
                "error": "MCP service not initialized"
            }
        
        # Do real-time connection check
        logger.debug("Performing real-time MCP connection check for list notebooks...")
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
        
        logger.debug("Calling list_notebooks on MCP service")
        try:
            result = await mcp_service.list_notebooks()
            logger.debug(f"List notebooks result: {result}")
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
        logger.info(f"List notebooks successful, found {len(clean_notebooks)} notebooks: {clean_notebooks}")
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
        
        # Ensure filename has .ipynb extension
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'
        
        logger.debug(f"Checking if notebook exists: {filename}")
        # First check if the notebook exists in the list of saved notebooks
        try:
            notebooks_list = await mcp_service.call_mcp_tool("listSavedNotebooks", {})
            logger.debug(f"Available notebooks: {notebooks_list}")
            
            available_notebooks = notebooks_list.get("notebooks", [])
            if filename not in available_notebooks:
                logger.warning(f"Notebook not found in saved notebooks: {filename}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Notebook not found: {filename}"
                )
        except Exception as list_error:
            logger.error(f"Failed to list notebooks: {list_error}")
            # Continue anyway, might still be able to load the notebook
        
        logger.debug(f"Attempting to load notebook: {filename}")
        # Try to load the notebook to get the current history
        try:
            load_result = await mcp_service.call_mcp_tool("loadNotebook", {"filepath": filename})
            logger.debug(f"Load notebook result: {load_result}")
            
            if not load_result or not load_result.get("loaded", False):
                logger.warning(f"Failed to load notebook: {filename}")
                # Create a basic notebook structure as fallback
                notebook_content = {
                    "cells": [
                        {
                            "cell_type": "markdown",
                            "metadata": {},
                            "source": [f"# {filename.replace('.ipynb', '')}\n\nThis notebook was exported from MCP Notebook Agent."]
                        }
                    ],
                    "metadata": {
                        "kernelspec": {
                            "display_name": "Python 3",
                            "language": "python",
                            "name": "python3"
                        },
                        "language_info": {
                            "name": "python",
                            "version": "3.12.0"
                        }
                    },
                    "nbformat": 4,
                    "nbformat_minor": 4
                }
            else:
                # Get the current history info to construct the notebook
                history_info = await mcp_service.call_mcp_tool("getHistoryInfo", {})
                logger.debug(f"History info: {history_info}")
                
                # Build cells from the current notebook history
                cells = []
                if history_info and history_info.get("total_cells", 0) > 0:
                    total_cells = history_info["total_cells"]
                    
                    for i in range(total_cells):
                        try:
                            cell_content = await mcp_service.call_mcp_tool("getCellContent", {"index": i})
                            if cell_content and cell_content.get("found", False):
                                cell_type = cell_content.get("cell_type", "code")
                                content = cell_content.get("content", "")
                                
                                if cell_type == "markdown":
                                    cell = {
                                        "cell_type": "markdown",
                                        "metadata": {},
                                        "source": [content]
                                    }
                                else:  # code cell
                                    cell = {
                                        "cell_type": "code",
                                        "execution_count": cell_content.get("execution_count"),
                                        "metadata": {},
                                        "outputs": cell_content.get("outputs", []),
                                        "source": [content]
                                    }
                                cells.append(cell)
                        except Exception as cell_error:
                            logger.error(f"Failed to get cell {i}: {cell_error}")
                            continue
                
                # Create the notebook structure
                notebook_content = {
                    "cells": cells,
                    "metadata": {
                        "kernelspec": {
                            "display_name": "Python 3",
                            "language": "python",
                            "name": "python3"
                        },
                        "language_info": {
                            "name": "python",
                            "version": "3.12.0"
                        }
                    },
                    "nbformat": 4,
                    "nbformat_minor": 4
                }
            
            notebook_json = json.dumps(notebook_content, indent=2, ensure_ascii=False)
            
        except Exception as load_error:
            logger.error(f"Failed to load notebook: {load_error}")
            # Fallback: create a basic notebook structure
            notebook_content = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [f"# {filename.replace('.ipynb', '')}\n\nThis notebook was exported from MCP Notebook Agent.\n\nNote: Failed to load original content."]
                    }
                ],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    },
                    "language_info": {
                        "name": "python",
                        "version": "3.12.0"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 4
            }
            notebook_json = json.dumps(notebook_content, indent=2, ensure_ascii=False)
        
        # Create streaming response for download with proper headers
        logger.info(f"Sending notebook download: {filename} ({len(notebook_json)} bytes)")
        
        response = StreamingResponse(
            io.BytesIO(notebook_json.encode('utf-8')),
            media_type="application/x-ipynb+json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/x-ipynb+json",
                "Content-Length": str(len(notebook_json.encode('utf-8'))),
                "Cache-Control": "no-cache"
            }
        )
        
        return response
        
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