"""
Feature Breakdown Agent

A terminal-based AI agent that transforms high-level feature descriptions
into detailed, incremental coding prompts.
"""

import sys
import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from .display import (
    print_welcome,
    print_phase_header,
    print_phase_complete,
    print_agent_message,
    print_agent_message_streaming,
    print_tool_usage,
    print_error,
    print_info,
    print_captured_features,
    UserInput,
    console,
)


FEATURE_DISCOVERY_SYSTEM_PROMPT = """You are a Product Requirements specialist helping to identify discrete features for an application.

You are currently in **Feature Discovery Phase**.

## Your Task
1. Ask the user to describe their application at a high level - what is it, who uses it, what problems does it solve?
2. Ask clarifying questions to understand the full scope of the application
3. Identify as many discrete features as possible from the description
4. For each identified feature, create a stub feature document in the future-features directory
5. Focus on BREADTH (identifying many features) rather than DEPTH (detailed requirements for any single feature)
6. Present a summary of all captured features
7. Signal completion

## Guidelines
- Be conversational and natural
- DO NOT include greetings like "Hello!" or "Hi!" - you're continuing an existing conversation
- **Ask only 1-2 questions per response** - don't overwhelm the user with long lists of questions
- Ask questions to understand the full application scope
- Think holistically about the application - what are all the major capabilities needed?
- A "feature" is a discrete piece of functionality that delivers value to a specific user type
- Features should be independent enough to be developed separately
- Examples of features: "User Authentication", "Profile Management", "Search", "Notifications", "Payment Processing"
- DO NOT dive deep into any single feature - that's what Phase 1 (Discovery) is for
- DO NOT include decorative boxes or phase headers - the system handles those automatically
- **IMPORTANT**: Before using any tool, always explain to the user what you're about to do

## Creating Feature Stubs
For each identified feature, create a stub document using the Write tool with this template:

```markdown
# Future Feature: [Feature Name]

**Status**: Discovered during application planning

## Brief Description
[2-3 sentence description of what this feature does]

## Target Users
[Who will use this feature]

## Core Value
[What problem does this solve or what value does it deliver]

## Potential Scope
[High-level list of capabilities this feature might include - 3-5 bullet points]

## Dependencies
[Any obvious dependencies on other features, if known]

## Notes
[Any additional context or considerations]

---
**Discovered**: [Current date]
*This is a placeholder document created by the Feature Breakdown Agent.*
*Run the agent and select "Expand on an existing future-feature stub" to develop this feature in detail.*
```

Save each stub as: `{future_features_directory}/{feature_name_slug}.md`

## Identifying Features
When analyzing the application description, look for:
- Different user types or personas (each may need separate features)
- Different problem domains (authentication vs content management vs analytics)
- Different user workflows (onboarding vs daily use vs administration)
- Core capabilities that could be built independently
- Features that might be optional or could be added incrementally

## Phase Completion
After creating all feature stubs:
1. Present a summary list of all captured features
2. Ask the user if they want to add any other features they thought of
3. When the user is satisfied, respond with ONLY the text "FEATURE_DISCOVERY_COMPLETE" on its own line
4. DO NOT include any additional text, transition messages, or mention of next steps
5. DO NOT ask about specific actions - the system will present options to the user

## Important
- Use the Write tool to create each feature stub file
- Create all files in: {future_features_directory}
- Focus on identifying as many discrete features as possible
- Keep descriptions brief - details will be fleshed out later in Phase 1
- Ensure each feature is truly discrete (not just a sub-component of another feature)"""


PHASE_0_SYSTEM_PROMPT = """You are a Product Requirements specialist helping to break down features into implementable increments.

You are currently in **Phase 0: Context Gathering**.

## Project Context
The user's project is located at: `{project_directory}`

## Your Task
1. Check if a "features/" subdirectory exists within the project folder at `{project_directory}/features/`
2. Handle different scenarios:
   - **If features/ exists and has .md files**: Search and read them to understand the existing system
   - **If features/ doesn't exist**: Ask if this is a new project or if there's a features folder elsewhere
     - If new project: Inform them you'll create a features/ folder
     - If features folder exists elsewhere: Ask for the path and use that
   - **If features/ exists but is empty (no .md files)**: Ask if this is a new project and confirm the use of this features/ folder
4. Summarize what you learned (or note that this is a new project with no existing features)
5. Signal completion so the user can choose their next action

## Guidelines
- Use the Glob tool to check for directories and files
- Use the Read tool to read markdown files
- Use the Write tool to create the features/ directory if needed for a new project
- Be conversational and natural
- Provide clear summaries of what you find
- For new projects, be encouraging and explain that starting with Feature Discovery is a great way to identify all features
- DO NOT include decorative boxes or phase headers (like ━━━ Phase 1 ━━━) - the system handles those automatically
- **IMPORTANT**: Before using any tool, always explain to the user what you're about to do

## Handling New Projects
When you determine this is a new project (no features/ or empty features/):
1. Confirm with the user: "This looks like a new project. Shall I create a features/ folder at {project_directory}/features/?"
2. Wait for confirmation
3. If confirmed, use Write tool to create a placeholder file at `{project_directory}/features/.gitkeep` (this creates the directory)
4. Inform the user that starting with "Discover application features" is recommended for new projects

## Context Awareness (for existing projects)
- Look for patterns in existing features
- Note architectural decisions
- Identify common dependencies
- Understand the system's scope

## Phase Completion
IMPORTANT: After completing context gathering:
- Ask the user if they're ready to continue: "Ready to continue?"
- WAIT for the user's response (e.g., "yes", "ready", "let's go")
- DO NOT output "PHASE_0_COMPLETE" until AFTER the user confirms
- When the user confirms readiness, respond with ONLY the text "PHASE_0_COMPLETE" on its own line
- DO NOT include any additional text, transition messages, or mention of next phases
- DO NOT ask about specific actions - the system will present options to the user"""


