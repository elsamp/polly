"""
Future Feature Template

Defines the template structure for capturing future features mentioned
during Phase 1 discovery that are out of scope for the current feature.
"""

from datetime import datetime


FUTURE_FEATURE_TEMPLATE = """# Future Feature: {feature_name}

**Status**: Placeholder for future planning

## Brief Description
{description}

## Mentioned In Context
This feature was mentioned during the discovery phase for: **{mentioned_in_feature}**

**Date Captured**: {capture_date}

## Initial Notes
{initial_notes}

---
*This is a placeholder document created by the Feature Breakdown Agent.*
*Run the agent again with this feature name when you're ready to develop it.*
"""


def generate_future_feature_stub(
    feature_name: str,
    description: str,
    mentioned_in_feature: str,
    initial_notes: str = "No additional notes."
) -> str:
    """Generate a minimal future feature placeholder document.

    Args:
        feature_name: Name of the future feature
        description: Brief 1-2 sentence description
        mentioned_in_feature: Name of the feature being discussed when this came up
        initial_notes: Any additional context from the conversation

    Returns:
        str: Formatted markdown document
    """
    capture_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return FUTURE_FEATURE_TEMPLATE.format(
        feature_name=feature_name,
        description=description,
        mentioned_in_feature=mentioned_in_feature,
        capture_date=capture_date,
        initial_notes=initial_notes
    )


def get_slug(feature_name: str) -> str:
    """Convert feature name to URL-friendly slug.

    Args:
        feature_name: Human-readable feature name

    Returns:
        str: Lowercase slug with hyphens
    """
    return feature_name.lower().replace(" ", "-").replace("_", "-")
