"""
Main FastAPI application for MCP Agent
"""
import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

from services.mcp_service import MCPService
from controllers.agent_controller import router as agent_router, set_mcp_service

# Load environment variables
load_dotenv()

# Configure logging levels to reduce noise
logging.getLogger("mcp.client").setLevel(logging.WARNING)  # Reduce MCP client logs
logging.getLogger("httpx").setLevel(logging.WARNING)       # Reduce HTTP client logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce access logs

# Global service instance
mcp_service = MCPService()



@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    print("🚀 Starting MCP Agent FastAPI server...")
    
    # Startup
    success = await mcp_service.initialize()
    if not success:
        print("❌ CRITICAL ERROR: Failed to initialize MCP service")
        sys.exit(1)
    
    # Inject service into controllers
    set_mcp_service(mcp_service)
    
    print("✅ MCP Agent is ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down MCP Agent...")


# Create FastAPI app
app = FastAPI(
    title="MCP Agent API",
    description="FastAPI server for MCP (Model Context Protocol) Agent interactions",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(agent_router, prefix="/api/v1", tags=["agent"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MCP Agent FastAPI Server", 
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    print("🌟 Starting MCP Agent FastAPI server...")
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",  # Reduce from "info" to "warning"
        access_log=False      # Disable access logs completely
    )