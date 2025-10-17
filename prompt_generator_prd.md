# Product Requirements Document: Feature Breakdown Agent

## Overview

### Purpose
A terminal-based AI agent that transforms high-level feature descriptions into detailed, incremental coding prompts suitable for instructing a coding agent on implementation.

### Target Users
- Product managers planning feature development
- Technical leads breaking down complex features
- Solo developers organizing implementation work
- Engineering teams structuring sprint work

### Core Value Proposition
Eliminates the tedious manual work of breaking features into implementable increments and writing detailed prompts, while ensuring each increment delivers testable user value as a vertical slice.

---

## User Workflow

### Phase 0: Context Gathering
**Agent Actions:**
1. Search for existing feature documentation in the project
2. Read relevant `.md` files to understand existing scope
3. Summarize what already exists
4. Build understanding of system architecture and dependencies

**User Actions:**
- Provide feature documentation directory location if needed
- Confirm understanding of existing features

### Phase 1: Discovery
**Agent Actions:**
1. Ask clarifying questions about the feature:
   - What problem does it solve?
   - Who are the users?
   - What are the technical constraints?
   - What dependencies exist?
   - What's the expected behavior?
2. Ask intelligent follow-up questions based on responses
3. Reference existing features when asking about integration points
4. Continue until complete understanding is achieved

**User Actions:**
- Answer questions about the feature
- Provide additional context when asked
- Confirm when discovery feels complete

**Exit Criteria:**
- Agent has clear understanding of feature scope
- Technical constraints are identified
- Dependencies are documented
- User confirms readiness to proceed

### Phase 2: Incremental Grouping
**Agent Actions:**
1. Group functionality into logical increments
2. For each increment, ensure:
   - It delivers clear user value (not just scaffolding)
   - It's independently testable by a user
   - It builds on previous increments
   - It's a vertical slice (touches all layers needed)
3. Identify dependencies on existing features
4. Note any potential scope overlap with existing features
5. Present the increment structure for review

**User Actions:**
- Review proposed increments
- Request adjustments to grouping
- Approve grouping to proceed

**Exit Criteria:**
- User approves the increment structure
- Each increment meets vertical slice criteria
- Dependencies are clearly identified

### Phase 3: Prompt Generation
**Agent Actions:**
1. For each increment, generate a detailed coding prompt using the specified template
2. Include all necessary context:
   - Feature overview
   - Specific increment scope
   - Dependencies (including references to existing feature docs)
   - Acceptance criteria
   - Technical constraints
   - Implementation guidance
3. Save each prompt as a separate `.md` file
4. Present summary of generated prompts

**User Actions:**
- Review generated prompts
- Request refinements if needed
- Confirm completion

**Exit Criteria:**
- All increments have corresponding prompt files
- Prompts follow the template structure
- User confirms prompts are ready to use

---

## Functional Requirements

### FR-1: Context Awareness
- **FR-1.1**: Agent must search for existing feature documentation before starting discovery
- **FR-1.2**: Agent must read and analyze existing `.md` files in specified directory
- **FR-1.3**: Agent must identify potential scope overlap with existing features
- **FR-1.4**: Agent must reference existing feature files when noting dependencies
- **FR-1.5**: Agent must allow user to specify custom feature documentation directory

### FR-2: Interactive Discovery
- **FR-2.1**: Agent must ask minimum 5 clarifying questions during discovery
- **FR-2.2**: Agent must ask follow-up questions based on user responses
- **FR-2.3**: Agent must explicitly signal when discovery phase is complete
- **FR-2.4**: Agent must allow user to provide additional context at any point
- **FR-2.5**: Agent must maintain conversation history throughout session

### FR-3: Increment Grouping
- **FR-3.1**: Agent must create 2-8 increments per feature (reasonable scope)
- **FR-3.2**: Each increment must deliver testable user value
- **FR-3.3**: Each increment must be a vertical slice (not horizontal layer)
- **FR-3.4**: Agent must present increment structure in clear, readable format
- **FR-3.5**: Agent must allow user to request regrouping
- **FR-3.6**: Agent must identify dependencies between increments
- **FR-3.7**: Agent must identify dependencies on existing features

