from fastmcp import FastMCP
import requests
import json
import pickle
import os
import time
from datetime import datetime, timedelta
from data_types import CodeCell, MarkdownCell, NotebookState
from utils import run_cell, debug_tool, mcp_logger
from typing import Dict, Union, List, Any
from tools import register_notebook_tools, register_cell_tools, register_execution_tools

mcp = FastMCP("KnowledgeMCP")

# Initialize the singleton notebook state
notebook_state = NotebookState.get_instance()


register_notebook_tools(mcp, notebook_state)
register_cell_tools(mcp, notebook_state)
register_execution_tools(mcp, notebook_state)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8002, path="/noteBooks/")
