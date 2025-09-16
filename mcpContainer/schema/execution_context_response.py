"""
Schema definitions for execution context operations.

This module defines the response schema for the getExecutionContext tool.
"""

from typing_extensions import TypedDict
from typing import Dict, Any


class ExecutionContextResponse(TypedDict):
    """
    Schema for execution context retrieval operation responses.
    
    Attributes:
        success: Boolean indicating if the context was successfully retrieved
        variables: Dictionary with current variables in execution context
        variable_count: Integer count of variables in the context
        message: String with status message or error description
    """
    success: bool
    variables: Dict[str, Any]
    variable_count: int
    message: str