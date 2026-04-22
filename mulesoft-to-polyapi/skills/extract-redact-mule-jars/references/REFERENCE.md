# extract-redact-mule-jars Reference

## Purpose

`./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh`
unpacks Mule application jars from `jars/` into top-level project folders and
redacts sensitive values inside `configuration-*.yaml`.

Use it when:

- the project only exists as a jar in `jars/`
- extracted folders need to be refreshed from the packaged jars
- existing extracted folders only need config re-sanitization
- the user manually unjared a project and now only needs sanitization

## Preconditions

Run from the `mulesoft-to-polyapi` pack root.

Required tools:

- `bash`
- `unzip`
- `python3`

Required inputs:

- one or more `.jar` files under `./jars/` for full extraction
- a specific jar path, jar filename, jar stem, or derived extracted project folder name for targeted extraction
- or existing top-level extracted project folders for `--redact-only`

Before running any extraction command, get explicit user confirmation. Extraction is destructive for the target folder and also performs redaction automatically after unpacking.

When matching a user-requested integration to folders or jars, do not require exact name equality. Treat common naming differences as likely matches and ask the user to confirm. Typical differences include:

- underscores versus hyphens
- `gha-` prefixes
- Mule build suffixes such as `-mule-application`, `_j17`, or `_java17`
- version formatting differences
- user-renamed extracted folders

## Commands

### Extract all jars

```bash
./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh
```

This:

- reads every `.jar` under `./jars/`
- derives a top-level output folder name for each jar
- deletes any existing folder with that target name
- unpacks the jar into the target folder
- redacts sensitive values in `configuration-*.yaml`

### Extract one jar only

```bash
./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh member_info_3.0.1
```

You can target a single extraction by:

- jar path
- jar filename under `./jars/`
- jar stem without `.jar`
- derived extracted project folder name

If more than one jar matches the requested target, the script stops and reports the ambiguous matches instead of guessing.

This command both extracts and redacts.

### Re-sanitize existing extracted projects

```bash
./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh --redact-only
```

### Re-sanitize specific extracted projects

```bash
./skills/extract-redact-mule-jars/scripts/extract_redact_mule_jars.sh --redact-only member_info_3.0.1 eventdispatcher_1.0.1
```

## Verification

After running the script, verify all of the following:

1. The expected top-level project folder exists.
2. The project folder contains a Mule source tree such as:
   - `META-INF/`
   - `api/`
   - `implementation/`
   - `_global.xml` or equivalent Mule XML files
3. Any `configuration-*.yaml` files inside the project contain `[REDACTED]` for sensitive values instead of live credentials.

Example checks:

```bash
find . -maxdepth 1 -type d ! -name '.*' ! -name 'jars'
find ./member_info_3.0.1 -type f -name 'configuration-*.yaml'
```

## Important Behaviour

- Full extraction is destructive for matching extracted project folders because the script removes and recreates them.
- Targeted extraction is still destructive for the selected target folder.
- `--redact-only` does not unpack jars; it only sanitizes existing folders.
- The output folders created by extraction are the folders later skills should use as `<PROJECT_ROOT>`.
