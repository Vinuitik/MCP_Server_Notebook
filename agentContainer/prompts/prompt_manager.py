"""
Prompt management utility for MCP Agent
Handles loading and versioning of system prompts
"""

import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages system prompts for the MCP agent with versioning support"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize the prompt manager
        
        Args:
            prompts_dir: Directory containing prompt files. If None, uses default.
        """
        if prompts_dir is None:
            # Default to the directory containing this file (the prompts directory)
            self.prompts_dir = Path(__file__).parent
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self.prompt_cache: Dict[str, str] = {}
        self.version = "1.0.0"  # Prompt version for tracking
        
        logger.info(f"PromptManager initialized with directory: {self.prompts_dir}")
        logger.info(f"Prompt version: {self.version}")
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        Load a system prompt from file
        
        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            
        Returns:
            The prompt content as a string
            
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        # Check cache first
        if prompt_name in self.prompt_cache:
            logger.debug(f"Loading prompt '{prompt_name}' from cache")
            return self.prompt_cache[prompt_name]
        
        # Load from file
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            error_msg = f"Prompt file not found: {prompt_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()
            
            # Cache the prompt
            self.prompt_cache[prompt_name] = prompt_content
            logger.info(f"Loaded prompt '{prompt_name}' from {prompt_file}")
            logger.debug(f"Prompt content length: {len(prompt_content)} characters")
            
            return prompt_content
            
        except Exception as e:
            error_msg = f"Error loading prompt file {prompt_file}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def get_entry_prompt(self) -> str:
        """Get the system prompt for the entry phase"""
        return self.load_prompt("entry_system_prompt")
    
    def get_refining_prompt(self) -> str:
        """Get the system prompt for the refining phase"""
        return self.load_prompt("refining_system_prompt")
    
    def get_code_attempt_prompt(self) -> str:
        """Get the system prompt for the code attempt phase"""
        return self.load_prompt("code_attempt_system_prompt")
    
    def clear_cache(self):
        """Clear the prompt cache (useful for reloading updated prompts)"""
        self.prompt_cache.clear()
        logger.info("Prompt cache cleared")
    
    def get_version(self) -> str:
        """Get the current prompt version"""
        return self.version
    
    def list_available_prompts(self) -> list:
        """List all available prompt files"""
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory does not exist: {self.prompts_dir}")
            return []
        
        prompt_files = list(self.prompts_dir.glob("*.txt"))
        prompt_names = [f.stem for f in prompt_files]
        logger.info(f"Available prompts: {prompt_names}")
        return prompt_names

# Global instance for easy access
prompt_manager = PromptManager()