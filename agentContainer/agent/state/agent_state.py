from typing import Dict, Any, List, Optional
from services.mcp_service import MCPService
import logging

logger = logging.getLogger('AGENT')

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
