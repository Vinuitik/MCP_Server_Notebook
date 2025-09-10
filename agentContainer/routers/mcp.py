from fastapi import APIRouter, Depends
from services.mcp_client import MCPClient
from dependencies.deps import get_mcp_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/tools")
async def get_available_tools(
    mcp_client: MCPClient = Depends(get_mcp_client)
):
    """Get available MCP tools"""
    return mcp_client.get_available_tools()

@router.get("/health")
async def mcp_health(
    mcp_client: MCPClient = Depends(get_mcp_client)
):
    """Check MCP server health"""
    is_healthy = mcp_client.health_check()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "mcp_server_connected": is_healthy
    }
