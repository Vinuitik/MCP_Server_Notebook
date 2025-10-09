from services.mcp_service import MCPService
from typing import Dict, Any, List, Optional
import json
import os
import logging
import traceback
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from google.auth import default
import asyncio
from dotenv import load_dotenv
from prompts.prompt_manager import prompt_manager

# Load environment variables
load_dotenv()

# Set up enhanced logging for agent debugging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
    datefmt='%H:%M:%S'
)

# Create agent-specific logger
logger = logging.getLogger('AGENT')
logger.setLevel(logging.DEBUG)

# Reduce noise from other libraries
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('anthropic').setLevel(logging.WARNING)
logging.getLogger('langchain').setLevel(logging.WARNING)
logging.getLogger('langgraph').setLevel(logging.WARNING)

# Initialize prompt manager and log available prompts
try:
    available_prompts = prompt_manager.list_available_prompts()
    logger.info(f"✅ Prompt manager initialized with prompts: {available_prompts}")
except Exception as e:
    logger.error(f"❌ CRITICAL: Failed to initialize prompt manager: {e}")
    logger.warning("⚠️  Agent will attempt to continue but prompts may not load correctly")

MAX_ATTEMPTS = 5

# Initialize model lazily to avoid credential issues at import time
_model = None

def get_model():
    """Get or create the ChatGoogleGenerativeAI model with proper credentials"""
    global _model
    if _model is None:
        logger.debug("🤖 Initializing ChatGoogleGenerativeAI model...")
        try:
            # Set up Google ADC credentials
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', './service-account-key.json')
            
            if not os.path.exists(credentials_path):
                error_msg = f"Google service account key file not found at: {credentials_path}"
                logger.error(f"❌ CRITICAL: {error_msg}")
                print(f"❌ CRITICAL: {error_msg}")
                raise ValueError(error_msg)
            
            # Set the environment variable for Google ADC
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            logger.debug(f"🔑 Google ADC credentials set: {credentials_path}")
            
            # Get model name from environment or use default
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0')
            logger.debug(f"🎯 Using model: {model_name}")
            
            # Initialize the model
            _model = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.7,  # Add some creativity
                max_tokens=4096   # Higher token limit for Gemini
            )
            logger.info(f"✅ ChatGoogleGenerativeAI model ({model_name}) initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize ChatGoogleGenerativeAI: {e}"
            logger.error(f"❌ CRITICAL: {error_msg}")
            logger.error(f"💥 Model initialization traceback: {traceback.format_exc()}")
            print(f"❌ CRITICAL: {error_msg}")
            raise e
    else:
        logger.debug("🤖 Using cached ChatGoogleGenerativeAI model")
    
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

def log_state_transition(from_state: str, to_state: str, state: AgenticState):
    """Log state transitions with key debugging info"""
    logger.info(f"🔄 STATE TRANSITION: {from_state} → {to_state}")
    logger.debug(f"   📊 Attempts: {state.get('attempts', 0)}")
    logger.debug(f"   🔧 Keep refining: {state.get('keep_refining', False)}")
    logger.debug(f"   📝 Outputs count: {len(state.get('outputs', []))}")
    logger.debug(f"   🛠️  Available tools: {len(state.get('available_tools', []))}")
    
    # Log MCP service status
    if state.get('mcp_service'):
        logger.debug(f"   🔌 MCP Service: CONNECTED")
    else:
        logger.warning(f"   🔌 MCP Service: DISCONNECTED ⚠️")

def log_mcp_operation(operation: str, success: bool, details: str = "", error: str = ""):
    """Log MCP service operations with detailed info"""
    if success:
        logger.info(f"✅ MCP {operation}: SUCCESS")
        if details:
            logger.debug(f"   📋 Details: {details}")
    else:
        logger.error(f"❌ MCP {operation}: FAILED")
        if error:
            logger.error(f"   💥 Error: {error}")
        if details:
            logger.debug(f"   📋 Details: {details}")
    
async def entry(state):
    log_state_transition("START", "ENTRY", state)
    
    try:
        # Check MCP service availability
        if state["mcp_service"]:
            logger.debug("🔌 MCP Service found in state")
            try:
                state["available_tools"] = state["mcp_service"].get_available_tools()
                log_mcp_operation("get_available_tools", True, f"Found {len(state['available_tools'])} tools")
            except Exception as mcp_error:
                log_mcp_operation("get_available_tools", False, error=str(mcp_error))
                state["available_tools"] = []
        else:
            logger.error("❌ CRITICAL: No MCP service available in state")
            state["available_tools"] = []
        
        logger.debug("📝 Loading entry prompt...")
        system_prompt = prompt_manager.get_entry_prompt()
        logger.debug(f"   📄 Prompt loaded (length: {len(system_prompt)})")

        prompt = f"""{system_prompt}

CURRENT TASK: Please refine the following task: {state['task']}

Previous outputs:
{chr(10).join(state['outputs'])}

Available MCP Tools: {', '.join(state.get('available_tools', []))}

Provide a refined task description that makes use of the available notebook tools and follows the MCP stateful workflow."""
        
        logger.debug(f"🤖 Sending prompt to model (length: {len(prompt)})")
        response = await get_model().ainvoke(prompt)
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        logger.info(f"✅ ENTRY phase completed")
        logger.debug(f"   📊 Response length: {len(response_content)}")
        logger.debug(f"   📝 Task refined: {response_content[:100]}..." if len(response_content) > 100 else f"   📝 Task refined: {response_content}")
        
        state["task"] = response_content
        return state
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Entry phase failed: {str(e)}")
        logger.error(f"   💥 Full traceback: {traceback.format_exc()}")
        state["outputs"].append(f"Entry phase error: {str(e)}")
        return state

async def refining(state):
    log_state_transition("CODE_ATTEMPT", "REFINING", state)
    
    try:
        if state["attempts"] >= MAX_ATTEMPTS:
            logger.warning(f"⏹️  STOPPING: Maximum attempts ({MAX_ATTEMPTS}) reached")
            logger.debug(f"   📊 Total outputs generated: {len(state.get('outputs', []))}")
            state["keep_refining"] = False
            return state
        else:
            logger.debug("📝 Loading refining prompt...")
            system_prompt = prompt_manager.get_refining_prompt()

            prompt = f"""{system_prompt}

Do you need to keep refining the code to accomplish the task: {state['task']}

Consider the MCP stateful workflow and whether you need to create more content, execute more operations, or if you're ready to save and finalize.

Answer yes or no. ONLY YES OR NO!"""
            
            logger.debug(f"🤖 Asking model about refinement continuation...")
            response = await get_model().ainvoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            should_continue = "yes" in response_text.lower()
            
            if should_continue:
                state["keep_refining"] = True
                logger.info(f"✅ REFINING: Continuing (model said: '{response_text.strip()}')")
                logger.debug(f"   🔄 Will proceed to attempt #{state['attempts'] + 1}")
            else:
                state["keep_refining"] = False
                logger.info(f"✅ REFINING: Stopping (model said: '{response_text.strip()}')")
                logger.debug(f"   🏁 Moving to FINISHED state")
                
        return state
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Refining phase failed: {str(e)}")
        logger.error(f"   💥 Full traceback: {traceback.format_exc()}")
        state["keep_refining"] = False
        state["outputs"].append(f"Refining phase error: {str(e)}")
        return state

async def finished(state):
    log_state_transition("REFINING", "FINISHED", state)
    
    try:
        # Get the current notebook data as the final result
        if state["mcp_service"]:
            logger.debug("🔌 MCP Service available, retrieving final notebook data...")
            try:
                # List notebooks to see what's available
                notebooks = await state["mcp_service"].list_notebooks()
                
                # Handle case where notebooks might be a string (error response) or dict
                if isinstance(notebooks, dict):
                    state["notebook_data"] = {"available_notebooks": notebooks}
                    notebook_count = len(notebooks.get('notebooks', []))
                    log_mcp_operation("list_notebooks", True, f"Retrieved {notebook_count} notebooks")
                    logger.debug(f"   📚 Notebooks: {list(notebooks.get('notebooks', {}).keys()) if notebooks.get('notebooks') else 'None'}")
                else:
                    # If notebooks is a string (likely an error), store it as such
                    state["notebook_data"] = {"available_notebooks": {"error": str(notebooks), "notebooks": []}}
                    log_mcp_operation("list_notebooks", False, error=f"Non-dict response: {type(notebooks)}")
                    logger.warning(f"   ⚠️  Unexpected response type: {type(notebooks)} - {notebooks}")
                    
            except Exception as e:
                error_msg = f"Error getting notebook data: {str(e)}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   💥 MCP error traceback: {traceback.format_exc()}")
                state["outputs"].append(error_msg)
                state["notebook_data"] = {"available_notebooks": {"error": error_msg, "notebooks": []}}
                log_mcp_operation("list_notebooks", False, error=error_msg)
        else:
            logger.error("❌ CRITICAL: No MCP service available for final notebook data")
            state["notebook_data"] = {"available_notebooks": {"error": "No MCP service available", "notebooks": []}}
        
        logger.info(f"🏁 FINISHED: Agent execution completed")
        logger.info(f"   📊 Total attempts: {state['attempts']}")
        logger.info(f"   📝 Total outputs: {len(state.get('outputs', []))}")
        logger.info(f"   📚 Notebook data: {'Available' if state.get('notebook_data') else 'Missing'}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Finished phase failed: {str(e)}")
        logger.error(f"   💥 Full traceback: {traceback.format_exc()}")
        state["outputs"].append(f"Finished phase error: {str(e)}")
        return state

