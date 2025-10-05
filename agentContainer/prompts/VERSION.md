# MCP Agent Prompt Versions

## Version 1.0.0 (Current)
- **Date**: October 5, 2025
- **Description**: Initial implementation of MCP stateful workflow prompts
- **Files**:
  - `entry_system_prompt.txt`: System prompt for task refinement phase
  - `refining_system_prompt.txt`: System prompt for refinement decision phase  
  - `code_attempt_system_prompt.txt`: System prompt for code execution phase

### Features:
- Comprehensive explanation of MCP stateful nature
- Clear workflow guidance: CREATE → DEVELOP → SAVE → EXPORT
- Emphasis on mandatory `saveNotebook` tool usage
- Best practices for systematic development
- Detailed operation sequences and guidelines

### Key Concepts Covered:
- MCP is stateful (not REST-like)
- Initial state is empty
- Operations accumulate state
- Persistence requires explicit saving
- Workflow best practices

## Version History

### Future Versions
- Will be documented here as prompts evolve
- Each version will maintain backward compatibility where possible
- Breaking changes will be clearly marked

## Usage
Use the `PromptManager` class to load prompts:
```python
from prompts.prompt_manager import prompt_manager

# Load specific prompts
entry_prompt = prompt_manager.get_entry_prompt()
refining_prompt = prompt_manager.get_refining_prompt()
code_prompt = prompt_manager.get_code_attempt_prompt()

# Check version
version = prompt_manager.get_version()
```