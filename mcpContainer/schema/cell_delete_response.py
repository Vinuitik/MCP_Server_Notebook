"""
Schema definition for cell deletion operations.

This module defines the response schema for the deleteCell tool.
"""

from typing import TypedDict


class CellDeleteResponse(TypedDict):
    """
    Schema for cell deletion operation responses.
    
    Attributes:
        deleted: Boolean indicating if the cell was successfully deleted
        message: String with status message or error description
        new_total: Integer representing the new total number of cells after deletion
        deleted_cell_type: String indicating the type of the deleted cell (or empty on failure)
    """
    deleted: bool
    message: str
    new_total: int
    deleted_cell_type: str