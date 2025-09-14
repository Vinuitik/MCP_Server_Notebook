"""
Debug utilities for MCP Server Notebook.

This module provides debugging tools and logging configuration for MCP tools.
"""

import functools
import time
import json
import logging
from typing import Any, Callable

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('/app/mcp_debug.log')  # File output
    ]
)

# Create logger for MCP tools
mcp_logger = logging.getLogger("MCP_Tools")


def debug_tool(func: Callable) -> Callable:
    """
    Decorator to add debugging to MCP tool functions.
    Logs tool usage, inputs, outputs, and exceptions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        
        # Log tool invocation with inputs
        input_data = {
            'args': args,
            'kwargs': kwargs
        }
        mcp_logger.info(f"🔧 TOOL CALLED: {tool_name}")
        mcp_logger.info(f"📥 INPUTS: {json.dumps(input_data, default=str, indent=2)}")
        
        try:
            # Execute the original function
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log successful output
            mcp_logger.info(f"✅ SUCCESS: {tool_name}")
            mcp_logger.info(f"📤 OUTPUT: {json.dumps(result, default=str, indent=2)}")
            mcp_logger.info(f"⏱️  EXECUTION TIME: {execution_time:.4f} seconds")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log exception details
            mcp_logger.error(f"❌ EXCEPTION in {tool_name}: {type(e).__name__}: {str(e)}")
            mcp_logger.error(f"⏱️  EXECUTION TIME: {execution_time:.4f} seconds")
            
            # Re-raise the exception to maintain original behavior
            raise
            
        finally:
            mcp_logger.info(f"🏁 TOOL FINISHED: {tool_name}")
            mcp_logger.info("-" * 80)  # Separator line
    
    return wrapper


__all__ = ['debug_tool', 'mcp_logger']