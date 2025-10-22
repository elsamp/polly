"""Tests for display.py module."""

import pytest
from io import StringIO
from rich.console import Console

from feature_breakdown_agent.display import (
    LeftAlignedMarkdown,
    create_markdown,
    console as default_console,
)


class TestLeftAlignedMarkdown:
    """Test the LeftAlignedMarkdown class."""

    def test_creates_markdown_object(self):
        """Should create a LeftAlignedMarkdown object."""
        md = LeftAlignedMarkdown("# Hello")

        assert isinstance(md, LeftAlignedMarkdown)

    def test_renders_without_error(self):
        """Should render markdown text without errors."""
        md = LeftAlignedMarkdown("# Test Heading\n\nSome content")
        test_console = Console(file=StringIO())

        # Should not raise any exceptions
        test_console.print(md)

    def test_uses_custom_heading_class(self):
        """Should use LeftAlignedHeading for headings."""
        md = LeftAlignedMarkdown("# Test")

        # Import to check the class
        from feature_breakdown_agent.display import LeftAlignedHeading

        # The elements dictionary should have our custom class
        assert md.elements["heading_open"] == LeftAlignedHeading

    def test_inline_code_lexer_disabled(self):
        """Should have inline code lexer disabled."""
        md = LeftAlignedMarkdown("Some `code` here")

        assert md.inline_code_lexer is None

    def test_hyperlinks_disabled(self):
        """Should have hyperlinks disabled."""
        md = LeftAlignedMarkdown("[link](http://example.com)")

        assert md.hyperlinks is False


class TestCreateMarkdown:
    """Test the create_markdown helper function."""

    def test_returns_left_aligned_markdown(self):
        """Should return a LeftAlignedMarkdown instance."""
        md = create_markdown("# Test")

        assert isinstance(md, LeftAlignedMarkdown)

    def test_accepts_string_input(self):
        """Should accept markdown string as input."""
        text = "# Heading\n\n- List item 1\n- List item 2"
        md = create_markdown(text)

        assert md is not None

    def test_empty_string(self):
        """Should handle empty string."""
        md = create_markdown("")

        assert isinstance(md, LeftAlignedMarkdown)


class TestPrintFunctions:
    """Test print functions with console capture."""

    def test_print_agent_message_plain(self):
        """Test print_agent_message with plain text."""
        from feature_breakdown_agent.display import print_agent_message

        test_console = Console(file=StringIO())
        # We can't easily test this without modifying the module,
        # so we'll just verify the function exists and is callable
        assert callable(print_agent_message)

    def test_print_error_function_exists(self):
        """Test print_error function exists."""
        from feature_breakdown_agent.display import print_error

        assert callable(print_error)

    def test_print_info_function_exists(self):
        """Test print_info function exists."""
        from feature_breakdown_agent.display import print_info

        assert callable(print_info)

    def test_print_success_function_exists(self):
        """Test print_success function exists."""
        from feature_breakdown_agent.display import print_success

        assert callable(print_success)

    def test_print_warning_function_exists(self):
        """Test print_warning function exists."""
        from feature_breakdown_agent.display import print_warning

        assert callable(print_warning)


class TestConsole:
    """Test the default console configuration."""

    def test_console_exists(self):
        """Default console should exist."""
        assert default_console is not None

    def test_custom_theme_defined(self):
        """Custom theme should be defined in the module."""
        from feature_breakdown_agent.display import custom_theme

        assert custom_theme is not None

    def test_custom_theme_has_required_styles(self):
        """Custom theme should have required style definitions."""
        from feature_breakdown_agent.display import custom_theme

        # Check for expected style names
        assert "agent" in custom_theme.styles
        assert "user" in custom_theme.styles
        assert "tool" in custom_theme.styles
        assert "success" in custom_theme.styles
        assert "error" in custom_theme.styles
        assert "warning" in custom_theme.styles
        assert "info" in custom_theme.styles


class TestUserInput:
    """Test the UserInput class."""

    def test_user_input_initialization(self):
        """UserInput should initialize without errors."""
        from feature_breakdown_agent.display import UserInput

        user_input = UserInput()

        assert user_input is not None
        assert hasattr(user_input, 'history')
        assert hasattr(user_input, 'session')

    def test_has_get_input_method(self):
        """UserInput should have get_input async method."""
        from feature_breakdown_agent.display import UserInput

        user_input = UserInput()

        assert hasattr(user_input, 'get_input')
        assert callable(user_input.get_input)

    def test_has_get_input_sync_method(self):
        """UserInput should have get_input_sync method."""
        from feature_breakdown_agent.display import UserInput

        user_input = UserInput()

        assert hasattr(user_input, 'get_input_sync')
        assert callable(user_input.get_input_sync)


class TestPrintCapturedFeatures:
    """Test print_captured_features function."""

    def test_function_exists(self):
        """print_captured_features should exist."""
        from feature_breakdown_agent.display import print_captured_features

        assert callable(print_captured_features)

    def test_handles_empty_list(self):
        """Should handle empty feature paths list."""
        from feature_breakdown_agent.display import print_captured_features

        # Should not raise an error
        print_captured_features([])

    def test_handles_feature_list(self):
        """Should handle list of feature paths."""
        from feature_breakdown_agent.display import print_captured_features

        paths = [
            "future-features/feature1.md",
            "future-features/feature2.md"
        ]

        # Should not raise an error
        print_captured_features(paths)


class TestPrintWelcome:
    """Test print_welcome function."""

    def test_function_exists(self):
        """print_welcome should exist."""
        from feature_breakdown_agent.display import print_welcome

        assert callable(print_welcome)

    def test_prints_without_error(self):
        """Should print welcome banner without errors."""
        from feature_breakdown_agent.display import print_welcome

        # Should not raise any errors
        print_welcome()
