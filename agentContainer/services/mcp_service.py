"""
MCP Service - Handles all MCP server interactions
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient


class MCPService:
    """Service for managing MCP server connections and operations"""
    
    def __init__(self):
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.mcp_client: Optional[MultiServerMCPClient] = None
        self.mcp_tools: List[Any] = []
        self.available_tools: List[str] = []
        self._initialized = False
        self._connected = False
        
        # Environment variables
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8002")
        
    async def initialize(self) -> bool:
        """Initialize the MCP service"""
        try:
            print("🔌 Connecting to MCP server...")
            await self._connect_to_mcp_server()
            
            self._initialized = True
            print("✅ MCP Service initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Failed to initialize MCP service: {e}")
            return False
    
    async def _connect_to_mcp_server(self):
        """Connect to the MCP server using LangChain MCP adapters with streamable_http transport"""
        if not self.mcp_server_url:
            raise ValueError("MCP_SERVER_URL environment variable is required")
            
        # Configure MCP server connection for streamable HTTP transport
        # For FastMCP streamable HTTP, use the full URL with path
        full_url = f"{self.mcp_server_url}/noteBooks/"
        
        server_config = {
            "notebook_server": {
                "transport": "streamable_http",
                "url": full_url
            }
        }
        
        try:
            # Create MCP client using LangChain adapters for streamable HTTP
            self.mcp_client = MultiServerMCPClient(server_config)
            
            # Get tools directly from the client
            self.mcp_tools = await self.mcp_client.get_tools()
            
            # Extract tool names
            self.available_tools = [tool.name for tool in self.mcp_tools]
            
            self._connected = True
            print(f"✅ Connected to MCP server. Available tools: {len(self.available_tools)}")
            
        except Exception as e:
            print(f"❌ CRITICAL ERROR: Failed to connect to MCP server: {e}")
            print(f"🔧 Attempted connection to: {full_url}")
            print(f"🔧 Make sure MCP server is running on {self.mcp_server_url}")
            self._connected = False
            self.available_tools = []
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool using the MCP client"""
        if not self._connected or not self.mcp_client:
            raise ValueError("MCP client not connected")
            
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available. Available tools: {self.available_tools}")
        
        try:
            # Find the tool object by name
            tool_obj = None
            for tool in self.mcp_tools:
                if tool.name == tool_name:
                    tool_obj = tool
                    break
            
            if tool_obj is None:
                raise ValueError(f"Tool object for '{tool_name}' not found")
            
            # Call the tool using its run method
            result = await tool_obj.arun(arguments)
            
            print(f"✅ MCP tool call '{tool_name}' succeeded")
            return result
            
        except Exception as e:
            print(f"❌ MCP tool call '{tool_name}' failed: {e}")
            raise
    
    async def list_notebooks(self) -> Any:
        """List all saved notebooks"""
        return await self.call_mcp_tool("listSavedNotebooks", {})
    
    async def save_notebook(self, filename: str, content: Dict[str, Any] = None) -> Any:
        """Save a notebook"""
        return await self.call_mcp_tool("saveNotebook", {
            "filename": filename
        })
    
    async def load_notebook(self, filepath: str) -> Any:
        """Load a notebook"""
        return await self.call_mcp_tool("loadNotebook", {"filepath": filepath})
    
    async def delete_notebook(self, filename: str) -> Any:
        """Delete a notebook"""
        return await self.call_mcp_tool("deleteNotebook", {"filename": filename})
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        return self._connected
    
    async def check_connection_status(self) -> bool:
        """Actively check if MCP server is reachable right now"""
        if not self.mcp_client:
            return False
            
        try:
            # Try to get tools list as a connection test
            tools = await self.mcp_client.get_tools()
            self._connected = True
            return True
        except Exception as e:
            print(f"🔍 Connection check failed: {e}")
            self._connected = False
            return False
    
    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools"""
        return self.available_tools.copy()
    
    def get_langchain_tools(self) -> List[Any]:
        """Get the actual LangChain tool objects for agent integration"""
        return self.mcp_tools.copy()
    
    def has_credentials(self) -> bool:
        """Check if Google credentials are available"""
        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        return google_creds is not None and os.path.exists(google_creds)