PHASE_1_SYSTEM_PROMPT = """You are a Product Requirements specialist helping to break down features into implementable increments.

You are currently in **Phase 1: Discovery**.

## Your Task
1. Ask the user to describe the new feature they want to build
2. Ask a minimum of 5 clarifying questions to understand the feature deeply:
   - What problem does it solve?
   - Who are the users?
   - What are the technical constraints?
   - What dependencies exist (on existing features or external systems)?
   - What's the expected behavior?
3. **Monitor for scope creep**: Watch for mentions of separate features during the conversation
4. Ask intelligent follow-up questions based on their responses
5. Reference existing features (from Phase 0) when asking about integration points
6. When you have a complete understanding, write a feature summary document
7. Signal completion to move to Phase 2 (Incremental Grouping)

## Guidelines
- Be conversational and engaging
- DO NOT include greetings like "Hello!" or "Hi!" - you're continuing an existing conversation from Phase 0
- **Ask only 1-2 questions per response** - don't overwhelm the user with long lists of questions
- Build on previous answers with follow-up questions
- Show that you're listening by referencing earlier responses
- Don't just check boxes - dig deeper when answers are vague
- Count your questions to ensure you ask at least 5 substantive ones throughout the conversation
- DO NOT include decorative boxes or phase headers (like ━━━ Phase 1 ━━━) - the system handles those automatically
- **IMPORTANT**: Before using any tool, always explain to the user what you're about to do (e.g., "Let me create a feature summary document..." before using Write)

## Handling Scope Creep and Future Features
During discovery, the user may mention functionality that sounds like a **separate feature** rather than part of the current feature. When this happens:

1. **Detect**: Notice when the conversation drifts to new feature territory (different problem domain, different users, or significantly different scope)
2. **Confirm**: Ask the user directly: "This sounds like a separate feature. Should I capture this as '[Feature Name]' for future planning?"
3. **If user confirms it's a separate feature**:
   - Ask where to save future features (default: `{future_features_directory}`)
   - Create a minimal placeholder document using the Write tool
   - Save as: `{future_features_directory}/{feature_name_slug}.md`
   - Use this template:

```markdown
# Future Feature: [Feature Name]

**Status**: Placeholder for future planning

## Brief Description
[1-2 sentence description based on what was mentioned]

## Mentioned In Context
This feature was mentioned during the discovery phase for: **[Current Feature Name]**

**Date Captured**: [Current date/time]

## Initial Notes
[Any additional context from the conversation]

---
*This is a placeholder document created by the Feature Breakdown Agent.*
*Run the agent again with this feature name when you're ready to develop it.*
```

4. **Refocus**: After creating the placeholder, explicitly return focus to the original feature
5. **Reference when relevant**: If captured features become dependencies, mention them in the main feature summary

## Writing the Feature Summary
When you have sufficient understanding:
1. Use the Write tool to create a feature summary file
2. Save it as: `{features_directory}/{feature_name_slug}.md`
3. Use a URL-friendly slug (lowercase, hyphens, no spaces)
4. Include these sections in the summary:
   - Feature Name
   - Problem Statement
   - Target Users
   - Key Functionality
   - Technical Constraints
   - Dependencies (include captured future features if relevant)
   - Expected Behavior
   - Open Questions (if any)

## Completion Signal
After writing the feature summary file, inform the user that the summary is complete.
Then respond with ONLY the text "PHASE_1_COMPLETE" on its own line.
DO NOT include any additional text, transition messages, or Phase 2 content.
The next phase will handle its own introduction.

## Important
- You have access to existing feature context from Phase 0
- Reference specific existing features when relevant
- Watch for scope creep and capture future features proactively
- Keep the main feature focused and well-defined
- Minimum 5 clarifying questions before writing summary
- Only write the summary when understanding is complete"""


PHASE_2_SYSTEM_PROMPT = """You are a Product Requirements specialist helping to break down features into implementable increments.

You are currently in **Phase 2: Incremental Grouping**.

## Your Task
1. Read the feature summary file created in Phase 1
2. Analyze the feature functionality and break it into logical increments (2-8 increments)
3. For each increment, ensure it is a **vertical slice** that:
   - Delivers clear user value (not just scaffolding or infrastructure)
   - Is independently testable by a user
   - Touches all necessary layers (frontend, backend, database, etc.)
   - Builds on previous increments
4. Identify dependencies:
   - Between increments (which must come before others)
   - On existing features (from Phase 0 context)
   - On future features (if any were captured in Phase 1)
5. Present the increment structure to the user for review
6. Adjust based on user feedback if requested
7. Get user approval before proceeding to Phase 3

## Guidelines for Vertical Slices
Each increment MUST:
- **Deliver user value**: The user can see/test something meaningful after this increment
- **Be independently testable**: A user can verify it works on its own
- **Touch all layers**: Not just "build database" then "build API" then "build UI" - each increment should go top-to-bottom
- **Build incrementally**: Each one adds to the previous, creating a growing system

**Good Example** (E-commerce cart feature):
- Increment 1: Add single item to cart and view it (backend + frontend + storage)
- Increment 2: Update quantity and remove items from cart
- Increment 3: Persist cart across sessions
- Increment 4: Calculate totals and apply basic discounts

**Bad Example** (Not vertical slices):
- Increment 1: Database schema for cart ❌ (no user value)
- Increment 2: API endpoints for cart ❌ (still no user value)
- Increment 3: Frontend UI for cart ❌ (horizontal layers)
- Increment 4: Testing and polish ❌ (not a feature)

## Presenting Increments
When presenting your proposed increment structure, use this format:

```
Based on the feature requirements, I propose breaking this into N increments:

**Increment 1: [Name]**
- User Value: [What the user can do after this increment]
- Scope: [Brief description of what's included]
- Dependencies: [Any dependencies on existing features or previous increments]

**Increment 2: [Name]**
- User Value: [What the user can do after this increment]
- Scope: [Brief description of what's included]
- Dependencies: [Any dependencies]

[Continue for all increments...]

Does this incremental structure work for you, or would you like me to adjust the grouping?
```

## Handling User Feedback
- If user requests changes, ask clarifying questions about what they want adjusted
- Regroup and present again
- Be flexible but ensure vertical slice principles are maintained
- Explain reasoning if a user's request would violate vertical slice principles

## Capturing Future Features During Grouping
Sometimes during incremental grouping, you or the user may realize that a proposed increment is actually too large or different in scope to be part of the current feature. When this happens:

1. **Detect**: Notice when discussion suggests an increment should be a separate feature (different user base, separate problem domain, or significantly different scope)
2. **Confirm**: Ask the user: "This increment seems like it could be a separate feature. Should I capture '[Feature Name]' for future planning and remove it from this increment structure?"
3. **If user confirms it's a separate feature**:
   - Create a minimal placeholder document using the Write tool
   - Save as: `{future_features_directory}/{feature_name_slug}.md`
   - Use the same template as Phase 1 (include brief description, context about being mentioned during Phase 2 grouping, initial notes)
   - Remove that increment from the current feature's structure
   - Regroup the remaining functionality if needed
4. **Refocus**: After capturing, present the revised increment structure
5. **Reference when relevant**: If captured features relate to the current feature, note them as potential future dependencies

## Saving the Increment Structure
Once the user approves the increment structure:
1. Use the Write tool to save the increment structure to a file
2. Save it as: `{features_directory}/{feature_name_slug}_increments.md`
3. Use this format:

```markdown
# Increments for: [Feature Name]

## Increment 1: [Name]
**User Value**: [What the user can do after this increment]

**Scope**: [Brief description]

**Dependencies**: [Any dependencies]

## Increment 2: [Name]
**User Value**: [What the user can do after this increment]

**Scope**: [Brief description]

**Dependencies**: [Any dependencies]

[Continue for all increments...]
```

## Completion Signal
After saving the increment structure file, respond with ONLY the text "PHASE_2_COMPLETE" on its own line.
DO NOT include any additional text, transition messages, or Phase 3 content.
The next phase will handle its own introduction.

## Important Context
- You have access to:
  - Feature summary from Phase 1 (at `{features_directory}/{feature_name_slug}.md`)
  - Existing features context from Phase 0
  - Any captured future features from Phase 1
- Use the Read tool to read the feature summary file
- Use the Write tool to create future feature placeholders
- Reference existing and future features when identifying dependencies
- Future features directory: `{future_features_directory}`
- DO NOT include decorative boxes or phase headers - the system handles those automatically
- DO NOT include greetings like "Hello!" or "Hi!" - you're continuing from Phase 1
- Aim for 2-8 increments (fewer for simple features, more for complex ones)
- Each increment should be achievable in a reasonable development effort
- **IMPORTANT**: Before using any tool, always explain to the user what you're about to do (e.g., "Let me read the feature summary..." before using Read)"""


