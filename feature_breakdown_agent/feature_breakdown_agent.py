"""
Feature Breakdown Agent (Polly)

A terminal-based AI agent that transforms high-level feature descriptions
into detailed, incremental coding prompts using Claude Skills.
"""

import sys
import os
import anyio
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from .display import (
    print_welcome,
    print_agent_message_streaming,
    print_tool_usage,
    print_error,
    print_info,
    UserInput,
    console,
)
from .coordinator_prompt import get_coordinator_prompt


async def run_agent():
    """Run the main Polly agent with a single long-running session."""
    import questionary

    # Display welcome banner
    print_welcome()

    # Get current working directory
    current_dir = os.getcwd()

    # Initialize user input handler
    user_input_handler = UserInput()

    # Show the user what directory we'll use
    console.print()
    print_info(f"Project folder: {current_dir}")
    console.print()

    # Ask user to confirm or specify different folder
    folder_choice = await questionary.select(
        "Would you like to use this folder?",
        choices=[
            "Use this folder",
            "Specify a different folder"
        ],
        style=questionary.Style([
            ('qmark', 'fg:#00d4aa bold'),
            ('question', 'fg:#00d4aa bold'),
            ('answer', 'fg:#00d4aa'),
            ('pointer', 'fg:#00d4aa bold'),
            ('highlighted', 'fg:#00d4aa bold'),
            ('selected', 'fg:#00d4aa'),
        ])
    ).ask_async()

    if folder_choice is None:
        console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
        return

    if folder_choice == "Use this folder":
        project_directory = "."
    else:
        # User wants to specify a different folder
        console.print()
        user_input = await user_input_handler.get_input("Enter project folder path: ")

        if user_input.lower() in ['exit', 'quit']:
            console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
            return

        project_directory = user_input.rstrip('/') if user_input else "."
        if not project_directory:
            project_directory = "."

    # Get coordinator system prompt with project directory injected
    coordinator_prompt = get_coordinator_prompt(project_directory)

    # Determine skills directory path (bundled with package)
    # The skills directory is at: feature_breakdown_agent/skills/
    package_dir = Path(__file__).parent
    skills_directory = package_dir / "skills"

    # Configure agent options
    options = ClaudeAgentOptions(
        system_prompt=coordinator_prompt,
        allowed_tools=["Read", "Write", "Glob", "Grep"],
        permission_mode="acceptEdits",  # Auto-accept file operations
        # Note: Skills are auto-discovered from the skills directory
        # The SDK will look for SKILL.md files in subdirectories
    )

    console.print()
    console.print("[info]Starting Polly...[/info]")
    console.print()

    # Use ClaudeSDKClient for single long-running session
    async with ClaudeSDKClient(options=options) as client:
        # Initial prompt to start the agent
        initial_prompt = f"""The user's project is located at: {os.path.abspath(project_directory)}

Please start by exploring the project:
1. Check if there's a "features/" directory and read any existing feature files
2. Check if there's a "future-features/" directory with feature stubs
3. Summarize what you found (or note this is a new project)
4. Based on what you learned, let the user know what they can do next

Remember:
- Be conversational and friendly
- Explain what you're doing as you explore
- Present options when it would be helpful
- Be ready to invoke skills based on the user's needs

Start exploring now."""

        await client.query(initial_prompt)

        response_text = ""
        first_block = True
        displayed_text = False

        # Collect and display initial response as it arrives
        async for message in client.receive_response():
            message_class = type(message).__name__

            if message_class == "AssistantMessage":
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = type(block).__name__
                        if block_type == "TextBlock":
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

        # Main conversation loop
        while True:
            try:
                user_input = await user_input_handler.get_input("You: ")

                if not user_input:
                    print_info("Please provide a response.")
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    console.print("\n[info]Exiting Feature Breakdown Agent. Goodbye![/info]")
                    return

                prompt = user_input

                # Send query to agent
                await client.query(prompt)

                console.print()

                response_text = ""
                first_block = True
                displayed_text = False

                # Collect and display response from agent as it arrives
                async for message in client.receive_response():
                    # Check message type using class name
                    message_class = type(message).__name__

                    if message_class == "AssistantMessage":
                        if hasattr(message, 'content'):
                            for block in message.content:
                                block_type = type(block).__name__
                                if block_type == "TextBlock":
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


def main():
    """Main entry point for the Feature Breakdown Agent."""
    anyio.run(run_agent)


if __name__ == "__main__":
    main()
