"""
Schema definitions for code cell execution operations.

This module defines the response schema for the executeCodeCell tool.
"""

from typing_extensions import TypedDict
from typing import Any, Optional


class ExecuteCodeCellResponse(TypedDict):
    """
    Schema for code cell execution operation responses.
    
    Attributes:
        executed: Boolean indicating if the cell was successfully executed
        stdout: String with standard output from execution
        result: Any result value from the last expression (if any)
        error: String with error message if execution failed
        execution_count: Integer execution count for the cell (-1 if failed)
        message: String with status message or error description
    """
    executed: bool
    stdout: str
    result: Any
    error: Optional[str]
    execution_count: int
    message: str