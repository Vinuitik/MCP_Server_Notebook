# MCP Agent Prompts

This directory contains system prompts for the MCP (Model Context Protocol) agent, organized for easy versioning and maintenance.

## Directory Structure

```
prompts/
├── __init__.py                    # Package initialization
├── prompt_manager.py              # Prompt loading and management utility  
├── VERSION.md                     # Version history and documentation
├── README.md                      # This file
├── entry_system_prompt.txt        # Prompt for task entry/refinement phase
├── refining_system_prompt.txt     # Prompt for refinement decision phase
└── code_attempt_system_prompt.txt # Prompt for code execution phase
```

## Usage

### Basic Usage
```python
from prompts.prompt_manager import prompt_manager

# Load specific prompts
entry_prompt = prompt_manager.get_entry_prompt()
refining_prompt = prompt_manager.get_refining_prompt() 
code_prompt = prompt_manager.get_code_attempt_prompt()
```

### Advanced Usage
```python
from prompts import PromptManager

# Create custom prompt manager with different directory
custom_manager = PromptManager("/path/to/custom/prompts")

# Check available prompts
available = prompt_manager.list_available_prompts()

# Get version info
version = prompt_manager.get_version()

# Clear cache to reload updated prompts
prompt_manager.clear_cache()
```

## Prompt Files

### entry_system_prompt.txt
System prompt used during the task entry and refinement phase. Explains MCP stateful nature and basic workflow.

### refining_system_prompt.txt  
System prompt for deciding whether to continue refining or move to completion. Emphasizes the importance of the save step.

### code_attempt_system_prompt.txt
Comprehensive prompt for the code execution phase with detailed MCP operations and best practices.

## Key Concepts Covered

All prompts emphasize these critical MCP concepts:

- **Stateful Nature**: MCP maintains persistent state (unlike REST APIs)
- **Empty Initial State**: No notebooks/cells exist at start
- **State Accumulation**: Operations build upon previous state
- **Mandatory Saving**: Must use `saveNotebook` to persist work
- **Workflow**: CREATE → DEVELOP → SAVE → EXPORT

## Versioning

- Current version: 1.0.0
- See `VERSION.md` for complete version history
- Each prompt file is versioned together as a cohesive set
- Breaking changes will be clearly documented

## Best Practices

1. **Version Control**: Track all changes to prompt files
2. **Testing**: Test prompt changes with actual agent runs
3. **Documentation**: Update VERSION.md when making changes
4. **Backup**: Keep copies of working prompt versions
5. **Validation**: Ensure prompts are consistent with MCP capabilities

## Contributing

When updating prompts:

1. Test changes thoroughly with the agent
2. Update version in `prompt_manager.py` and `VERSION.md`
3. Document changes and rationale
4. Consider backward compatibility
5. Update this README if structure changes