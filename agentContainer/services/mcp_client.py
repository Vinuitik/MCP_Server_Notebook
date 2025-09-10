import requests
import logging
from typing import Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.server_url = settings.mcp_server_url
        self.timeout = settings.mcp_timeout
        self.retry_attempts = settings.mcp_retry_attempts
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            response = requests.post(
                f"{self.server_url}/call/{tool_name}",
                json=arguments,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to call MCP tool {tool_name}: {e}")
            return {"error": f"Failed to call MCP tool: {str(e)}"}
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get list of available tools from MCP server"""
        try:
            response = requests.get(f"{self.server_url}/tools", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get tools: {e}")
            return {"error": f"Failed to get tools: {str(e)}"}
    
    def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
