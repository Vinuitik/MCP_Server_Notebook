from fastmcp import FastMCP
from utils import debug_tool
from typing import Dict, Union
from data_types import CodeCell, MarkdownCell, NotebookState

def register_cell_tools(mcp: FastMCP, notebook_state: NotebookState):
    @debug_tool
    @mcp.tool()
    def createMarkdownCell(content: str) -> Dict[str, Union[bool, int, str]]:
        """
        Create a markdown cell with the given content and add it to the end of history.
        
        Args:
            content: The markdown content for the cell
            
        Returns:
            Dictionary with:
            - created: bool (True if successful, False otherwise)
            - index: int (current index in history, -1 if failed)
            - message: str (status message)
        """
        try:
            if not content or not content.strip():
                return {
                    "created": False,
                    "index": -1,
                    "message": "Content cannot be empty"
                }
            
            # Create the markdown cell
            markdown_cell = MarkdownCell(source=content.strip())
            
            # Add to history
            notebook_state.history.append(markdown_cell)
            
            # Return success with current index
            current_index = len(notebook_state.history) - 1
            return {
                "created": True,
                "index": current_index,
                "message": f"Markdown cell created successfully at index {current_index}"
            }
            
        except Exception as e:
            return {
                "created": False,
                "index": -1,
                "message": f"Failed to create markdown cell: {str(e)}"
            }


    @debug_tool
    @mcp.tool()
    def createCodeCell(content: str) -> Dict[str, Union[bool, int, str]]:
        """
        Create a code cell with the given content and add it to the end of history.
        
        Args:
            content: The code content for the cell
            
        Returns:
            Dictionary with:
            - created: bool (True if successful, False otherwise)
            - index: int (current index in history, -1 if failed)
            - message: str (status message)
        """
        try:
            if not content or not content.strip():
                return {
                    "created": False,
                    "index": -1,
                    "message": "Content cannot be empty"
                }
            
            # Create the code cell
            code_cell = CodeCell(
                source=content.strip(),
                execution_count= None
            )
            
            # Add to history
            notebook_state.history.append(code_cell)
            
            # Return success with current index
            current_index = len(notebook_state.history) - 1
            return {
                "created": True,
                "index": current_index,
                "message": f"Code cell created successfully at index {current_index}"
            }
            
        except Exception as e:
            return {
                "created": False,
                "index": -1,
                "message": f"Failed to create code cell: {str(e)}"
            }

    @debug_tool
    @mcp.tool()
    def getHistoryInfo() -> Dict[str, Union[int, list]]:
        """
        Get information about the current notebook history.
        
        Returns:
            Dictionary with:
            - total_cells: int (total number of cells)
            - cell_types: list (types of cells in order)
            - code_cells: int (number of code cells)
            - markdown_cells: int (number of markdown cells)
            - executed_cells: int (number of executed code cells)
            - global_execution_count: int (current global execution count)
        """
        
        cell_types = [cell.cell_type for cell in notebook_state.history]
        code_cells = sum(1 for cell in notebook_state.history if cell.cell_type == "code")
        markdown_cells = sum(1 for cell in notebook_state.history if cell.cell_type == "markdown")
        executed_cells = sum(1 for cell in notebook_state.history if cell.cell_type == "code" and getattr(cell, 'execution_count', None) is not None)
        
        return {
            "total_cells": len(notebook_state.history),
            "cell_types": cell_types,
            "code_cells": code_cells,
            "markdown_cells": markdown_cells,
            "executed_cells": executed_cells,
            "global_execution_count": notebook_state.global_execution_count
        }

    @debug_tool
    @mcp.tool()
    def getCellContent(index: int) -> Dict[str, Union[bool, str]]:
        """
        Get the content of a cell at the specified index.
        
        Args:
            index: The index of the cell in history
            
        Returns:
            Dictionary with:
            - found: bool (True if cell exists, False otherwise)
            - content: str (cell content or error message)
            - cell_type: str (type of the cell)
            - execution_count: int (execution count for code cells)
            - outputs: List (outputs for code cells)
        """
        try:
            if index < 0 or index >= len(notebook_state.history):
                return {
                    "found": False,
                    "content": f"Invalid index. History contains {len(notebook_state.history)} cells (0-{len(notebook_state.history)-1})",
                    "cell_type": "",
                    "execution_count": None,
                    "outputs": []
                }
            
            cell = notebook_state.history[index]
            result = {
                "found": True,
                "content": cell.source,
                "cell_type": cell.cell_type
            }
            
            # Add execution info for code cells
            if cell.cell_type == "code":
                result["execution_count"] = getattr(cell, 'execution_count', None)
                result["outputs"] = getattr(cell, 'outputs', [])
            else:
                result["execution_count"] = None
                result["outputs"] = []
            
            return result
            
        except Exception as e:
            return {
                "found": False,
                "content": f"Error retrieving cell: {str(e)}",
                "cell_type": "",
                "execution_count": None,
                "outputs": []
            }

    @debug_tool
    @mcp.tool()
    def insertMarkdownCell(content: str, index: int) -> Dict[str, Union[bool, int, str]]:
        """
        Insert a markdown cell at the specified index, shifting existing cells to the right.
        
        Args:
            content: The markdown content for the cell
            index: The position to insert the cell at (0-based)
            
        Returns:
            Dictionary with:
            - created: bool (True if successful, False otherwise)
            - index: int (actual index where cell was inserted, -1 if failed)
            - message: str (status message)
        """
        try:
            if not content or not content.strip():
                return {
                    "created": False,
                    "index": -1,
                    "message": "Content cannot be empty"
                }
            
            if index < 0 or index > len(notebook_state.history):
                return {
                    "created": False,
                    "index": -1,
                    "message": f"Invalid index. Must be between 0 and {len(notebook_state.history)} (inclusive)"
                }
            
            # Create the markdown cell
            markdown_cell = MarkdownCell(source=content.strip())
            
            # Insert at specified position
            notebook_state.history.insert(index, markdown_cell)
            
            return {
                "created": True,
                "index": index,
                "message": f"Markdown cell inserted successfully at index {index}"
            }
            
        except Exception as e:
            return {
                "created": False,
                "index": -1,
                "message": f"Failed to insert markdown cell: {str(e)}"
            }

    @debug_tool
    @mcp.tool()
    def insertCodeCell(content: str, index: int) -> Dict[str, Union[bool, int, str]]:
        """
        Insert a code cell at the specified index, shifting existing cells to the right.
        
        Args:
            content: The code content for the cell
            index: The position to insert the cell at (0-based)
            
        Returns:
            Dictionary with:
            - created: bool (True if successful, False otherwise)
            - index: int (actual index where cell was inserted, -1 if failed)
            - message: str (status message)
        """
        try:
            if not content or not content.strip():
                return {
                    "created": False,
                    "index": -1,
                    "message": "Content cannot be empty"
                }
            
            if index < 0 or index > len(notebook_state.history):
                return {
                    "created": False,
                    "index": -1,
                    "message": f"Invalid index. Must be between 0 and {len(notebook_state.history)} (inclusive)"
                }
            
            # Create the code cell
            code_cell = CodeCell(
                source=content.strip(),
                execution_count=None
            )
            
            # Insert at specified position
            notebook_state.history.insert(index, code_cell)
            
            return {
                "created": True,
                "index": index,
                "message": f"Code cell inserted successfully at index {index}"
            }
            
        except Exception as e:
            return {
                "created": False,
                "index": -1,
                "message": f"Failed to insert code cell: {str(e)}"
            }

    @debug_tool
    @mcp.tool()
    def updateCell(index: int, content: str) -> Dict[str, Union[bool, str]]:
        """
        Update the content of an existing cell at the specified index.
        
        Args:
            index: The index of the cell to update
            content: The new content for the cell
            
        Returns:
            Dictionary with:
            - updated: bool (True if successful, False otherwise)
            - message: str (status message)
            - cell_type: str (type of the updated cell)
        """
        try:
            if index < 0 or index >= len(notebook_state.history):
                return {
                    "updated": False,
                    "message": f"Invalid index. History contains {len(notebook_state.history)} cells (0-{len(notebook_state.history)-1})",
                    "cell_type": ""
                }
            
            if not content or not content.strip():
                return {
                    "updated": False,
                    "message": "Content cannot be empty",
                    "cell_type": ""
                }
            
            # Update the cell content
            cell = notebook_state.history[index]
            cell.source = content.strip()
            
            return {
                "updated": True,
                "message": f"Cell at index {index} updated successfully",
                "cell_type": cell.cell_type
            }
            
        except Exception as e:
            return {
                "updated": False,
                "message": f"Failed to update cell: {str(e)}",
                "cell_type": ""
            }

    @debug_tool
    @mcp.tool()
    def deleteCell(index: int) -> Dict[str, Union[bool, str, int]]:
        """
        Delete a cell at the specified index, shifting remaining cells to the left.
        
        Args:
            index: The index of the cell to delete
            
        Returns:
            Dictionary with:
            - deleted: bool (True if successful, False otherwise)
            - message: str (status message)
            - new_total: int (new total number of cells after deletion)
            - deleted_cell_type: str (type of the deleted cell)
        """
        try:
            if index < 0 or index >= len(notebook_state.history):
                return {
                    "deleted": False,
                    "message": f"Invalid index. History contains {len(notebook_state.history)} cells (0-{len(notebook_state.history)-1})",
                    "new_total": len(notebook_state.history),
                    "deleted_cell_type": ""
                }
            
            # Get cell type before deletion for confirmation
            deleted_cell = notebook_state.history[index]
            deleted_cell_type = deleted_cell.cell_type
            
            # Remove the cell
            notebook_state.history.pop(index)
            
            return {
                "deleted": True,
                "message": f"{deleted_cell_type.capitalize()} cell at index {index} deleted successfully",
                "new_total": len(notebook_state.history),
                "deleted_cell_type": deleted_cell_type
            }
            
        except Exception as e:
            return {
                "deleted": False,
                "message": f"Failed to delete cell: {str(e)}",
                "new_total": len(notebook_state.history),
                "deleted_cell_type": ""
            }

    @debug_tool
    @mcp.tool()
    def moveCell(from_index: int, to_index: int) -> Dict[str, Union[bool, str]]:
        """
        Move a cell from one position to another.
        
        Args:
            from_index: The current index of the cell to move
            to_index: The target index to move the cell to
            
        Returns:
            Dictionary with:
            - moved: bool (True if successful, False otherwise)
            - message: str (status message)
            - cell_type: str (type of the moved cell)
        """
        try:
            if from_index < 0 or from_index >= len(notebook_state.history):
                return {
                    "moved": False,
                    "message": f"Invalid from_index. History contains {len(notebook_state.history)} cells (0-{len(notebook_state.history)-1})",
                    "cell_type": ""
                }
            
            if to_index < 0 or to_index >= len(notebook_state.history):
                return {
                    "moved": False,
                    "message": f"Invalid to_index. History contains {len(notebook_state.history)} cells (0-{len(notebook_state.history)-1})",
                    "cell_type": ""
                }
            
            if from_index == to_index:
                return {
                    "moved": True,
                    "message": "Cell is already at the target position",
                    "cell_type": notebook_state.history[from_index].cell_type
                }
            
            # Move the cell
            cell = notebook_state.history.pop(from_index)
            notebook_state.history.insert(to_index, cell)
            
            return {
                "moved": True,
                "message": f"{cell.cell_type.capitalize()} cell moved from index {from_index} to {to_index}",
                "cell_type": cell.cell_type
            }
            
        except Exception as e:
            return {
                "moved": False,
                "message": f"Failed to move cell: {str(e)}",
                "cell_type": ""
            }

    @debug_tool
    @mcp.tool()
    def clearHistory() -> Dict[str, Union[bool, str, int]]:
        """
        Clear all cells from the history and optionally reset the execution context.
        
        Returns:
            Dictionary with:
            - cleared: bool (True if successful, False otherwise)
            - message: str (status message)
            - previous_total: int (number of cells that were cleared)
        """
        
        try:
            previous_total = notebook_state.clear_history()
            
            # Also clear execution context and reset execution count
            notebook_state.reset_execution_context()
            
            return {
                "cleared": True,
                "message": f"History cleared successfully. Removed {previous_total} cells and reset execution context",
                "previous_total": previous_total
            }
            
        except Exception as e:
            return {
                "cleared": False,
                "message": f"Failed to clear history: {str(e)}",
                "previous_total": len(notebook_state.history)
            }

