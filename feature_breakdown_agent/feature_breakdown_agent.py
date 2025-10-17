"""
Feature Breakdown Agent

A terminal-based AI agent that transforms high-level feature descriptions
into detailed, incremental coding prompts.
"""

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

    # Create client and start conversation
    async with ClaudeSDKClient(options=options) as client:
        # Initial agent greeting
        print("Agent: Hello! Let's start by understanding your existing codebase.")
        print("       Where is your feature documentation located?")
        print("       (Press Enter for default: './features/')")

        # Note: We start with the conversation loop directly
        # instead of sending an initial query

        # Conversation loop
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    print("\nExiting Feature Breakdown Agent. Goodbye!")
                    break

                # Send user message
                await client.query(user_input)

                # Collect response text to check for completion
                response_text = ""
                print("\nAgent: ", end="", flush=True)

                async for message in client.receive_response():
                    msg_type = getattr(message, 'type', None)
                    if msg_type == "assistant":
                        for block in message.content:
                            if block.type == "text":
                                print(block.text, end="", flush=True)
                                response_text += block.text
                            elif block.type == "tool_use":
                                print(f"\n[🔧 Using {block.tool_name}...]", end="", flush=True)
                    elif msg_type == "result":
                        print("\n")
                        break

                # Check if phase is complete
                if "PHASE_0_COMPLETE" in response_text:
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
                print("Please try again or type 'exit' to quit.")


def main():
    """Main entry point for the Feature Breakdown Agent."""
    anyio.run(run_phase_0)


if __name__ == "__main__":
    main()
