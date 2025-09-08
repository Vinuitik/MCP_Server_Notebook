from fastmcp import FastMCP
import requests
import json
from datetime import datetime, timedelta

mcp = FastMCP("KnowledgeMCP")


@mcp.tool()
def 



if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000, path="/knowledgeMCP/")
