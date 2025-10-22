"""Tests for coordinator_prompt.py module."""

import pytest
from pathlib import Path
import tempfile
import shutil

from feature_breakdown_agent.coordinator_prompt import (
    load_skill_metadata,
    format_skills_metadata,
    get_coordinator_prompt,
)


class TestLoadSkillMetadata:
    """Test the load_skill_metadata function."""

    def test_load_valid_skills(self, temp_skills_dir):
        """Should load all valid SKILL.md files from directory."""
        skills = load_skill_metadata(temp_skills_dir)

        assert len(skills) == 2
        assert any(s['name'] == 'test-skill' for s in skills)
        assert any(s['name'] == 'another-skill' for s in skills)

    def test_skill_has_required_fields(self, temp_skills_dir):
        """Each skill should have name, description, and path."""
        skills = load_skill_metadata(temp_skills_dir)

        for skill in skills:
            assert 'name' in skill
            assert 'description' in skill
            assert 'path' in skill
            assert skill['name']  # Not empty
            assert skill['description']  # Not empty

    def test_nonexistent_directory(self):
        """Should return empty list for nonexistent directory."""
        fake_path = Path("/nonexistent/path/to/skills")
        skills = load_skill_metadata(fake_path)

        assert skills == []

    def test_empty_directory(self):
        """Should return empty list for directory with no skills."""
        temp_dir = tempfile.mkdtemp()
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()

        try:
            skills = load_skill_metadata(skills_dir)
            assert skills == []
        finally:
            shutil.rmtree(temp_dir)

    def test_malformed_yaml_frontmatter(self):
        """Should skip skills with malformed YAML frontmatter."""
        temp_dir = tempfile.mkdtemp()
        skills_dir = Path(temp_dir) / "skills"
        bad_skill_dir = skills_dir / "bad-skill"
        bad_skill_dir.mkdir(parents=True)

        # Create SKILL.md with missing frontmatter
        (bad_skill_dir / "SKILL.md").write_text("""# Bad Skill
No frontmatter here!""")

        try:
            skills = load_skill_metadata(skills_dir)
            assert skills == []  # Should skip malformed skill
        finally:
            shutil.rmtree(temp_dir)

    def test_missing_name_field(self):
        """Should skip skills missing required name field."""
        temp_dir = tempfile.mkdtemp()
        skills_dir = Path(temp_dir) / "skills"
        incomplete_skill_dir = skills_dir / "incomplete-skill"
        incomplete_skill_dir.mkdir(parents=True)

        # Create SKILL.md with only description
        (incomplete_skill_dir / "SKILL.md").write_text("""---
description: Missing name field
---
# Incomplete Skill""")

        try:
            skills = load_skill_metadata(skills_dir)
            assert skills == []
        finally:
            shutil.rmtree(temp_dir)


class TestFormatSkillsMetadata:
    """Test the format_skills_metadata function."""

    def test_format_multiple_skills(self, mock_skill_metadata):
        """Should format multiple skills as markdown list."""
        formatted = format_skills_metadata(mock_skill_metadata)

        assert "**test-skill**:" in formatted
        assert "A test skill for validation" in formatted
        assert "**another-skill**:" in formatted
        assert "Another test skill" in formatted

    def test_format_empty_list(self):
        """Should return appropriate message for empty skill list."""
        formatted = format_skills_metadata([])

        assert formatted == "No skills available."

    def test_format_single_skill(self):
        """Should format single skill correctly."""
        single_skill = [
            {"name": "solo-skill", "description": "The only skill"}
        ]
        formatted = format_skills_metadata(single_skill)

        assert "**solo-skill**:" in formatted
        assert "The only skill" in formatted


class TestGetCoordinatorPrompt:
    """Test the get_coordinator_prompt function."""

    def test_injects_project_directory(self, temp_skills_dir):
        """Should inject project directory path into prompt."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        assert "/test/project" in prompt

    def test_injects_features_directory(self, temp_skills_dir):
        """Should inject features directory path."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        assert "/test/project/features" in prompt

    def test_injects_future_features_directory(self, temp_skills_dir):
        """Should inject future-features directory path."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        assert "/test/project/future-features" in prompt

    def test_injects_prompts_directory(self, temp_skills_dir):
        """Should inject prompts directory path."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        assert "/test/project/prompts" in prompt

    def test_injects_skills_directory(self, temp_skills_dir):
        """Should inject skills directory path."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        assert str(temp_skills_dir) in prompt

    def test_injects_skills_metadata(self, temp_skills_dir):
        """Should inject formatted skills metadata."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        # Should contain skill names and descriptions
        assert "test-skill" in prompt
        assert "another-skill" in prompt

    def test_prompt_structure(self, temp_skills_dir):
        """Prompt should maintain expected structure."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        # Should contain key sections
        assert "You are Polly" in prompt
        assert "Core Purpose" in prompt
        assert "Available Skills" in prompt
        assert "Project Structure" in prompt
        assert "Conversational Interaction Style" in prompt

    def test_no_placeholder_strings(self, temp_skills_dir):
        """Should not contain unreplaced placeholder strings."""
        project_dir = "/test/project"
        prompt = get_coordinator_prompt(project_dir, temp_skills_dir)

        # Check for unreplaced placeholders
        assert "{project_directory}" not in prompt
        assert "{features_directory}" not in prompt
        assert "{future_features_directory}" not in prompt
        assert "{prompts_directory}" not in prompt
        assert "{skills_directory}" not in prompt
        assert "{skills_metadata}" not in prompt
