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


PHASE_0_SYSTEM_PROMPT = """You are a Product Requirements specialist helping to break down features into implementable increments.

You are currently in **Phase 0: Context Gathering**.

## Your Task
1. Ask the user where their feature documentation is located (default: "./features/")
2. Search for existing feature documentation files (*.md) in that directory using the Glob tool
3. Read the relevant feature files using the Read tool to understand the existing system
4. Summarize what you learned about existing features
5. Ask the user if they're ready to proceed to Phase 1 (Discovery)

## Guidelines
- Use the Read tool to read markdown files
- Use the Glob tool to search for *.md files in directories
- Be conversational and natural
- Provide clear summaries of what you find
- If no feature docs exist, that's fine - note it and proceed
- Always ask for user confirmation before transitioning to the next phase

## Context Awareness
- Look for patterns in existing features
- Note architectural decisions
- Identify common dependencies
- Understand the system's scope

## Phase Completion
IMPORTANT: After summarizing existing features, ask the user: "Are you ready to proceed to Phase 1 (Discovery)?"
- WAIT for the user's response (e.g., "yes", "ready", "let's go")
- DO NOT output "PHASE_0_COMPLETE" until AFTER the user confirms
- Only when the user confirms readiness in their response, then output "PHASE_0_COMPLETE" on its own line"""


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
- Ask one question at a time for better flow
- Build on previous answers with follow-up questions
- Show that you're listening by referencing earlier responses
- Don't just check boxes - dig deeper when answers are vague
- Count your questions to ensure you ask at least 5 substantive ones

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
After writing the feature summary file, inform the user and respond with "PHASE_1_COMPLETE" on its own line to signal completion.

## Important
- You have access to existing feature context from Phase 0
- Reference specific existing features when relevant
- Watch for scope creep and capture future features proactively
- Keep the main feature focused and well-defined
- Minimum 5 clarifying questions before writing summary
- Only write the summary when understanding is complete"""


async def run_phase_0() -> tuple[str, str]:
    """Run Phase 0: Context Gathering.

    Returns:
        tuple: (features_directory, existing_features_context)
    """
    # Display welcome banner
    print_welcome()

    # Display phase header
    print_phase_header(0, "Context Gathering")

    features_directory = None
    existing_features_context = ""

    # Initialize user input handler
    user_input_handler = UserInput()

    # Configure agent options for Phase 0
    options = ClaudeAgentOptions(
        system_prompt=PHASE_0_SYSTEM_PROMPT,
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",  # Auto-accept file reads
    )

    # Use ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Initial agent greeting
        print_agent_message("Hello! Let's start by understanding your existing codebase.")
        console.print("       Where is your feature documentation located?")
        print_info("(Press Enter for default: './features/')")
        console.print()

        first_message = True

        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    # Use default
                    user_input = "./features/"

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
                    return None, None

                # Build conversation context for first message
                if first_message:
                    # Store the features directory for later phases
                    features_directory = user_input

                    # First message - add context about what we're doing
                    prompt = f"""The user wants to break down a new feature. First, let's gather context about their existing features.

The user says their feature documentation is located at: {user_input}

Please:
1. Use the Glob tool to search for *.md files in that directory
2. Read the feature documentation files you find
3. Summarize what existing features they have
4. Ask if they're ready to proceed to Phase 1 (Discovery) for their new feature"""
                    first_message = False
                else:
                    prompt = user_input

                # Send query to agent
                await client.query(prompt)

                console.print()

                response_text = ""
                tool_used = False

                # Collect response from agent
                async for message in client.receive_response():
                    # Check message type using class name
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    response_text += block.text
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    if not tool_used:
                                        tool_used = True
                                    print_tool_usage(tool_name)
                                    console.print()
                    elif message_class == "ResultMessage":
                        break

                # Display the full response with markdown rendering
                console.print("[agent]Agent:[/agent]")
                console.print()
                print_agent_message_streaming(response_text)
                console.print()

                # Store context for Phase 1
                existing_features_context += response_text + "\n"

                # Check if phase is complete (only on explicit signal)
                if "PHASE_0_COMPLETE" in response_text:
                    print_phase_complete(0, "Context Gathering")
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


async def run_phase_1(features_directory: str, existing_features_context: str, future_features_directory: str = "./future-features/") -> tuple[bool, list[str]]:
    """Run Phase 1: Discovery.

    Args:
        features_directory: Path to features directory from Phase 0
        existing_features_context: Summary of existing features from Phase 0
        future_features_directory: Path to save future feature placeholders

    Returns:
        tuple: (success: bool, captured_future_features: list[str])
            - success: True if phase completed successfully, False if user exited
            - captured_future_features: List of future feature file paths created
    """
    # Display phase header
    print_phase_header(1, "Discovery")

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
        initial_prompt = f"""We've completed Phase 0 (Context Gathering).

Here's what we learned about existing features:
{existing_features_context}

The features are located in: {features_directory}
Future features will be saved to: {future_features_directory}

Now let's start Phase 1 (Discovery). Please ask the user to describe the new feature they want to build, then ask clarifying questions to understand it deeply."""

        await client.query(initial_prompt)

        response_text = ""
        tool_used = False

        # Collect initial response
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
                            response_text += block.text
                        elif block_type == "ToolUseBlock":
                            tool_name = getattr(block, 'name', 'unknown')
                            if not tool_used:
                                tool_used = True
                            print_tool_usage(tool_name)
                            console.print()
            elif message_class == "ResultMessage":
                break

        # Display the full response with markdown rendering
        console.print("[agent]Agent:[/agent]")
        console.print()
        print_agent_message_streaming(response_text)
        console.print()

        # Conversation loop
        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    print_info("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
                    return False, []

                # Send user input to agent
                await client.query(user_input)

                console.print()

                response_text = ""
                tool_used = False

                # Collect response from agent
                async for message in client.receive_response():
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    response_text += block.text
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    if not tool_used:
                                        tool_used = True
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

                # Display the full response with markdown rendering
                console.print("[agent]Agent:[/agent]")
                console.print()
                print_agent_message_streaming(response_text)
                console.print()

                # Check if phase is complete
                if "PHASE_1_COMPLETE" in response_text:
                    extra_info = None
                    if captured_future_features:
                        extra_info = f"Captured {len(captured_future_features)} future feature(s) for later planning"
                    print_phase_complete(1, "Discovery", extra_info)
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


async def run_all_phases():
    """Run all phases in sequence."""
    # Phase 0: Context Gathering
    features_directory, existing_features_context = await run_phase_0()

    if features_directory is None:
        return  # User exited

    # Calculate future features directory as sibling to features directory
    # Examples:
    #   "./features/" → "./future-features/"
    #   "docs/features/" → "docs/future-features/"
    #   "./features" → "./future-features/"
    import os
    features_parent = os.path.dirname(features_directory.rstrip('/'))
    if not features_parent:
        features_parent = '.'
    future_features_directory = os.path.join(features_parent, 'future-features')

    # Phase 1: Discovery
    phase_1_success, captured_future_features = await run_phase_1(
        features_directory,
        existing_features_context,
        future_features_directory
    )

    if not phase_1_success:
        return  # User exited

    # Display captured future features if any
    if captured_future_features:
        print_captured_features(captured_future_features)

    # TODO: Phase 2 and 3 to be implemented
    # When implementing Phase 2/3, pass captured_future_features to reference as dependencies
    console.print()
    print_info("(Phases 2 and 3 will be implemented next)")
    console.print()


def main():
    """Main entry point for the Feature Breakdown Agent."""
    anyio.run(run_all_phases)


if __name__ == "__main__":
    main()
