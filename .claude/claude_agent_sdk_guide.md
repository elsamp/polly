# Claude Agent SDK Development Guide

## Overview

The Claude Agent SDK is a production-ready framework for building custom AI agents. It's the same infrastructure that powers Claude Code itself, providing tools for file operations, code execution, context management, and multi-agent orchestration.

**Key Concept**: Think of the SDK as giving Claude a "computer" - file system access, ability to run commands, and tools to accomplish tasks autonomously.

## Installation & Setup

### Prerequisites
```bash
# Python 3.10+ required
python --version

# Node.js 18+ required for Claude Code CLI
node --version

# Install Claude Code CLI globally
npm install -g @anthropic-ai/claude-code
```

### Install the SDK
```bash
pip install claude-agent-sdk
```

### Authentication
Set your API key as an environment variable:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Alternative: Use Claude Code authentication (no API key needed):
```bash
# SDK will use your Claude Code session
```

### Verify Installation
```bash
claude doctor  # Check Claude Code setup
```

## Core Concepts

### 1. Two Interaction Modes

**query() - Simple Streaming**
- For lightweight, stateless interactions
- Returns AsyncIterator of messages
- Good for one-off tasks

**ClaudeSDKClient - Full Session Management**
- For interactive, multi-turn conversations
- Maintains context across messages
- Supports custom tools and hooks
- **Use this for interactive applications**

### 2. The Agent Loop
Agents follow a natural feedback cycle:
```
Gather Context → Take Action → Verify Work → Repeat
```

Design your agent's capabilities around this loop.

### 3. Tools Are Primary Actions
Tools appear prominently in Claude's context window. The agent will naturally use tools to accomplish tasks. Built-in tools include:
- **Read**: Read file contents
- **Write**: Create/modify files
- **Bash**: Execute shell commands
- **Grep**: Search file contents
- **Glob**: Find files by pattern
- **WebSearch**: Search the web

### 4. Context Management
- The SDK automatically compacts context when approaching limits
- Each agent/subagent has isolated context (200K tokens)
- Use CLAUDE.md for persistent project context

## Basic Usage Patterns

### Pattern 1: Simple Query (One-Shot)
```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

### Pattern 2: Interactive Conversation (Recommended for Terminal Apps)
```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def interactive_session():
    system_prompt = """You are a helpful assistant specializing in [domain].
    
    Your capabilities:
    - [List what the agent can do]
    
    Your workflow:
    - [Describe the process]
    """
    
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=["Read", "Write"],
        permission_mode="manual"  # Ask before file operations
    )
    
    async with ClaudeSDKClient(options=options) as client:
        # Initial query
        await client.query("Hello! Let's work on [task].")
        
        # Stream response
        async for message in client.receive_response():
            if message.type == "assistant":
                for block in message.content:
                    if block.type == "text":
                        print(block.text)
        
        # Continue conversation loop
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
            
            await client.query(user_input)
            async for message in client.receive_response():
                # Process response
                pass

# Run it
import anyio
anyio.run(interactive_session)
```

### Pattern 3: Custom Tools (In-Process MCP)
```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("calculate_sum", "Add two numbers together", {"a": float, "b": float})
async def calculate_sum(args):
    result = args["a"] + args["b"]
    return {
        "content": [{
            "type": "text",
            "text": f"The sum is {result}"
        }]
    }

# Create MCP server
calc_server = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[calculate_sum]
)

