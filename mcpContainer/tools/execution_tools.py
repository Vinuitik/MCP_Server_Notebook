from fastmcp import FastMCP
from utils import debug_tool, run_cell
from typing import Dict, Union, List
from data_types import NotebookState

def register_execution_tools(mcp: FastMCP, notebook_state: NotebookState):
    @mcp.tool()
    @debug_tool
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
        
        try:
            if index < 0 or index >= len(notebook_state.history):
                return {
                    "executed": False,
                    "stdout": "",
                    "result": None,
                    "error": f"Invalid index. History contains {len(notebook_state.history)} cells (0-{len(notebook_state.history)-1})",
                    "execution_count": -1,
                    "message": f"Invalid index. History contains {len(notebook_state.history)} cells (0-{len(notebook_state.history)-1})"
                }
            
            cell = notebook_state.history[index]
            
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
            execution_result = run_cell(cell.source, notebook_state.execution_context)
            
            # Update execution count
            cell.execution_count = notebook_state.get_next_execution_count()
            
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
    @debug_tool
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
        
        try:
            results = []
            executed_count = 0
            total_cells = len(notebook_state.history)
            
            for index, cell in enumerate(notebook_state.history):
                if cell.cell_type == "code":
                    # Execute the cell using persistent context
                    execution_result = run_cell(cell.source, notebook_state.execution_context)
                    
                    # Update execution count
                    cell.execution_count = notebook_state.get_next_execution_count()
                    
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
                "total_cells": len(notebook_state.history),
                "executed_cells": 0,
                "results": [],
                "message": f"Failed to execute cells: {str(e)}"
            }

    @mcp.tool()
    @debug_tool
    def restartKernel() -> Dict[str, Union[bool, str]]:
        """
        Restart the kernel by clearing the execution context and resetting execution count.
        
        Returns:
            Dictionary with:
            - restarted: bool (True if successful, False otherwise)
            - message: str (status message)
        """
        
        try:
            # Use the notebook state reset method
            notebook_state.reset_execution_context()
            
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
    @debug_tool
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
        
        try:
            # Use the notebook state method to get user variables
            user_variables = notebook_state.get_user_variables()
            
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