### FR-4: Prompt Generation
- **FR-4.1**: Agent must use consistent template for all prompts
- **FR-4.2**: Agent must save each prompt as separate `.md` file
- **FR-4.3**: Filenames must follow pattern: `increment_NN_description.md`
- **FR-4.4**: Each prompt must include:
  - Feature overview
  - Increment-specific scope
  - Dependencies (with file references)
  - Acceptance criteria (3-5 items minimum)
  - Technical constraints
  - Implementation guidance
- **FR-4.5**: Agent must generate prompts sequentially (increment 1, then 2, etc.)

### FR-5: Terminal Interface
- **FR-5.1**: Application must run in terminal/command line
- **FR-5.2**: User input via standard input prompts
- **FR-5.3**: Agent responses stream naturally (not dumped all at once)
- **FR-5.4**: Tool usage (file reads, searches) should be visible to user
- **FR-5.5**: User can interrupt with Ctrl+C and resume conversation
- **FR-5.6**: User can exit cleanly with 'exit' or 'quit' command

---

## Technical Requirements

### TR-1: Technology Stack
- Python 3.10+
- Claude Agent SDK (Python)
- anyio for async runtime
- Claude Sonnet 4.5 model

### TR-2: Architecture
- Single conversational agent (no subagents needed)
- ClaudeSDKClient for session management
- Custom MCP tool for prompt generation
- File system tools: Read, Write, Grep, Glob

### TR-3: Agent Configuration
```python
ClaudeAgentOptions(
    system_prompt=<detailed_prompt>,
    allowed_tools=["Read", "Write", "Grep", "Glob", "mcp__prompt-tools__generate_prompt"],
    permission_mode="acceptEdits",  # Auto-accept file operations
    setting_sources=["project"],  # Load CLAUDE.md if present
)
```

### TR-4: File Organization
#### Agent Application Project Structure
The project where the agent application is developed and maintained:
```
feature-breakdown-agent/
├── src/
│   ├── feature_breakdown_agent.py    # Main application
│   ├── prompt_template.py            # Template definition
│   └── utils.py                      # Helper functions (optional)
├── tests/                            # Unit tests
├── CLAUDE_AGENT_SDK_GUIDE.md        # SDK reference guide
├── README.md                         # Usage instructions
├── requirements.txt                  # Python dependencies
├── .claude/
│   └── CLAUDE.md                     # Agent development context
└── .gitignore
```

