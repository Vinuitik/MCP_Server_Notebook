import traceback
import logging
from prompts.prompt_manager import prompt_manager
from ..utils.model_utils import get_model
from ..state.agent_state import log_state_transition, log_mcp_operation

logger = logging.getLogger('AGENT')

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
                    logger.info(f"   🛠️  Tool {i}/{len(response.tool_calls)}: {tool_name}")
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