# Use in agent
options = ClaudeAgentOptions(
    mcp_servers={"calc": calc_server},
    allowed_tools=["mcp__calc__calculate_sum"]
)
```

**Key Advantage**: Custom tools run in-process (no subprocess overhead), making them fast and easy to debug.

### Pattern 4: Subagents (For Specialization)
```python
options = ClaudeAgentOptions(
    agents={
        'researcher': {
            'description': 'Research specialist for gathering information',
            'prompt': 'You are a thorough researcher...',
            'tools': ['Read', 'Grep', 'WebSearch'],
            'model': 'sonnet'
        },
        'writer': {
            'description': 'Content creation specialist',
            'prompt': 'You are a skilled writer...',
            'tools': ['Write'],
            'model': 'sonnet'
        }
    }
)
```

Claude automatically invokes subagents based on task matching. Each maintains separate context.

## Configuration Options (ClaudeAgentOptions)

### Essential Options
```python
options = ClaudeAgentOptions(
    # System behavior
    system_prompt="Your agent's role and instructions",
    max_turns=10,  # Limit conversation length
    
    # Tool permissions
    allowed_tools=["Read", "Write"],  # Explicitly allow
    disallowed_tools=["Bash"],  # Explicitly deny
    
    # Permission mode
    permission_mode="manual",  # Options: manual, acceptEdits, acceptAll
    
    # Working directory
    cwd="/path/to/project",
    
    # Load project context
    setting_sources=["project"],  # Loads .claude/CLAUDE.md
    
    # MCP servers (custom tools)
    mcp_servers={"server-name": server_instance},
    
    # Subagents
    agents={"agent-name": agent_config},
    
    # Hooks
    hooks={"PreToolUse": [hook_function]}
)
```

### Permission Modes
- **manual**: Ask user before every tool use (safest)
- **acceptEdits**: Auto-accept file reads/writes
- **acceptAll**: Auto-accept everything (use with caution)

## Project Context with CLAUDE.md

Create `.claude/CLAUDE.md` in your project:
```markdown
# Project Context

## Purpose
[What this project does]

## Architecture
[Key components and structure]

## Conventions
- [Coding standards]
- [File organization]
- [Testing approach]

## Important Files
- `src/main.py`: Entry point
- `config/settings.json`: Configuration

## Current State
[What's been built, what's in progress]
```

Load it in your agent:
```python
options = ClaudeAgentOptions(
    setting_sources=["project"],
    cwd="/path/to/project"  # Where .claude/ directory lives
)
```

## Best Practices

### 1. Design for the Agent Loop
Structure your system prompt around: gather context → take action → verify → repeat

### 2. Start with Narrow Permissions
```python
# Good: Specific, minimal permissions
allowed_tools=["Read", "Grep"]

# Avoid: Too permissive initially
allowed_tools=["Bash"]  # Can run any command!
```

### 3. Use Clear, Structured System Prompts
```python
system_prompt = """
You are a [role] that [purpose].

CAPABILITIES:
- [What you can do]
- [What tools you have]

WORKFLOW:
Step 1: [First action]
Step 2: [Next action]

RULES:
- [Important constraints]
- [Expected behavior]
"""
```

### 4. Handle Message Types Properly
```python
async for message in client.receive_response():
    if message.type == "assistant":
        for block in message.content:
            if block.type == "text":
                print(block.text)
            elif block.type == "tool_use":
                print(f"[Using {block.tool_name}]")
    elif message.type == "tool_result":
        # Tool completed
        pass
    elif message.type == "result":
        # Final result
        break
```

### 5. Use Hooks for Safety and Logging
```python
from claude_agent_sdk import HookMatcher

async def validate_tool_use(input_data, tool_use_id, context):
    tool_name = input_data["tool_name"]
    
    # Add validation logic
    if tool_name == "Bash":
        command = input_data["tool_input"].get("command", "")
        if "rm -rf" in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Dangerous command blocked"
                }
            }
    
    return {}  # Allow by default

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[validate_tool_use])
        ]
    }
)
```

### 6. For Terminal Apps: Stream Output Naturally
```python
async def print_streaming_response(client):
    """Helper to print responses in real-time"""
    async for message in client.receive_response():
        if message.type == "assistant":
            for block in message.content:
                if block.type == "text":
                    print(block.text, end="", flush=True)
                elif block.type == "tool_use":
                    print(f"\n[🔧 Using {block.tool_name}]", flush=True)
        elif message.type == "result":
            print("\n")  # Final newline
            break
```

### 7. Error Handling
```python
from claude_agent_sdk import (
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError
)

try:
    async for message in query(prompt="Hello"):
        pass
