"""
Schema definition for history information operations.

This module defines the response schema for the getHistoryInfo tool.
"""

from typing import TypedDict, List


class HistoryInfoResponse(TypedDict):
    """
    Schema for history information operation responses.
    
    Attributes:
        total_cells: Integer representing the total number of cells in history
        cell_types: List of strings indicating the types of cells in order
        code_cells: Integer count of code cells
        markdown_cells: Integer count of markdown cells
        executed_cells: Integer count of executed code cells
        global_execution_count: Integer representing the current global execution count
    """
    total_cells: int
    cell_types: List[str]
    code_cells: int
    markdown_cells: int
    executed_cells: int
    global_execution_count: int