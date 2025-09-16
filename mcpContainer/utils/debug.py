"""
Debug utilities for MCP Server Notebook.

This module provides debugging tools and logging configuration for MCP tools.
"""

import functools
import time
import json
import logging
import sys
from typing import Any, Callable


def debug_tool(func: Callable) -> Callable:
    """
    Decorator to add debugging to MCP tool functions.
    Uses print() statements for debugging output since they work correctly with uvicorn.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()
        
        # Print tool invocation with inputs
        input_data = {
            'args': args,
            'kwargs': kwargs
        }
        print(f"🔧 TOOL CALLED: {tool_name}", flush=True)
        print(f"📥 INPUTS: {json.dumps(input_data, default=str, indent=2)}", flush=True)
        
        try:
            # Execute the original function
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Print successful output
            print(f"✅ SUCCESS: {tool_name}", flush=True)
            print(f"📤 OUTPUT: {json.dumps(result, default=str, indent=2)}", flush=True)
            print(f"⏱️  EXECUTION TIME: {execution_time:.4f} seconds", flush=True)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Print exception details
            print(f"❌ EXCEPTION in {tool_name}: {type(e).__name__}: {str(e)}", flush=True)
            print(f"⏱️  EXECUTION TIME: {execution_time:.4f} seconds", flush=True)
            
            # Re-raise the exception to maintain original behavior
            raise
            
        finally:
            print(f"🏁 TOOL FINISHED: {tool_name}", flush=True)
            print("-" * 80, flush=True)  # Separator line
    
    return wrapper


__all__ = ['debug_tool', 'mcp_logger']