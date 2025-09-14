from fastmcp import FastMCP
import requests
import json
import pickle
import os
import time
from datetime import datetime, timedelta
from data_types import CodeCell, MarkdownCell
from utils import run_cell, debug_tool, mcp_logger
from typing import Dict, Union, List, Any
from tools import register_notebook_tools, register_cell_tools, register_execution_tools

mcp = FastMCP("KnowledgeMCP")

# Global history to store all notebook cells
history = []

# Global execution context to persist variables across cell executions
execution_context = {}

# Global execution counter
global_execution_count = 1


register_notebook_tools(mcp)
register_cell_tools(mcp)
register_execution_tools(mcp)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8002, path="/noteBooks/")
