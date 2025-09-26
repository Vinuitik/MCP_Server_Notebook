import os
import sys
import httpx
from dotenv import load_dotenv
from google.auth import default
from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

print("🚀 Starting MCP Agent...")
print(f"Current working directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

class MCPAgent:
    def __init__(self):
        print("📋 Loading environment variables...")
        self.google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.project_id = os.getenv("PROJECT_ID")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        
        print(f"   GOOGLE_APPLICATION_CREDENTIALS: {self.google_credentials_path}")
        print(f"   PROJECT_ID: {self.project_id}")
        print(f"   MCP_SERVER_URL: {self.mcp_server_url}")
        
        self.credentials = None
        self.llm = None
        self.http_client = None
        
        # Validate required environment variables
        if not self.google_credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required")
        if not self.project_id:
            raise ValueError("PROJECT_ID environment variable is required")
        
        # Load Google Cloud credentials
        print("🔐 Loading Google Cloud credentials...")
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Google Cloud service account credentials"""
        # Resolve the absolute path for the credentials file
        if self.google_credentials_path:
            if not os.path.isabs(self.google_credentials_path):
                # Convert relative path to absolute path
                self.google_credentials_path = os.path.abspath(self.google_credentials_path)
            
            print(f"Looking for credentials file at: {self.google_credentials_path}")
            
            if os.path.exists(self.google_credentials_path):
                print("✅ Service account key file found")
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.google_credentials_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                print(f"✅ Loaded credentials for: {self.credentials.service_account_email}")
            else:
                print(f"❌ Service account key file not found at: {self.google_credentials_path}")
                raise FileNotFoundError(f"Service account key file not found: {self.google_credentials_path}")
        else:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required")
        
    async def connect_to_mcp_server(self):
        """Connect to the MCP server using HTTP client"""
        # For streamable HTTP transport, use httpx client
        self.http_client = httpx.AsyncClient(
            base_url=f"{self.mcp_server_url}/noteBooks/",
            timeout=30.0
        )
        
        # Test the connection
        try:
            response = await self.http_client.get("/")
            print(f"Connected to MCP server, status: {response.status_code}")
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            raise
        
    def initialize_ai_agent(self):
        """Initialize AI agent with Gemini 2.5 model using service account"""
        # Set up environment for Google authentication
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_credentials_path
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-exp",
            credentials=self.credentials,
            project=self.project_id,
            temperature=0.7
        )
        
    async def call_mcp_tool(self, tool_name: str, **kwargs):
        """Call an MCP tool via HTTP"""
        if not self.http_client:
            raise RuntimeError("Not connected to MCP server")
            
        try:
            response = await self.http_client.post(
                f"/tools/{tool_name}",
                json=kwargs
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling MCP tool {tool_name}: {e}")
            raise
        
    async def run(self):
        """Main execution method"""
        # Connect to MCP server
        await self.connect_to_mcp_server()
        
        # Initialize AI agent
        self.initialize_ai_agent()
        
        print("AI Agent initialized and connected to MCP server")
        
    async def close(self):
        """Clean up resources"""
        if self.http_client:
            await self.http_client.aclose()

# Main execution
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = MCPAgent()
        try:
            await agent.run()
        finally:
            await agent.close()
    
    asyncio.run(main())