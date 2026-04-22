# Effective `markdownlint` Rules

This reference captures the effective Markdown linting behavior observed for
the current repository.

- Plugin: `DavidAnson.vscode-markdownlint`
- Rule index: `markdownlint` `Rules.md` at `v0.40.0`
- Repo config: none found
- Settings overrides: none found
- Effective default config: all upstream rules enabled except `MD013`
- VS Code diagnostics: library `error` is shown as `Warning` by default

## Enabled by Default

```text
MD001 heading-increment
MD003 heading-style
MD004 ul-style
MD005 list-indent
MD007 ul-indent
MD009 no-trailing-spaces
MD010 no-hard-tabs
MD011 no-reversed-links
MD012 no-multiple-blanks
MD014 commands-show-output
MD018 no-missing-space-atx
MD019 no-multiple-space-atx
MD020 no-missing-space-closed-atx
MD021 no-multiple-space-closed-atx
MD022 blanks-around-headings
MD023 heading-start-left
MD024 no-duplicate-heading
MD025 single-title
MD026 no-trailing-punctuation
MD027 no-multiple-space-blockquote
MD028 no-blanks-blockquote
MD029 ol-prefix
MD030 list-marker-space
MD031 blanks-around-fences
MD032 blanks-around-lists
MD033 no-inline-html
MD034 no-bare-urls
MD035 hr-style
MD036 no-emphasis-as-heading
MD037 no-space-in-emphasis
MD038 no-space-in-code
MD039 no-space-in-links
MD040 fenced-code-language
MD041 first-line-heading
MD042 no-empty-links
MD043 required-headings
MD044 proper-names
MD045 no-alt-text
MD046 code-block-style
MD047 single-trailing-newline
MD048 code-fence-style
MD049 emphasis-style
MD050 strong-style
MD051 link-fragments
MD052 reference-links-images
MD053 link-image-reference-definitions
MD054 link-image-style
MD055 table-pipe-style
MD056 table-column-count
MD058 blanks-around-tables
MD059 descriptive-link-text
MD060 table-column-style
```

## Disabled by Default

```text
MD013 line-length
```

The marketplace page says the extension enables all rules except `MD013` by
default. In this repo, no local config file or settings override that default,
so `MD013` should not be enforced unless a new config is added.

## Defaults That Affect Authoring

- `MD003`, `MD004`, `MD035`, `MD046`, `MD048`, `MD049`, `MD050`, and `MD055`
  use `style: consistent`.
- `MD007` uses 2-space unordered-list nesting and does not indent the first
  list level.
- `MD009` allows 2 trailing spaces only for explicit hard line breaks.
- `MD012` allows at most 1 blank line in a row.
- `MD022` requires 1 blank line above and below headings.
- `MD024` forbids duplicate headings across the whole document, not only among
  siblings.
- `MD025` allows one title heading at level `1`. A front matter title can
  count as the title.
- `MD026` forbids trailing punctuation in headings.
- `MD029` allows either all-`1.` ordered lists or incrementing list numbers.
- `MD030` requires 1 space after list markers.
- `MD031` requires blank lines around fenced code blocks, including inside list
  items.
- `MD033` disallows inline HTML. No elements are whitelisted.
- `MD034` disallows bare URLs.
- `MD040` requires a language on every fenced code block.
- `MD041` expects the first heading line to be an H1 unless front matter
  provides the title.
- `MD051` checks link fragments case-sensitively by default.
- `MD052` disallows shortcut reference links and ignores only the label `x`.
- `MD053` ignores only the definition `//`.
- `MD054` allows autolink, inline, full, collapsed, and shortcut link and
  image styles.
- `MD058` requires blank lines around tables.
- `MD059` forbids weak link text such as `click here`, `here`, `link`, and
  `more`.
- `MD060` uses `style: any` and `aligned_delimiter: false`. Each table still
  needs to match one supported style all the way through; mixed styles still
  fail.

## Practical Defaults for New Markdown

- Prefer ATX headings.
- Keep headings, lists, tables, and fenced code blocks separated by blank
  lines.
- Use fenced code blocks with a language tag.
- Use descriptive links instead of bare URLs.
- Prefer compact spaced tables:

```md
| Name | Value |
| --- | --- |
| A | B |
```

- Do not add inline HTML for layout or visual spacing.
- Do not wrap prose aggressively for `MD013` unless that rule is explicitly
  enabled by config.
