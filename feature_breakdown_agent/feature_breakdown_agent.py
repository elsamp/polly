"""
Feature Breakdown Agent

A terminal-based AI agent that transforms high-level feature descriptions
into detailed, incremental coding prompts.
"""

import sys
import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


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

When the user confirms readiness, respond with "PHASE_0_COMPLETE" on its own line to signal completion."""


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
    print("=" * 70)
    print("Welcome to the Feature Breakdown Agent!")
    print("=" * 70)
    print("\nThis agent will help you break down features into implementable")
    print("increments through a 4-phase process:")
    print("\n  Phase 0: Context Gathering")
    print("  Phase 1: Discovery")
    print("  Phase 2: Incremental Grouping")
    print("  Phase 3: Prompt Generation")
    print("\n" + "=" * 70)
    print("\nStarting Phase 0: Context Gathering...")
    print("=" * 70 + "\n")

    features_directory = None
    existing_features_context = ""

    # Configure agent options for Phase 0
    options = ClaudeAgentOptions(
        system_prompt=PHASE_0_SYSTEM_PROMPT,
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits",  # Auto-accept file reads
    )

    # Use ClaudeSDKClient for stateful conversation
    async with ClaudeSDKClient(options=options) as client:
        # Initial agent greeting
        print("Agent: Hello! Let's start by understanding your existing codebase.")
        print("       Where is your feature documentation located?")
        print("       (Press Enter for default: './features/')")

        first_message = True

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    # Use default
                    user_input = "./features/"

                if user_input.lower() in ['exit', 'quit']:
                    print("\nExiting Feature Breakdown Agent. Goodbye!")
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

                print("\nAgent: ", end="", flush=True)

                response_text = ""
                # Stream response from agent
                async for message in client.receive_response():
                    # Check message type using class name
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    print(block.text, end="", flush=True)
                                    response_text += block.text
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    print(f"\n[Using {tool_name}...]", end="", flush=True)
                    elif message_class == "ResultMessage":
                        break

                print("\n")

                # Store context for Phase 1
                existing_features_context += response_text + "\n"

                # Check if phase is complete
                if "PHASE_0_COMPLETE" in response_text or "phase 1" in response_text.lower():
                    print("\n" + "=" * 70)
                    print("Phase 0 Complete!")
                    print("=" * 70 + "\n")
                    return features_directory, existing_features_context

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                print(f"\n\nError: {e}")
                import traceback
                traceback.print_exc()
                print("Please try again or type 'exit' to quit.")


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
    print("=" * 70)
    print("Starting Phase 1: Discovery...")
    print("=" * 70 + "\n")

    # Track captured future features during this phase
    captured_future_features = []

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

        print("Agent: ", end="", flush=True)

        # Get initial response
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
                            print(block.text, end="", flush=True)
                        elif block_type == "ToolUseBlock":
                            tool_name = getattr(block, 'name', 'unknown')
                            print(f"\n[Using {tool_name}...]", end="", flush=True)
            elif message_class == "ResultMessage":
                break

        print("\n")

        # Conversation loop
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    print("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    print("\nExiting Feature Breakdown Agent. Goodbye!")
                    return False, []

                # Send user input to agent
                await client.query(user_input)

                print("\nAgent: ", end="", flush=True)

                response_text = ""
                # Stream response from agent
                async for message in client.receive_response():
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
                                    print(block.text, end="", flush=True)
                                    response_text += block.text
                                elif block_type == "ToolUseBlock":
                                    tool_name = getattr(block, 'name', 'unknown')
                                    print(f"\n[Using {tool_name}...]", end="", flush=True)

                                    # Track future feature file writes
                                    if tool_name == "Write":
                                        # Check if this is a future feature file
                                        if hasattr(block, 'input') and 'file_path' in block.input:
                                            file_path = block.input['file_path']
                                            if future_features_directory in file_path:
                                                captured_future_features.append(file_path)
                                                print(f" (Future feature captured)", end="", flush=True)
                    elif message_class == "ResultMessage":
                        break

                print("\n")

                # Check if phase is complete
                if "PHASE_1_COMPLETE" in response_text:
                    print("\n" + "=" * 70)
                    print("Phase 1 Complete!")
                    if captured_future_features:
                        print(f"Captured {len(captured_future_features)} future feature(s) for later planning")
                    print("=" * 70 + "\n")
                    return True, captured_future_features

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                print(f"\n\nError: {e}")
                import traceback
                traceback.print_exc()
                print("Please try again or type 'exit' to quit.")


async def run_all_phases():
    """Run all phases in sequence."""
    # Phase 0: Context Gathering
    features_directory, existing_features_context = await run_phase_0()

    if features_directory is None:
        return  # User exited

    # Phase 1: Discovery
    phase_1_success, captured_future_features = await run_phase_1(features_directory, existing_features_context)

    if not phase_1_success:
        return  # User exited

    # Display captured future features if any
    if captured_future_features:
        print("\n" + "=" * 70)
        print("Future Features Captured:")
        print("=" * 70)
        for feature_path in captured_future_features:
            print(f"  - {feature_path}")
        print("=" * 70 + "\n")

    # TODO: Phase 2 and 3 to be implemented
    # When implementing Phase 2/3, pass captured_future_features to reference as dependencies
    print("\n(Phases 2 and 3 will be implemented next)")


def main():
    """Main entry point for the Feature Breakdown Agent."""
    anyio.run(run_all_phases)


if __name__ == "__main__":
    main()