async def code_attempt(state):
    attempt_num = state['attempts'] + 1
    log_state_transition("ENTRY" if state['attempts'] == 0 else "REFINING", "CODE_ATTEMPT", state)
    logger.info(f"🔧 CODE ATTEMPT #{attempt_num}")
    
    try:
        logger.debug("📝 Loading code attempt prompt...")
        system_prompt = prompt_manager.get_code_attempt_prompt()

        prompt = f"""{system_prompt}

CURRENT TASK: {state['task']}

Available MCP Tools: {', '.join(state.get('available_tools', []))}

Use the tools available to accomplish the task following the MCP stateful workflow.
Be systematic and check if each step runs properly. 
Remember to save your work using 'saveNotebook' when complete.

Provide specific tool calls and code that should be executed."""
        
        logger.debug(f"🤖 Sending prompt to model (length: {len(prompt)})")
        
        # Get LangChain tools from MCP service for direct tool integration
        mcp_tools = []
        if state["mcp_service"]:
            logger.debug("🔌 Loading LangChain MCP tools...")
            try:
                mcp_tools = state["mcp_service"].get_langchain_tools()
                log_mcp_operation("get_langchain_tools", True, f"Loaded {len(mcp_tools)} tools")
            except Exception as e:
                log_mcp_operation("get_langchain_tools", False, error=str(e))
        else:
            logger.warning("⚠️  No MCP service available for tool loading")
        
        # If we have tools, bind them to the model for direct tool calling
        if mcp_tools:
            logger.debug(f"🔗 Binding {len(mcp_tools)} tools to model...")
            model_with_tools = get_model().bind_tools(mcp_tools)
            response = await model_with_tools.ainvoke(prompt)
        else:
            logger.debug("🤖 Using model without tools (fallback mode)")
            response = await get_model().ainvoke(prompt)
            
        response_text = response.content if hasattr(response, 'content') else str(response)
        logger.debug(f"✅ Model response received (length: {len(response_text)})")
        
        # Check if model made tool calls
        tool_calls_executed = 0
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"🔧 Executing {len(response.tool_calls)} tool calls...")
            
            for i, tool_call in enumerate(response.tool_calls, 1):
                try:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    logger.info(f"   �️  Tool {i}/{len(response.tool_calls)}: {tool_name}")
                    logger.debug(f"      📋 Args: {tool_args}")
                    
                    result = await state["mcp_service"].call_mcp_tool(tool_name, tool_args)
                    tool_calls_executed += 1
                    
                    log_mcp_operation(f"call_mcp_tool({tool_name})", True, f"Result: {str(result)[:100]}...")
                    response_text += f"\n\n✅ Tool '{tool_name}' executed successfully: {result}"
                    
                except Exception as e:
                    tool_name = tool_call.get('name', 'unknown')
                    error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                    logger.error(f"❌ Tool execution failed: {error_msg}")
                    logger.error(f"   💥 Tool error traceback: {traceback.format_exc()}")
                    log_mcp_operation(f"call_mcp_tool({tool_name})", False, error=error_msg)
                    response_text += f"\n\n❌ {error_msg}"
        
        # Fallback: Try to execute MCP tools based on text parsing (legacy approach)
        elif state["mcp_service"]:
            logger.debug("🔍 Checking for legacy tool patterns in response...")
            try:
                # Parse potential tool calls from the response
                if "saveNotebook" in response_text:
                    logger.info("📄 Found saveNotebook command in response")
                    filename = "agent_notebook.ipynb"  # default
                    logger.debug(f"   💾 Saving as: {filename}")
                    result = await state["mcp_service"].call_mcp_tool("saveNotebook", {"filename": filename})
                    tool_calls_executed += 1
                    log_mcp_operation("saveNotebook", True, f"Saved: {filename}")
                    response_text += f"\n\n✅ Notebook saved: {result}"
                
                if "createCodeCell" in response_text:
                    logger.info("📝 Found createCodeCell command in response")
                    tool_calls_executed += 1
                    # Add more parsing logic here if needed
                    
            except Exception as e:
                error_msg = f"Error using MCP tools: {str(e)}"
                logger.error(f"❌ Legacy tool execution failed: {error_msg}")
                logger.error(f"   💥 MCP tools error traceback: {traceback.format_exc()}")
                log_mcp_operation("legacy_tools", False, error=error_msg)
                response_text += f"\n\n❌ {error_msg}"
        else:
            logger.error("❌ CRITICAL: No MCP service available for tool execution")
        
        state["outputs"].append(response_text)
        state["attempts"] += 1
        
        logger.info(f"✅ CODE ATTEMPT #{attempt_num} completed")
        logger.info(f"   🛠️  Tools executed: {tool_calls_executed}")
        logger.info(f"   📊 Total attempts: {state['attempts']}")
        logger.debug(f"   📝 Output length: {len(response_text)}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Code attempt #{attempt_num} failed: {str(e)}")
        logger.error(f"   💥 Full traceback: {traceback.format_exc()}")
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
    logger.info("="*80)
    logger.info("🤖 AGENT EXECUTION STARTING")
    logger.info("="*80)
    
    task_preview = task[:100] + "..." if len(task) > 100 else task
    logger.info(f"📋 Task: {task_preview}")
    logger.debug(f"📋 Full task: {task}")
    
    try:
        start_time = datetime.now()
        logger.debug(f"⏰ Start time: {start_time.strftime('%H:%M:%S.%f')}")
        
        # Validate MCP service
        if not mcp_service:
            error_msg = "No MCP service provided"
            logger.error(f"❌ CRITICAL: {error_msg}")
            return {
                "task": task,
                "outputs": [f"Agent execution failed: {error_msg}"],
                "attempts": 0,
                "notebook_data": None,
                "success": False,
                "error": error_msg
            }
        
        logger.debug("🔌 MCP Service validation passed")
        
        initial_state = AgenticState({
            "task": task,
            "mcp_service": mcp_service,
            "outputs": [],
            "attempts": 0,
            "keep_refining": True,
            "available_tools": [],
            "notebook_data": None
        })
        
        logger.debug("📦 Initial state created")
        logger.debug(f"   📝 Task length: {len(task)}")
        logger.debug(f"   🔧 Keep refining: {initial_state['keep_refining']}")
        
        logger.info("🏗️  Creating agent graph...")
        agent_graph = await create_agent_with_mcp(mcp_service)
        logger.debug("✅ Agent graph created successfully")
        
        # Run the graph
        logger.info("🚀 STARTING GRAPH EXECUTION")
        logger.info("-" * 50)
        
        final_state = await agent_graph.ainvoke(initial_state)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info("-" * 50)
        logger.info("🏁 GRAPH EXECUTION COMPLETED")
        logger.info(f"⏰ Execution time: {execution_time:.2f} seconds")
        
        result = {
            "task": final_state.get("task", ""),
            "outputs": final_state.get("outputs", []),
            "attempts": final_state.get("attempts", 0),
            "notebook_data": final_state.get("notebook_data"),
            "success": final_state.get("attempts", 0) > 0
        }
        
        # Final summary logging
        logger.info("="*80)
        logger.info("📊 AGENT EXECUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"✅ Success: {result['success']}")
        logger.info(f"🔄 Attempts: {result['attempts']}")
        logger.info(f"📝 Outputs: {len(result['outputs'])}")
        logger.info(f"📚 Notebook data: {'Available' if result['notebook_data'] else 'Missing'}")
        logger.info(f"⏰ Duration: {execution_time:.2f}s")
        
        if result['outputs']:
            logger.debug("📋 Output details:")
            for i, output in enumerate(result['outputs'], 1):
                output_preview = output[:200] + "..." if len(output) > 200 else output
                logger.debug(f"   {i}. {output_preview}")
        
        return result
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
        
        logger.error("="*80)
        logger.error("❌ AGENT EXECUTION FAILED")
        logger.error("="*80)
        logger.error(f"💥 Error: {str(e)}")
        logger.error(f"⏰ Failed after: {execution_time:.2f}s")
        logger.error(f"📍 Full traceback:")
        logger.error(traceback.format_exc())
        
        # Return error state
        return {
            "task": task,
            "outputs": [f"Agent execution failed: {str(e)}"],
            "attempts": 0,
            "notebook_data": None,
            "success": False,
            "error": str(e)
        }