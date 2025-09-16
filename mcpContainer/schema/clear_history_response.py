"""
Schema definition for history clearing operations.

This module defines the response schema for the clearHistory tool.
"""

from typing import TypedDict


class ClearHistoryResponse(TypedDict):
    """
    Schema for history clearing operation responses.
    
    Attributes:
        cleared: Boolean indicating if the history was successfully cleared
        message: String with status message or error description
        previous_total: Integer representing the number of cells that were cleared
    """
    cleared: bool
    message: str
    previous_total: int