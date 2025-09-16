"""
Schema package for MCP Server Notebook

This package contains custom schema definitions for the MCP tools,
providing structured response types and input validation schemas.
"""

from .cell_creation_response import CellCreationResponse
from .cell_update_response import CellUpdateResponse
from .cell_delete_response import CellDeleteResponse
from .cell_move_response import CellMoveResponse
from .history_info_response import HistoryInfoResponse
from .cell_content_response import CellContentResponse
from .clear_history_response import ClearHistoryResponse

# Future schema imports will go here
# from .execution_response import ExecutionResponse

__all__ = [
    'CellCreationResponse',
    'CellUpdateResponse',
    'CellDeleteResponse',
    'CellMoveResponse',
    'HistoryInfoResponse',
    'CellContentResponse',
    'ClearHistoryResponse',
    # Future exports will be added here
    # 'ExecutionResponse',
]

__version__ = "1.0.0"