except CLINotFoundError:
    print("Error: Claude Code CLI not installed")
    print("Run: npm install -g @anthropic-ai/claude-code")
except CLIConnectionError:
    print("Error: Cannot connect to Claude Code")
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
except ClaudeSDKError as e:
    print(f"SDK error: {e}")
```

## Common Patterns for Terminal Applications

### Interactive CLI with Commands
```python
async def cli_app():
    print("Welcome! Type 'help' for commands, 'exit' to quit.\n")
    
    options = ClaudeAgentOptions(
        system_prompt="""You are a CLI assistant.
        
        Available commands:
        - /analyze <file>: Analyze a file
        - /generate <output>: Generate content
        - help: Show help
        """,
        allowed_tools=["Read", "Write", "Grep"]
    )
    
    async with ClaudeSDKClient(options=options) as client:
        while True:
            try:
                user_input = input(">> ").strip()
                
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit']:
                    break
                if user_input == 'help':
                    print("Commands: /analyze, /generate, exit")
                    continue
                
                await client.query(user_input)
                async for msg in client.receive_response():
                    # Handle response
                    pass
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
                continue
```

### Progress Indicators
```python
import sys

def show_thinking():
    """Show agent is processing"""
    print("Thinking", end="", flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print()

# Use before awaiting response
show_thinking()
async for message in client.receive_response():
    # ...
```

### Multi-Phase Workflows
```python
system_prompt = """
You are a multi-phase workflow assistant.

PHASE 1: DISCOVERY
- Ask clarifying questions
- Signal completion: "Phase 1 complete."

PHASE 2: ANALYSIS  
- Process gathered information
- Signal completion: "Phase 2 complete."

PHASE 3: OUTPUT
- Generate final deliverables
- Signal completion: "Done."

Work through phases sequentially. Wait for user confirmation between phases.
"""
```

## Common Pitfalls to Avoid

### ❌ Don't: Use query() for interactive conversations
```python
# Bad: No context between calls
async for msg in query(prompt="First question"):
    pass
async for msg in query(prompt="Follow-up"):  # Lost context!
    pass
```

### ✅ Do: Use ClaudeSDKClient for conversations
```python
# Good: Maintains context
async with ClaudeSDKClient(options=options) as client:
    await client.query("First question")
    await client.query("Follow-up")  # Has context!
```

### ❌ Don't: Forget to handle all message types
```python
# Bad: Only handles text
async for message in client.receive_response():
    print(message.content[0].text)  # May crash on tool_use!
```

### ✅ Do: Check block types
```python
# Good: Handles all types
for block in message.content:
    if block.type == "text":
        print(block.text)
    elif block.type == "tool_use":
        print(f"Using {block.tool_name}")
```

### ❌ Don't: Set overly broad permissions initially
```python
# Bad: Too permissive
allowed_tools=["Bash"]  # Can do anything!
permission_mode="acceptAll"
```

### ✅ Do: Start restrictive, expand as needed
```python
# Good: Specific and controlled
allowed_tools=["Read", "Grep"]
permission_mode="manual"
```

## Debugging Tips

### 1. Print Tool Calls
```python
async for message in client.receive_response():
    if message.type == "assistant":
        for block in message.content:
            if block.type == "tool_use":
                print(f"DEBUG: Tool={block.tool_name}, Input={block.tool_input}")
```

### 2. Log to File
```python
import logging

logging.basicConfig(
    filename='agent.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s'
)

# In your code
logging.info(f"User input: {user_input}")
logging.info(f"Agent response: {response_text}")
```

### 3. Use permission_mode="manual" During Development
This lets you see and approve every tool use, helping you understand agent behavior.

## Example: Complete Terminal Application

```python
import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server
)

# Custom tool
@tool("save_note", "Save a note to file", {"content": str, "filename": str})
async def save_note(args):
    with open(args["filename"], "w") as f:
        f.write(args["content"])
    return {"content": [{"type": "text", "text": f"Saved to {args['filename']}"}]}

# MCP server
note_server = create_sdk_mcp_server(
    name="notes",
    version="1.0.0",
    tools=[save_note]
)

