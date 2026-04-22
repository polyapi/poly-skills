---
name: markdownlint-compliance
description: Writes and edits Markdown that complies with the locally used VS
  Code `markdownlint` extension defaults in the current repo. Use when
  creating Markdown, fixing markdownlint findings, or normalizing headings,
  lists, code fences, links, and tables.
compatibility: Based on `DavidAnson.vscode-markdownlint` with upstream
  `markdownlint` v0.40.0 rules and no repo-local overrides detected.
---

# Skill: markdownlint-compliance

Use this skill whenever a task touches `.md` files in this repo and the output
must stay clean under the VS Code `markdownlint` extension the user runs.

## Effective Source of Truth

- Plugin: `DavidAnson.vscode-markdownlint`
- Rule reference: `markdownlint` `Rules.md` at `v0.40.0`
- Repo config: no `.markdownlint*` or `markdownlint.*` file found
- Settings overrides: no `markdownlint.*` setting found in repo or user
  settings
- Effective default behavior: upstream rules, with `MD013` disabled by the
  extension's default configuration

## Workflow

1. Assume the extension default configuration is in force unless the current
   repo later adds a `.markdownlint*` or `.markdownlint-cli2.*` file.
2. Before editing headings, lists, code fences, links, or tables, read
   `references/effective-rules.md`.
3. Preserve the document's established style whenever a rule uses
   `consistent`.
4. Use the safe authoring pattern below unless the file already uses another
   valid consistent pattern.
5. After edits, scan the changed section for the common failures:
   `MD022`, `MD031`, `MD032`, `MD034`, `MD040`, `MD055`, `MD058`, and
   `MD060`.
6. Do not reflow prose only to satisfy an 80 character limit unless a repo,
   workspace, or file-level config explicitly enables `MD013`.

## Safe Authoring Pattern

- Use one H1 only and increment heading levels one step at a time.
- Keep one blank line before and after headings, lists, tables, and fenced
  code blocks.
- Use ATX headings with one space after `#`.
- Keep unordered list markers consistent and indent nested bullets by
  2 spaces.
- Use one space after ordered and unordered list markers.
- Avoid trailing spaces and hard tabs.
- Use fenced code blocks and add an explicit language.
- Avoid inline HTML and bare URLs.
- Use descriptive link text.
- Keep every table in one style from top to bottom. Prefer
  `| A | B |` plus `| --- | --- |`.
- End the file with exactly one trailing newline.

## Rules

- Treat `consistent` as "follow the style already established in the file".
- Do not mix table styles within the same table. `MD060` uses `style: any`,
  but a table still needs to fully match one supported style.
- Avoid adding `markdownlint-disable` comments unless the user explicitly asks
  for a rule suppression or there is no compliant representation.
- Do not use raw HTML for layout.
- Always include alt text for images.

## Reference

See `references/effective-rules.md` for the active rule inventory and the
default options that affect authoring.
