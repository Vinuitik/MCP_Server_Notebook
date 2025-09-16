"""
Schema definition for cell move operations.

This module defines the response schema for the moveCell tool.
"""

from typing import TypedDict


class CellMoveResponse(TypedDict):
    """
    Schema for cell move operation responses.
    
    Attributes:
        moved: Boolean indicating if the cell was successfully moved
        message: String with status message or error description
        cell_type: String indicating the type of the moved cell (or empty on failure)
    """
    moved: bool
    message: str
    cell_type: str