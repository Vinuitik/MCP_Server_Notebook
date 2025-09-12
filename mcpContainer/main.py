from fastmcp import FastMCP
import requests
import json
import pickle
import os
from datetime import datetime, timedelta
from data_types import CodeCell, MarkdownCell
from utils import run_cell
from typing import Dict, Union, List, Any

mcp = FastMCP("KnowledgeMCP")

# Global history to store all notebook cells
history = []

# Global execution context to persist variables across cell executions
execution_context = {}

# Global execution counter
global_execution_count = 1


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
        - code_cells: int (number of code cells)
        - markdown_cells: int (number of markdown cells)
        - executed_cells: int (number of executed code cells)
        - global_execution_count: int (current global execution count)
    """
    global global_execution_count
    
    cell_types = [cell.cell_type for cell in history]
    code_cells = sum(1 for cell in history if cell.cell_type == "code")
    markdown_cells = sum(1 for cell in history if cell.cell_type == "markdown")
    executed_cells = sum(1 for cell in history if cell.cell_type == "code" and getattr(cell, 'execution_count', None) is not None)
    
    return {
        "total_cells": len(history),
        "cell_types": cell_types,
        "code_cells": code_cells,
        "markdown_cells": markdown_cells,
        "executed_cells": executed_cells,
        "global_execution_count": global_execution_count
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
        - execution_count: int (execution count for code cells)
        - outputs: List (outputs for code cells)
    """
    try:
        if index < 0 or index >= len(history):
            return {
                "found": False,
                "content": f"Invalid index. History contains {len(history)} cells (0-{len(history)-1})",
                "cell_type": "",
                "execution_count": None,
                "outputs": []
            }
        
        cell = history[index]
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
def executeCodeCell(index: int) -> Dict[str, Union[bool, str, int]]:
    """
    Execute a code cell at the specified index and update its execution count.
    
    Args:
        index: The index of the code cell to execute
        
    Returns:
        Dictionary with:
        - executed: bool (True if successful, False otherwise)
        - stdout: str (standard output from execution)
        - result: any (result of the last expression, if any)
        - error: str (error message if execution failed)
        - execution_count: int (new execution count for the cell)
        - message: str (status message)
    """
    global execution_context, global_execution_count
    
    try:
        if index < 0 or index >= len(history):
            return {
                "executed": False,
                "stdout": "",
                "result": None,
                "error": f"Invalid index. History contains {len(history)} cells (0-{len(history)-1})",
                "execution_count": -1,
                "message": f"Invalid index. History contains {len(history)} cells (0-{len(history)-1})"
            }
        
        cell = history[index]
        
        # Check if it's a code cell
        if cell.cell_type != "code":
            return {
                "executed": False,
                "stdout": "",
                "result": None,
                "error": f"Cell at index {index} is not a code cell (it's {cell.cell_type})",
                "execution_count": -1,
                "message": f"Cannot execute {cell.cell_type} cell"
            }
        
        # Execute the cell using persistent context
        execution_result = run_cell(cell.source, execution_context)
        
        # Update execution count
        cell.execution_count = global_execution_count
        global_execution_count += 1
        
        # Store outputs in the cell
        outputs = []
        
        # Add stdout output if present
        if execution_result.get("stdout"):
            outputs.append({
                "output_type": "stream",
                "name": "stdout",
                "text": execution_result["stdout"]
            })
        
        # Add result output if present
        if execution_result.get("result") is not None:
            outputs.append({
                "output_type": "execute_result",
                "execution_count": cell.execution_count,
                "data": {
                    "text/plain": str(execution_result["result"])
                }
            })
        
        # Add error output if present
        if execution_result.get("error"):
            outputs.append({
                "output_type": "error",
                "ename": "ExecutionError",
                "evalue": "Cell execution failed",
                "traceback": execution_result["error"].split('\n')
            })
        
        cell.outputs = outputs
        
        return {
            "executed": True,
            "stdout": execution_result.get("stdout", ""),
            "result": execution_result.get("result"),
            "error": execution_result.get("error"),
            "execution_count": cell.execution_count,
            "message": f"Code cell at index {index} executed successfully" if not execution_result.get("error") else f"Code cell executed with errors"
        }
        
    except Exception as e:
        return {
            "executed": False,
            "stdout": "",
            "result": None,
            "error": f"Failed to execute cell: {str(e)}",
            "execution_count": -1,
            "message": f"Failed to execute cell: {str(e)}"
        }


