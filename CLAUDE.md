# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Feature Breakdown Agent** - a terminal-based AI agent built with the Claude Agent SDK (Python) that transforms high-level feature descriptions into detailed, incremental coding prompts. It helps product managers, technical leads, and developers break down complex features into implementable vertical slices.

**Primary PRD**: See `prompt_generator_prd.md` for complete product requirements.

## Architecture

### Core Design
- **Single conversational agent** (no subagents) using Claude Sonnet 4.5
- Built on **Claude Agent SDK (Python)** with anyio async runtime
- **Four-phase workflow**: Context Gathering → Discovery → Incremental Grouping → Prompt Generation
- Each phase has explicit exit criteria and user confirmation points

### Key Components
- `ClaudeSDKClient` for session management
- Custom MCP tool `mcp__prompt-tools__generate_prompt` for template-based prompt generation
- File system tools: Read, Write, Grep, Glob for context awareness

### Agent Configuration Pattern
```python
ClaudeAgentOptions(
    system_prompt=<detailed_prompt>,
    allowed_tools=["Read", "Write", "Grep", "Glob", "mcp__prompt-tools__generate_prompt"],
    permission_mode="acceptEdits",  # Auto-accept file operations
    setting_sources=["project"],  # Load CLAUDE.md if present
)
```

## Project Structure

### Development Structure (This Repo)
```
feature-breakdown-agent/
├── feature_breakdown_agent/         # Main package directory
│   ├── __init__.py                  # Package initialization
│   ├── feature_breakdown_agent.py   # Main application entry
│   ├── prompt_template.py           # Template definition (see PRD line 215-287)
│   └── utils.py                     # Optional helpers
├── tests/                           # Unit tests
├── CLAUDE.md                        # This file
├── CLAUDE_AGENT_SDK_GUIDE.md       # SDK reference documentation (to be created)
├── pyproject.toml                   # uv/pip project configuration
├── .python-version                  # Python 3.10+
└── prompt_generator_prd.md         # Complete product specification
```

### Target Project Structure (Where Agent Runs)
Users run this agent in their own projects, which should have:
```
user-project/
├── features/                         # Existing feature docs (agent reads these)
├── prompts/                          # Generated prompts (agent creates these)
│   └── [feature-name]/              # Organized by feature
│       ├── increment_01_*.md
│       └── increment_02_*.md
```

## Development Commands

### Setup
```bash
# Install dependencies and package in editable mode
uv pip install -e .
```

### Run Agent
```bash
# Using uv run
uv run feature-breakdown-agent

# Or directly with Python
uv run python feature_breakdown_agent/feature_breakdown_agent.py
```

### Testing
```bash
pytest tests/
```

## Critical Implementation Details

### The Four Phases

**Phase 0: Context Gathering**
- Agent searches for existing feature documentation in target project
- Reads `.md` files to understand existing scope
- Builds understanding of system architecture and dependencies
- See PRD lines 21-30

**Phase 1: Discovery**
- Minimum 5 clarifying questions required (FR-2.1)
- Intelligent follow-up questions based on responses
- References existing features when asking about integration
- User must confirm completion before proceeding

**Phase 2: Incremental Grouping**
- Must create 2-8 increments per feature (FR-3.1)
- Each increment must be a **vertical slice** - delivers user value, not just scaffolding
- Each increment must be independently testable by a user
- Agent identifies dependencies between increments and on existing features
- User must approve grouping before proceeding

**Phase 3: Prompt Generation**
- Generate prompts sequentially (increment 1, then 2, etc.)
- Use consistent template for all prompts (see prompt_template.py)
- Save as `increment_NN_description.md` format
- Each prompt must include: feature overview, scope, dependencies (with file references), acceptance criteria (3-5 minimum), technical constraints, implementation guidance

### Vertical Slice Principle
A vertical slice must:
- Deliver clear user value (not just infrastructure)
- Be independently testable by a user
- Touch all necessary layers (frontend, backend, database, etc.)
- Build on previous increments

### Context Awareness Requirements
- FR-1.1-1.5: Agent MUST search for existing feature docs before discovery
- Agent must identify potential scope overlap with existing features
- Agent must reference existing feature files when noting dependencies
- User can specify custom feature documentation directory

### User Experience Expectations
- Natural conversational flow (not robotic)
- Phase transitions clearly marked
- Tool usage indicated (e.g., "[Searching existing features...]")
- Progress visible during generation
- File paths displayed when files are created
- Graceful error handling with recovery options
- User can interrupt with Ctrl+C and resume

## Prompt Template Structure

Generated prompts must follow this exact structure (see PRD lines 215-287):

```markdown
# Feature: [Feature Name]
# Increment N: [Increment Name]

## Overview
## Scope of This Increment
### What's Included
### What's NOT Included
## Dependencies
### Previous Increments
### Existing Features
### External Dependencies
## User Value
### User Story
## Acceptance Criteria (3-5 minimum)
## Technical Constraints
## Testing Strategy
## Edge Cases to Consider
```

Footer must include:
- "Generated by Feature Breakdown Agent"
- Timestamp
- Feature name
- "Increment N of M"

## Technology Constraints

- **Python 3.10+** minimum
- **Claude Agent SDK (Python)** - refer to CLAUDE_AGENT_SDK_GUIDE.md for SDK patterns
- **anyio** for async runtime
- **Claude Sonnet 4.5** model specifically

## Testing Strategy

### Manual Testing Focus (PRD lines 374-393)
- Agent reads existing feature docs correctly
- Agent asks relevant clarifying questions
- Agent groups functionality into logical increments
- Generated prompts follow template exactly
- Files saved with correct naming convention
- Dependencies correctly identified
- Exit and restart works cleanly
- Conversation context maintained throughout

### Critical Edge Cases
- No existing feature documentation
- Very large features (10+ increments)
- Very small features (2 increments)
- Complex dependency chains
- User provides minimal vs. detailed answers
- User requests to redo grouping multiple times

## Success Criteria (MVP)

Must have for V1:
- Agent completes all 4 phases successfully
- Generates properly formatted prompt files
- Reads existing feature documentation
- Interactive conversation with user input
- Uses prompt template consistently
- Identifies scope overlap with existing features
- Validates increments are vertical slices

## Out of Scope (V1)

Not building:
- Web interface or GUI (terminal only)
- Authentication or multi-user support
- Cloud storage or sync
- Integration with project management tools
- Automatic execution of generated prompts
- Version control integration

## File References

- **Complete specification**: prompt_generator_prd.md
- **SDK documentation**: CLAUDE_AGENT_SDK_GUIDE.md (to be created)
- **Main application**: feature_breakdown_agent/feature_breakdown_agent.py
- **Template definition**: feature_breakdown_agent/prompt_template.py (to be created)
