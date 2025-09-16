"""
Schema definitions for notebook loading operations.

This module defines the response schema for the loadNotebook tool.
"""

from typing_extensions import TypedDict


class LoadNotebookResponse(TypedDict):
    """
    Schema for notebook loading operation responses.
    
    Attributes:
        loaded: Boolean indicating if the notebook was successfully loaded
        cells_loaded: Integer count of cells loaded from the notebook
        message: String with status message or error description
    """
    loaded: bool
    cells_loaded: int
    message: str