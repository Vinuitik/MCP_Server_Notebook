# Improved MCP Agent Container with LangChain

## Overview

This is an improved implementation of the MCP Agent Container that replaces manual intent detection with intelligent AI-powered tool selection using LangChain.

## Key Improvements

### 1. **Intelligent Tool Selection**
- **Before**: Manual string matching (`if "create" in user_lower and "markdown" in user_lower`)
- **After**: LangChain agent automatically decides which tools to use based on context and user intent

### 2. **Better Tool Definitions**
- **Before**: Hard-coded tool mappings with limited descriptions
- **After**: Comprehensive tool descriptions with proper Pydantic schemas for validation

### 3. **Conversation Memory**
- **Before**: No conversation history
- **After**: ConversationBufferWindowMemory keeps track of the last 10 exchanges for context

### 4. **Error Handling**
- **Before**: Basic error messages
- **After**: Graceful error handling with fallbacks and detailed logging

### 5. **Extensibility**
- **Before**: Adding new tools required manual intent detection code
- **After**: Simply add new tools with proper descriptions and schemas

## Architecture

### Core Components

1. **LangChainAgentService** (`services/langchain_agent_service.py`)
   - Main agent orchestrator
   - Tool definitions with proper schemas
   - Memory management
   - Agent executor with error handling

2. **ImprovedNotebookService** (`services/improved_notebook_service.py`)
   - Clean interface for the chat endpoints
   - Wraps the LangChain agent
   - Provides additional utility methods

3. **Improved Chat Router** (`routers/improved_chat.py`)
   - New `/v2/chat` endpoints
   - Additional endpoints for history management
   - Status monitoring

## Available Tools

### 1. `create_markdown_cell`
- **Purpose**: Create markdown documentation cells
- **Input**: `content: str` - The markdown content
- **Usage**: "Add a markdown cell explaining the data preprocessing steps"

### 2. `create_code_cell`
- **Purpose**: Create executable Python code cells
- **Input**: `content: str` - The Python code
- **Usage**: "Create a code cell that imports pandas and numpy"

### 3. `run_cell`
- **Purpose**: Execute code cells and see results
- **Input**: `index: int` - Cell index to execute
- **Usage**: "Run the first cell" or "Execute cell 2"

### 4. `get_notebook_history`
- **Purpose**: View all notebook cells and their status
- **Input**: None
- **Usage**: "Show me what's in the notebook" or "What cells do I have?"

### 5. `get_available_mcp_tools`
- **Purpose**: Get information about available tools
- **Input**: None
- **Usage**: "What can you help me with?" or "What tools are available?"

## API Endpoints

### New Endpoints (v2)

- `POST /v2/chat/` - Main chat endpoint using LangChain agent
- `GET /v2/chat/history` - Get conversation history
- `DELETE /v2/chat/history` - Clear conversation history
- `GET /v2/chat/status` - Get service and MCP server status
- `GET /v2/chat/health` - Health check

### Legacy Endpoints (maintained for compatibility)

- `POST /chat/` - Original chat endpoint
- `GET /tools` - Original tools endpoint

## Configuration

### New Dependencies

Add to `requirements.txt`:
```
langchain==0.1.0
langchain-google-genai==0.0.6
langchain-community==0.0.10
```

### Environment Variables

Same as before:
- `GEMINI_API_KEY` - Google Gemini API key
- `MCP_SERVER_URL` - MCP server endpoint

## Usage Examples

### Natural Language Examples

1. **Documentation**: "Add a markdown cell that explains what this notebook does"
2. **Code Creation**: "Create a code cell that loads a CSV file into a pandas DataFrame"
3. **Execution**: "Run the data loading cell"
4. **Exploration**: "Show me all the cells in this notebook"
5. **Help**: "What can you help me with?"

### Agent Intelligence

The agent can understand context and make intelligent decisions:

- **User**: "I need to analyze some sales data. Start by setting up the imports."
- **Agent**: Creates a code cell with relevant imports (pandas, numpy, matplotlib, etc.)

- **User**: "Now add documentation about the data source"
- **Agent**: Creates a markdown cell with a template for data source documentation

- **User**: "Execute the imports"
- **Agent**: Runs the appropriate cell and shows results

## Deployment

### Docker

The container builds and runs the same way:

```bash
docker-compose up --build
```

### Access Points

- **Legacy Chat**: `http://localhost:9001/chat`
- **Improved Chat**: `http://localhost:9001/v2/chat`
- **API Docs**: `http://localhost:9001/docs`

## Benefits

1. **Better User Experience**: More natural conversations
2. **Intelligent Tool Selection**: No more rigid command patterns
3. **Context Awareness**: Remembers previous interactions
4. **Easier Maintenance**: Adding new tools is much simpler
5. **Better Error Handling**: Graceful failure recovery
6. **Future-Proof**: Easy to extend with new capabilities

## Migration

- **Existing clients** can continue using `/chat` endpoint
- **New clients** should use `/v2/chat` for better experience
- **No breaking changes** to existing functionality