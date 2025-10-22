# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **Polly (Feature Breakdown Agent)** - a terminal-based AI agent built with the Claude Agent SDK (Python) that transforms high-level feature descriptions into detailed, incremental coding prompts. It helps product managers, technical leads, and developers break down complex features into implementable vertical slices.

**Primary PRD**: See `prompt_generator_prd.md` for complete product requirements.

## Architecture

### Core Design
- **Single conversational agent** using Claude Sonnet 4.5 with Claude Skills framework
- Built on **Claude Agent SDK (Python)** with anyio async runtime
- **Skills-based architecture**: Four specialized skills for different actions
- **Conversational interaction**: Agent autonomously decides when to use skills
- Long-running session maintains context throughout the user's workflow

### Key Components
- `ClaudeSDKClient` for session management
- **Four Claude Skills** for specialized tasks (see Skills section below)
- Coordinator system prompt that guides overall agent behavior
- File system tools: Read, Write, Grep, Glob for context awareness

### Agent Configuration Pattern
```python
ClaudeAgentOptions(
    system_prompt=coordinator_prompt,
    allowed_tools=["Read", "Write", "Grep", "Glob"],
    permission_mode="acceptEdits",  # Auto-accept file operations
)
```

## Skills Framework

This application uses the Claude Skills framework to modularize capabilities. Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and detailed instructions.

### Available Skills

**1. Feature Identification** (`feature-identification`)
- Break down high-level application descriptions into discrete features
- Create feature stubs for multiple features
- Focus on BREADTH (many features) rather than depth

**2. Feature Discovery** (`feature-discovery`)
- Conduct deep Q&A to understand a single feature
- Create comprehensive feature descriptions
- Capture scope creep as future features
- Focus on DEPTH (detailed understanding)

**3. Iteration Breakdown** (`iteration-breakdown`)
- Break features into 2-8 vertical slices
- Ensure each increment delivers user value
- Identify dependencies between increments

**4. Prompt Generation** (`prompt-generation`)
- Generate detailed coding prompts for each increment
- Follow standardized template structure
- Provide comprehensive implementation guidance

### Skill Structure

Each skill follows this pattern:

```
feature_breakdown_agent/skills/
└── skill-name/
    └── SKILL.md          # Skill definition with YAML frontmatter
```

SKILL.md format:
```yaml
---
name: skill-name
description: When to use this skill (loaded into agent context)
---
# Detailed instructions (loaded when skill is invoked)
```

## Project Structure

### Development Structure (This Repo)
```
feature-breakdown-agent/
├── feature_breakdown_agent/         # Main package directory
│   ├── __init__.py                  # Package initialization
│   ├── feature_breakdown_agent.py   # Main application entry (~240 lines)
│   ├── coordinator_prompt.py        # Main coordinator system prompt
│   ├── display.py                   # Rich-based terminal UI
│   └── skills/                      # Claude Skills directory
│       ├── feature-identification/
│       │   ├── SKILL.md
│       │   └── future-feature-template.md
│       ├── feature-discovery/
│       │   ├── SKILL.md
│       │   ├── feature-template.md
│       │   └── future-feature-template.md
│       ├── iteration-breakdown/
│       │   ├── SKILL.md
│       │   └── increments-template.md
│       └── prompt-generation/
│           ├── SKILL.md
│           └── prompt-template.md
├── tests/                           # Unit tests
├── CLAUDE.md                        # This file
├── pyproject.toml                   # uv/pip project configuration
├── .python-version                  # Python 3.10+
└── prompt_generator_prd.md         # Complete product specification
```

### Target Project Structure (Where Agent Runs)
Users run this agent in their own projects, which should have:
```
user-project/
├── features/                         # Detailed feature descriptions
├── future-features/                  # Feature stubs for future planning
└── prompts/                          # Generated coding prompts
    └── [feature-name]/              # Organized by feature
        ├── increment_01_*.md
        └── increment_02_*.md
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
uv run polly

# Or using the full name
uv run feature-breakdown-agent

# Or directly with Python
uv run python feature_breakdown_agent/feature_breakdown_agent.py
```

### Testing
```bash
pytest tests/
```

## Critical Implementation Details

### The Four Skills (Replacing Old Phases)

**Feature Identification** (was: Feature Identification phase)
- Agent asks questions to understand the application
- Identifies multiple discrete features
- Creates stub documents in `future-features/` directory
- User must approve feature list before stubs are created