async def main():
    system_prompt = """You are a note-taking assistant.
    
    You can:
    - Create notes using the save_note tool
    - Read existing notes using Read
    - Search notes using Grep
    
    Be concise and helpful."""
    
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        mcp_servers={"notes": note_server},
        allowed_tools=["Read", "Grep", "mcp__notes__save_note"],
        permission_mode="acceptEdits"
    )
    
    print("Note-Taking Assistant")
    print("Commands: 'exit' to quit\n")
    
    async with ClaudeSDKClient(options=options) as client:
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                await client.query(user_input)
                
                print("Assistant: ", end="", flush=True)
                async for message in client.receive_response():
                    if message.type == "assistant":
                        for block in message.content:
                            if block.type == "text":
                                print(block.text, end="", flush=True)
                            elif block.type == "tool_use":
                                print(f"\n[Using {block.tool_name}...]", end="", flush=True)
                    elif message.type == "result":
                        print("\n")
                        break
                        
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                print(f"\nError: {e}")

if __name__ == "__main__":
    anyio.run(main)
```

## Reference Documentation

### Official Resources
- **Main Docs**: https://docs.claude.com/en/api/agent-sdk/overview
- **Python SDK GitHub**: https://github.com/anthropics/claude-agent-sdk-python
- **TypeScript SDK GitHub**: https://github.com/anthropics/claude-agent-sdk-typescript
- **Engineering Blog**: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

### Key Docs Pages
- Subagents: https://docs.claude.com/en/api/agent-sdk/subagents
- Streaming vs Single Mode: https://docs.claude.com/en/api/agent-sdk/streaming-vs-single-mode
- Modifying System Prompts: https://docs.claude.com/en/api/agent-sdk/modifying-system-prompts
- MCP Documentation: https://docs.claude.com/en/docs/claude-code/mcp

### Example Repositories
- **Official Examples**: See examples/ folder in Python SDK repo
- **Tutorial Projects**: https://github.com/kenneth-liao/claude-agent-sdk-intro
- **Community Agents**: https://github.com/wshobson/agents

### Tutorials
- DataCamp Tutorial: https://www.datacamp.com/tutorial/how-to-use-claude-agent-sdk
- Building Agents Guide: https://blog.promptlayer.com/building-agents-with-claude-codes-sdk/

## Quick Reference

### Import Statements
```python
from claude_agent_sdk import (
    query,                    # Simple query function
    ClaudeSDKClient,         # Full session client
    ClaudeAgentOptions,      # Configuration
    tool,                    # Decorator for custom tools
    create_sdk_mcp_server,   # Create MCP server
    HookMatcher,             # For hooks
    AssistantMessage,        # Message types
    UserMessage,
    TextBlock,               # Content blocks
    ToolUseBlock,
    ToolResultBlock,
    ClaudeSDKError,          # Errors
    CLINotFoundError,
    ProcessError
)
```

### Common Tool Names
- File operations: `Read`, `Write`
- Search: `Grep`, `Glob`
- Execution: `Bash`
- Web: `WebSearch`, `WebFetch`
- Custom: `mcp__<server-name>__<tool-name>`

### Permission Modes
- `manual` - Ask every time
- `acceptEdits` - Auto-accept reads/writes
- `acceptAll` - Auto-accept everything

---

## Summary

The Claude Agent SDK gives you a production-ready framework for building autonomous agents. Key principles:

1. **Use ClaudeSDKClient for interactive apps** - maintains context
2. **Design around the agent loop** - gather, act, verify, repeat
3. **Start with narrow permissions** - expand as needed
4. **Structure system prompts clearly** - role, capabilities, workflow, rules
5. **Use custom tools for domain-specific actions** - in-process MCP is fast and simple
6. **Handle all message types** - text, tool_use, tool_result, result
7. **Test with permission_mode="manual"** during development

The SDK handles the hard infrastructure (context management, tool execution, session state) so you can focus on agent behavior and workflow design.

Good luck building! 🚀
