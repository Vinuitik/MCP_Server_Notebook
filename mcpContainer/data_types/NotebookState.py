from typing import List, Dict, Any, Union
from .CodeCell import CodeCell
from .Mardown import MarkdownCell


class NotebookState:
    """
    Singleton class to manage the global state of the notebook including:
    - history: List of all cells in the notebook
    - execution_context: Dictionary containing variables from code execution
    - global_execution_count: Counter for cell executions
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotebookState, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not NotebookState._initialized:
            self.history: List[Union[CodeCell, MarkdownCell]] = []
            self.execution_context: Dict[str, Any] = {}
            self.global_execution_count: int = 1
            NotebookState._initialized = True

    def reset_execution_context(self):
        """Reset the execution context and global execution count"""
        self.execution_context.clear()
        self.global_execution_count = 1
        # Clear outputs from all cells and reset execution counts
        for cell in self.history:
            if cell.cell_type == "code":
                cell.outputs = []
                cell.execution_count = None

    def clear_history(self):
        """Clear all cells from history"""
        previous_total = len(self.history)
        self.history.clear()
        return previous_total

    def get_next_execution_count(self) -> int:
        """Get the next execution count and increment the global counter"""
        current_count = self.global_execution_count
        self.global_execution_count += 1
        return current_count

    def get_user_variables(self) -> Dict[str, str]:
        """Get user-defined variables from execution context (excluding built-ins)"""
        return {
            k: str(v) for k, v in self.execution_context.items() 
            if not k.startswith('__') and k not in ['__builtins__']
        }

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance