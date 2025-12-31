# Rules System

This repository uses a **canonical rule system** to manage AI/LLM coding rules. Instead of maintaining separate rules for different tools (Cursor, Antigravity, etc.), we define them once in `.rules/` and generate the tool-specific files.

## 1. Rule Format

All rules are located in the `.rules/` directory as Markdown files (`.rules/<rule-name>.md`).

Each rule file **must** contain two metadata blocks at the very top, followed by the rule content:

```markdown
<!-- cursor:
description: Short description for Cursor
globs:
  - "**/*.ts"
alwaysApply: true
-->

<!-- antigravity:
trigger: always_on
-->

## Rule Title

Rule content goes here...
```

### Metadata Blocks
- **`<!-- cursor: ... -->`**: Contains the YAML frontmatter used by Cursor (e.g., `description`, `globs`, `alwaysApply`).
- **`<!-- antigravity: ... -->`**: Contains the YAML frontmatter used by Antigravity (e.g., `trigger`).

### Content
The rest of the file is standard Markdown. This content is appended to the generated files for all tools.

## 2. Creating a New Rule

1.  Create a new file in `.rules/`. Example: `.rules/my-new-rule.md`.
2.  Add the required metadata blocks (Cursor and Antigravity).
3.  Write your rule guidelines in Markdown.

## 3. Generating Rules

After creating or modifying a rule in `.rules/`, you must regenerate the tool-specific files.

### Using the Script (Recommended)
Run the generation script directly:

```bash
./scripts/generate_rules.sh
```

### Using Setup
The setup script also runs rule generation automatically:

```bash
./setup.sh
```

## 4. Generated Outputs

The script generates the following files:

- **Cursor**: `.cursor/rules/<rule-name>/RULE.md`
- **Antigravity**: `.agent/rules/<rule-name>.md`

> **Note**: Do not edit files in `.cursor/rules/` or `.agent/rules/` directly. They will be overwritten by the generator. Always edit the source in `.rules/`.
