from fastmcp import FastMCP
from utils import debug_tool
from typing import Dict, Union, List
from utils import serialize_execution_context
import os
import json
from datetime import datetime
from data_types import CodeCell, MarkdownCell, NotebookState
from schema import (
    SaveNotebookResponse,
    ListNotebooksResponse,
    DeleteNotebookResponse,
    LoadNotebookResponse,
    ExportNotebookResponse
)

def register_notebook_tools(mcp: FastMCP, notebook_state: NotebookState):
    @mcp.tool()
    @debug_tool
    def saveNotebook(filename: str) -> SaveNotebookResponse:
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
            # Get only user-defined variables (excluding built-ins)
            user_variables = notebook_state.get_user_variables()
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
                        "version": "3.12.0"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 4,
                "user_variables": user_variables,
                "global_execution_count": notebook_state.global_execution_count
            }
            
            # Convert cells to notebook format
            for cell in notebook_state.history:
                cell_data = {
                    "cell_type": cell.cell_type,
                    "metadata": getattr(cell, 'metadata', {}),
                    "source": cell.source.split('\n') if cell.source else [""]
                }
                
                if cell.cell_type == "code":
                    cell_data["execution_count"] = cell.execution_count
                    cell_data["outputs"] = getattr(cell, 'outputs', [])
                
                notebook_data["cells"].append(cell_data)
            
            # Test JSON serialization first before creating any files
            try:
                json_string = json.dumps(notebook_data, indent=2, ensure_ascii=False)
            except (TypeError, ValueError) as json_error:
                return {
                    "saved": False,
                    "filepath": "",
                    "message": f"Failed to serialize notebook data to JSON: {str(json_error)}"
                }
            
            # Ensure the filename has .ipynb extension
            if not filename.endswith('.ipynb'):
                filename += '.ipynb'
            
            # Create notebooks directory if it doesn't exist
            notebooks_dir = '/app/notebooks'
            os.makedirs(notebooks_dir, exist_ok=True)
            
            # Save to file (only after successful JSON serialization)
            filepath = os.path.join(notebooks_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_string)
            
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
    @debug_tool
    def listSavedNotebooks() -> ListNotebooksResponse:
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
    @debug_tool
    def deleteNotebook(filename: str) -> DeleteNotebookResponse:
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
    @debug_tool
    def loadNotebook(filepath: str) -> LoadNotebookResponse:
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
            notebook_state.history.clear()
            
            # Load execution context if available
            if "execution_context" in notebook_data:
                notebook_state.execution_context.clear()
                notebook_state.execution_context.update(notebook_data["execution_context"])
            
            # Load global execution count if available
            if "global_execution_count" in notebook_data:
                notebook_state.global_execution_count = notebook_data["global_execution_count"]
            
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
                
                notebook_state.history.append(cell)
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
    @debug_tool
    def exportNotebook(filename: str, format: str = "json") -> ExportNotebookResponse:
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
                    
                    for i, cell in enumerate(notebook_state.history):
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
                    
                    for i, cell in enumerate(notebook_state.history):
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
