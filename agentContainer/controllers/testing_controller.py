"""
Testing Controller - FastAPI routes for testing MCP functionality
"""
import logging
import io
import json
import traceback
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from datetime import datetime

from services.mcp_service import MCPService

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
    logger.info(f"Setting MCP service for testing controller: {type(service).__name__}")
    mcp_service = service
    logger.info("MCP service set successfully for testing controller")


@router.get("/test-notebook")
async def create_test_notebook():
    """
    Create a test notebook with markdown and code cells, save it, and return as downloadable file
    """
    logger.info("Test notebook creation requested")
    
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
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        notebook_filename = f"test_notebook_{timestamp}.ipynb"
        
        logger.info(f"Creating test notebook: {notebook_filename}")
        
        
        # Step 2: Add a markdown cell
        logger.debug("Adding markdown cell...")
        markdown_content = """# Test Notebook

This is a **test notebook** created by the testing controller.

## Features:
- Markdown cell with formatting
- Code cell with Python code
- Automatic saving and download

Created at: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_result = await mcp_service.call_mcp_tool("createMarkdownCell", {
            "content": markdown_content
        })
        logger.debug(f"Markdown cell result: {markdown_result}")
        
        # Step 3: Add a code cell
        logger.debug("Adding code cell...")
        code_content = """# Test Python code
import datetime
import math

# Display current time
now = datetime.datetime.now()
print(f"Current time: {now}")

# Simple calculation
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
average = total / len(numbers)

print(f"Numbers: {numbers}")
print(f"Sum: {total}")
print(f"Average: {average}")

# Mathematical operations
print(f"Pi: {math.pi}")
print(f"Square root of 16: {math.sqrt(16)}")

print("Test notebook created successfully!")"""
        
        code_result = await mcp_service.call_mcp_tool("createCodeCell", {
            "content": code_content
        })
        logger.debug(f"Code cell result: {code_result}")
        
        # Step 4: Save the notebook
        logger.debug(f"Saving notebook: {notebook_filename}")
        save_result = await mcp_service.call_mcp_tool("saveNotebook", {
            "filename": notebook_filename
        })
        logger.debug(f"Save result: {save_result}")
        
        # Step 5: Export notebook for download
        logger.debug(f"Exporting notebook for download: {notebook_filename}")
        export_result = await mcp_service.call_mcp_tool("exportNotebook", {
            "filename": notebook_filename,
            "format": "ipynb"
        })
        logger.debug(f"Export result: {export_result}")
        
        # Step 6: Get notebook content for download
        if export_result and "content" in str(export_result):
            notebook_json = export_result
        else:
            # Fallback: try to load the notebook directly
            load_result = await mcp_service.call_mcp_tool("loadNotebook", {
                "filepath": notebook_filename
            })
            
            if load_result:
                # Create a basic notebook structure if needed
                notebook_json = {
                    "cells": [
                        {
                            "cell_type": "markdown",
                            "metadata": {},
                            "source": [markdown_content]
                        },
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "outputs": [],
                            "source": [code_content]
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
                            "version": "3.8.0"
                        }
                    },
                    "nbformat": 4,
                    "nbformat_minor": 4
                }
            else:
                raise Exception("Failed to load notebook content")
        
        # Convert to JSON string if it's not already
        if isinstance(notebook_json, str):
            notebook_content = notebook_json
        else:
            notebook_content = json.dumps(notebook_json, indent=2)
        
        logger.info(f"Test notebook created successfully: {notebook_filename} ({len(notebook_content)} bytes)")
        
        # Return as downloadable file
        response = StreamingResponse(
            io.BytesIO(notebook_content.encode('utf-8')),
            media_type="application/x-ipynb+json",
            headers={
                "Content-Disposition": f"attachment; filename={notebook_filename}",
                "Content-Type": "application/x-ipynb+json",
                "Content-Length": str(len(notebook_content.encode('utf-8'))),
                "Cache-Control": "no-cache"
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create test notebook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create test notebook: {str(e)}"
        )


@router.get("/test-mcp-tools")
async def test_mcp_tools():
    """
    Test various MCP tools to ensure they're working correctly
    """
    logger.info("MCP tools test requested")
    
    try:
        if not mcp_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not initialized"
            )
        
        if not mcp_service.is_connected():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="MCP service not connected"
            )
        
        test_results = {}
        
        # Test 1: List available tools
        logger.debug("Testing: Get available tools")
        available_tools = mcp_service.get_available_tools()
        test_results["available_tools"] = {
            "success": True,
            "tools": available_tools,
            "count": len(available_tools)
        }
        
        # Test 2: List saved notebooks
        logger.debug("Testing: List saved notebooks")
        try:
            notebooks_result = await mcp_service.list_notebooks()
            test_results["list_notebooks"] = {
                "success": True,
                "result": notebooks_result
            }
        except Exception as e:
            test_results["list_notebooks"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 3: Test basic MCP tool call (if available)
        logger.debug("Testing: Basic MCP tool call")
        if "listSavedNotebooks" in available_tools:
            try:
                list_result = await mcp_service.call_mcp_tool("listSavedNotebooks", {})
                test_results["mcp_tool_call"] = {
                    "success": True,
                    "tool": "listSavedNotebooks",
                    "result": list_result
                }
            except Exception as e:
                test_results["mcp_tool_call"] = {
                    "success": False,
                    "tool": "listSavedNotebooks",
                    "error": str(e)
                }
        else:
            test_results["mcp_tool_call"] = {
                "success": False,
                "error": "listSavedNotebooks tool not available"
            }
        
        # Summary
        successful_tests = sum(1 for test in test_results.values() if test.get("success", False))
        total_tests = len(test_results)
        
        response = {
            "success": True,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests
            },
            "test_results": test_results,
            "mcp_service_status": {
                "initialized": mcp_service.is_initialized(),
                "connected": mcp_service.is_connected(),
                "has_credentials": mcp_service.has_api_key()
            }
        }
        
        logger.info(f"MCP tools test completed: {successful_tests}/{total_tests} tests passed")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MCP tools test failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MCP tools test failed: {str(e)}"
        )


@router.get("/health")
async def testing_health_check():
    """Health check for testing controller"""
    return {
        "status": "healthy",
        "controller": "testing",
        "message": "Testing controller is operational",
        "mcp_connected": mcp_service.is_connected() if mcp_service else False
    }