@mcp.tool()
def executeAllCells() -> Dict[str, Union[bool, str, int, List[Dict]]]:
    """
    Execute all code cells in the notebook in order.
    
    Returns:
        Dictionary with:
        - executed: bool (True if all cells executed, False if any failed)
        - total_cells: int (total number of cells)
        - executed_cells: int (number of code cells executed)
        - results: List[Dict] (results for each executed cell)
        - message: str (status message)
    """
    global execution_context, global_execution_count
    
    try:
        results = []
        executed_count = 0
        total_cells = len(history)
        
        for index, cell in enumerate(history):
            if cell.cell_type == "code":
                # Execute the cell using persistent context
                execution_result = run_cell(cell.source, execution_context)
                
                # Update execution count
                cell.execution_count = global_execution_count
                global_execution_count += 1
                
                # Store outputs in the cell
                outputs = []
                
                # Add stdout output if present
                if execution_result.get("stdout"):
                    outputs.append({
                        "output_type": "stream",
                        "name": "stdout",
                        "text": execution_result["stdout"]
                    })
                
                # Add result output if present
                if execution_result.get("result") is not None:
                    outputs.append({
                        "output_type": "execute_result",
                        "execution_count": cell.execution_count,
                        "data": {
                            "text/plain": str(execution_result["result"])
                        }
                    })
                
                # Add error output if present
                if execution_result.get("error"):
                    outputs.append({
                        "output_type": "error",
                        "ename": "ExecutionError",
                        "evalue": "Cell execution failed",
                        "traceback": execution_result["error"].split('\n')
                    })
                
                cell.outputs = outputs
                executed_count += 1
                
                # Add to results
                results.append({
                    "index": index,
                    "executed": True,
                    "stdout": execution_result.get("stdout", ""),
                    "result": execution_result.get("result"),
                    "error": execution_result.get("error"),
                    "execution_count": cell.execution_count
                })
                
                # If there's an error, you might want to continue or stop
                # For now, we'll continue execution even with errors
        
        success = all(not result.get("error") for result in results)
        
        return {
            "executed": success,
            "total_cells": total_cells,
            "executed_cells": executed_count,
            "results": results,
            "message": f"Executed {executed_count} code cells out of {total_cells} total cells" + 
                      ("" if success else " (some cells had errors)")
        }
        
    except Exception as e:
        return {
            "executed": False,
            "total_cells": len(history),
            "executed_cells": 0,
            "results": [],
            "message": f"Failed to execute cells: {str(e)}"
        }


@mcp.tool()
def restartKernel() -> Dict[str, Union[bool, str]]:
    """
    Restart the kernel by clearing the execution context and resetting execution count.
    
    Returns:
        Dictionary with:
        - restarted: bool (True if successful, False otherwise)
        - message: str (status message)
    """
    global execution_context, global_execution_count
    
    try:
        # Clear the execution context
        execution_context.clear()
        
        # Reset execution count
        global_execution_count = 1
        
        # Clear outputs from all cells and reset execution counts
        for cell in history:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None
        
        return {
            "restarted": True,
            "message": "Kernel restarted successfully. All variables cleared and execution counts reset."
        }
        
    except Exception as e:
        return {
            "restarted": False,
            "message": f"Failed to restart kernel: {str(e)}"
        }


@mcp.tool()
def getExecutionContext() -> Dict[str, Union[bool, Dict, str]]:
    """
    Get the current execution context (variables and their values).
    
    Returns:
        Dictionary with:
        - success: bool (True if successful, False otherwise)
        - variables: Dict (current variables in execution context)
        - variable_count: int (number of variables)
        - message: str (status message)
    """
    global execution_context
    
    try:
        # Filter out built-in variables and functions
        user_variables = {
            k: str(v) for k, v in execution_context.items() 
            if not k.startswith('__') and k not in ['__builtins__']
        }
        
        return {
            "success": True,
            "variables": user_variables,
            "variable_count": len(user_variables),
            "message": f"Retrieved {len(user_variables)} user-defined variables"
        }
        
    except Exception as e:
        return {
            "success": False,
            "variables": {},
            "variable_count": 0,
            "message": f"Failed to get execution context: {str(e)}"
        }


