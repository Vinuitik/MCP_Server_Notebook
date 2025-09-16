"""
Schema definitions for notebook deletion operations.

This module defines the response schema for the deleteNotebook tool.
"""

from typing_extensions import TypedDict


class DeleteNotebookResponse(TypedDict):
    """
    Schema for notebook deletion operation responses.
    
    Attributes:
        deleted: Boolean indicating if the notebook was successfully deleted
        message: String with status message or error description
    """
    deleted: bool
    message: str