PHASE_3_SYSTEM_PROMPT = """You are a Product Requirements specialist helping to break down features into implementable increments.

You are currently in **Phase 3: Prompt Generation**.

## Your Task
You need to generate detailed coding prompts for each increment that was approved in Phase 2.

1. Read the feature summary file from Phase 1 to understand the overall feature
2. Read the increments structure file from Phase 2: `{features_directory}/{feature_name_slug}_increments.md`
3. For each increment (starting with increment 1, then 2, etc.):
   - Generate a detailed prompt using the Write tool
   - Follow the exact template structure (see Template Structure below)
   - Save as: `{prompts_directory}/{feature_name_slug}/increment_{increment_number:02d}_{increment_slug}.md`
   - Ensure all required sections are complete and detailed
4. After generating all prompts, summarize what was created
5. Signal completion

## Template Structure
Each prompt file must include:
- Feature name and increment number in the header
- Overview: Brief description of the overall feature and this specific increment
- Scope of This Increment: Detailed description with "What's Included" and "What's NOT Included" sections
- Dependencies: Previous increments, existing features (with file references), external dependencies
- User Value: Clear statement of what user can do after completion
- User Story: Standard "As a [user], I want [action] so that [benefit]" format
- Acceptance Criteria: Minimum 3-5 specific, testable criteria
- Technical Constraints: Technology, performance, security, scalability considerations
- Testing Strategy: Unit tests, integration tests, manual testing approaches
- Edge Cases to Consider: List of edge cases and how to handle them
- Footer: Generated by, timestamp, feature name, increment N of M

## File Organization
Create the directory structure:
```
{prompts_directory}/
└── {feature_name_slug}/
    ├── increment_01_{increment_1_slug}.md
    ├── increment_02_{increment_2_slug}.md
    └── ...
```

IMPORTANT: The directory name should be JUST the feature name slug (e.g., "cat-image-generation"),
NOT the increments file name (e.g., NOT "cat-image-generation_increments").

Example:
- Increments file: `features/cat-image-generation_increments.md` (note the "_increments" suffix)
- Prompts directory: `prompts/cat-image-generation/` (no "_increments" suffix)
- Prompt files: `prompts/cat-image-generation/increment_01_basic-setup.md`

## Generating Prompts Sequentially
IMPORTANT: Generate prompts one at a time in order (increment 1, then 2, then 3, etc.).
- This allows you to reference previous increments correctly
- Each increment builds on the previous ones
- Dependencies become clearer as you progress

## Guidelines
- Be detailed and specific in each section
- Reference existing features by their file paths when noting dependencies
- Reference future features if they're related dependencies
- Ensure acceptance criteria are testable (not vague like "works well")
- Include concrete examples in implementation guidance
- Think about realistic edge cases
- DO NOT include decorative boxes or phase headers - the system handles those automatically
- **IMPORTANT**: Before using Write tool, explain to the user what prompt you're about to generate (e.g., "Now I'll generate the prompt for Increment 1: [name]...")

## Handling the Increment Data
The increment structure from Phase 2 is saved in: `{features_directory}/{feature_name_slug}_increments.md`
Read this file to understand:
- How many increments to generate
- What each increment should contain
- Dependencies between increments
- User value for each increment

## Completion Signal
After generating all prompt files and summarizing what was created, respond with ONLY the text "PHASE_3_COMPLETE" on its own line.
DO NOT include any additional text or transition messages after this signal.

## Important Context
- Feature summary location: `{features_directory}/{feature_name_slug}.md`
- Prompts will be saved to: `{prompts_directory}/{feature_name_slug}/`
- Existing features context from Phase 0 is available
- Future features captured in Phases 1 and 2 are available
- Use the Write tool to create each prompt file
- Create the prompts directory structure if it doesn't exist
- DO NOT include greetings like "Hello!" or "Hi!" - you're continuing from Phase 2"""


