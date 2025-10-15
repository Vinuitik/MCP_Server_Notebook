from services.mcp_service import MCPService
from typing import Dict, Any
import logging
import traceback
from datetime import datetime
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from prompts.prompt_manager import prompt_manager

from .state.agent_state import AgenticState
from .nodes.entry import entry
from .nodes.refining import refining
from .nodes.code_attempt import code_attempt
from .nodes.finished import finished

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