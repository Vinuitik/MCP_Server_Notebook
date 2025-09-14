import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp import ClientSession
from mcp.client.sse import sse_client

# Load environment variables
load_dotenv()

class MCPAgent:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.llm = None
        self.mcp_session = None
        
    async def connect_to_mcp_server(self):
        """Connect to the MCP server using SSE"""
        server_url = f"{self.mcp_server_url}/noteBooks/"
        
        self.mcp_session = await sse_client(server_url)
        await self.mcp_session.__aenter__()
        
    def initialize_ai_agent(self):
        """Initialize AI agent with Gemini 2.5 model"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-exp",
            google_api_key=self.gemini_api_key,
            temperature=0.7
        )
        
    async def run(self):
        """Main execution method"""
        # Connect to MCP server
        await self.connect_to_mcp_server()
        
        # Initialize AI agent
        self.initialize_ai_agent()
        
        print("AI Agent initialized and connected to MCP server")

# Main execution
if __name__ == "__main__":
    import asyncio
    
    agent = MCPAgent()
    asyncio.run(agent.run())