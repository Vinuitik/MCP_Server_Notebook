"""
Pydantic models for the MCP Agent API
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str
    mcp_connected: bool


class MCPToolRequest(BaseModel):
    """Request model for calling MCP tools"""
    tool_name: str
    arguments: Dict[str, Any] = {}


class MCPToolResponse(BaseModel):
    """Response model for MCP tool calls"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


class NotebookRequest(BaseModel):
    """Request model for notebook operations"""
    name: str
    content: Optional[Dict[str, Any]] = None


class AgentStatusResponse(BaseModel):
    """Agent status response model"""
    agent_initialized: bool
    mcp_connected: bool
    available_tools: List[str]
    google_credentials_loaded: bool


class ChatMessage(BaseModel):
    """Chat message request model"""
    message: str


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
