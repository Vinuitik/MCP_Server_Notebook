import google.generativeai as genai
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.llm_model)
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini AI"""
        try:
            generation_config = genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I'm having trouble processing your request right now."
    
    def create_notebook_prompt(self, user_message: str, tools_info: str) -> str:
        """Create a structured prompt for notebook operations"""
        return f"""You are an AI assistant that helps users manage Jupyter notebooks through MCP (Model Context Protocol) tools.

Available MCP Tools:
{tools_info}

Your job is to:
1. Understand what the user wants to do with their notebook
2. Provide clear, conversational responses about notebook operations
3. Be helpful and explain what actions can be performed

User's request: {user_message}

Respond conversationally and helpfully. If the user wants to create, run, or manage notebook cells, explain what you can help them with.
Keep your response concise but informative.
"""
