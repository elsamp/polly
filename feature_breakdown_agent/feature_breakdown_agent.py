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


async def run_phase_0():
    """Run Phase 0: Context Gathering."""
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
                    break

                # Build conversation context for first message
                if first_message:
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

                # Check if phase is complete
                if "PHASE_0_COMPLETE" in response_text or "phase 1" in response_text.lower():
                    print("\n" + "=" * 70)
                    print("Phase 0 Complete!")
                    print("=" * 70)
                    print("\n(Phase 1 will be implemented next)")
                    break

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
                continue
            except Exception as e:
                print(f"\n\nError: {e}")
                import traceback
                traceback.print_exc()
                print("Please try again or type 'exit' to quit.")


def main():
    """Main entry point for the Feature Breakdown Agent."""
    anyio.run(run_phase_0)


if __name__ == "__main__":
    main()
