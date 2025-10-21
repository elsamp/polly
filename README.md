# Polly - Feature Breakdown Agent

A conversational AI agent that transforms high-level feature descriptions into detailed, incremental coding prompts using the Claude Skills framework.

## Overview

Polly helps product managers, technical leads, and developers break down complex features into implementable vertical slices through an intelligent, conversational workflow powered by Claude Skills:

• **Feature Identification** - Break down high-level application descriptions into discrete features
• **Feature Discovery** - Deep dive into a single feature with interactive Q&A
• **Iteration Breakdown** - Split features into 2-8 vertical slices with clear user value
• **Prompt Generation** - Generate detailed, ready-to-implement coding prompts

## Key Features

### Skills-Based Architecture

Polly uses Claude Skills to modularize its capabilities. Each skill is invoked autonomously by the agent based on the conversation:

- **feature-identification** - Identify multiple discrete features from app descriptions
- **feature-discovery** - Conduct deep discovery on a single feature
- **iteration-breakdown** - Break features into vertical slices
- **prompt-generation** - Generate implementation prompts

### Conversational Interaction

Polly maintains a single, long-running conversation session where it:
- Autonomously decides when to use skills based on your requests
- Maintains context throughout the entire workflow
- Can present options when helpful (but doesn't require explicit menus)
- Feels natural and responsive

### Future Feature Capture

During discovery or breakdown, Polly can identify scope creep and capture separate features as placeholders for later planning.

### Smart Context Awareness

On startup, Polly:
- Explores your project for existing feature documentation
- Understands what you've already defined
- Identifies incomplete features
- Guides you on what to do next

## Installation

### Prerequisites

- Python 3.10+
- Claude Agent SDK

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

**Important:** Run Polly from within your project directory. The agent will use your current working directory as the project root.

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
   ___      _ _
  / _ \___ | | |_   _
 / /_)/ _ \| | | | | |
/ ___/ (_) | | | |_| |
\/    \___/|_|_|\__, |
                |___/

A terminal-based AI agent that helps you define features and transform
high level feature descriptions into detailed, incremental coding prompts.

Project folder: /Users/you/your-project
Would you like to use this folder?
  > Use this folder
    Specify a different folder

Starting Polly...

Agent: Let me check if there's a features directory...
[Using Glob...]

Agent: I found 3 existing features in your project:
- User Authentication
- Profile Management
- Search Functionality

Would you like to continue one of these features, start a new one, or
identify more features for your application?

You: I want to add a notification system

Agent: Great! Let me help you develop that feature. To start with, can
you tell me what types of notifications you're envisioning? For example,
email, in-app, push notifications, or something else?

You: Email and in-app notifications

Agent: Perfect. Who will be receiving these notifications? End users,
administrators, or both?

[Conversation continues with deep discovery...]

Agent: Based on our discussion, I've created a comprehensive feature
description saved to features/notification-system.md. Would you like
me to break this down into implementable increments now?

You: yes

[Agent uses iteration-breakdown skill to create vertical slices...]

Agent: I've broken this into 4 increments. Would you like me to generate
the detailed coding prompts for each increment?

You: yes

[Agent uses prompt-generation skill...]

Agent: I've generated 4 detailed prompts in prompts/notification-system/.
These are ready to use with developers or AI coding agents! Would you
like to work on another feature?
```

### Workflow Options

Polly adapts to your needs:

**New Project:**
1. "I'm building a task management app" → Feature Identification → Multiple feature stubs
2. Pick a feature → Feature Discovery → Detailed description
3. Iteration Breakdown → Vertical slices
4. Prompt Generation → Implementation guides

**Existing Project:**
- "Continue working on user authentication" → Resumes where you left off
- "Add a new reporting feature" → Feature Discovery for new feature
- "I have feature stubs from before" → Expand on specific stub

**Natural Requests:**
- "Break down my search feature"
- "Help me identify features for my app"
- "Generate prompts for the authentication feature"

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development guidance.

### Project Structure

**Development (This Repo):**
```
feature-breakdown-agent/
├── feature_breakdown_agent/
│   ├── feature_breakdown_agent.py   # Main agent (~240 lines)
│   ├── coordinator_prompt.py        # Coordinator system prompt
│   ├── display.py                   # Terminal UI
│   └── skills/                      # Claude Skills
│       ├── feature-identification/
│       │   └── SKILL.md
│       ├── feature-discovery/
│       │   └── SKILL.md
│       ├── iteration-breakdown/
│       │   └── SKILL.md
│       └── prompt-generation/
│           └── SKILL.md
├── tests/
├── CLAUDE.md                        # Development context
└── pyproject.toml
```

**User Projects (Where Polly Runs):**
```
your-project/
├── features/              # Feature descriptions (Polly creates/reads)
├── future-features/       # Feature stubs for later (Polly creates)
└── prompts/              # Generated coding prompts (Polly creates)
    └── {feature-name}/
        ├── increment_01_*.md
        ├── increment_02_*.md
        └── ...
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_agent.py
```

### Architecture

**Skills-Based Design:**
- Single long-running agent session (not multiple phases)
- Skills invoked autonomously based on conversation
- Natural context retention throughout session
- ~240 lines of orchestration code (vs ~2000 in phase-based version)

**Key Advantages:**
- Much more maintainable (skills are self-contained)
- More flexible (users can request actions naturally)
- Better context management (single session)
- Easier to extend (add new skills without touching core)

## Current Status

✅ **Skills-Based Refactor Complete**

**Implemented:**
- ✅ Claude Skills framework integration
- ✅ Single conversational agent session
- ✅ Autonomous skill invocation
- ✅ Feature Identification skill
- ✅ Feature Discovery skill
- ✅ Iteration Breakdown skill
- ✅ Prompt Generation skill
- ✅ Context-aware exploration on startup
- ✅ Future feature capture
- ✅ Conversational interaction style
- ✅ Global CLI command (`polly`)

## Documentation

- **[PRD](prompt_generator_prd.md)** - Complete product requirements
- **[CLAUDE.md](CLAUDE.md)** - Development context and skills architecture
- **[Skills](feature_breakdown_agent/skills/)** - Individual skill definitions

## License

MIT