@mcp.tool()
def saveNotebook(filename: str) -> Dict[str, Union[bool, str]]:
    """
    Save the current notebook state to a file.
    
    Args:
        filename: The name of the file to save the notebook to
        
    Returns:
        Dictionary with:
        - saved: bool (True if successful, False otherwise)
        - filepath: str (full path to saved file)
        - message: str (status message)
    """
    try:
        # Create a notebook structure
        notebook_data = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4,
            "execution_context": execution_context,
            "global_execution_count": global_execution_count
        }
        
        # Convert cells to notebook format
        for cell in history:
            cell_data = {
                "cell_type": cell.cell_type,
                "metadata": getattr(cell, 'metadata', {}),
                "source": cell.source.split('\n') if cell.source else [""]
            }
            
            if cell.cell_type == "code":
                cell_data["execution_count"] = cell.execution_count
                cell_data["outputs"] = getattr(cell, 'outputs', [])
            
            notebook_data["cells"].append(cell_data)
        
        # Ensure the filename has .ipynb extension
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'
        
        # Create notebooks directory if it doesn't exist
        notebooks_dir = '/app/notebooks'
        os.makedirs(notebooks_dir, exist_ok=True)
        
        # Save to file
        filepath = os.path.join(notebooks_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook_data, f, indent=2, ensure_ascii=False)
        
        return {
            "saved": True,
            "filepath": filepath,
            "message": f"Notebook saved successfully to {filepath}"
        }
        
    except Exception as e:
        return {
            "saved": False,
            "filepath": "",
            "message": f"Failed to save notebook: {str(e)}"
        }


@mcp.tool()
def listSavedNotebooks() -> Dict[str, Union[bool, List[str], str]]:
    """
    List all saved notebook files.
    
    Returns:
        Dictionary with:
        - success: bool (True if successful, False otherwise)
        - notebooks: List[str] (list of notebook filenames)
        - count: int (number of notebooks found)
        - message: str (status message) 
    """
    try:
        notebooks_dir = '/app/notebooks'
        
        # Create directory if it doesn't exist
        os.makedirs(notebooks_dir, exist_ok=True)
        
        # List all .ipynb files
        notebooks = [f for f in os.listdir(notebooks_dir) if f.endswith('.ipynb')]
        notebooks.sort()  # Sort alphabetically
        
        return {
            "success": True,
            "notebooks": notebooks,
            "count": len(notebooks),
            "message": f"Found {len(notebooks)} saved notebooks"
        }
        
    except Exception as e:
        return {
            "success": False,
            "notebooks": [],
            "count": 0,
            "message": f"Failed to list notebooks: {str(e)}"
        }


