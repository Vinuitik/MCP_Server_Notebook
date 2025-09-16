"""
Schema definitions for kernel restart operations.

This module defines the response schema for the restartKernel tool.
"""

from typing_extensions import TypedDict


class RestartKernelResponse(TypedDict):
    """
    Schema for kernel restart operation responses.
    
    Attributes:
        restarted: Boolean indicating if the kernel was successfully restarted
        message: String with status message or error description
    """
    restarted: bool
    message: str