#### Target Project Structure
The project where the agent is used to generate prompts (user's working project):
```
user-project/
├── features/                         # Existing feature documentation
│   ├── auth.md
│   ├── profile.md
│   └── payments.md
├── prompts/                          # Generated prompts (created by agent)
│   ├── notifications/                # Organized by feature
│   │   ├── increment_01_infrastructure.md
│   │   ├── increment_02_inapp_display.md
│   │   └── ...
│   └── search/
│       ├── increment_01_basic_search.md
│       └── ...
├── src/                              # User's application code
├── .claude/
│   └── CLAUDE.md                     # User's project context (optional)
└── [other project files]

---

## Prompt Template Specification

Each generated prompt must follow this structure:

```markdown
# Feature: [Feature Name]
# Increment N: [Increment Name]

## Overview
[Brief description of the overall feature and this specific increment]

## Scope of This Increment
[Detailed description of what will be built in this increment]

### What's Included
- [Specific functionality item 1]
- [Specific functionality item 2]
- [Specific functionality item 3]

### What's NOT Included (Deferred to Later Increments)
- [Functionality deferred to next increment]
- [Future enhancements]

## Dependencies

### Previous Increments
- [Reference to increment N-1, if applicable]
- [What must be complete before this increment]

### Existing Features
- [Reference to existing_feature.md] - [Why it's relevant]
- [Another feature file] - [Integration points]

### External Dependencies
- [Third-party libraries, APIs, or services needed]
- [Infrastructure requirements]

## User Value
[Clear statement of what user can do after this increment is complete]

### User Story
As a [user type], I want to [action] so that [benefit].

## Acceptance Criteria
1. [Specific, testable criterion]
2. [Specific, testable criterion]
3. [Specific, testable criterion]
4. [Specific, testable criterion]
5. [Specific, testable criterion]

## Technical Constraints
- [Technology limitations]
- [Performance requirements]
- [Security considerations]
- [Scalability needs]

## Testing Strategy
- **Unit tests**: [What to test]
- **Integration tests**: [What to test]
- **Manual testing**: [What to verify]

## Edge Cases to Consider
- [Edge case 1 and how to handle]
- [Edge case 2 and how to handle]
- [Edge case 3 and how to handle]


---
**Generated by Feature Breakdown Agent**
**Date**: [Timestamp]
**Feature**: [Feature name]
**Increment**: N of M
```

---

## System Prompt Specification

The agent's system prompt must include:

1. **Role Definition**: Product Requirements specialist
2. **Context Awareness Instructions**: How to search and analyze existing features
3. **Phase Definitions**: Clear descriptions of phases 0-3
4. **Transition Criteria**: When to move between phases
5. **Increment Criteria**: What makes a good vertical slice
6. **Overlap Prevention Rules**: How to check against existing features
7. **Template Requirements**: Reference to prompt template structure

---

## User Experience Requirements

### UX-1: Conversational Flow
- Agent responses should feel natural, not robotic
- Agent should briefly acknowledge user input before proceeding
- Agent should summarize understanding before transitions
- Agent should ask permission before major transitions

### UX-2: Visual Clarity
- Phase transitions should be clearly marked
- Tool usage should be indicated (e.g., "[Searching existing features...]")
- Progress should be visible during generation
- File paths should be displayed when files are created

### UX-3: Error Handling
- Graceful handling of file not found errors
- Clear error messages for invalid input
- Ability to recover from interrupted operations
- Confirmation prompts before overwriting existing files

### UX-4: Flexibility
- User can request changes at any phase
- User can provide additional context at any time
- User can skip context gathering if no existing features
- User can regenerate specific prompts without redoing all

---

## Success Criteria

### Must Have (MVP)
- ✅ Agent completes all 4 phases successfully
- ✅ Generates properly formatted prompt files
- ✅ Reads existing feature documentation
- ✅ Interactive conversation with user input
- ✅ Uses prompt template consistently
- ✅ Saves output to files

### Should Have
- ✅ Identifies scope overlap with existing features
- ✅ Validates increments are vertical slices
- ✅ Clear visual indicators for tool usage
- ✅ Graceful error handling
- ✅ Progress indicators during generation

### Could Have (Future)
- [ ] Edit existing prompts after generation
- [ ] Export all prompts as single document
- [ ] Generate visual dependency graph
- [ ] Support for multiple feature documentation formats
- [ ] Integration with project management tools
- [ ] Validation of generated prompts against template

---

## Out of Scope (V1)

- Web interface or GUI
- Authentication or multi-user support
- Cloud storage or sync
- Integration with specific project management tools (Jira, Linear, etc.)
- Automatic execution of generated prompts
- Version control integration
- Collaborative editing of prompts

---

## Testing Requirements

### Manual Testing Checklist
- [ ] Agent successfully reads existing feature docs
- [ ] Agent asks relevant clarifying questions
- [ ] Agent groups functionality into logical increments
- [ ] Generated prompts follow template exactly
- [ ] Files are saved with correct naming convention
- [ ] Dependencies are correctly identified
- [ ] User can exit and restart cleanly
- [ ] Conversation context is maintained throughout

### Edge Cases to Test
- [ ] No existing feature documentation
- [ ] Very large feature (10+ increments)
- [ ] Very small feature (2 increments)
- [ ] Feature with complex dependencies
- [ ] Feature with no dependencies
- [ ] User provides minimal answers
- [ ] User provides very detailed answers
- [ ] User requests to redo grouping multiple times

