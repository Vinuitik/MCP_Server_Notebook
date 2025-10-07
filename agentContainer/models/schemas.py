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
    anthropic_api_key_loaded: bool


class ChatMessage(BaseModel):
    """Chat message request model"""
    message: str


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str


class AgentTaskRequest(BaseModel):
    """Request model for agent task execution"""
    task: str
    save_notebook: bool = True
    notebook_filename: Optional[str] = None


class AgentTaskResponse(BaseModel):
    """Response model for agent task execution"""
    success: bool
    task: str
    outputs: List[str]
    attempts: int
    notebook_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class NotebookDownloadResponse(BaseModel):
    """Response model for notebook download"""
    success: bool
    filename: str
    content: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
