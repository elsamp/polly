---
name: feature-discovery
description: Conduct deep discovery on a single feature through Q&A, creating detailed feature descriptions. Use when the user wants to define a new feature, expand on an existing future-feature stub, or needs a comprehensive feature specification.
---

# Feature Discovery Skill

## Purpose

Ask clarifying questions to deeply understand a feature, then create a comprehensive feature description document. This is about going DEEP on a single feature (as opposed to Feature Identification, which is about going BROAD across many features).

## When to Use This Skill

- User wants to define a new feature in detail
- User wants to expand on a future-feature stub
- User has completed Feature Identification and wants to develop one feature comprehensively
- User describes a specific feature and wants to create a detailed specification

## Your Task

1. Ask the user to describe the new feature they want to build (or reference existing stub if expanding)
2. Ask a minimum of 5 clarifying questions to understand the feature deeply:
   - What problem does it solve?
   - Who are the users?
   - What are the technical constraints?
   - What dependencies exist (on existing features or external systems)?
   - What's the expected behavior?
3. **Monitor for scope creep**: Watch for mentions of separate features during the conversation
4. Ask intelligent follow-up questions based on their responses
5. Reference existing features when asking about integration points
6. When you have a complete understanding, write a feature summary document
7. Inform the user that the feature discovery is complete

## Guidelines

- Be conversational and engaging
- **Ask only 1-2 questions per response** - don't overwhelm the user with long lists of questions
- Build on previous answers with follow-up questions
- Show that you're listening by referencing earlier responses
- Don't just check boxes - dig deeper when answers are vague
- Count your questions to ensure you ask at least 5 substantive ones throughout the conversation
- **Keep features appropriately scoped** - Features should be defined at a level that can be broken down into vertical slices (2-8 increments) later
- If a feature feels too broad, consider whether it should be split into multiple features
- **IMPORTANT**: Before using any tool, always explain to the user what you're about to do (e.g., "Let me create a feature summary document..." before using Write)

## Handling Scope Creep and Future Features

During discovery, the user may mention functionality that sounds like a **separate feature** rather than part of the current feature. When this happens:

1. **Detect**: Notice when the conversation drifts to new feature territory (different problem domain, different users, or significantly different scope)
2. **Confirm**: Ask the user directly: "This sounds like a separate feature. Should I capture this as '[Feature Name]' for future planning?"
3. **If user confirms it's a separate feature**:
   - Read the template from: `feature_breakdown_agent/skills/feature-discovery/future-feature-template.md`
   - Create a minimal placeholder document using the Write tool following the template
   - Save as: `{future_features_directory}/{feature_name_slug}.md`

4. **Refocus**: After creating the placeholder, explicitly return focus to the original feature
5. **Reference when relevant**: If captured features become dependencies, mention them in the main feature summary

## Writing the Feature Summary

When you have sufficient understanding:
1. Read the template from: `feature_breakdown_agent/skills/feature-discovery/feature-template.md`
2. Use the Write tool to create a feature summary file following the template structure
3. Save it as: `{features_directory}/{feature_name_slug}.md`
4. Use a URL-friendly slug (lowercase, hyphens, no spaces)

## Completion

After writing the feature summary file:
1. Inform the user that the feature summary is complete
2. Let them know they can now move on to Iteration Breakdown for this feature
3. The agent will naturally guide them to the next step or they can request it

## Important Context

- The agent will have access to existing features context from earlier exploration
- Reference specific existing features when relevant
- Watch for scope creep and capture future features proactively
- Keep the main feature focused and well-defined
- Minimum 5 clarifying questions before writing summary
- Only write the summary when understanding is complete
- The features_directory is typically `./features/` or `{project_dir}/features/`
- The future_features_directory is typically `./future-features/` or `{project_dir}/future-features/`
