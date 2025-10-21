---
name: iteration-breakdown
description: Break down a feature into implementable increments (vertical slices). Use when a feature has been fully discovered and needs to be structured into 2-8 testable, user-valuable increments.
---

# Iteration Breakdown Skill

## Purpose

Analyze a feature description and break it into logical increments (2-8 increments), where each increment is a **vertical slice** that delivers clear user value and is independently testable.

## When to Use This Skill

- User has completed Feature Discovery for a feature
- User has a feature summary document and wants to break it into increments
- User asks to create an incremental plan or iteration structure
- User wants to know how to implement a feature step by step

## Your Task

1. Read the feature summary file to understand what needs to be built
2. Analyze the feature functionality and break it into logical increments (2-8 increments)
3. For each increment, ensure it is a **vertical slice** that:
   - Delivers clear user value (not just scaffolding or infrastructure)
   - Is independently testable by a user
   - Touches all necessary layers (frontend, backend, database, etc.)
   - Builds on previous increments
4. Identify dependencies:
   - Between increments (which must come before others)
   - On existing features (from project context)
   - On future features (if any were captured during Feature Discovery)
5. Present the increment structure to the user for review
6. Adjust based on user feedback if requested
7. Get user approval before saving the increment structure
8. Save the approved increment structure to a file

## Guidelines for Vertical Slices

Each increment MUST:
- **Deliver user value**: The user can see/test something meaningful after this increment
- **Be independently testable**: A user can verify it works on its own
- **Touch all layers**: Not just "build database" then "build API" then "build UI" - each increment should go top-to-bottom
- **Build incrementally**: Each one adds to the previous, creating a growing system

**Good Example** (E-commerce cart feature):
- Increment 1: Add single item to cart and view it (backend + frontend + storage)
- Increment 2: Update quantity and remove items from cart
- Increment 3: Persist cart across sessions
- Increment 4: Calculate totals and apply basic discounts

**Bad Example** (Not vertical slices):
- Increment 1: Database schema for cart ❌ (no user value)
- Increment 2: API endpoints for cart ❌ (still no user value)
- Increment 3: Frontend UI for cart ❌ (horizontal layers)
- Increment 4: Testing and polish ❌ (not a feature)

## Presenting Increments

When presenting your proposed increment structure, use this format:

```
Based on the feature requirements, I propose breaking this into N increments:

**Increment 1: [Name]**
- User Value: [What the user can do after this increment]
- Scope: [Brief description of what's included]
- Dependencies: [Any dependencies on existing features or previous increments]

**Increment 2: [Name]**
- User Value: [What the user can do after this increment]
- Scope: [Brief description of what's included]
- Dependencies: [Any dependencies]

[Continue for all increments...]

Does this incremental structure work for you, or would you like me to adjust the grouping?
```

## Handling User Feedback

- If user requests changes, ask clarifying questions about what they want adjusted
- Regroup and present again
- Be flexible but ensure vertical slice principles are maintained
- Explain reasoning if a user's request would violate vertical slice principles

## Capturing Future Features During Grouping

Sometimes during incremental grouping, you or the user may realize that a proposed increment is actually too large or different in scope to be part of the current feature. When this happens:

1. **Detect**: Notice when discussion suggests an increment should be a separate feature (different user base, separate problem domain, or significantly different scope)
2. **Confirm**: Ask the user: "This increment seems like it could be a separate feature. Should I capture '[Feature Name]' for future planning and remove it from this increment structure?"
3. **If user confirms it's a separate feature**:
   - Read the template from: `feature_breakdown_agent/skills/feature-discovery/future-feature-template.md`
   - Create a minimal placeholder document using the Write tool following the template
   - Save as: `{future_features_directory}/{feature_name_slug}.md`
   - Remove that increment from the current feature's structure
   - Regroup the remaining functionality if needed
4. **Refocus**: After capturing, present the revised increment structure
5. **Reference when relevant**: If captured features relate to the current feature, note them as potential future dependencies

## Saving the Increment Structure

Once the user approves the increment structure:
1. Read the template from: `feature_breakdown_agent/skills/iteration-breakdown/increments-template.md`
2. Use the Write tool to save the increment structure following the template
3. Save it as: `{features_directory}/{feature_name_slug}_increments.md`

## Completion

After saving the increment structure file:
1. Inform the user that the increment structure has been saved
2. Let them know they can now move on to Prompt Generation for this feature
3. The agent will naturally guide them to the next step or they can request it

## Important Context

- You have access to:
  - Feature summary from Feature Discovery (at `{features_directory}/{feature_name_slug}.md`)
  - Existing features context from project exploration
  - Any captured future features from earlier phases
- Use the Read tool to read the feature summary file
- Use the Write tool to create future feature placeholders if needed
- Reference existing and future features when identifying dependencies
- The features_directory is typically `./features/` or `{project_dir}/features/`
- The future_features_directory is typically `./future-features/` or `{project_dir}/future-features/`
- Aim for 2-8 increments (fewer for simple features, more for complex ones)
- Each increment should be achievable in a reasonable development effort
- **IMPORTANT**: Before using any tool, always explain to the user what you're about to do (e.g., "Let me read the feature summary..." before using Read)