**Feature Discovery** (was: Phase 1)
- Minimum 5 clarifying questions required
- Intelligent follow-up questions based on responses
- Monitors for scope creep and captures future features
- Creates detailed feature description in `features/` directory
- User confirms understanding before document creation

**Iteration Breakdown** (was: Phase 2)
- Must create 2-8 increments per feature
- Each increment must be a **vertical slice** - delivers user value
- Each increment must be independently testable
- Identifies dependencies between increments and on existing features
- User must approve grouping before saving
- Creates increment structure file: `features/{feature-name}_increments.md`

**Prompt Generation** (was: Phase 3)
- Generates prompts sequentially (increment 1, then 2, etc.)
- Uses consistent template for all prompts
- Saves as `prompts/{feature-name}/increment_NN_description.md`
- Each prompt includes: overview, scope, dependencies, acceptance criteria, technical constraints, testing strategy

### Vertical Slice Principle
A vertical slice must:
- Deliver clear user value (not just infrastructure)
- Be independently testable by a user
- Touch all necessary layers (frontend, backend, database, etc.)
- Build on previous increments

### Context Awareness Requirements
- Agent explores existing feature docs on startup
- Agent identifies potential scope overlap with existing features
- Agent references existing feature files when noting dependencies
- Single session maintains conversation context throughout

### User Experience Expectations
- Conversational flow (agent decides when to use skills)
- Agent can present options when helpful (not always required)
- Tool usage indicated (e.g., "[Using Glob...]")
- Streaming responses for natural interaction
- File paths displayed when files are created
- Graceful error handling with recovery options
- User can interrupt with Ctrl+C

## Coordinator System Prompt

The main agent uses a coordinator system prompt (in `coordinator_prompt.py`) that:
- Introduces Polly and its purpose
- Describes available skills
- Guides when to use each skill
- Maintains conversational interaction style
- Explains project structure expectations
- Allows agent to present choices when appropriate

## Technology Constraints

- **Python 3.10+** minimum
- **Claude Agent SDK (Python)** with Claude Skills support
- **anyio** for async runtime
- **Claude Sonnet 4.5** model specifically
- **Rich** for terminal UI
- **Prompt Toolkit** for enhanced input
- **Questionary** for menu selections

## Testing Strategy

### Manual Testing Focus
- Agent explores existing feature docs correctly
- Skills are invoked appropriately based on user requests
- Agent asks relevant clarifying questions
- Agent groups functionality into logical increments
- Generated files follow template conventions
- Files saved with correct naming convention
- Dependencies correctly identified
- Conversational flow feels natural
- Context maintained throughout session

### Critical Edge Cases
- No existing feature documentation
- Very large features (10+ increments)
- Very small features (2 increments)
- Complex dependency chains
- User provides minimal vs. detailed answers
- User changes mind during conversation
- Scope creep detection and future feature capture

## Success Criteria (MVP)

Must have for V1:
- Agent uses skills appropriately based on conversation
- Generates properly formatted files using skills
- Reads existing feature documentation on startup
- Maintains conversation context in single session
- Uses prompt templates consistently
- Identifies scope overlap with existing features
- Validates increments are vertical slices
- Conversational interaction that feels natural

## Out of Scope (V1)

Not building:
- Web interface or GUI (terminal only)
- Authentication or multi-user support
- Cloud storage or sync
- Integration with project management tools
- Automatic execution of generated prompts
- Version control integration (beyond reading/writing files)

## Key Architectural Differences from Original

### Before (Phase-Based)
- 5 separate system prompts (~1500 lines of prompts)
- New agent session for each phase
- Manual context passing between phases
- Explicit phase transitions with completion signals
- ~2000 lines of orchestration code

### After (Skills-Based)
- 1 coordinator prompt + 4 skill SKILL.md files
- Single long-running agent session
- Natural context retention in conversation
- Skills invoked autonomously by agent
- ~240 lines of orchestration code
- Much more maintainable and extensible

## File References

- **Complete specification**: prompt_generator_prd.md
- **Main application**: feature_breakdown_agent/feature_breakdown_agent.py (~240 lines)
- **Coordinator prompt**: feature_breakdown_agent/coordinator_prompt.py
- **Skills directory**: feature_breakdown_agent/skills/
- **Display utilities**: feature_breakdown_agent/display.py
