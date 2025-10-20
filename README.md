# Feature Breakdown Agent

A terminal-based AI agent that transforms high-level feature descriptions into detailed, incremental coding prompts.

## Overview

This agent helps product managers, technical leads, and developers break down complex features into implementable vertical slices through an intelligent workflow:

• **Context Gathering** - Reads existing feature documentation to understand your codebase
• **Discovery** - Conducts an interactive conversation with minimum 5 clarifying questions
• **Incremental Grouping** - Breaks features into 2-8 vertical slices with clear user value
• **Prompt Generation** - Generates detailed, ready-to-implement coding prompts

## Key Features

### Multi-Path Workflow
After context gathering, choose how to proceed:
- **Discover application features** - Identify multiple discrete features at once (great for new projects)
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

**Option 1: Install with uv (recommended - cleanest for development)**

```bash
# From this directory, install in editable mode
uv tool install --editable .

# Now you can run 'polly' from anywhere!
cd /path/to/any-project
polly
```

**Option 2: Install with pipx (recommended for end users)**

```bash
# Install pipx if you don't have it
pip install --user pipx
pipx ensurepath

# From this directory, install globally
pipx install .

# Now you can run 'polly' from anywhere!
cd /path/to/any-project
polly
```

**Option 3: Install with pip**

```bash
# From this directory, install globally
pip install .

# Run from anywhere
cd /path/to/any-project
polly
```

**Option 4: Development mode with uv (requires uv run prefix)**

```bash
# Install in editable mode
uv pip install -e .

# Run from your project using uv run
cd /path/to/any-project
uv run polly
```

## Usage

### Basic Usage

**Important:** Run the agent from within your project directory. The agent will use your current working directory as the project root.

```bash
# Navigate to your project
cd /path/to/your-project

# If you installed with Option 1, 2, or 3:
polly

# If you installed with Option 4 (uv pip install -e):
uv run polly

# You can also use the full command name:
feature-breakdown-agent
```

### Example Session

```
======================================================================
Welcome to the Feature Breakdown Agent!
======================================================================

Starting: Context Gathering
───────────────────────────────────────────────────────────────

Agent: Hello! Let's start by understanding your project.

Project folder: /Users/you/your-project
       Is this correct? (Press Enter to confirm, or type a different path)

You: [Press Enter]

[Agent checks for features/ folder and existing documentation]

Agent: I found 3 existing features. Ready to continue?

You: yes

✓ Context Gathering Complete

═══════════════════════════════════════════════════════════════
How would you like to proceed?

  1. Discover application features (create multiple feature stubs)
  2. Define a new feature
  3. Expand on an existing future-feature stub
  4. Continue with an existing feature
  5. Exit
═══════════════════════════════════════════════════════════════

Enter your choice (1-5): 1

[Proceeds to Feature Discovery or Phase 1...]
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
- ✅ Context Gathering
- ✅ Feature Discovery (identify multiple features at once)
- ✅ Discovery (with future-feature capture)
- ✅ Incremental Grouping (with vertical slice validation)
- ✅ Prompt Generation (template-based)
- ✅ Multi-path workflow (discover/new/expand/continue)
- ✅ Continuous session support
- ✅ Smart phase detection and resumption
- ✅ Global CLI command (`polly`)

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
