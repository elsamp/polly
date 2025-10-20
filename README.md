# Feature Breakdown Agent

A terminal-based AI agent that transforms high-level feature descriptions into detailed, incremental coding prompts.

## Overview

This agent helps product managers, technical leads, and developers break down complex features into implementable vertical slices through an intelligent 4-phase workflow:

1. **Phase 0: Context Gathering** - Reads existing feature documentation to understand your codebase
2. **Phase 1: Discovery** - Conducts an interactive conversation with minimum 5 clarifying questions
3. **Phase 2: Incremental Grouping** - Breaks features into 2-8 vertical slices with clear user value
4. **Phase 3: Prompt Generation** - Generates detailed, ready-to-implement coding prompts

## Key Features

### Multi-Path Workflow
After context gathering, choose how to proceed:
- **Define a new feature** - Start fresh with Phase 1 discovery
- **Expand a future-feature stub** - Build on previously captured ideas
- **Continue an incomplete feature** - Resume at the appropriate phase

### Future Feature Capture
During discovery or grouping, the agent can identify scope creep and capture separate features as placeholders for later planning.

### Continuous Session
Work on multiple features in a single session - after completing a feature, the agent returns to the action menu instead of exiting.

### Smart Phase Detection
When continuing an incomplete feature, the agent automatically determines which phase to resume:
- Missing increments → Resume at Phase 2
- Missing prompts → Resume at Phase 3

## Installation

### Prerequisites

- Python 3.10+
- Claude Code CLI (for agent SDK)

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

### Setup

```bash
# Clone the repository
cd feature-breakdown-agent

# Install dependencies
uv pip install -e .

# Install dev dependencies (for testing)
uv pip install -e ".[dev]"
```

## Usage

### Basic Usage

```bash
# Run the agent
uv run feature-breakdown-agent

# Or with python directly
uv run python feature_breakdown_agent/feature_breakdown_agent.py
```

### Example Session

```
======================================================================
Welcome to the Feature Breakdown Agent!
======================================================================

Phase 0: Context Gathering
───────────────────────────────────────────────────────────────

Agent: Hello! Let's start by understanding your existing codebase.
       Where is your feature documentation located?
       (Press Enter for default: './features/')

You: ./features/

[Agent searches and reads existing feature documentation]

Agent: I found 3 existing features. Ready to continue?

You: yes

✓ Phase 0 Complete: Context Gathering

═══════════════════════════════════════════════════════════════
How would you like to proceed?

  1. Define a new feature
  2. Expand on an existing future-feature stub
  3. Continue with an existing feature
  4. Exit
═══════════════════════════════════════════════════════════════

Enter your choice (1-4): 1

[Proceeds to Phase 1: Discovery...]
```

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guidance.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_phase_0.py
```

### Current Status

✅ **MVP Complete** - All core features implemented

**Implemented:**
- ✅ Phase 0: Context Gathering
- ✅ Phase 1: Discovery (with future-feature capture)
- ✅ Phase 2: Incremental Grouping (with vertical slice validation)
- ✅ Phase 3: Prompt Generation (template-based)
- ✅ Multi-path workflow (new/expand/continue)
- ✅ Continuous session support
- ✅ Smart phase detection and resumption

**Project Structure:**
```
your-project/
├── features/              # Feature documentation (agent reads)
├── future-features/       # Captured ideas for later (agent creates)
└── prompts/              # Generated prompts (agent creates)
    └── {feature-name}/
        ├── increment_01_*.md
        ├── increment_02_*.md
        └── ...
```

## Documentation

- **[PRD](prompt_generator_prd.md)** - Complete product requirements
- **[CLAUDE.md](CLAUDE.md)** - Development context and architecture
- **[Agent SDK Guide](.claude/claude_agent_sdk_guide.md)** - SDK reference

## License

MIT
