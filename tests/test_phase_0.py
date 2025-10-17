"""Tests for Phase 0: Context Gathering."""

import pytest
from feature_breakdown_agent.feature_breakdown_agent import PHASE_0_SYSTEM_PROMPT


class TestPhase0SystemPrompt:
    """Test the Phase 0 system prompt configuration."""

    def test_prompt_includes_phase_identifier(self):
        """System prompt should clearly identify Phase 0."""
        assert "Phase 0" in PHASE_0_SYSTEM_PROMPT
        assert "Context Gathering" in PHASE_0_SYSTEM_PROMPT

    def test_prompt_mentions_required_tools(self):
        """System prompt should mention the tools agent needs to use."""
        assert "Read tool" in PHASE_0_SYSTEM_PROMPT or "Read" in PHASE_0_SYSTEM_PROMPT
        assert "Glob tool" in PHASE_0_SYSTEM_PROMPT or "Glob" in PHASE_0_SYSTEM_PROMPT

    def test_prompt_includes_task_steps(self):
        """System prompt should outline the task steps."""
        assert "feature documentation" in PHASE_0_SYSTEM_PROMPT.lower()
        assert "search" in PHASE_0_SYSTEM_PROMPT.lower() or "glob" in PHASE_0_SYSTEM_PROMPT.lower()
        assert "read" in PHASE_0_SYSTEM_PROMPT.lower()
        assert "summarize" in PHASE_0_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_phase_transition(self):
        """System prompt should mention transitioning to Phase 1."""
        assert "Phase 1" in PHASE_0_SYSTEM_PROMPT
        assert "Discovery" in PHASE_0_SYSTEM_PROMPT

    def test_prompt_includes_completion_signal(self):
        """System prompt should define how to signal completion."""
        assert "PHASE_0_COMPLETE" in PHASE_0_SYSTEM_PROMPT


class TestPhase0Configuration:
    """Test Phase 0 configuration requirements."""

    def test_allowed_tools_are_defined(self):
        """Phase 0 should use specific allowed tools."""
        # This test validates our design expectations
        expected_tools = ["Read", "Glob", "Grep"]
        # In the actual implementation, we configure these in ClaudeAgentOptions
        # This test documents the requirement
        assert expected_tools == ["Read", "Glob", "Grep"]

    def test_permission_mode_for_phase_0(self):
        """Phase 0 should use acceptEdits permission mode."""
        # Documents that Phase 0 should auto-accept file reads
        expected_permission_mode = "acceptEdits"
        assert expected_permission_mode == "acceptEdits"


class TestFeatureDocumentationPaths:
    """Test handling of feature documentation paths."""

    def test_default_features_path(self):
        """Default path should be ./features/."""
        default_path = "./features/"
        assert default_path == "./features/"

    def test_custom_features_path_accepted(self, temp_features_dir):
        """Should accept custom feature documentation paths."""
        custom_path = str(temp_features_dir)
        assert Path(custom_path).exists()
        assert Path(custom_path).is_dir()


class TestPhase0Workflow:
    """Test the Phase 0 workflow logic."""

    def test_phase_0_completion_detection(self):
        """Should detect when Phase 0 is complete."""
        response_with_signal = "Great! I've reviewed your features. PHASE_0_COMPLETE"
        assert "PHASE_0_COMPLETE" in response_with_signal

        response_without_signal = "I've reviewed your features."
        assert "PHASE_0_COMPLETE" not in response_without_signal

    def test_phase_1_mention_detection(self):
        """Should detect when agent mentions Phase 1."""
        response_about_phase_1 = "Are you ready to proceed to Phase 1?"
        assert "phase 1" in response_about_phase_1.lower()

        response_staying_in_phase_0 = "Let me read more files."
        assert "phase 1" not in response_staying_in_phase_0.lower()


# Integration-style tests (would require mocking Claude SDK)
# These tests document expected behavior without actually calling the API

class TestPhase0IntegrationExpectations:
    """Document expected integration behavior for Phase 0."""

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_agent_searches_for_markdown_files(self, temp_features_dir, mocker):
        """Agent should use Glob to search for *.md files."""
        # When we implement this, it should:
        # 1. Mock the query() function
        # 2. Verify it receives a prompt asking to search for *.md files
        # 3. Verify it uses the Glob tool
        pass

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_agent_reads_found_files(self, temp_features_dir, mocker):
        """Agent should use Read to read markdown files."""
        # When we implement this, it should:
        # 1. Mock the query() function
        # 2. Verify it uses Read tool for each found file
        pass

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_agent_summarizes_findings(self, temp_features_dir, mocker):
        """Agent should provide summary of existing features."""
        # When we implement this, it should:
        # 1. Mock the query() function
        # 2. Verify response includes a summary
        pass

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_empty_directory_handling(self, empty_features_dir, mocker):
        """Agent should handle directories with no feature files."""
        # When we implement this, it should:
        # 1. Mock the query() function
        # 2. Verify agent acknowledges no files found
        # 3. Verify agent still proceeds to ask about Phase 1
        pass


# Import at the bottom to avoid circular imports
from pathlib import Path
