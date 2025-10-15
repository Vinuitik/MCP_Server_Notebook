import traceback
import logging
from ..state.agent_state import log_state_transition, log_mcp_operation

logger = logging.getLogger('AGENT')

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
