"""Tests for validating the actual SKILL.md files in the package.

These tests validate the real skills directory structure to ensure
all skills are properly configured and ready for use.
"""

import pytest
import re
from pathlib import Path


# Get the package skills directory
PACKAGE_DIR = Path(__file__).parent.parent / "feature_breakdown_agent"
SKILLS_DIR = PACKAGE_DIR / "skills"


class TestSkillsDirectoryStructure:
    """Validate the skills directory structure."""

    def test_skills_directory_exists(self):
        """Skills directory should exist in the package."""
        assert SKILLS_DIR.exists()
        assert SKILLS_DIR.is_dir()

    def test_has_skill_subdirectories(self):
        """Skills directory should contain skill subdirectories."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        assert len(skill_dirs) > 0, "No skill subdirectories found"

    def test_all_expected_skills_exist(self):
        """All four expected skills should exist."""
        expected_skills = [
            "feature-identification",
            "feature-discovery",
            "iteration-breakdown",
            "prompt-generation"
        ]

        for skill_name in expected_skills:
            skill_path = SKILLS_DIR / skill_name
            assert skill_path.exists(), f"Skill directory '{skill_name}' not found"
            assert skill_path.is_dir(), f"'{skill_name}' is not a directory"


class TestSkillMdFiles:
    """Validate SKILL.md files in each skill directory."""

    def test_all_skills_have_skill_md(self):
        """Each skill directory should have a SKILL.md file."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            assert skill_md.exists(), f"SKILL.md missing in {skill_dir.name}"
            assert skill_md.is_file(), f"SKILL.md in {skill_dir.name} is not a file"

    def test_skill_md_has_yaml_frontmatter(self):
        """Each SKILL.md should have YAML frontmatter."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text()

            # Check for YAML frontmatter pattern (---\n...\n---)
            assert content.startswith("---"), \
                f"SKILL.md in {skill_dir.name} missing YAML frontmatter start"

            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            assert frontmatter_match, \
                f"SKILL.md in {skill_dir.name} has malformed YAML frontmatter"

    def test_skill_md_has_name_field(self):
        """Each SKILL.md should have a 'name' field in frontmatter."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text()

            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            assert frontmatter_match

            frontmatter = frontmatter_match.group(1)
            name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)

            assert name_match, f"SKILL.md in {skill_dir.name} missing 'name' field"
            assert name_match.group(1).strip(), \
                f"SKILL.md in {skill_dir.name} has empty 'name' field"

    def test_skill_md_has_description_field(self):
        """Each SKILL.md should have a 'description' field in frontmatter."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text()

            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            assert frontmatter_match

            frontmatter = frontmatter_match.group(1)
            desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)

            assert desc_match, \
                f"SKILL.md in {skill_dir.name} missing 'description' field"
            assert desc_match.group(1).strip(), \
                f"SKILL.md in {skill_dir.name} has empty 'description' field"

    def test_skill_md_has_content_after_frontmatter(self):
        """Each SKILL.md should have instructions after frontmatter."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text()

            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.+)', content, re.DOTALL)
            assert frontmatter_match, \
                f"SKILL.md in {skill_dir.name} has no content after frontmatter"

            instructions = frontmatter_match.group(2).strip()
            assert len(instructions) > 0, \
                f"SKILL.md in {skill_dir.name} has empty instructions section"


class TestSkillTemplateFiles:
    """Validate that referenced template files exist."""

    @pytest.mark.parametrize("skill_name,expected_templates", [
        ("feature-identification", ["future-feature-template.md"]),
        ("feature-discovery", ["feature-template.md", "future-feature-template.md"]),
        ("iteration-breakdown", ["increments-template.md"]),
        ("prompt-generation", ["prompt-template.md"]),
    ])
    def test_skill_has_expected_templates(self, skill_name, expected_templates):
        """Each skill should have its expected template files."""
        skill_dir = SKILLS_DIR / skill_name

        for template_name in expected_templates:
            template_path = skill_dir / template_name
            assert template_path.exists(), \
                f"Template '{template_name}' missing in {skill_name}"
            assert template_path.is_file(), \
                f"'{template_name}' in {skill_name} is not a file"


class TestSkillNaming:
    """Validate skill naming conventions."""

    def test_skill_name_matches_directory(self):
        """Skill 'name' field should match directory name."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text()

            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            frontmatter = frontmatter_match.group(1)
            name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)

            skill_name = name_match.group(1).strip()
            directory_name = skill_dir.name

            assert skill_name == directory_name, \
                f"Skill name '{skill_name}' doesn't match directory '{directory_name}'"

    def test_skill_names_use_kebab_case(self):
        """Skill names should use kebab-case (lowercase with hyphens)."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            directory_name = skill_dir.name

            # Should be lowercase
            assert directory_name == directory_name.lower(), \
                f"Skill directory '{directory_name}' should be lowercase"

            # Should only contain letters, numbers, and hyphens
            assert re.match(r'^[a-z0-9-]+$', directory_name), \
                f"Skill directory '{directory_name}' should use kebab-case"


class TestSkillDescriptions:
    """Validate skill descriptions are meaningful."""

    def test_descriptions_are_not_empty(self):
        """Skill descriptions should not be empty or just whitespace."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text()

            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            frontmatter = frontmatter_match.group(1)
            desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)

            description = desc_match.group(1).strip()

            assert len(description) > 10, \
                f"Description in {skill_dir.name} is too short (should be meaningful)"

    def test_descriptions_provide_usage_guidance(self):
        """Descriptions should indicate when to use the skill."""
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        for skill_dir in skill_dirs:
            skill_md = skill_dir / "SKILL.md"
            content = skill_md.read_text()

            frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            frontmatter = frontmatter_match.group(1)
            desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)

            description = desc_match.group(1).strip()

            # Description should give context about purpose
            # (checking length is a simple heuristic for meaningfulness)
            assert len(description.split()) >= 3, \
                f"Description in {skill_dir.name} should have at least 3 words"
