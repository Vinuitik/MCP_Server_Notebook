"""
MCP Agent Prompts Package

This package contains system prompts for the MCP agent with versioning support.
"""

from .prompt_manager import prompt_manager, PromptManager

__version__ = "1.0.0"
__all__ = ["prompt_manager", "PromptManager"]