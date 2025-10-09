"""
Schema package for MCP Server Notebook

This package contains custom schema definitions for the MCP tools,
providing structured response types and input validation schemas.
"""

# Cell operation schemas
from .cell_creation_response import CellCreationResponse
from .cell_update_response import CellUpdateResponse
from .cell_delete_response import CellDeleteResponse
from .cell_move_response import CellMoveResponse
from .history_info_response import HistoryInfoResponse
from .cell_content_response import CellContentResponse
from .clear_history_response import ClearHistoryResponse

# Notebook operation schemas
from .save_notebook_response import SaveNotebookResponse
from .list_notebooks_response import ListNotebooksResponse
from .delete_notebook_response import DeleteNotebookResponse
from .load_notebook_response import LoadNotebookResponse

# Execution operation schemas
from .execute_code_cell_response import ExecuteCodeCellResponse
from .execute_all_cells_response import ExecuteAllCellsResponse
from .restart_kernel_response import RestartKernelResponse
from .execution_context_response import ExecutionContextResponse

__all__ = [
    # Cell operation schemas
    'CellCreationResponse',
    'CellUpdateResponse',
    'CellDeleteResponse',
    'CellMoveResponse',
    'HistoryInfoResponse',
    'CellContentResponse',
    'ClearHistoryResponse',
    # Notebook operation schemas
    'SaveNotebookResponse',
    'ListNotebooksResponse',
    'DeleteNotebookResponse',
    'LoadNotebookResponse',
    # Execution operation schemas
    'ExecuteCodeCellResponse',
    'ExecuteAllCellsResponse',
    'RestartKernelResponse',
    'ExecutionContextResponse',
]

__version__ = "1.0.0"