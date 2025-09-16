"""
Schema definitions for notebook listing operations.

This module defines the response schema for the listSavedNotebooks tool.
"""

from typing_extensions import TypedDict
from typing import List


class ListNotebooksResponse(TypedDict):
    """
    Schema for notebook listing operation responses.
    
    Attributes:
        success: Boolean indicating if the listing was successful
        notebooks: List of notebook filenames found
        count: Integer count of notebooks found
        message: String with status message or error description
    """
    success: bool
    notebooks: List[str]
    count: int
    message: str