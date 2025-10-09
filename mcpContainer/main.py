from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import requests
import json
import pickle
import os
import time
import asyncio
import uvicorn
from datetime import datetime, timedelta
from data_types import CodeCell, MarkdownCell, NotebookState
from utils import run_cell, debug_tool
from typing import Dict, Union, List, Any
from tools import register_notebook_tools, register_cell_tools, register_execution_tools

mcp = FastMCP("KnowledgeMCP")

# Initialize the singleton notebook state
notebook_state = NotebookState.get_instance()

register_notebook_tools(mcp, notebook_state)
register_cell_tools(mcp, notebook_state)
register_execution_tools(mcp, notebook_state)

# Create separate FastAPI app for HTTP endpoints
fastapi_app = FastAPI(title="Notebook File Server", description="HTTP endpoints for notebook file operations")

# Add regular FastAPI endpoints for direct file serving
@fastapi_app.get("/notebooks/{filename}")
async def download_notebook_file(filename: str):
    """Direct file download endpoint for notebook files"""
    try:
        # Ensure filename has .ipynb extension
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'
        
        # Construct file path
        notebooks_dir = '/app/notebooks'
        filepath = os.path.join(notebooks_dir, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail=f"Notebook file not found: {filename}")
        
        # Return the file directly
        return FileResponse(
            path=filepath,
            media_type="application/x-ipynb+json",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve notebook file: {str(e)}")


@fastapi_app.get("/notebooks/list/all")
async def list_notebook_files():
    """List all notebook files in the notebooks directory"""
    try:
        notebooks_dir = '/app/notebooks'
        
        # Create directory if it doesn't exist
        os.makedirs(notebooks_dir, exist_ok=True)
        
        # List all .ipynb files
        notebooks = [f for f in os.listdir(notebooks_dir) if f.endswith('.ipynb')]
        notebooks.sort()  # Sort alphabetically
        
        return JSONResponse({
            "success": True,
            "notebooks": notebooks,
            "count": len(notebooks),
            "message": f"Found {len(notebooks)} saved notebooks"
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "notebooks": [],
            "count": 0,
            "message": f"Failed to list notebooks: {str(e)}"
        }, status_code=500)


@fastapi_app.get("/health")
async def health_check():
    """Health check endpoint for FastAPI server"""
    return JSONResponse({
        "status": "healthy",
        "service": "notebook-file-server",
        "timestamp": datetime.now().isoformat()
    })


async def run_mcp_server():
    """Run the MCP server asynchronously"""
    print("Starting MCP server on port 8002...")
    await mcp.run_async(transport="streamable-http", host="0.0.0.0", port=8002, path="/noteBooks/")


async def run_fastapi_server():
    """Run the FastAPI server asynchronously"""
    print("Starting FastAPI server on port 8003...")
    config = uvicorn.Config(
        fastapi_app, 
        host="0.0.0.0", 
        port=8003,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """Main function to run both servers concurrently"""
    print("Starting dual server setup...")
    print("MCP Server: http://localhost:8002/noteBooks/")
    print("FastAPI Server: http://localhost:8003")
    
    try:
        # Run both servers concurrently
        await asyncio.gather(
            run_mcp_server(),
            run_fastapi_server(),
            return_exceptions=True
        )
    except Exception as e:
        print(f"Error running servers: {e}")
    except KeyboardInterrupt:
        print("Shutting down servers...")


if __name__ == "__main__":
    asyncio.run(main())