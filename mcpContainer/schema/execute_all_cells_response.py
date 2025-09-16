"""
Schema definitions for executing all cells operations.

This module defines the response schema for the executeAllCells tool.
"""

from typing_extensions import TypedDict
from typing import List, Dict, Any


class ExecuteAllCellsResponse(TypedDict):
    """
    Schema for execute all cells operation responses.
    
    Attributes:
        executed: Boolean indicating if all cells executed successfully
        total_cells: Integer total number of cells in notebook
        executed_cells: Integer number of code cells that were executed
        results: List of dictionaries with results for each executed cell
        message: String with status message or error description
    """
    executed: bool
    total_cells: int
    executed_cells: int
    results: List[Dict[str, Any]]
    message: str