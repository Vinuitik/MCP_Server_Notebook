import traceback
import logging
from prompts.prompt_manager import prompt_manager
from ..utils.model_utils import get_model
from ..state.agent_state import log_state_transition

logger = logging.getLogger('AGENT')

MAX_ATTEMPTS = 5

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