@mcp.tool()
def deleteNotebook(filename: str) -> Dict[str, Union[bool, str]]:
    """
    Delete a saved notebook file.
    
    Args:
        filename: The name of the notebook file to delete
        
    Returns:
        Dictionary with:
        - deleted: bool (True if successful, False otherwise)
        - message: str (status message)
    """
    try:
        # Ensure the filename has .ipynb extension
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'
        
        notebooks_dir = '/app/notebooks'
        filepath = os.path.join(notebooks_dir, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return {
                "deleted": False,
                "message": f"Notebook file not found: {filename}"
            }
        
        # Delete the file
        os.remove(filepath)
        
        return {
            "deleted": True,
            "message": f"Notebook {filename} deleted successfully"
        }
        
    except Exception as e:
        return {
            "deleted": False,
            "message": f"Failed to delete notebook: {str(e)}"
        }


@mcp.tool()
def loadNotebook(filepath: str) -> Dict[str, Union[bool, str, int]]:
    """
    Load a notebook from a file.
    
    Args:
        filepath: The path to the notebook file to load (can be full path or just filename)
        
    Returns:
        Dictionary with:
        - loaded: bool (True if successful, False otherwise)
        - cells_loaded: int (number of cells loaded)
        - message: str (status message)
    """
    global execution_context, global_execution_count, history
    
    try:
        # If filepath doesn't contain a directory, assume it's in the notebooks directory
        if not os.path.dirname(filepath):
            if not filepath.endswith('.ipynb'):
                filepath += '.ipynb'
            filepath = os.path.join('/app/notebooks', filepath)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return {
                "loaded": False,
                "cells_loaded": 0,
                "message": f"File not found: {filepath}"
            }
        
        # Load the notebook file
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        # Clear current history
        history.clear()
        
        # Load execution context if available
        if "execution_context" in notebook_data:
            execution_context.clear()
            execution_context.update(notebook_data["execution_context"])
        
        # Load global execution count if available
        if "global_execution_count" in notebook_data:
            global_execution_count = notebook_data["global_execution_count"]
        
        # Load cells
        cells_loaded = 0
        for cell_data in notebook_data.get("cells", []):
            cell_type = cell_data.get("cell_type", "")
            source = cell_data.get("source", [])
            
            # Join source lines if it's a list
            if isinstance(source, list):
                source = '\n'.join(source)
            
            if cell_type == "markdown":
                cell = MarkdownCell(source=source)
                cell.metadata = cell_data.get("metadata", {})
            elif cell_type == "code":
                cell = CodeCell(
                    source=source,
                    execution_count=cell_data.get("execution_count")
                )
                cell.metadata = cell_data.get("metadata", {})
                cell.outputs = cell_data.get("outputs", [])
            else:
                continue  # Skip unknown cell types
            
            history.append(cell)
            cells_loaded += 1
        
        return {
            "loaded": True,
            "cells_loaded": cells_loaded,
            "message": f"Notebook loaded successfully. {cells_loaded} cells loaded from {filepath}"
        }
        
    except Exception as e:
        return {
            "loaded": False,
            "cells_loaded": 0,
            "message": f"Failed to load notebook: {str(e)}"
        }


@mcp.tool()
def exportNotebook(filename: str, format: str = "json") -> Dict[str, Union[bool, str]]:
    """
    Export the current notebook to different formats.
    
    Args:
        filename: The name of the file to export to
        format: The format to export to ("json", "py", "md")
        
    Returns:
        Dictionary with:
        - exported: bool (True if successful, False otherwise)
        - filepath: str (full path to exported file)
        - message: str (status message)
    """
    try:
        notebooks_dir = '/app/notebooks'
        os.makedirs(notebooks_dir, exist_ok=True)
        
        if format == "json":
            # Export as JSON (same as saveNotebook but different function)
            return saveNotebook(filename)
            
        elif format == "py":
            # Export as Python script
            if not filename.endswith('.py'):
                filename += '.py'
            
            filepath = os.path.join(notebooks_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Jupyter Notebook exported to Python\n")
                f.write(f"# Generated on {datetime.now().isoformat()}\n\n")
                
                for i, cell in enumerate(history):
                    if cell.cell_type == "markdown":
                        # Convert markdown to comments
                        f.write(f"# Cell {i} - Markdown\n")
                        for line in cell.source.split('\n'):
                            f.write(f"# {line}\n")
                        f.write("\n")
                    
                    elif cell.cell_type == "code":
                        f.write(f"# Cell {i} - Code\n")
                        if hasattr(cell, 'execution_count') and cell.execution_count:
                            f.write(f"# Execution count: {cell.execution_count}\n")
                        f.write(cell.source)
                        f.write("\n\n")
            
        elif format == "md":
            # Export as Markdown
            if not filename.endswith('.md'):
                filename += '.md'
            
            filepath = os.path.join(notebooks_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Jupyter Notebook\n\n")
                f.write(f"*Exported on {datetime.now().isoformat()}*\n\n")
                
                for i, cell in enumerate(history):
                    if cell.cell_type == "markdown":
                        f.write(cell.source)
                        f.write("\n\n")
                    
                    elif cell.cell_type == "code":
                        f.write("```python\n")
                        f.write(cell.source)
                        f.write("\n```\n\n")
                        
                        # Add outputs if available
                        if hasattr(cell, 'outputs') and cell.outputs:
                            for output in cell.outputs:
                                if output.get('output_type') == 'stream':
                                    f.write("```\n")
                                    f.write(output.get('text', ''))
                                    f.write("\n```\n\n")
                                elif output.get('output_type') == 'execute_result':
                                    data = output.get('data', {})
                                    if 'text/plain' in data:
                                        f.write("```\n")
                                        f.write(data['text/plain'])
                                        f.write("\n```\n\n")
        
        else:
            return {
                "exported": False,
                "filepath": "",
                "message": f"Unsupported format: {format}. Supported formats: json, py, md"
            }
        
        return {
            "exported": True,
            "filepath": filepath,
            "message": f"Notebook exported successfully to {filepath} in {format} format"
        }
        
    except Exception as e:
        return {
            "exported": False,
            "filepath": "",
            "message": f"Failed to export notebook: {str(e)}"
        }


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
    global execution_context, global_execution_count
    
    try:
        previous_total = len(history)
        history.clear()
        
        # Also clear execution context and reset execution count
        execution_context.clear()
        global_execution_count = 1
        
        return {
            "cleared": True,
            "message": f"History cleared successfully. Removed {previous_total} cells and reset execution context",
            "previous_total": previous_total
        }
        
    except Exception as e:
        return {
            "cleared": False,
            "message": f"Failed to clear history: {str(e)}",
            "previous_total": len(history)
        }



if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8002, path="/noteBooks/")
