# MCP Agent Integration

This document describes the new agentic capabilities added to the MCP Server Notebook project.

## Overview

The project now includes an intelligent agent that can:
1. Connect to the MCP server to access notebook tools
2. Execute complex tasks using notebook operations
3. Return state information and downloadable notebooks
4. Provide API endpoints for interaction

## Agent Architecture

### AgenticState
The agent uses a state-based architecture with the following components:
- `task`: The current task being executed
- `outputs`: List of outputs from previous attempts
- `attempts`: Number of attempts made
- `keep_refining`: Whether to continue refining the approach
- `mcp_service`: Connection to the MCP server
- `notebook_data`: Current notebook state
- `available_tools`: List of available MCP tools

### Agent Workflow
1. **Entry**: Refines the task based on available tools
2. **Code Attempt**: Executes actions using MCP tools
3. **Refining**: Determines if more refinement is needed
4. **Routing Decision**: Decides next action
5. **Finished**: Completes the task and returns results

## API Endpoints

### Agent Endpoints

#### POST `/api/v1/agent/run`
Execute an agent task.

**Request Body:**
```json
{
  "task": "Create a simple Python notebook with data analysis examples",
  "save_notebook": true,
  "notebook_filename": "my_notebook.ipynb"
}
```

**Response:**
```json
{
  "success": true,
  "task": "Refined task description",
  "outputs": ["Step 1 output", "Step 2 output"],
  "attempts": 3,
  "notebook_data": {...}
}
```

#### GET `/api/v1/agent/download/{filename}`
Download a notebook file.

**Response:** Binary notebook file with appropriate headers for download.

#### GET `/api/v1/agent/notebook/{filename}`
Get notebook information and download URL.

**Response:**
```json
{
  "success": true,
  "filename": "my_notebook.ipynb",
  "download_url": "/api/v1/agent/download/my_notebook.ipynb"
}
```

### Existing Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Agent status
- `GET /api/v1/notebooks` - List all notebooks
- `POST /api/v1/notebooks` - Save a notebook
- `GET /api/v1/notebooks/{name}` - Load a notebook
- `DELETE /api/v1/notebooks/{name}` - Delete a notebook

## Running the System

### Prerequisites
1. Docker and Docker Compose
2. Python 3.12+
3. Required environment variables:
   - `GOOGLE_APPLICATION_CREDENTIALS`
   - `PROJECT_ID`
   - `MCP_SERVER_URL`

### Starting the Services
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs agentContainer
```

### Testing the Agent
```bash
# Run the integration test
python test_agent_integration.py
```

## Example Usage

### 1. Basic Task Execution
```python
import requests

response = requests.post("http://localhost:8001/api/v1/agent/run", json={
    "task": "Create a notebook with matplotlib examples",
    "save_notebook": True
})

result = response.json()
print(f"Task completed: {result['success']}")
```

### 2. Download Generated Notebook
```python
# Get notebook info
info_response = requests.get("http://localhost:8001/api/v1/agent/notebook/my_notebook.ipynb")
info = info_response.json()

if info['success']:
    # Download the notebook
    download_response = requests.get(f"http://localhost:8001{info['download_url']}")
    
    with open("my_notebook.ipynb", "wb") as f:
        f.write(download_response.content)
```

## MCP Tools Available to Agent

The agent has access to all MCP server tools:
- `createCodeCell` - Create new code cells
- `createMarkdownCell` - Create new markdown cells
- `executeCodeCell` - Execute code cells
- `saveNotebook` - Save notebook to file
- `loadNotebook` - Load notebook from file
- `listSavedNotebooks` - List all saved notebooks
- `deleteNotebook` - Delete a notebook
- `exportNotebook` - Export notebook in different formats
- `getCellContent` - Get content of specific cells
- `updateCellContent` - Update cell content
- `deleteCells` - Delete specific cells
- `moveCells` - Move cells to different positions

## Configuration

### Environment Variables
```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
PROJECT_ID=your-project-id

# MCP Server
MCP_SERVER_URL=http://mcpContainer:8000

# Server Configuration
HOST=0.0.0.0
PORT=8001
```

### Docker Configuration
The agent container is configured to:
- Connect to the MCP server container
- Expose port 8001 for API access
- Mount Google credentials securely
- Handle async operations efficiently

## Error Handling

The agent includes comprehensive error handling for:
- MCP server connection issues
- Tool execution failures
- Notebook operations errors
- Invalid task requests
- Network connectivity problems

## Future Enhancements

Potential improvements:
1. **Advanced Tool Parsing**: Better extraction of tool calls from LLM responses
2. **Streaming Responses**: Real-time updates during task execution
3. **Task Templates**: Pre-defined task templates for common operations
4. **Multi-Agent Coordination**: Multiple agents working together
5. **Enhanced State Management**: Persistent state across sessions
6. **Webhook Integration**: External system notifications