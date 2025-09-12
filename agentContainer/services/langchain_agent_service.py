"""
Proper LangChain MCP Agent Service using langchain-mcp-adapters.
This follows the correct pattern from the ai_agent implementation.
"""

from typing import List, Any, Dict
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from config.settings import settings
import logging
import asyncio

logger = logging.getLogger(__name__)


class ProperMCPAgentService:
    """Proper MCP Agent Service using langchain-mcp-adapters"""
    
    def __init__(self):
        self.agent = None
        self.mcp_client = None
        self.llm = None
        self.tools = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the agent and all its dependencies"""
        if self._initialized:
            return
            
        logger.info("Initializing MCP Agent with LangChain adapters...")
        
        try:
            # Setup MCP client
            await self._setup_mcp_client()
            
            # Setup LLM
            self._setup_llm()
            
            # Create agent
            self._create_agent()
            
            self._initialized = True
            logger.info("MCP Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP Agent: {e}", exc_info=True)
            raise
    
    async def _setup_mcp_client(self) -> None:
        """Setup the MCP client and retrieve tools with retry logic"""
        max_retries = getattr(settings, 'mcp_retry_attempts', 3)
        retry_delay = 2
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Attempting to connect to MCP server (attempt {attempt + 1}/{max_retries + 1})")
                
                # Create MCP client using langchain-mcp-adapters
                self.mcp_client = MultiServerMCPClient({
                    "notebook_mcp": {
                        "transport": "streamable_http",
                        "url": settings.mcp_server_url,
                    }
                })
                
                # Get tools directly as LangChain tools
                self.tools = await self.mcp_client.get_tools()
                logger.info(f"Successfully retrieved {len(self.tools)} tools from MCP server")
                
                # Log available tools
                tool_names = [tool.name for tool in self.tools]
                logger.info(f"Available tools: {tool_names}")
                
                return
                
            except Exception as e:
                logger.warning(f"MCP connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect to MCP server after {max_retries + 1} attempts")
                    raise Exception(f"Could not connect to MCP server at {settings.mcp_server_url}: {str(e)}")
    
    def _setup_llm(self) -> None:
        """Setup the Google Gemini LLM"""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=settings.llm_temperature,
            transport="rest"
        )
        logger.info(f"LLM initialized with model: {settings.llm_model}")
    
    def _create_agent(self) -> None:
        """Create the ReAct agent with LLM and tools"""
        self.agent = create_react_agent(self.llm, self.tools)
        logger.info("ReAct agent created successfully with MCP tools")
    
    async def process_message(self, message: str) -> str:
        """
        Process a user message through the agent
        
        Args:
            message: User's input message
            
        Returns:
            Agent's response as a string
        """
        if not self._initialized:
            raise RuntimeError("Agent service not initialized. Call initialize() first.")
        
        logger.info(f"Processing message: {message[:100]}...")
        
        try:
            # Invoke the agent with the message
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": message}]
            })
            
            # Extract the response text from the result
            if "messages" in result and len(result["messages"]) > 0:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    response_text = last_message.content
                else:
                    response_text = str(last_message)
            else:
                response_text = str(result)
            
            logger.info("Message processed successfully")
            return response_text
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return f"I encountered an error while processing your request: {str(e)}"
    
    def get_tool_by_name(self, tool_name: str) -> Any:
        """Get a specific tool by name"""
        if not self.tools:
            return None
            
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def list_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        if not self.tools:
            return []
        return [tool.name for tool in self.tools]
    
    @property
    def is_initialized(self) -> bool:
        """Check if the service is initialized"""
        return self._initialized