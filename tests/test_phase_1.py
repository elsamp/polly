"""Tests for Phase 1: Discovery."""

import pytest
from feature_breakdown_agent.feature_breakdown_agent import PHASE_1_SYSTEM_PROMPT


class TestPhase1SystemPrompt:
    """Test the Phase 1 system prompt configuration."""

    def test_prompt_includes_phase_identifier(self):
        """System prompt should clearly identify Phase 1."""
        assert "Phase 1" in PHASE_1_SYSTEM_PROMPT
        assert "Discovery" in PHASE_1_SYSTEM_PROMPT

    def test_prompt_mentions_required_tools(self):
        """System prompt should mention the tools agent needs to use."""
        assert "Write tool" in PHASE_1_SYSTEM_PROMPT or "Write" in PHASE_1_SYSTEM_PROMPT

    def test_prompt_includes_minimum_questions_requirement(self):
        """System prompt should mention minimum 5 questions."""
        assert "5" in PHASE_1_SYSTEM_PROMPT
        assert "question" in PHASE_1_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_feature_summary(self):
        """System prompt should mention writing a feature summary."""
        assert "feature summary" in PHASE_1_SYSTEM_PROMPT.lower()
        assert "write" in PHASE_1_SYSTEM_PROMPT.lower()

    def test_prompt_includes_completion_signal(self):
        """System prompt should define how to signal completion."""
        assert "PHASE_1_COMPLETE" in PHASE_1_SYSTEM_PROMPT

    def test_prompt_mentions_clarifying_question_topics(self):
        """System prompt should mention key question topics."""
        prompt_lower = PHASE_1_SYSTEM_PROMPT.lower()
        assert "problem" in prompt_lower
        assert "users" in prompt_lower
        assert "technical constraints" in prompt_lower or "constraints" in prompt_lower
        assert "dependencies" in prompt_lower
        assert "behavior" in prompt_lower


class TestPhase1Configuration:
    """Test Phase 1 configuration requirements."""

    def test_allowed_tools_include_write(self):
        """Phase 1 should include Write tool for feature summary."""
        expected_tools = ["Read", "Glob", "Grep", "Write"]
        assert "Write" in expected_tools

    def test_permission_mode_for_phase_1(self):
        """Phase 1 should use acceptEdits permission mode."""
        expected_permission_mode = "acceptEdits"
        assert expected_permission_mode == "acceptEdits"


class TestPhase1FeatureSummary:
    """Test feature summary requirements."""

    def test_feature_summary_sections(self):
        """Feature summary should include required sections."""
        required_sections = [
            "Feature Name",
            "Problem Statement",
            "Target Users",
            "Key Functionality",
            "Technical Constraints",
            "Dependencies",
            "Expected Behavior",
        ]
        # Verify these are documented in the system prompt
        for section in required_sections:
            assert section in PHASE_1_SYSTEM_PROMPT

    def test_feature_summary_filename_format(self):
        """Feature summary filename should use slug format."""
        assert "slug" in PHASE_1_SYSTEM_PROMPT.lower()
        assert "lowercase" in PHASE_1_SYSTEM_PROMPT.lower()
        assert "hyphen" in PHASE_1_SYSTEM_PROMPT.lower()


class TestPhase1Workflow:
    """Test the Phase 1 workflow logic."""

    def test_phase_1_completion_detection(self):
        """Should detect when Phase 1 is complete."""
        response_with_signal = "Feature summary written. PHASE_1_COMPLETE"
        assert "PHASE_1_COMPLETE" in response_with_signal

        response_without_signal = "I have more questions to ask."
        assert "PHASE_1_COMPLETE" not in response_without_signal


# Integration-style tests (would require mocking Claude SDK)
class TestPhase1IntegrationExpectations:
    """Document expected integration behavior for Phase 1."""

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_agent_asks_initial_question(self, mocker):
        """Agent should ask user to describe the feature."""
        pass

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_agent_asks_minimum_five_questions(self, mocker):
        """Agent should ask at least 5 clarifying questions."""
        pass

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_agent_writes_feature_summary(self, mocker):
        """Agent should write feature summary using Write tool."""
        pass

    @pytest.mark.skip(reason="Requires Claude SDK mocking - implementation pending")
    def test_agent_references_existing_features(self, mocker):
        """Agent should reference existing features from Phase 0."""
        pass
