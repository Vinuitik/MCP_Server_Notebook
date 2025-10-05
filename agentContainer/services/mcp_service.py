"""
MCP Service - Handles all MCP server interactions
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from langchain_anthropic import ChatAnthropic
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPService:
    """Service for managing MCP server connections and operations"""
    
    def __init__(self):
        self.llm: Optional[ChatAnthropic] = None
        self.mcp_client: Optional[Client] = None
        self.available_tools: List[str] = []
        self._initialized = False
        self._connected = False
        
        # Environment variables
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8002")
        
    async def initialize(self) -> bool:
        """Initialize the MCP service"""
        try:
            print("🔌 Connecting to MCP server...")
            await self._connect_to_mcp_server()
            
            print("🤖 Initializing AI agent...")
            self._initialize_ai_agent()
            
            self._initialized = True
            print("✅ MCP Service initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize MCP service: {e}")
            return False
    
    async def _connect_to_mcp_server(self):
        """Connect to the MCP server"""
        if not self.mcp_server_url:
            raise ValueError("MCP_SERVER_URL environment variable is required")
            
        transport = StreamableHttpTransport(
            url=f"{self.mcp_server_url}/noteBooks/"
        )
        
        self.mcp_client = Client(transport)
        
        # Test connection and get available tools
        async with self.mcp_client:
            tools = await self.mcp_client.list_tools()
            print(f"🔧 Debug - tools type: {type(tools)}")
            print(f"🔧 Debug - tools content: {tools}")
            
            # Safely extract tool names
            self.available_tools = []
            if hasattr(tools, 'tools'):
                # If tools is a response object with a tools attribute
                tool_list = tools.tools
            else:
                # If tools is already a list
                tool_list = tools
                
            for tool in tool_list:
                print(f"🔧 Debug - tool type: {type(tool)}, tool: {tool}")
                if hasattr(tool, 'name'):
                    self.available_tools.append(tool.name)
                elif isinstance(tool, dict) and 'name' in tool:
                    self.available_tools.append(tool['name'])
                else:
                    print(f"⚠️ Warning - unexpected tool format: {tool}")
                    self.available_tools.append(str(tool))
            
        self._connected = True
        print(f"✅ Connected to MCP server. Available tools: {self.available_tools}")
    
    def _initialize_ai_agent(self):
        """Initialize the AI agent"""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            
        self.llm = ChatAnthropic(
            model=self.claude_model,
            anthropic_api_key=self.anthropic_api_key,
            temperature=0.7,
            max_tokens=4096
        )
        print(f"✅ AI agent initialized with model: {self.claude_model}")
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool"""
        if not self._connected or not self.mcp_client:
            raise RuntimeError("MCP service not connected")
            
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available. Available tools: {self.available_tools}")
        
        async with self.mcp_client:
            result = await self.mcp_client.call_tool(tool_name, arguments)
            return result.content[0].text if result.content else None
    
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
    
    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools"""
        return self.available_tools.copy()
    
    def has_api_key(self) -> bool:
        """Check if Anthropic API key is available"""
        return self.anthropic_api_key is not None