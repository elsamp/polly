"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_features_dir():
    """Create a temporary directory with sample feature files."""
    temp_dir = tempfile.mkdtemp()
    features_dir = Path(temp_dir) / "features"
    features_dir.mkdir()

    # Create sample feature files
    (features_dir / "auth.md").write_text("""# Authentication Feature

## Overview
User authentication with email/password.

## Components
- Login form
- Session management
- Password hashing

## Dependencies
- bcrypt library
- JWT tokens
""")

    (features_dir / "profile.md").write_text("""# Profile Feature

## Overview
User profile management.

## Components
- Profile view
- Edit form
- Avatar upload

## Dependencies
- Auth feature
- AWS S3
""")

    yield features_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def empty_features_dir():
    """Create an empty temporary features directory."""
    temp_dir = tempfile.mkdtemp()
    features_dir = Path(temp_dir) / "features"
    features_dir.mkdir()

    yield features_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_project_structure():
    """Create complete temporary project structure."""
    temp_dir = tempfile.mkdtemp()
    project = Path(temp_dir) / "project"

    # Create directory structure
    (project / "features").mkdir(parents=True)
    (project / "future-features").mkdir(parents=True)
    (project / "prompts").mkdir(parents=True)

    yield project

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_skills_dir():
    """Create temporary skills directory with valid SKILL.md files."""
    temp_dir = tempfile.mkdtemp()
    skills_dir = Path(temp_dir) / "skills"

    # Create a valid mock skill
    skill_dir = skills_dir / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: A test skill for validation
---
# Test Skill Instructions

This is a test skill.""")

    # Create another skill
    skill2_dir = skills_dir / "another-skill"
    skill2_dir.mkdir(parents=True)
    (skill2_dir / "SKILL.md").write_text("""---
name: another-skill
description: Another test skill
---
# Another Skill

More instructions.""")

    yield skills_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_skill_metadata():
    """Return sample skill metadata (no files needed)."""
    return [
        {
            "name": "test-skill",
            "description": "A test skill for validation",
            "path": "skills/test-skill/SKILL.md"
        },
        {
            "name": "another-skill",
            "description": "Another test skill",
            "path": "skills/another-skill/SKILL.md"
        }
    ]
