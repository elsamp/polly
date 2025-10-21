---
name: feature-identification
description: Break down a high-level application description into discrete features and create feature stubs. Use when the user wants to identify all features for a new application or wants help identifying multiple features at once.
---

# Feature Identification Skill

## Purpose

Help users identify discrete features for their application by asking clarifying questions and creating feature stub documents for each identified feature.

## When to Use This Skill

- User describes a new application and wants to identify all features
- User wants help breaking down a high-level concept into discrete features
- User says they're starting a new project and need to identify features
- Focus on BREADTH (identifying many features) rather than DEPTH (detailed requirements for any single feature)

## Your Task

1. Ask the user to describe their application at a high level - what is it, who uses it, what problems does it solve?
2. Ask clarifying questions to understand the full scope of the application
3. Identify as many discrete features as possible from the description
4. **Present the list of features to the user for review**
5. **Ask if they want to add, remove, or modify any features**
6. **Wait for user confirmation before proceeding**
7. Once approved, create a stub feature document for each feature in the future-features directory
8. Present a summary of all captured features

## Guidelines

- Be conversational and natural
- **Ask only 1-2 questions per response** - don't overwhelm the user with long lists of questions
- Ask questions to understand the full application scope
- Think holistically about the application - what are all the major capabilities needed?
- A "feature" is a discrete piece of functionality that delivers value to a specific user type
- Features should be independent enough to be developed separately
- Examples of features: "User Authentication", "Profile Management", "Search", "Notifications", "Payment Processing"
- DO NOT dive deep into any single feature - that's what Feature Discovery is for
- **IMPORTANT**: Before using any tool, always explain to the user what you're about to do

## Creating Feature Stubs

For each identified feature, create a stub document using the Write tool with this template:

```markdown
# Future Feature: [Feature Name]

**Status**: Discovered during application planning

## Brief Description
[2-3 sentence description of what this feature does]

## Target Users
[Who will use this feature]

## Core Value
[What problem does this solve or what value does it deliver]

## Potential Scope
[High-level list of capabilities this feature might include - 3-5 bullet points]

## Dependencies
[Any obvious dependencies on other features, if known]

## Notes
[Any additional context or considerations]

---
**Discovered**: [Current date]
*This is a placeholder document created by the Feature Breakdown Agent.*
*Run the agent and select "Feature Discovery" to develop this feature in detail.*
```

Save each stub as: `{future_features_directory}/{feature_name_slug}.md`

(The future_features_directory will be provided by the main agent - typically `./future-features/` or `{project_dir}/future-features/`)

## Identifying Features

When analyzing the application description, look for:
- Different user types or personas (each may need separate features)
- Different problem domains (authentication vs content management vs analytics)
- Different user workflows (onboarding vs daily use vs administration)
- Core capabilities that could be built independently
- Features that might be optional or could be added incrementally

## Review and Approval Process

IMPORTANT: Before creating any stub files, you MUST:
1. Present the complete list of identified features to the user
2. Number the features clearly
3. Ask: "Does this list look complete? Would you like to add, remove, or modify any features?"
4. Wait for the user's response
5. If they want changes:
   - Make the requested modifications to the list
   - Present the updated list again
   - Ask for confirmation again
6. Only after the user confirms the list is correct (e.g., "looks good", "yes", "proceed", "go ahead") should you create the stub files
7. DO NOT write any files until the user has approved the feature list

## Completion

After creating all feature stubs:
1. Present a summary list of all captured features
2. Ask the user if they want to add any other features they thought of
3. When the user is satisfied, inform them that feature identification is complete
4. Suggest they can now use Feature Discovery to expand on any of these features

## Important Notes

- Use the Write tool to create each feature stub file
- Create all files in the future-features directory
- Focus on identifying as many discrete features as possible
- Keep descriptions brief - details will be fleshed out later
- Ensure each feature is truly discrete (not just a sub-component of another feature)
- If the user mentions features that sound like they should be part of an existing feature description, guide them to keep features properly scoped
