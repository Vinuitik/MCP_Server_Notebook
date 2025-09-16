"""
Schema definition for cell update operations.

This module defines the response schema for the updateCell tool.
"""

from typing import TypedDict


class CellUpdateResponse(TypedDict):
    """
    Schema for cell update operation responses.
    
    Attributes:
        updated: Boolean indicating if the cell was successfully updated
        message: String with status message or error description
        cell_type: String indicating the type of the updated cell (or empty on failure)
    """
    updated: bool
    message: str
    cell_type: str