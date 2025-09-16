"""
Schema definitions for cell creation operations.

This module defines the response schema for cell creation tools like
createMarkdownCell and createCodeCell to replace complex return type annotations.
"""

from typing import TypedDict


class CellCreationResponse(TypedDict):
    """
    Schema for cell creation operation responses.
    
    Attributes:
        created: Boolean indicating if the cell was successfully created
        index: Integer index where the cell was inserted (-1 if failed)
        message: String with status message or error description
    """
    created: bool
    index: int
    message: str