async def run_phase_0() -> tuple[str, str]:
    """Run Phase 0: Context Gathering.

    Returns:
        tuple: (features_directory, existing_features_context)
    """
    # Display welcome banner
    print_welcome()

    # Display phase header
    print_phase_header("Context Gathering")

    project_directory = None
    existing_features_context = ""

    # Initialize user input handler
    user_input_handler = UserInput()

    # Get current working directory
    import os
    current_dir = os.getcwd()

    # Show the user what directory we'll use
    print_agent_message("Hello! Let's start by understanding your project.")
    console.print()
    print_info(f"Project folder: {current_dir}")
    console.print("       Is this correct? (Press Enter to confirm, or type a different path)")
    console.print()

    user_input = await user_input_handler.get_input("You: ")

    if user_input.lower() in ['exit', 'quit']:
        console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
        return None, None

    # Store the project directory - use current dir if user just pressed Enter
    if not user_input:
        project_directory = "."
    else:
        project_directory = user_input.rstrip('/')
        if not project_directory:
            project_directory = "."

    # Now configure agent options with the project directory injected
    phase_0_prompt = PHASE_0_SYSTEM_PROMPT.replace("{project_directory}", project_directory)

    options = ClaudeAgentOptions(
        system_prompt=phase_0_prompt,
        allowed_tools=["Read", "Glob", "Grep", "Write"],  # Added Write for creating features/ directory
        permission_mode="acceptEdits",  # Auto-accept file operations
    )

    # Use ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Initial query to start Phase 0
        initial_prompt = f"""The user wants to work on their project located at: {project_directory}

Please:
1. Check if there's a "features/" subdirectory in the project folder using the Glob tool
2. Handle the scenario appropriately:
   - If features/ exists and has .md files: Read them and summarize existing features
   - If features/ doesn't exist: Ask if this is a new project or if features are stored elsewhere
   - If features/ exists but is empty: Ask if this is a new project and confirm the use of this folder
3. For new projects, you can create a features/ folder when confirmed
4. After understanding the project context, ask if they're ready to continue"""

        await client.query(initial_prompt)

        console.print()

        response_text = ""
        first_block = True
        displayed_text = False
        phase_complete = False

        # Collect and display initial response as it arrives
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
                            # Check if this block contains the completion signal
                            if "PHASE_0_COMPLETE" in block.text:
                                phase_complete = True
                                response_text += block.text
                                # Don't display completion signal text
                                continue

                            # Display agent label before first content
                            if first_block:
                                console.print("[agent]Agent:[/agent]")
                                console.print()
                                first_block = False

                            # Add spacing before subsequent text blocks
                            if displayed_text:
                                console.print()

                            # Display text immediately as it arrives
                            print_agent_message_streaming(block.text)
                            response_text += block.text
                            displayed_text = True
                        elif block_type == "ToolUseBlock":
                            tool_name = getattr(block, 'name', 'unknown')
                            print_tool_usage(tool_name)
                            console.print()
            elif message_class == "ResultMessage":
                break

        # Add spacing after response (only if we displayed something)
        if displayed_text:
            console.print()

        # Store context for Phase 1
        existing_features_context += response_text + "\n"

        # Check if phase completed immediately
        if phase_complete:
            print_phase_complete("Context Gathering")
            # Construct features_directory from project_directory
            import os
            if project_directory:
                features_directory = os.path.join(project_directory, "features")
            else:
                # Fallback to default if somehow not set
                features_directory = "./features"
            return features_directory, existing_features_context

        # Conversation loop
        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    print_info("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
                    return None, None

                prompt = user_input

                # Send query to agent
                await client.query(prompt)

                console.print()

                response_text = ""
                first_block = True
                displayed_text = False
                phase_complete = False

                # Collect and display response from agent as it arrives
                async for message in client.receive_response():
                    # Check message type using class name
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    # Check if this block contains the completion signal
                                    if "PHASE_0_COMPLETE" in block.text:
                                        phase_complete = True
                                        response_text += block.text
                                        # Don't display completion signal text
                                        continue

                                    # Display agent label before first content
                                    if first_block:
                                        console.print("[agent]Agent:[/agent]")
                                        console.print()
                                        first_block = False

                                    # Add spacing before subsequent text blocks
                                    if displayed_text:
                                        console.print()

                                    # Display text immediately as it arrives
                                    print_agent_message_streaming(block.text)
                                    response_text += block.text
                                    displayed_text = True
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    print_tool_usage(tool_name)
                                    console.print()
                    elif message_class == "ResultMessage":
                        break

                # Add spacing after response (only if we displayed something)
                if displayed_text:
                    console.print()

                # Store context for Phase 1
                existing_features_context += response_text + "\n"

                # Check if phase is complete
                if phase_complete:
                    print_phase_complete("Context Gathering")
                    # Construct features_directory from project_directory
                    import os
                    if project_directory:
                        features_directory = os.path.join(project_directory, "features")
                    else:
                        # Fallback to default if somehow not set
                        features_directory = "./features"
                    return features_directory, existing_features_context

            except KeyboardInterrupt:
                console.print("\n")
                print_info("Interrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                console.print("\n")
                print_error(str(e))
                import traceback
                traceback.print_exc()
                print_info("Please try again or type 'exit' to quit.")


async def run_feature_discovery_phase(future_features_directory: str) -> tuple[bool, list[str]]:
    """Run Feature Discovery Phase: Identify discrete features from high-level app description.

    Args:
        future_features_directory: Path to save future feature stubs

    Returns:
        tuple: (success: bool, discovered_features: list[str])
            - success: True if phase completed successfully, False if user exited
            - discovered_features: List of feature file paths created
    """
    # Display phase header
    from .display import print_phase_header, print_phase_complete
    print_phase_header("Feature Discovery")

    # Track discovered features during this phase
    discovered_features = []

    # Initialize user input handler
    user_input_handler = UserInput()

    # Configure agent options for Feature Discovery
    # Inject directory path into the system prompt
    discovery_prompt = FEATURE_DISCOVERY_SYSTEM_PROMPT.replace("{future_features_directory}", future_features_directory)

    options = ClaudeAgentOptions(
        system_prompt=discovery_prompt,
        allowed_tools=["Write"],
        permission_mode="acceptEdits",  # Auto-accept file writes
    )

    # Use ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Initial context for Feature Discovery
        initial_prompt = """The user has selected Feature Discovery to identify discrete features for their application.

You are continuing a conversation from Phase 0, so DO NOT include greetings or re-introduce yourself.

Start by asking them to describe their application at a high level, then help them identify as many discrete features as possible. Create a stub document for each feature in the future-features directory.

Remember: Focus on BREADTH (many features) not DEPTH (detailed requirements). Details will come later when they expand on each feature."""

        await client.query(initial_prompt)

        response_text = ""
        first_block = True
        displayed_text = False
        phase_complete = False

        # Collect and display initial response as it arrives
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
                            # Check if this block contains the completion signal
                            if "FEATURE_DISCOVERY_COMPLETE" in block.text:
                                phase_complete = True
                                response_text += block.text
                                # Don't display completion signal text
                                continue

                            # Display agent label before first content
                            if first_block:
                                console.print("[agent]Agent:[/agent]")
                                console.print()
                                first_block = False

                            # Add spacing before subsequent text blocks
                            if displayed_text:
                                console.print()

                            # Display text immediately as it arrives
                            print_agent_message_streaming(block.text)
                            response_text += block.text
                            displayed_text = True
                        elif block_type == "ToolUseBlock":
                            tool_name = getattr(block, 'name', 'unknown')
                            print_tool_usage(tool_name)

                            # Track feature file writes
                            if tool_name == "Write":
                                if hasattr(block, 'input') and 'file_path' in block.input:
                                    file_path = block.input['file_path']
                                    if future_features_directory in file_path:
                                        discovered_features.append(file_path)
                                        console.print(" [success](Feature stub created)[/success]")
                            console.print()
            elif message_class == "ResultMessage":
                break

        # Add spacing after response
        if response_text:
            console.print()

        # Check if phase completed immediately
        if phase_complete:
            print_phase_complete("Feature Discovery", f"Discovered {len(discovered_features)} feature(s)")
            return True, discovered_features

        # Conversation loop
        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    print_info("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Returning to menu...[/info]")
                    return False, []

                # Send user input to agent
                await client.query(user_input)

                console.print()

                response_text = ""
                first_block = True
                displayed_text = False
                phase_complete = False

                # Collect and display response from agent as it arrives
                async for message in client.receive_response():
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    # Check if this block contains the completion signal
                                    if "FEATURE_DISCOVERY_COMPLETE" in block.text:
                                        phase_complete = True
                                        response_text += block.text
                                        # Don't display completion signal text
                                        continue

                                    # Display agent label before first content
                                    if first_block:
                                        console.print("[agent]Agent:[/agent]")
                                        console.print()
                                        first_block = False

                                    # Add spacing before subsequent text blocks
                                    if displayed_text:
                                        console.print()

                                    # Display text immediately as it arrives
                                    print_agent_message_streaming(block.text)
                                    response_text += block.text
                                    displayed_text = True
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    print_tool_usage(tool_name)

                                    # Track feature file writes
                                    if tool_name == "Write":
                                        if hasattr(block, 'input') and 'file_path' in block.input:
                                            file_path = block.input['file_path']
                                            if future_features_directory in file_path:
                                                discovered_features.append(file_path)
                                                console.print(" [success](Feature stub created)[/success]")
                                    console.print()
                    elif message_class == "ResultMessage":
                        break

                # Add spacing after response (only if we displayed something)
                if displayed_text:
                    console.print()

                # Check if phase is complete
                if phase_complete:
                    print_phase_complete("Feature Discovery", f"Discovered {len(discovered_features)} feature(s)")
                    return True, discovered_features

            except KeyboardInterrupt:
                console.print("\n")
                print_info("Interrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                console.print("\n")
                print_error(str(e))
                import traceback
                traceback.print_exc()
                print_info("Please try again or type 'exit' to quit.")


async def get_user_action_choice(features_directory: str, future_features_directory: str) -> tuple[str, str | None]:
    """Present user with choice of actions after Phase 0.

    Args:
        features_directory: Path to features directory
        future_features_directory: Path to future-features directory

    Returns:
        tuple: (action: str, selected_file: str | None)
            - action: One of "discover", "new", "expand", "continue", or "exit"
            - selected_file: Path to selected file for "expand" or "continue", None for "discover" or "new"
    """
    from pathlib import Path

    console.print()
    console.print("[info]═══════════════════════════════════════════════════════════════[/info]")
    console.print()
    console.print("[agent]How would you like to proceed?[/agent]")
    console.print()
    console.print("  [bold]1.[/bold] Discover application features (create multiple feature stubs)")
    console.print("  [bold]2.[/bold] Define a new feature")
    console.print("  [bold]3.[/bold] Expand on an existing future-feature stub")
    console.print("  [bold]4.[/bold] Continue with an existing feature")
    console.print("  [bold]5.[/bold] Exit")
    console.print()
    console.print("[info]═══════════════════════════════════════════════════════════════[/info]")
    console.print()

    user_input_handler = UserInput()

    while True:
        try:
            choice = await user_input_handler.get_input("Enter your choice (1-5): ")
            choice = choice.strip()

            if choice.lower() in ['exit', 'quit'] or choice == "5":
                return "exit", None

            if choice == "1":
                return "discover", None

            elif choice == "2":
                return "new", None

            elif choice == "3":
                # List available future-features
                future_features_path = Path(future_features_directory)
                if not future_features_path.exists():
                    console.print()
                    print_error(f"No future-features directory found at: {future_features_directory}")
                    print_info("Please choose option 1 to define a new feature.")
                    console.print()
                    continue

                future_feature_files = list(future_features_path.glob("*.md"))
                if not future_feature_files:
                    console.print()
                    print_error("No future-feature stubs found.")
                    print_info("Please choose option 1 to define a new feature.")
                    console.print()
                    continue

                # Display available future-features
                console.print()
                console.print("[agent]Available future-features:[/agent]")
                console.print()
                for idx, file in enumerate(future_feature_files, 1):
                    console.print(f"  [bold]{idx}.[/bold] {file.stem}")
                console.print()

                # Get user selection
                selection = await user_input_handler.get_input(f"Select a future-feature (1-{len(future_feature_files)}): ")
                selection = selection.strip()

                if selection.lower() in ['exit', 'quit']:
                    return "exit", None

                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(future_feature_files):
                        return "expand", str(future_feature_files[idx])
                    else:
                        print_error("Invalid selection. Please try again.")
                        console.print()
                        continue
                except ValueError:
                    print_error("Invalid input. Please enter a number.")
                    console.print()
                    continue

            elif choice == "4":
                # Find incomplete features
                incomplete_features = find_incomplete_features(features_directory)

                if not incomplete_features:
                    console.print()
                    print_error("No incomplete features found.")
                    print_info("Please choose option 1 to define a new feature.")
                    console.print()
                    continue

                # Display incomplete features
                console.print()
                console.print("[agent]Incomplete features:[/agent]")
                console.print()
                for idx, (feature_slug, status) in enumerate(incomplete_features, 1):
                    console.print(f"  [bold]{idx}.[/bold] {feature_slug} ({status})")
                console.print()

                # Get user selection
                selection = await user_input_handler.get_input(f"Select a feature (1-{len(incomplete_features)}): ")
                selection = selection.strip()

                if selection.lower() in ['exit', 'quit']:
                    return "exit", None

                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(incomplete_features):
                        feature_slug, _ = incomplete_features[idx]
                        return "continue", feature_slug
                    else:
                        print_error("Invalid selection. Please try again.")
                        console.print()
                        continue
                except ValueError:
                    print_error("Invalid input. Please enter a number.")
                    console.print()
                    continue
            else:
                print_error("Invalid choice. Please enter 1-5.")
                console.print()
                continue

        except KeyboardInterrupt:
            console.print("\n")
            print_info("Interrupted. Type 'exit' to quit.")
            continue


def find_incomplete_features(features_directory: str) -> list[tuple[str, str]]:
    """Find features that are incomplete (missing increments or prompts).

    Args:
        features_directory: Path to features directory

    Returns:
        list: List of (feature_slug, status) tuples
            status can be: "missing increments", "missing prompts", "incomplete prompts"
    """
    from pathlib import Path
    import os

    features_path = Path(features_directory)
    if not features_path.exists():
        return []

    # Calculate prompts directory (sibling to features)
    features_parent = os.path.dirname(features_directory.rstrip('/'))
    if not features_parent:
        features_parent = '.'
    prompts_directory = os.path.join(features_parent, 'prompts')
    prompts_path = Path(prompts_directory)

    incomplete = []

    # Get all feature summary files (exclude *_increments.md files)
    feature_files = [f for f in features_path.glob("*.md") if not f.stem.endswith("_increments")]

    for feature_file in feature_files:
        feature_slug = feature_file.stem

        # Check for increments file
        increments_file = features_path / f"{feature_slug}_increments.md"
        if not increments_file.exists():
            incomplete.append((feature_slug, "missing increments"))
            continue

        # Check for prompts directory
        feature_prompts_dir = prompts_path / feature_slug
        if not feature_prompts_dir.exists():
            incomplete.append((feature_slug, "missing prompts"))
            continue

        # Check if prompts directory is empty
        prompt_files = list(feature_prompts_dir.glob("increment_*.md"))
        if not prompt_files:
            incomplete.append((feature_slug, "missing prompts"))

    return incomplete


def determine_resume_phase(features_directory: str, feature_slug: str) -> int:
    """Determine which phase to resume for an incomplete feature.

    Args:
        features_directory: Path to features directory
        feature_slug: Slug of the feature to resume

    Returns:
        int: Phase number to resume (1, 2, or 3)
    """
    from pathlib import Path
    import os

    features_path = Path(features_directory)

    # Check if feature summary exists
    feature_file = features_path / f"{feature_slug}.md"
    if not feature_file.exists():
        # No feature summary - start from Phase 1
        return 1

    # Check if increments file exists
    increments_file = features_path / f"{feature_slug}_increments.md"
    if not increments_file.exists():
        # Has summary but no increments - start from Phase 2
        return 2

    # Has both summary and increments - check for prompts
    features_parent = os.path.dirname(features_directory.rstrip('/'))
    if not features_parent:
        features_parent = '.'
    prompts_directory = os.path.join(features_parent, 'prompts')
    feature_prompts_dir = Path(prompts_directory) / feature_slug

    if not feature_prompts_dir.exists() or not list(feature_prompts_dir.glob("increment_*.md")):
        # Has summary and increments but no prompts - start from Phase 3
        return 3

    # Has everything but may be incomplete - start from Phase 3 to regenerate
    return 3


async def run_phase_1(features_directory: str, existing_features_context: str, future_features_directory: str = "./future-features/", initial_feature_context: str = None) -> tuple[bool, list[str]]:
    """Run Phase 1: Discovery.

    Args:
        features_directory: Path to features directory from Phase 0
        existing_features_context: Summary of existing features from Phase 0
        future_features_directory: Path to save future feature placeholders
        initial_feature_context: Optional context from a future-feature stub to expand

    Returns:
        tuple: (success: bool, captured_future_features: list[str])
            - success: True if phase completed successfully, False if user exited
            - captured_future_features: List of future feature file paths created
    """
    # Display phase header
    print_phase_header("Discovery")

    # Track captured future features during this phase
    captured_future_features = []

    # Initialize user input handler
    user_input_handler = UserInput()

    # Configure agent options for Phase 1
    # Inject directory paths into the system prompt
    phase_1_prompt = PHASE_1_SYSTEM_PROMPT.replace("{features_directory}", features_directory)
    phase_1_prompt = phase_1_prompt.replace("{future_features_directory}", future_features_directory)

    options = ClaudeAgentOptions(
        system_prompt=phase_1_prompt,
        allowed_tools=["Read", "Glob", "Grep", "Write"],
        permission_mode="acceptEdits",  # Auto-accept file operations
    )

    # Use ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Initial context for Phase 1
        if initial_feature_context:
            # Expanding a future-feature stub
            initial_prompt = f"""We've completed Phase 0 (Context Gathering).

Here's what we learned about existing features:
{existing_features_context}

The features are located in: {features_directory}
Future features will be saved to: {future_features_directory}

Now let's start Phase 1 (Discovery). The user has selected a future-feature stub to expand on.

You are continuing a conversation from Phase 0, so DO NOT include greetings or re-introduce yourself.

Here's the content of the future-feature stub:

{initial_feature_context}

Please use this as the starting point for your discovery conversation. Ask clarifying questions to expand on this initial concept and develop it into a fully detailed feature. Reference the stub content when asking questions to show you're building on the existing idea."""
        else:
            # Starting fresh with a new feature
            initial_prompt = f"""We've completed Phase 0 (Context Gathering).

Here's what we learned about existing features:
{existing_features_context}

The features are located in: {features_directory}
Future features will be saved to: {future_features_directory}

Now let's start Phase 1 (Discovery). You are continuing a conversation from Phase 0, so DO NOT include greetings or re-introduce yourself.

Please ask the user to describe the new feature they want to build, then ask clarifying questions to understand it deeply."""

        await client.query(initial_prompt)

        response_text = ""
        first_block = True
        displayed_text = False
        phase_complete = False

        # Collect and display initial response as it arrives
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
                            # Check if this block contains the completion signal
                            if "PHASE_1_COMPLETE" in block.text:
                                phase_complete = True
                                response_text += block.text
                                # Don't display completion signal text
                                continue

                            # Display agent label before first content
                            if first_block:
                                console.print("[agent]Agent:[/agent]")
                                console.print()
                                first_block = False

                            # Add spacing before subsequent text blocks
                            if displayed_text:
                                console.print()

                            # Display text immediately as it arrives
                            print_agent_message_streaming(block.text)
                            response_text += block.text
                            displayed_text = True
                        elif block_type == "ToolUseBlock":
                            tool_name = getattr(block, 'name', 'unknown')
                            print_tool_usage(tool_name)
                            console.print()
            elif message_class == "ResultMessage":
                break

        # Add spacing after response
        if response_text:
            console.print()

        # Check if phase completed immediately
        if phase_complete:
            extra_info = None
            if captured_future_features:
                extra_info = f"Captured {len(captured_future_features)} future feature(s) for later planning"
            print_phase_complete("Discovery", extra_info)
            return True, captured_future_features

        # Conversation loop
        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    print_info("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Returning to menu...[/info]")
                    return False, []

                # Send user input to agent
                await client.query(user_input)

                console.print()

                response_text = ""
                first_block = True
                displayed_text = False
                phase_complete = False

                # Collect and display response from agent as it arrives
                async for message in client.receive_response():
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    # Check if this block contains the completion signal
                                    if "PHASE_1_COMPLETE" in block.text:
                                        phase_complete = True
                                        response_text += block.text
                                        # Don't display completion signal text
                                        continue

                                    # Display agent label before first content
                                    if first_block:
                                        console.print("[agent]Agent:[/agent]")
                                        console.print()
                                        first_block = False

                                    # Add spacing before subsequent text blocks
                                    if displayed_text:
                                        console.print()

                                    # Display text immediately as it arrives
                                    print_agent_message_streaming(block.text)
                                    response_text += block.text
                                    displayed_text = True
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    print_tool_usage(tool_name)

                                    # Track future feature file writes
                                    if tool_name == "Write":
                                        # Check if this is a future feature file
                                        if hasattr(block, 'input') and 'file_path' in block.input:
                                            file_path = block.input['file_path']
                                            if future_features_directory in file_path:
                                                captured_future_features.append(file_path)
                                                console.print(" [success](Future feature captured)[/success]")
                                    console.print()
                    elif message_class == "ResultMessage":
                        break

                # Add spacing after response (only if we displayed something)
                if displayed_text:
                    console.print()

                # Check if phase is complete
                if phase_complete:
                    extra_info = None
                    if captured_future_features:
                        extra_info = f"Captured {len(captured_future_features)} future feature(s) for later planning"
                    print_phase_complete("Discovery", extra_info)
                    return True, captured_future_features

            except KeyboardInterrupt:
                console.print("\n")
                print_info("Interrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                console.print("\n")
                print_error(str(e))
                import traceback
                traceback.print_exc()
                print_info("Please try again or type 'exit' to quit.")


async def run_phase_2(features_directory: str, existing_features_context: str, captured_future_features_phase1: list[str], future_features_directory: str) -> tuple[bool, list[str]]:
    """Run Phase 2: Incremental Grouping.

    Args:
        features_directory: Path to features directory
        existing_features_context: Summary of existing features from Phase 0
        captured_future_features_phase1: List of future feature file paths from Phase 1
        future_features_directory: Path to save future feature placeholders

    Returns:
        tuple: (success: bool, captured_future_features: list[str])
            - success: True if phase completed successfully, False if user exited
            - captured_future_features: List of future feature file paths created during Phase 2
    """
    # Display phase header
    print_phase_header("Incremental Grouping")

    # Track captured future features during this phase
    captured_future_features_phase2 = []

    # Initialize user input handler
    user_input_handler = UserInput()

    # Configure agent options for Phase 2
    # We need to know the feature name slug - we'll extract it from the latest feature file
    # The feature file should be at features_directory/[feature-name].md
    import os
    from pathlib import Path

    # Find the most recently modified .md file in features_directory (should be from Phase 1)
    feature_files = list(Path(features_directory).glob("*.md"))
    if not feature_files:
        print_error("No feature summary file found. Cannot proceed to Phase 2.")
        return False, []

    # Get the most recent feature file
    latest_feature_file = max(feature_files, key=lambda p: p.stat().st_mtime)
    feature_name_slug = latest_feature_file.stem

    # Inject paths into the system prompt
    phase_2_prompt = PHASE_2_SYSTEM_PROMPT.replace("{features_directory}", features_directory)
    phase_2_prompt = phase_2_prompt.replace("{feature_name_slug}", feature_name_slug)
    phase_2_prompt = phase_2_prompt.replace("{future_features_directory}", future_features_directory)

    options = ClaudeAgentOptions(
        system_prompt=phase_2_prompt,
        allowed_tools=["Read", "Glob", "Grep", "Write"],
        permission_mode="acceptEdits",
    )

    # Use ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Build context about captured future features
        future_features_context = ""
        if captured_future_features_phase1:
            future_features_context = f"\n\nCaptured future features from Phase 1:\n"
            for feature_path in captured_future_features_phase1:
                future_features_context += f"- {feature_path}\n"

        # Initial context for Phase 2
        initial_prompt = f"""We've completed Phase 1 (Discovery).

The feature summary was saved to: {latest_feature_file}

Here's what we know from earlier phases:

**Existing Features** (from Phase 0):
{existing_features_context}
{future_features_context}

Future features directory: {future_features_directory}

Now let's start Phase 2 (Incremental Grouping). You are continuing a conversation from Phase 1, so DO NOT include greetings.

Please:
1. Read the feature summary file to understand what needs to be built
2. Break the feature into logical increments (2-8 increments)
3. Ensure each increment is a vertical slice that delivers user value
4. Identify dependencies on existing features and between increments
5. Present your proposed increment structure for my review

Remember: Each increment must be independently testable and deliver clear user value. If during our discussion you notice that a proposed increment should really be a separate feature, ask me if we should capture it for future planning."""

        await client.query(initial_prompt)

        response_text = ""
        first_block = True
        displayed_text = False
        phase_complete = False

        # Collect and display initial response as it arrives
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
                            # Check if this block contains the completion signal
                            if "PHASE_2_COMPLETE" in block.text:
                                phase_complete = True
                                response_text += block.text
                                # Don't display completion signal text
                                continue

                            # Display agent label before first content
                            if first_block:
                                console.print("[agent]Agent:[/agent]")
                                console.print()
                                first_block = False

                            # Add spacing before subsequent text blocks
                            if displayed_text:
                                console.print()

                            # Display text immediately as it arrives
                            print_agent_message_streaming(block.text)
                            response_text += block.text
                            displayed_text = True
                        elif block_type == "ToolUseBlock":
                            tool_name = getattr(block, 'name', 'unknown')
                            print_tool_usage(tool_name)

                            # Track future feature file writes
                            if tool_name == "Write":
                                # Check if this is a future feature file
                                if hasattr(block, 'input') and 'file_path' in block.input:
                                    file_path = block.input['file_path']
                                    if future_features_directory in file_path:
                                        captured_future_features_phase2.append(file_path)
                                        console.print(" [success](Future feature captured)[/success]")
                            console.print()
            elif message_class == "ResultMessage":
                break

        # Add spacing after response
        if response_text:
            console.print()

        # Check if phase completed immediately
        if phase_complete:
            extra_info = None
            if captured_future_features_phase2:
                extra_info = f"Captured {len(captured_future_features_phase2)} future feature(s) during grouping"
            print_phase_complete("Incremental Grouping", extra_info)
            return True, captured_future_features_phase2

        # Conversation loop
        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    print_info("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Returning to menu...[/info]")
                    return False, []

                # Send user input to agent
                await client.query(user_input)

                console.print()

                response_text = ""
                first_block = True
                displayed_text = False
                phase_complete = False

                # Collect and display response from agent as it arrives
                async for message in client.receive_response():
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    # Check if this block contains the completion signal
                                    if "PHASE_2_COMPLETE" in block.text:
                                        phase_complete = True
                                        response_text += block.text
                                        # Don't display completion signal text
                                        continue

                                    # Display agent label before first content
                                    if first_block:
                                        console.print("[agent]Agent:[/agent]")
                                        console.print()
                                        first_block = False

                                    # Add spacing before subsequent text blocks
                                    if displayed_text:
                                        console.print()

                                    # Display text immediately as it arrives
                                    print_agent_message_streaming(block.text)
                                    response_text += block.text
                                    displayed_text = True
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    print_tool_usage(tool_name)

                                    # Track future feature file writes
                                    if tool_name == "Write":
                                        # Check if this is a future feature file
                                        if hasattr(block, 'input') and 'file_path' in block.input:
                                            file_path = block.input['file_path']
                                            if future_features_directory in file_path:
                                                captured_future_features_phase2.append(file_path)
                                                console.print(" [success](Future feature captured)[/success]")
                                    console.print()
                    elif message_class == "ResultMessage":
                        break

                # Add spacing after response (only if we displayed something)
                if displayed_text:
                    console.print()

                # Check if phase is complete
                if phase_complete:
                    extra_info = None
                    if captured_future_features_phase2:
                        extra_info = f"Captured {len(captured_future_features_phase2)} future feature(s) during grouping"
                    print_phase_complete("Incremental Grouping", extra_info)
                    return True, captured_future_features_phase2

            except KeyboardInterrupt:
                console.print("\n")
                print_info("Interrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                console.print("\n")
                print_error(str(e))
                import traceback
                traceback.print_exc()
                print_info("Please try again or type 'exit' to quit.")


async def run_phase_3(
    features_directory: str,
    existing_features_context: str,
    all_captured_future_features: list[str],
    prompts_directory: str = "./prompts"
) -> bool:
    """Run Phase 3: Prompt Generation.

    Args:
        features_directory: Path to features directory
        existing_features_context: Summary of existing features from Phase 0
        all_captured_future_features: Combined list of future feature files from Phases 1 and 2
        prompts_directory: Base directory for generated prompts (default: "./prompts")

    Returns:
        bool: True if phase completed successfully, False if user exited
    """
    # Display phase header
    print_phase_header("Prompt Generation")

    # Initialize user input handler
    user_input_handler = UserInput()

    # Find the most recently modified .md file in features_directory (should be from Phase 1)
    import os
    from pathlib import Path

    feature_files = list(Path(features_directory).glob("*.md"))
    if not feature_files:
        print_error("No feature summary file found. Cannot proceed to Phase 3.")
        return False

    # Get the most recent feature file
    latest_feature_file = max(feature_files, key=lambda p: p.stat().st_mtime)
    feature_name_slug = latest_feature_file.stem

    # Inject paths into the system prompt
    phase_3_prompt = PHASE_3_SYSTEM_PROMPT.replace("{features_directory}", features_directory)
    phase_3_prompt = phase_3_prompt.replace("{feature_name_slug}", feature_name_slug)
    phase_3_prompt = phase_3_prompt.replace("{prompts_directory}", prompts_directory)

    options = ClaudeAgentOptions(
        system_prompt=phase_3_prompt,
        allowed_tools=["Read", "Glob", "Grep", "Write"],
        permission_mode="acceptEdits",
    )

    # Use ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Build context about captured future features
        future_features_context = ""
        if all_captured_future_features:
            future_features_context = f"\n\nCaptured future features from earlier phases:\n"
            for feature_path in all_captured_future_features:
                future_features_context += f"- {feature_path}\n"

        # Initial context for Phase 3
        initial_prompt = f"""We've completed Phase 2 (Incremental Grouping).

The feature summary is located at: {latest_feature_file}
The increment structure is saved at: {features_directory}/{feature_name_slug}_increments.md

Here's what we know from earlier phases:

**Existing Features** (from Phase 0):
{existing_features_context}
{future_features_context}

Now let's start Phase 3 (Prompt Generation). You are continuing a conversation from Phase 2, so DO NOT include greetings.

Please:
1. Read the feature summary file to refresh your understanding
2. Read the increments structure file to see the approved increment breakdown
3. Generate a detailed prompt file for each increment, starting with Increment 1
4. Save each prompt to: {prompts_directory}/{feature_name_slug}/increment_NN_description.md
5. Follow the template structure exactly
6. After generating all prompts, summarize what was created

Remember to generate prompts sequentially (one at a time) so dependencies are clear."""

        await client.query(initial_prompt)

        response_text = ""
        first_block = True
        displayed_text = False
        phase_complete = False

        # Collect and display initial response as it arrives
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
                            # Check if this block contains the completion signal
                            if "PHASE_3_COMPLETE" in block.text:
                                phase_complete = True
                                response_text += block.text
                                # Don't display completion signal text
                                continue

                            # Display agent label before first content
                            if first_block:
                                console.print("[agent]Agent:[/agent]")
                                console.print()
                                first_block = False

                            # Add spacing before subsequent text blocks
                            if displayed_text:
                                console.print()

                            # Display text immediately as it arrives
                            print_agent_message_streaming(block.text)
                            response_text += block.text
                            displayed_text = True
                        elif block_type == "ToolUseBlock":
                            tool_name = getattr(block, 'name', 'unknown')
                            print_tool_usage(tool_name)
                            console.print()
            elif message_class == "ResultMessage":
                break

        # Add spacing after response
        if response_text:
            console.print()

        # Check if phase completed immediately (agent did all work in first response)
        if phase_complete:
            print_phase_complete("Prompt Generation")
            return True

        # Conversation loop
        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    print_info("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Returning to menu...[/info]")
                    return False

                # Send user input to agent
                await client.query(user_input)

                console.print()

                response_text = ""
                first_block = True
                displayed_text = False
                phase_complete = False

                # Collect and display response from agent as it arrives
                async for message in client.receive_response():
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    # Check if this block contains the completion signal
                                    if "PHASE_3_COMPLETE" in block.text:
                                        phase_complete = True
                                        response_text += block.text
                                        # Don't display completion signal text
                                        continue

                                    # Display agent label before first content
                                    if first_block:
                                        console.print("[agent]Agent:[/agent]")
                                        console.print()
                                        first_block = False

                                    # Add spacing before subsequent text blocks
                                    if displayed_text:
                                        console.print()

                                    # Display text immediately as it arrives
                                    print_agent_message_streaming(block.text)
                                    response_text += block.text
                                    displayed_text = True
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    print_tool_usage(tool_name)
                                    console.print()
                    elif message_class == "ResultMessage":
                        break

                # Add spacing after response (only if we displayed something)
                if displayed_text:
                    console.print()

                # Check if phase is complete
                if phase_complete:
                    print_phase_complete("Prompt Generation")
                    return True

            except KeyboardInterrupt:
                console.print("\n")
                print_info("Interrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                console.print("\n")
                print_error(str(e))
                import traceback
                traceback.print_exc()
                print_info("Please try again or type 'exit' to quit.")


async def run_all_phases():
    """Run all phases in sequence."""
    import os
    from pathlib import Path

    # Phase 0: Context Gathering
    features_directory, existing_features_context = await run_phase_0()

    if features_directory is None:
        return  # User exited

    # Calculate future features directory as sibling to features directory
    # Examples:
    #   "./features/" → "./future-features/"
    #   "docs/features/" → "docs/future-features/"
    #   "./features" → "./future-features/"
    features_parent = os.path.dirname(features_directory.rstrip('/'))
    if not features_parent:
        features_parent = '.'
    future_features_directory = os.path.join(features_parent, 'future-features')

    # Main workflow loop - allows user to work on multiple features in one session
    while True:
        # Get user's choice of action
        action, selected_file = await get_user_action_choice(features_directory, future_features_directory)

        if action == "exit":
            console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
            return

        # Initialize variables that will be used across phases
        captured_future_features = []
        captured_future_features_phase2 = []
        initial_feature_context = None
        resume_phase = 1

        # Handle different action paths
        if action == "discover":
            # Run Feature Discovery Phase to identify and create multiple feature stubs
            discovery_success, discovered_features = await run_feature_discovery_phase(future_features_directory)

            if not discovery_success:
                continue  # Go back to action choice menu

            # Display discovered features
            if discovered_features:
                print_captured_features(discovered_features)
                console.print()
                print_info("You can now select 'Expand on an existing future-feature stub' to develop any of these features.")
                console.print()

            # Loop back to action choice menu
            continue

        elif action == "new":
            # Continue with normal flow starting at Phase 1
            resume_phase = 1

        elif action == "expand":
            # Read the future-feature stub and pass it to Phase 1
            try:
                with open(selected_file, 'r') as f:
                    initial_feature_context = f.read()
                console.print()
                print_info(f"Expanding on future-feature: {Path(selected_file).stem}")
                console.print()
                resume_phase = 1
            except Exception as e:
                print_error(f"Failed to read future-feature file: {e}")
                continue  # Go back to action choice menu

        elif action == "continue":
            # Determine which phase to resume
            feature_slug = selected_file  # In this case, selected_file is the feature slug
            resume_phase = determine_resume_phase(features_directory, feature_slug)
            console.print()
            print_info(f"Continuing feature: {feature_slug}")
            print_info(f"Resuming at Phase {resume_phase}")
            console.print()

        # Execute phases based on resume_phase
        if resume_phase <= 1:
            # Phase 1: Discovery
            phase_1_success, captured_future_features = await run_phase_1(
                features_directory,
                existing_features_context,
                future_features_directory,
                initial_feature_context=initial_feature_context
            )

            if not phase_1_success:
                continue  # Go back to action choice menu

            # Display captured future features if any from Phase 1
            if captured_future_features:
                print_captured_features(captured_future_features)

        if resume_phase <= 2:
            # Phase 2: Incremental Grouping
            phase_2_success, captured_future_features_phase2 = await run_phase_2(
                features_directory,
                existing_features_context,
                captured_future_features,
                future_features_directory
            )

            if not phase_2_success:
                continue  # Go back to action choice menu

            # Display captured future features from Phase 2 if any
            if captured_future_features_phase2:
                print_captured_features(captured_future_features_phase2)

        # Combine all captured future features for Phase 3
        all_captured_future_features = captured_future_features + captured_future_features_phase2

        # Calculate prompts directory as sibling to features directory
        # Examples:
        #   "./features/" → "./prompts/"
        #   "docs/features/" → "docs/prompts/"
        #   "./features" → "./prompts/"
        prompts_directory = os.path.join(features_parent, 'prompts')

        if resume_phase <= 3:
            # Phase 3: Prompt Generation
            phase_3_success = await run_phase_3(
                features_directory,
                existing_features_context,
                all_captured_future_features,
                prompts_directory=prompts_directory
            )

            if not phase_3_success:
                continue  # Go back to action choice menu

        # All phases complete!
        console.print()
        console.print("[success]✨ All phases complete! Your feature prompts are ready to use. ✨[/success]")
        console.print()

        # Loop back to action choice menu for next feature


def main():
    """Main entry point for the Feature Breakdown Agent."""
    anyio.run(run_all_phases)


if __name__ == "__main__":
    main()
