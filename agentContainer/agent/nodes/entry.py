import traceback
import logging
from prompts.prompt_manager import prompt_manager
from ..utils.model_utils import get_model
from ..state.agent_state import log_state_transition, log_mcp_operation

logger = logging.getLogger('AGENT')

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
