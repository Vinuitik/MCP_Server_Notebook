from services.mcp_service import MCPService
from typing import Dict, Any, List, Optional
import json
import os
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MAX_ATTEMPTS = 5

# Initialize model lazily to avoid credential issues at import time
_model = None

def get_model():
    """Get or create the ChatGoogleGenerativeAI model with proper credentials"""
    global _model
    if _model is None:
        try:
            # Ensure credentials are available
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            print(f"🔐 Looking for credentials at: {credentials_path}")
            
            if not credentials_path:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            
            if not os.path.exists(credentials_path):
                raise ValueError(f"Google credentials file not found at: {credentials_path}")
            
            # Set the environment variable for Google Auth
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            print(f"✅ Google credentials loaded from: {credentials_path}")
            
            # Get model name from environment or use default
            model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
            print(f"🤖 Using Gemini model: {model_name}")
            
            # Initialize the model
            _model = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=None,  # Use service account instead
                convert_system_message_to_human=True,
                temperature=0.7,  # Add some creativity
                max_tokens=2048   # Reasonable token limit
            )
            print(f"✅ ChatGoogleGenerativeAI model ({model_name}) initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize ChatGoogleGenerativeAI: {e}")
            # For development, you could fallback to a mock model
            raise e
    
    return _model

class AgenticState(dict):
    keep_refining: bool = True
    task: str = ""
    outputs: list = []
    attempts: int = 0
    checking_outcome: str = ""
    mcp_service: Optional[MCPService] = None
    notebook_data: Optional[Dict[str, Any]] = None
    available_tools: List[str] = []
    
async def entry(state):
    if state["mcp_service"]:
        state["available_tools"] = state["mcp_service"].get_available_tools()
    
    prompt = f"""Please refine the following task: {state['task']}

Previous outputs:
{chr(10).join(state['outputs'])}

Available MCP Tools: {', '.join(state.get('available_tools', []))}

Provide a refined task description that makes use of the available notebook tools."""
    
    response = await get_model().ainvoke(prompt)
    state["task"] = response.content if hasattr(response, 'content') else str(response)
    return state

async def refining(state):
    if state["attempts"] >= MAX_ATTEMPTS:
        state["keep_refining"] = False
        return state
    else:
        prompt = f"""Based on the task: {state['task']}

Do you need to keep refining the code to accomplish it? Answer yes or no. ONLY YES OR NO!"""
        
        response = await get_model().ainvoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        if "yes" in response_text.lower():
            state["keep_refining"] = True
        else:
            state["keep_refining"] = False
    return state

async def finished(state):
    # Get the current notebook data as the final result
    if state["mcp_service"]:
        try:
            # List notebooks to see what's available
            notebooks = await state["mcp_service"].list_notebooks()
            state["notebook_data"] = {"available_notebooks": notebooks}
        except Exception as e:
            state["outputs"].append(f"Error getting notebook data: {str(e)}")
    
    return state

async def code_attempt(state):
    prompt = f"""Based on the task: {state['task']}

Available MCP Tools: {', '.join(state.get('available_tools', []))}

Use the tools available to you to accomplish the task. You can:
1. Create, execute, and manage notebook cells
2. Save and load notebooks  
3. Work with code and markdown cells
4. Export notebooks in different formats

Be systematic and check if each step runs properly. Order matters for execution.

Provide specific tool calls and code that should be executed."""

    response = await get_model().ainvoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    # Try to execute MCP tools based on the response
    if state["mcp_service"]:
        try:
            # Parse potential tool calls from the response
            # This is a simplified approach - in practice you'd want more sophisticated parsing
            if "saveNotebook" in response_text:
                # Extract filename if mentioned
                filename = "agent_notebook.ipynb"  # default
                result = await state["mcp_service"].call_mcp_tool("saveNotebook", {"filename": filename})
                response_text += f"\n\nNotebook saved: {result}"
            
            if "createCodeCell" in response_text:
                # This would need to be implemented in your MCP service
                pass
                
        except Exception as e:
            response_text += f"\n\nError using MCP tools: {str(e)}"
    
    state["outputs"].append(response_text)
    state["attempts"] += 1
    return state

# Create the graph using correct LangGraph API
builder = StateGraph(AgenticState)
builder.add_node("entry", entry)
builder.add_node("refining", refining)
builder.add_node("codeAttempt", code_attempt)
builder.add_node("finished", finished)

builder.set_entry_point("entry")

builder.add_edge("entry", "codeAttempt")
builder.add_edge("codeAttempt", "refining")

builder.add_conditional_edges(
    "refining",
    # Routing function based on keep_refining flag
    lambda state: "codeAttempt" if state.get("keep_refining", False) else "finished",
    {
        "codeAttempt": "codeAttempt",
        "finished": "finished"
    }
)

builder.add_edge("finished", END)

graph = builder.compile()

async def create_agent_with_mcp(mcp_service: MCPService):
    """Factory function to create an agent with MCP service"""
    return graph

async def run_agent(task: str, mcp_service: MCPService) -> Dict[str, Any]:
    """Run the agent with a given task and MCP service"""
    initial_state = AgenticState({
        "task": task,
        "mcp_service": mcp_service,
        "outputs": [],
        "attempts": 0,
        "keep_refining": True,
        "available_tools": [],
        "notebook_data": None
    })
    
    agent_graph = await create_agent_with_mcp(mcp_service)
    
    # Run the graph
    final_state = await agent_graph.ainvoke(initial_state)
    
    return {
        "task": final_state.get("task", ""),
        "outputs": final_state.get("outputs", []),
        "attempts": final_state.get("attempts", 0),
        "notebook_data": final_state.get("notebook_data"),
        "success": final_state.get("attempts", 0) > 0
    }