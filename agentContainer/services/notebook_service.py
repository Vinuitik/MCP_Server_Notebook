import logging
from typing import Optional
from services.mcp_client import MCPClient
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class NotebookService:
    def __init__(self, mcp_client: MCPClient, ai_service: AIService):
        self.mcp_client = mcp_client
        self.ai_service = ai_service
        self.conversation_history = []
    
    async def process_message(self, user_message: str) -> str:
        """Process user message using AI and MCP tools"""
        try:
            # Get tools context
            tools_info = self._get_tools_context()
            
            # Get AI response
            prompt = self.ai_service.create_notebook_prompt(user_message, tools_info)
            ai_response = await self.ai_service.generate_response(prompt)
            
            # Execute MCP actions if needed
            action_result = self._execute_mcp_actions(user_message)
            
            if action_result:
                return f"{ai_response}\n\n{action_result}"
            else:
                return ai_response
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _get_tools_context(self) -> str:
        """Get context about available MCP tools"""
        return """
        - createMarkdownCell(content): Create a markdown cell with given content
        - createCodeCell(source): Create a code cell with given source code  
        - runCell(index): Execute a cell at the given index
        - getHistory(): Get the current notebook history/cells
        """
    
    def _execute_mcp_actions(self, user_message: str) -> Optional[str]:
        """Execute MCP actions based on user intent"""
        user_lower = user_message.lower()
        
        # Simple intent detection for MCP tool calls
        if "create" in user_lower and "markdown" in user_lower:
            return self._handle_create_markdown(user_message)
        elif "create" in user_lower and "code" in user_lower:
            return self._handle_create_code(user_message)
        elif "run" in user_lower and "cell" in user_lower:
            return self._handle_run_cell(user_message)
        elif "history" in user_lower or "show" in user_lower:
            return self._handle_show_history()
        
        return None
    
    def _handle_create_markdown(self, message: str) -> str:
        """Handle markdown cell creation"""
        content = self._extract_content_after_keyword(message, "markdown")
        if not content:
            content = "# New Markdown Cell\n\nEdit this content as needed."
        
        result = self.mcp_client.call_tool("createMarkdownCell", {"content": content})
        
        if result.get("created"):
            return f"✅ Created markdown cell at index {result.get('index')}"
        else:
            return f"❌ Failed to create markdown cell: {result.get('message', 'Unknown error')}"
    
    def _handle_create_code(self, message: str) -> str:
        """Handle code cell creation"""
        code = self._extract_content_after_keyword(message, "code")
        if not code:
            code = "print('Hello from new code cell!')"
        
        result = self.mcp_client.call_tool("createCodeCell", {"source": code})
        
        if result.get("created"):
            return f"✅ Created code cell at index {result.get('index')}"
        else:
            return f"❌ Failed to create code cell: {result.get('message', 'Unknown error')}"
    
    def _handle_run_cell(self, message: str) -> str:
        """Handle cell execution"""
        words = message.split()
        index = None
        for word in words:
            if word.isdigit():
                index = int(word)
                break
        
        if index is None:
            return "❌ Please specify a cell index to run (e.g., 'run cell 0')"
        
        result = self.mcp_client.call_tool("runCell", {"index": index})
        
        if result.get("executed"):
            output = result.get("output", "No output")
            return f"✅ Executed cell {index}. Output: {output}"
        else:
            return f"❌ Failed to run cell {index}: {result.get('message', 'Unknown error')}"
    
    def _handle_show_history(self) -> str:
        """Handle showing notebook history"""
        result = self.mcp_client.call_tool("getHistory", {})
        
        if "history" in result:
            history = result["history"]
            if not history:
                return "📝 No cells in history yet."
            
            response = "📝 Current Notebook:\n\n"
            for i, cell in enumerate(history):
                cell_type = cell.get("cell_type", "unknown")
                if cell_type == "markdown":
                    content = cell.get("source", "")[:50]
                    response += f"Cell {i}: Markdown - {content}...\n"
                elif cell_type == "code":
                    source = cell.get("source", "")[:50]
                    response += f"Cell {i}: Code - {source}...\n"
            
            return response
        else:
            return f"❌ Failed to get history: {result.get('message', 'Unknown error')}"
    
    def _extract_content_after_keyword(self, message: str, keyword: str) -> str:
        """Extract content after a keyword in the message"""
        message_lower = message.lower()
        keyword_pos = message_lower.find(keyword)
        if keyword_pos == -1:
            return ""
        
        # Find content after keyword
        start_pos = keyword_pos + len(keyword)
        content = message[start_pos:].strip()
        
        # Remove common prefixes
        for prefix in ["cell", "with", ":", '"', "'", "that says", "containing"]:
            if content.lower().startswith(prefix):
                content = content[len(prefix):].strip()
        
        # Remove quotes if wrapped
        if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
            content = content[1:-1]
            
        return content
