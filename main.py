from fastmcp import FastMCP
import requests
import json
from datetime import datetime, timedelta
from data_types import CodeCell, MarkdownCell
from typing import Dict, Union

mcp = FastMCP("KnowledgeMCP")

# Global history to store all notebook cells
history = []


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
        history.append(markdown_cell)
        
        # Return success with current index
        current_index = len(history) - 1
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
        history.append(code_cell)
        
        # Return success with current index
        current_index = len(history) - 1
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


@mcp.tool()
def getHistoryInfo() -> Dict[str, Union[int, list]]:
    """
    Get information about the current notebook history.
    
    Returns:
        Dictionary with:
        - total_cells: int (total number of cells)
        - cell_types: list (types of cells in order)
    """
    return {
        "total_cells": len(history),
        "cell_types": [cell.cell_type for cell in history]
    }


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
    """
    try:
        if index < 0 or index >= len(history):
            return {
                "found": False,
                "content": f"Invalid index. History contains {len(history)} cells (0-{len(history)-1})",
                "cell_type": ""
            }
        
        cell = history[index]
        return {
            "found": True,
            "content": cell.source,
            "cell_type": cell.cell_type
        }
        
    except Exception as e:
        return {
            "found": False,
            "content": f"Error retrieving cell: {str(e)}",
            "cell_type": ""
        }


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
        
        if index < 0 or index > len(history):
            return {
                "created": False,
                "index": -1,
                "message": f"Invalid index. Must be between 0 and {len(history)} (inclusive)"
            }
        
        # Create the markdown cell
        markdown_cell = MarkdownCell(source=content.strip())
        
        # Insert at specified position
        history.insert(index, markdown_cell)
        
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
        
        if index < 0 or index > len(history):
            return {
                "created": False,
                "index": -1,
                "message": f"Invalid index. Must be between 0 and {len(history)} (inclusive)"
            }
        
        # Create the code cell
        code_cell = CodeCell(
            source=content.strip(),
            execution_count=None
        )
        
        # Insert at specified position
        history.insert(index, code_cell)
        
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
        if index < 0 or index >= len(history):
            return {
                "updated": False,
                "message": f"Invalid index. History contains {len(history)} cells (0-{len(history)-1})",
                "cell_type": ""
            }
        
        if not content or not content.strip():
            return {
                "updated": False,
                "message": "Content cannot be empty",
                "cell_type": ""
            }
        
        # Update the cell content
        cell = history[index]
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
        if index < 0 or index >= len(history):
            return {
                "deleted": False,
                "message": f"Invalid index. History contains {len(history)} cells (0-{len(history)-1})",
                "new_total": len(history),
                "deleted_cell_type": ""
            }
        
        # Get cell type before deletion for confirmation
        deleted_cell = history[index]
        deleted_cell_type = deleted_cell.cell_type
        
        # Remove the cell
        history.pop(index)
        
        return {
            "deleted": True,
            "message": f"{deleted_cell_type.capitalize()} cell at index {index} deleted successfully",
            "new_total": len(history),
            "deleted_cell_type": deleted_cell_type
        }
        
    except Exception as e:
        return {
            "deleted": False,
            "message": f"Failed to delete cell: {str(e)}",
            "new_total": len(history),
            "deleted_cell_type": ""
        }


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
        if from_index < 0 or from_index >= len(history):
            return {
                "moved": False,
                "message": f"Invalid from_index. History contains {len(history)} cells (0-{len(history)-1})",
                "cell_type": ""
            }
        
        if to_index < 0 or to_index >= len(history):
            return {
                "moved": False,
                "message": f"Invalid to_index. History contains {len(history)} cells (0-{len(history)-1})",
                "cell_type": ""
            }
        
        if from_index == to_index:
            return {
                "moved": True,
                "message": "Cell is already at the target position",
                "cell_type": history[from_index].cell_type
            }
        
        # Move the cell
        cell = history.pop(from_index)
        history.insert(to_index, cell)
        
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


@mcp.tool()
def clearHistory() -> Dict[str, Union[bool, str, int]]:
    """
    Clear all cells from the history.
    
    Returns:
        Dictionary with:
        - cleared: bool (True if successful, False otherwise)
        - message: str (status message)
        - previous_total: int (number of cells that were cleared)
    """
    try:
        previous_total = len(history)
        history.clear()
        
        return {
            "cleared": True,
            "message": f"History cleared successfully. Removed {previous_total} cells",
            "previous_total": previous_total
        }
        
    except Exception as e:
        return {
            "cleared": False,
            "message": f"Failed to clear history: {str(e)}",
            "previous_total": len(history)
        }



if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8002, path="/knowledgeMCP/")
