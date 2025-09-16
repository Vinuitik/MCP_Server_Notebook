"""
Schema definitions for notebook export operations.

This module defines the response schema for the exportNotebook tool.
"""

from typing_extensions import TypedDict


class ExportNotebookResponse(TypedDict):
    """
    Schema for notebook export operation responses.
    
    Attributes:
        exported: Boolean indicating if the notebook was successfully exported
        filepath: String with the full path to the exported file
        message: String with status message or error description
    """
    exported: bool
    filepath: str
    message: str