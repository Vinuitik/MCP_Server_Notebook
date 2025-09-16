"""
Schema definitions for notebook save operations.

This module defines the response schema for the saveNotebook tool.
"""

from typing_extensions import TypedDict


class SaveNotebookResponse(TypedDict):
    """
    Schema for notebook save operation responses.
    
    Attributes:
        saved: Boolean indicating if the notebook was successfully saved
        filepath: String with the full path to the saved file
        message: String with status message or error description
    """
    saved: bool
    filepath: str
    message: str