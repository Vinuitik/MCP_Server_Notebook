from services.mcp_service import MCPService
from typing import Dict, Any, List, Optional
import json
import os
import logging
import traceback
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
import asyncio
from dotenv import load_dotenv
from prompts.prompt_manager import prompt_manager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize prompt manager and log available prompts
try:
    available_prompts = prompt_manager.list_available_prompts()
    logger.info(f"Prompt manager initialized successfully. Available prompts: {available_prompts}")
    logger.info(f"Prompt version: {prompt_manager.get_version()}")
except Exception as e:
    logger.error(f"Failed to initialize prompt manager: {e}")
    logger.warning("Agent will attempt to continue but prompts may not load correctly")

MAX_ATTEMPTS = 5

# Initialize model lazily to avoid credential issues at import time
_model = None

def get_model():
    """Get or create the ChatAnthropic model with proper credentials"""
    global _model
    if _model is None:
        try:
            logger.info("Initializing ChatAnthropic model...")
            
            # Ensure API key is available
            api_key = os.getenv('ANTHROPIC_API_KEY')
            logger.info(f"🔐 Looking for API key: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else 'None'}")
            print(f"🔐 Looking for API key: {'*' * (len(api_key) - 4) + api_key[-4:] if api_key else 'None'}")
            
            if not api_key:
                error_msg = "ANTHROPIC_API_KEY environment variable not set"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Get model name from environment or use default
            model_name = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
            logger.info(f"🤖 Using Claude model: {model_name}")
            print(f"🤖 Using Claude model: {model_name}")
            
            # Initialize the model
            logger.debug("Creating ChatAnthropic instance...")
            _model = ChatAnthropic(
                model=model_name,
                anthropic_api_key=api_key,
                temperature=0.7,  # Add some creativity
                max_tokens=4096   # Higher token limit for Claude
            )
            logger.info(f"✅ ChatAnthropic model ({model_name}) initialized successfully")
            print(f"✅ ChatAnthropic model ({model_name}) initialized successfully")
            
        except Exception as e:
            error_msg = f"❌ Failed to initialize ChatAnthropic: {e}"
            logger.error(error_msg)
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(error_msg)
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
    logger.info("Agent entry phase started")
    logger.debug(f"Initial state: {state}")
    
    try:
        if state["mcp_service"]:
            logger.debug("Getting available tools from MCP service")
            state["available_tools"] = state["mcp_service"].get_available_tools()
            logger.info(f"Available tools: {state['available_tools']}")
        else:
            logger.warning("No MCP service available in state")
        
        system_prompt = prompt_manager.get_entry_prompt()

        prompt = f"""{system_prompt}

CURRENT TASK: Please refine the following task: {state['task']}

Previous outputs:
{chr(10).join(state['outputs'])}

Available MCP Tools: {', '.join(state.get('available_tools', []))}

Provide a refined task description that makes use of the available notebook tools and follows the MCP stateful workflow."""
        
        logger.debug(f"Sending prompt to model: {prompt[:200]}...")
        response = await get_model().ainvoke(prompt)
        response_content = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"Model response received (length: {len(response_content)})")
        logger.debug(f"Model response: {response_content[:500]}...")
        
        state["task"] = response_content
        logger.info("Entry phase completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Entry phase failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        state["outputs"].append(f"Entry phase error: {str(e)}")
        return state

async def refining(state):
    logger.info(f"Refining phase started (attempt {state['attempts']})")
    
    try:
        if state["attempts"] >= MAX_ATTEMPTS:
            logger.info(f"Maximum attempts ({MAX_ATTEMPTS}) reached, stopping refinement")
            state["keep_refining"] = False
            return state
        else:
            system_prompt = prompt_manager.get_refining_prompt()

            prompt = f"""{system_prompt}

Do you need to keep refining the code to accomplish the task: {state['task']}

Consider the MCP stateful workflow and whether you need to create more content, execute more operations, or if you're ready to save and finalize.

Answer yes or no. ONLY YES OR NO!"""
            
            logger.debug(f"Sending refinement prompt to model")
            response = await get_model().ainvoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            logger.info(f"Refinement decision: {response_text}")
            
            if "yes" in response_text.lower():
                state["keep_refining"] = True
                logger.info("Continuing refinement")
            else:
                state["keep_refining"] = False
                logger.info("Stopping refinement")
                
        return state
        
    except Exception as e:
        logger.error(f"Refining phase failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        state["keep_refining"] = False
        state["outputs"].append(f"Refining phase error: {str(e)}")
        return state

async def finished(state):
    logger.info("Finished phase started")
    
    try:
        # Get the current notebook data as the final result
        if state["mcp_service"]:
            logger.debug("Getting final notebook data from MCP service")
            try:
                # List notebooks to see what's available
                notebooks = await state["mcp_service"].list_notebooks()
                state["notebook_data"] = {"available_notebooks": notebooks}
                logger.info(f"Final notebook data: {notebooks}")
            except Exception as e:
                error_msg = f"Error getting notebook data: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Notebook data error traceback: {traceback.format_exc()}")
                state["outputs"].append(error_msg)
        else:
            logger.warning("No MCP service available for final notebook data")
        
        logger.info(f"Agent execution finished with {state['attempts']} attempts")
        logger.debug(f"Final state: {state}")
        return state
        
    except Exception as e:
        logger.error(f"Finished phase failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        state["outputs"].append(f"Finished phase error: {str(e)}")
        return state

async def code_attempt(state):
    logger.info(f"Code attempt phase started (attempt {state['attempts'] + 1})")
    
    try:
        system_prompt = prompt_manager.get_code_attempt_prompt()

        prompt = f"""{system_prompt}

CURRENT TASK: {state['task']}

Available MCP Tools: {', '.join(state.get('available_tools', []))}

Use the tools available to accomplish the task following the MCP stateful workflow.
Be systematic and check if each step runs properly. 
Remember to save your work using 'saveNotebook' when complete.

Provide specific tool calls and code that should be executed."""

        logger.debug(f"Sending code attempt prompt to model")
        
        # Get LangChain tools from MCP service for direct tool integration
        mcp_tools = []
        if state["mcp_service"]:
            try:
                mcp_tools = state["mcp_service"].get_langchain_tools()
                logger.info(f"Loaded {len(mcp_tools)} LangChain MCP tools")
            except Exception as e:
                logger.warning(f"Could not load LangChain tools: {e}")
        
        # If we have tools, bind them to the model for direct tool calling
        if mcp_tools:
            model_with_tools = get_model().bind_tools(mcp_tools)
            response = await model_with_tools.ainvoke(prompt)
        else:
            response = await get_model().ainvoke(prompt)
            
        response_text = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"Model response received for code attempt (length: {len(response_text)})")
        logger.debug(f"Model response: {response_text[:500]}...")
        
        # Check if model made tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"Model made {len(response.tool_calls)} tool calls")
            
            for tool_call in response.tool_calls:
                try:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    result = await state["mcp_service"].call_mcp_tool(tool_name, tool_args)
                    response_text += f"\n\n✅ Tool '{tool_name}' executed successfully: {result}"
                    logger.info(f"Tool execution result: {result}")
                    
                except Exception as e:
                    error_msg = f"❌ Error executing tool '{tool_call.get('name', 'unknown')}': {str(e)}"
                    logger.error(error_msg)
                    response_text += f"\n\n{error_msg}"
        
        # Fallback: Try to execute MCP tools based on text parsing (legacy approach)
        elif state["mcp_service"]:
            logger.debug("No tool calls found, attempting text-based tool parsing")
            try:
                # Parse potential tool calls from the response
                if "saveNotebook" in response_text:
                    logger.info("Found saveNotebook command in response")
                    filename = "agent_notebook.ipynb"  # default
                    logger.debug(f"Saving notebook as: {filename}")
                    result = await state["mcp_service"].call_mcp_tool("saveNotebook", {"filename": filename})
                    response_text += f"\n\n✅ Notebook saved: {result}"
                    logger.info(f"Notebook save result: {result}")
                
                if "createCodeCell" in response_text:
                    logger.info("Found createCodeCell command in response")
                    # This would need more sophisticated parsing
                    logger.debug("createCodeCell would need content extraction from response")
                    
            except Exception as e:
                error_msg = f"❌ Error using MCP tools: {str(e)}"
                logger.error(error_msg)
                logger.error(f"MCP tools error traceback: {traceback.format_exc()}")
                response_text += f"\n\n{error_msg}"
        else:
            logger.warning("No MCP service available for tool execution")
        
        state["outputs"].append(response_text)
        state["attempts"] += 1
        logger.info(f"Code attempt completed (total attempts: {state['attempts']})")
        return state
        
    except Exception as e:
        logger.error(f"Code attempt phase failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_output = f"Code attempt error: {str(e)}"
        state["outputs"].append(error_output)
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
    """Factory function to create an agent with MCP service pre-configured"""
    # Create a new state graph instance
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
        lambda state: "codeAttempt" if state.get("keep_refining", False) else "finished",
        {
            "codeAttempt": "codeAttempt",
            "finished": "finished"
        }
    )

    builder.add_edge("finished", END)
    
    # Compile the graph
    mcp_graph = builder.compile()
    
    # Store reference to MCP service (optional enhancement for future use)
    mcp_graph._mcp_service = mcp_service
    
    return mcp_graph

async def run_agent(task: str, mcp_service: MCPService) -> Dict[str, Any]:
    """Run the agent with a given task and MCP service"""
    logger.info(f"Starting agent run with task: {task[:100]}..." if len(task) > 100 else f"Starting agent run with task: {task}")
    logger.debug(f"MCP service provided: {type(mcp_service).__name__}")
    
    try:
        start_time = datetime.now()
        
        initial_state = AgenticState({
            "task": task,
            "mcp_service": mcp_service,
            "outputs": [],
            "attempts": 0,
            "keep_refining": True,
            "available_tools": [],
            "notebook_data": None
        })
        
        logger.debug(f"Initial state created: {initial_state}")
        
        logger.info("Creating agent graph...")
        agent_graph = await create_agent_with_mcp(mcp_service)
        logger.info("Agent graph created successfully")
        
        # Run the graph
        logger.info("Starting graph execution...")
        final_state = await agent_graph.ainvoke(initial_state)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Graph execution completed in {execution_time:.2f} seconds")
        logger.debug(f"Final state: {final_state}")
        
        result = {
            "task": final_state.get("task", ""),
            "outputs": final_state.get("outputs", []),
            "attempts": final_state.get("attempts", 0),
            "notebook_data": final_state.get("notebook_data"),
            "success": final_state.get("attempts", 0) > 0
        }
        
        logger.info(f"Agent run completed successfully: {result['success']} with {result['attempts']} attempts")
        return result
        
    except Exception as e:
        logger.error(f"Agent run failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return error state
        return {
            "task": task,
            "outputs": [f"Agent execution failed: {str(e)}"],
            "attempts": 0,
            "notebook_data": None,
            "success": False,
            "error": str(e)
        }