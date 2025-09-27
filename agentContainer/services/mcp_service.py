"""
MCP Service - Handles all MCP server interactions
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class MCPService:
    """Service for managing MCP server connections and operations"""
    
    def __init__(self):
        self.credentials: Optional[service_account.Credentials] = None
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.mcp_client: Optional[Client] = None
        self.available_tools: List[str] = []
        self._initialized = False
        self._connected = False
        
        # Environment variables
        self.google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.project_id = os.getenv("PROJECT_ID")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        
    async def initialize(self) -> bool:
        """Initialize the MCP service"""
        try:
            print("🔐 Loading Google Cloud credentials...")
            self._load_google_credentials()
            
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
    
    def _load_google_credentials(self):
        """Load Google Cloud service account credentials"""
        if not self.google_credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required")
            
        if not os.path.exists(self.google_credentials_path):
            raise FileNotFoundError(f"Service account key file not found: {self.google_credentials_path}")
            
        self.credentials = service_account.Credentials.from_service_account_file(
            self.google_credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        print(f"✅ Loaded credentials for: {self.credentials.service_account_email}")
    
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
            self.available_tools = [tool.name for tool in tools]
            
        self._connected = True
        print(f"✅ Connected to MCP server. Available tools: {self.available_tools}")
    
    def _initialize_ai_agent(self):
        """Initialize the AI agent"""
        if not self.project_id:
            raise ValueError("PROJECT_ID environment variable is required")
            
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_credentials_path
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            credentials=self.credentials,
            project=self.project_id,
            temperature=0.7
        )
        print("✅ AI agent initialized")
    
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
    
    async def save_notebook(self, name: str, content: Dict[str, Any]) -> Any:
        """Save a notebook"""
        return await self.call_mcp_tool("saveNotebook", {
            "name": name,
            "content": content
        })
    
    async def load_notebook(self, name: str) -> Any:
        """Load a notebook"""
        return await self.call_mcp_tool("loadNotebook", {"name": name})
    
    async def delete_notebook(self, name: str) -> Any:
        """Delete a notebook"""
        return await self.call_mcp_tool("deleteNotebook", {"name": name})
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized
    
    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        return self._connected
    
    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools"""
        return self.available_tools.copy()
    
    def has_google_credentials(self) -> bool:
        """Check if Google credentials are loaded"""
        return self.credentials is not None