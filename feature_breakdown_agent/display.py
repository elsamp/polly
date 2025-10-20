"""
Display utilities for the Feature Breakdown Agent.

Provides Rich-based formatting for beautiful terminal output and
Prompt Toolkit integration for enhanced input handling.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from rich.markdown import Markdown as RichMarkdown
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style as PromptStyle


# Custom theme for the agent
custom_theme = Theme({
    "phase": "bold cyan",
    "agent": "green",
    "user": "yellow",
    "tool": "magenta",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "blue",
    "markdown.h1": "bold white",
    "markdown.h2": "bold white",
    "markdown.h3": "bold white",
})

# Initialize Rich console
console = Console(theme=custom_theme)


# Import Markdown internals
from rich.markdown import Heading as RichHeading
from rich.text import Text as RichText

# Custom Heading class that uses left justification
class LeftAlignedHeading(RichHeading):
    """Heading element that aligns left instead of center."""

    def __rich_console__(self, console, options):
        """Render the heading with left alignment."""
        text = self.text
        text.justify = "left"  # Force left alignment
        yield text


# Custom Markdown that doesn't center headings
class LeftAlignedMarkdown(Markdown):
    """Markdown subclass that left-aligns all headings."""

    def __init__(self, markup, **kwargs):
        super().__init__(markup, inline_code_lexer=None, hyperlinks=False, **kwargs)
        # Replace the Heading class with our left-aligned version
        self.elements["heading_open"] = LeftAlignedHeading


# Helper function to create left-aligned markdown
def create_markdown(text: str) -> LeftAlignedMarkdown:
    """Create a Markdown object with left-aligned text.

    Args:
        text: The markdown text to render

    Returns:
        LeftAlignedMarkdown object configured for left alignment
    """
    return LeftAlignedMarkdown(text)

# Prompt Toolkit styling
prompt_style = PromptStyle.from_dict({
    'prompt': '#ansigreen bold',
})


def print_welcome():
    """Display welcome banner."""
    welcome_text = """
# Feature Breakdown Agent

A terminal-based AI agent that transforms high-level feature descriptions
into detailed, incremental coding prompts.

## Getting Started
- **New Project?** Start with Feature Discovery to identify all features at once
- **Existing Project?** Define new features or expand on existing stubs

## Process Overview
• **Context Gathering** - Understanding your project
• **Discovery** - Exploring feature ideas in detail
• **Incremental Grouping** - Breaking down into vertical slices
• **Prompt Generation** - Creating detailed prompts
"""
    console.print(Panel(Markdown(welcome_text), border_style="cyan", padding=(1, 2)))


def print_phase_header(phase_name: str):
    """Display phase transition header.

    Args:
        phase_name: Human-readable phase name (e.g., "Context Gathering", "Feature Discovery")
    """
    console.print()
    console.print(Panel(
        f"[bold white]Starting: {phase_name}[/bold white]",
        border_style="phase",
        padding=(0, 2)
    ))
    console.print()


def print_phase_complete(phase_name: str, extra_info: str = None):
    """Display phase completion message.

    Args:
        phase_name: Human-readable phase name (e.g., "Context Gathering", "Feature Discovery")
        extra_info: Optional additional information to display
    """
    console.print()
    message = f"✓ {phase_name} Complete"
    if extra_info:
        message += f"\n\n{extra_info}"

    console.print(Panel(
        message,
        border_style="success",
        padding=(0, 2)
    ))
    console.print()


def print_agent_message(message: str, render_markdown: bool = False):
    """Display agent message with formatting.

    Args:
        message: The agent's message text
        render_markdown: If True, render the message as markdown with styling
    """
    console.print("[agent]Agent:[/agent] ", end="")
    if render_markdown:
        console.print(create_markdown(message))
    else:
        console.print(message)


def print_agent_message_streaming(message: str, render_markdown: bool = True):
    """Display agent message with markdown rendering (for streaming responses).

    This function is designed to be called after collecting the full response text
    from the agent, allowing proper markdown rendering.

    Args:
        message: The agent's full message text
        render_markdown: If True, render the message as markdown with styling
    """
    if render_markdown:
        # For markdown rendering, we need the full text at once
        console.print(create_markdown(message))
    else:
        console.print(message, end="")


def print_tool_usage(tool_name: str):
    """Display tool usage indicator.

    Args:
        tool_name: Name of the tool being used
    """
    console.print(f"[tool][Using {tool_name}...][/tool]", end="")


def print_error(message: str):
    """Display error message.

    Args:
        message: Error message text
    """
    console.print(f"[error]Error:[/error] {message}")


def print_info(message: str):
    """Display info message.

    Args:
        message: Info message text
    """
    console.print(f"[info]{message}[/info]")


def print_success(message: str):
    """Display success message.

    Args:
        message: Success message text
    """
    console.print(f"[success]{message}[/success]")


def print_warning(message: str):
    """Display warning message.

    Args:
        message: Warning message text
    """
    console.print(f"[warning]{message}[/warning]")


def print_captured_features(feature_paths: list[str]):
    """Display list of captured future features.

    Args:
        feature_paths: List of file paths for captured features
    """
    if not feature_paths:
        return

    content = f"[success]Captured {len(feature_paths)} future feature(s) for later planning:[/success]\n\n"
    for path in feature_paths:
        content += f"  • {path}\n"

    console.print(Panel(
        content,
        title="Future Features",
        border_style="info",
        padding=(0, 2)
    ))
    console.print()


class UserInput:
    """Enhanced user input handler using Prompt Toolkit."""

    def __init__(self):
        """Initialize the input handler with history."""
        self.history = InMemoryHistory()
        self.session = PromptSession(
            history=self.history,
            style=prompt_style,
        )

    async def get_input(self, prompt_text: str = "You: ", multiline: bool = False) -> str:
        """Get user input with enhanced editing capabilities.

        Args:
            prompt_text: The prompt to display
            multiline: Whether to enable multiline input

        Returns:
            User input string
        """
        try:
            # Use prompt_toolkit for better input handling
            user_input = await self.session.prompt_async(
                prompt_text,
                multiline=multiline,
            )
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            raise KeyboardInterrupt()

    def get_input_sync(self, prompt_text: str = "You: ", multiline: bool = False) -> str:
        """Synchronous version of get_input.

        Args:
            prompt_text: The prompt to display
            multiline: Whether to enable multiline input

        Returns:
            User input string
        """
        try:
            user_input = self.session.prompt(
                prompt_text,
                multiline=multiline,
            )
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            raise KeyboardInterrupt()
