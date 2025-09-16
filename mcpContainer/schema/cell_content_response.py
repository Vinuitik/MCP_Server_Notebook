"""
Schema definition for cell content retrieval operations.

This module defines the response schema for the getCellContent tool.
"""

from typing import TypedDict, List, Optional


class CellContentResponse(TypedDict):
    """
    Schema for cell content retrieval operation responses.
    
    Attributes:
        found: Boolean indicating if the cell was found at the specified index
        content: String with cell content or error message
        cell_type: String indicating the type of the cell (or empty on failure)
        execution_count: Optional integer for execution count (code cells only)
        outputs: List of outputs for code cells (empty list for markdown cells or on failure)
    """
    found: bool
    content: str
    cell_type: str
    execution_count: Optional[int]
    outputs: List