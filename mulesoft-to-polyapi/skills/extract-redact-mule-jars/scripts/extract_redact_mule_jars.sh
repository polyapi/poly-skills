#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
JARS_DIR="$BASE_DIR/jars"
REDACTED_VALUE="[REDACTED]"

log() {
  printf '%s\n' "$*"
}

usage() {
  cat <<EOF
Usage:
  $(basename "$0")
      Extract jars from $JARS_DIR and redact credentials in configuration-*.yaml.
      Extraction always performs redaction after unpacking.

  $(basename "$0") <jar_or_project ...>
      Extract only the specified jar(s). Each target may be:
      - a jar path
      - a jar filename under $JARS_DIR
      - a jar stem without .jar
      - a derived extracted project folder name such as member_info_3.0.1
      Extraction always performs redaction after unpacking.

  $(basename "$0") --redact-only [project_dir ...]
      Redact credentials in existing extracted project folders without unpacking jars.
      If no project_dir values are provided, all top-level project folders under
      $BASE_DIR are sanitized.
EOF
}

# Turn app name tokens into snake_case while preserving existing underscores.
to_snake_case() {
  local name="$1"
  name="${name//-/_}"
  printf '%s' "$name"
}

# Derive output folder from a jar filename following repo conventions.
derive_folder_name() {
  local jar_filename="$1"
  local stem runtime="" version="" name_part=""
  local token

  stem="${jar_filename%.jar}"

  # Remove common publisher/build suffixes.
  stem="${stem#gha-}"
  stem="${stem%_j17}"
  stem="${stem%_java17}"
  stem="${stem%-mule-application_v2}"
  stem="${stem%-mule-application}"

  # Capture trailing runtime/mule version in parentheses, e.g. v1.1(4.6.0).
  if [[ "$stem" =~ ^(.*)\(([0-9]+(\.[0-9]+)+)\)$ ]]; then
    stem="${BASH_REMATCH[1]}"
    runtime="${BASH_REMATCH[2]}"
  fi

  # Split by '-' and keep everything before the first version token as name.
  IFS='-' read -r -a tokens <<< "$stem"
  for token in "${tokens[@]}"; do
    if [[ "$token" =~ ^[vV]?[0-9]+(\.[0-9]+)+$ ]]; then
      version="$token"
      break
    fi

    if [[ -z "$name_part" ]]; then
      name_part="$token"
    else
      name_part+="-$token"
    fi
  done

  # Fallback if no version token was found.
  if [[ -z "$name_part" ]]; then
    name_part="$stem"
  fi

  name_part="$(to_snake_case "$name_part")"

  if [[ -n "$version" ]]; then
    name_part+="_${version}"
  fi

  if [[ -n "$runtime" ]]; then
    name_part+="_${runtime}"
  fi

  printf '%s' "$name_part"
}

# Derive the legacy folder name shape used by older extraction logic.
derive_legacy_folder_name() {
  local jar_filename="$1"
  local stem

  stem="${jar_filename%.jar}"
  stem="${stem%_j17}"
  stem="${stem%_java17}"
  stem="${stem%-mule-application_v2}"
  stem="${stem%-mule-application}"

  if [[ "$stem" =~ ^(.*)\(([0-9]+(\.[0-9]+)+)\)$ ]]; then
    stem="${BASH_REMATCH[1]}"
  fi

  printf '%s' "$stem"
}

redact_configuration_file() {
  local config_file="$1"

  python3 - "$config_file" "$REDACTED_VALUE" <<'PY'
from pathlib import Path
import re
import sys

config_path = Path(sys.argv[1])
redacted_value = sys.argv[2]

sensitive_keys = {
    "app_id",
    "appkey",
    "auth",
    "client_id",
    "clientid",
    "client_secret",
    "clientsecret",
    "host",
    "id",
    "key",
    "key_password",
    "pass",
    "password",
    "path",
    "pwd",
    "servicename",
    "token",
    "user",
    "username",
    "x-app-key",
}
sensitive_paths = {
    "token.auth",
}
key_line_pattern = re.compile(r"^(\s*)([A-Za-z0-9_.-]+)(\s*:\s*)(.*?)(\r?\n?)$")


def split_comment(raw_value: str) -> tuple[str, str]:
    in_single_quote = False
    in_double_quote = False

    for index, char in enumerate(raw_value):
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            continue

        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            continue

        if (
            char == "#"
            and not in_single_quote
            and not in_double_quote
            and (index == 0 or raw_value[index - 1].isspace())
        ):
            return raw_value[:index], raw_value[index:]

    return raw_value, ""


def build_redacted_scalar(raw_value: str) -> str:
    leading_whitespace = raw_value[: len(raw_value) - len(raw_value.lstrip())]
    trailing_whitespace = raw_value[len(raw_value.rstrip()) :]
    scalar = raw_value.strip()

    if len(scalar) >= 2 and scalar[0] == scalar[-1] and scalar[0] in {"'", '"'}:
        replacement = f"{scalar[0]}{redacted_value}{scalar[0]}"
    else:
        replacement = redacted_value

    return f"{leading_whitespace}{replacement}{trailing_whitespace}"


lines = config_path.read_text().splitlines(True)
sanitized_lines: list[str] = []
path_stack: list[tuple[int, str]] = []

for line in lines:
    match = key_line_pattern.match(line)
    if not match:
        sanitized_lines.append(line)
        continue

    indentation, key, separator, raw_value, newline = match.groups()
    indent_level = len(indentation.expandtabs(2))

    while path_stack and indent_level <= path_stack[-1][0]:
        path_stack.pop()

    current_path = ".".join([path_key for _, path_key in path_stack] + [key]).lower()
    value_without_comment, comment = split_comment(raw_value)
    has_scalar_value = value_without_comment.strip() != ""

    if has_scalar_value and (
        key.lower() in sensitive_keys or current_path in sensitive_paths
    ):
        raw_value = f"{build_redacted_scalar(value_without_comment)}{comment}"

    sanitized_lines.append(f"{indentation}{key}{separator}{raw_value}{newline}")

    if not has_scalar_value:
        path_stack.append((indent_level, key))

config_path.write_text("".join(sanitized_lines))
PY
}

redact_project_configurations() {
  local project_dir="$1"
  local config_file

  while IFS= read -r -d '' config_file; do
    redact_configuration_file "$config_file"
    log "Sanitized:  $config_file"
  done < <(find "$project_dir" -type f -name 'configuration-*.yaml' -print0)
}

resolve_project_dir() {
  local project_dir="$1"

  if [[ -d "$project_dir" ]]; then
    printf '%s' "$project_dir"
    return 0
  fi

  if [[ -d "$BASE_DIR/$project_dir" ]]; then
    printf '%s' "$BASE_DIR/$project_dir"
    return 0
  fi

  return 1
}

redact_existing_projects() {
  local requested_targets=("$@")
  local project_dirs=()
  local requested_target resolved_target project_dir

  if [[ ${#requested_targets[@]} -eq 0 ]]; then
    while IFS= read -r -d '' project_dir; do
      project_dirs+=("$project_dir")
    done < <(find "$BASE_DIR" -mindepth 1 -maxdepth 1 -type d ! -name 'jars' ! -name '.*' -print0)
  else
    for requested_target in "${requested_targets[@]}"; do
      if ! resolved_target="$(resolve_project_dir "$requested_target")"; then
        log "ERROR: Project directory not found: $requested_target"
        exit 1
      fi
      project_dirs+=("$resolved_target")
    done
  fi

  if [[ ${#project_dirs[@]} -eq 0 ]]; then
    log "No project directories found to sanitize."
    exit 0
  fi

  for project_dir in "${project_dirs[@]}"; do
    log "Sanitizing: $project_dir"
    redact_project_configurations "$project_dir"
  done

  log "Done. Sanitized ${#project_dirs[@]} project(s)."
}

all_jar_files() {
  if [[ ! -d "$JARS_DIR" ]]; then
    log "ERROR: Jars directory not found: $JARS_DIR"
    exit 1
  fi

  shopt -s nullglob
  local jars=("$JARS_DIR"/*.jar)
  shopt -u nullglob

  if [[ ${#jars[@]} -eq 0 ]]; then
    log "No .jar files found in $JARS_DIR"
    exit 0
  fi

  printf '%s\n' "${jars[@]}"
}

resolve_single_jar_target() {
  local requested_target="$1"
  local candidate resolved_name jar_file jar_name folder_name legacy_folder jar_stem
  local matches=()

  if [[ -f "$requested_target" ]]; then
    printf '%s' "$requested_target"
    return 0
  fi

  if [[ -f "$JARS_DIR/$requested_target" ]]; then
    printf '%s' "$JARS_DIR/$requested_target"
    return 0
  fi

  while IFS= read -r jar_file; do
    jar_name="$(basename "$jar_file")"
    jar_stem="${jar_name%.jar}"
    folder_name="$(derive_folder_name "$jar_name")"
    legacy_folder="$(derive_legacy_folder_name "$jar_name")"

    if [[ "$requested_target" == "$jar_name" ]]; then
      matches+=("$jar_file")
      continue
    fi

    if [[ "$requested_target" == "$jar_stem" ]]; then
      matches+=("$jar_file")
      continue
    fi

    if [[ "$requested_target" == "$folder_name" ]]; then
      matches+=("$jar_file")
      continue
    fi

    if [[ "$requested_target" == "$legacy_folder" ]]; then
      matches+=("$jar_file")
      continue
    fi
  done < <(all_jar_files)

  if [[ ${#matches[@]} -eq 1 ]]; then
    printf '%s' "${matches[0]}"
    return 0
  fi

  if [[ ${#matches[@]} -gt 1 ]]; then
    log "ERROR: Ambiguous jar target: $requested_target"
    for candidate in "${matches[@]}"; do
      resolved_name="$(basename "$candidate")"
      log "  - $resolved_name"
    done
    exit 1
  fi

  return 1
}

resolve_jar_targets() {
  local requested_targets=("$@")
  local resolved_targets=()
  local requested_target resolved_target

  if [[ ${#requested_targets[@]} -eq 0 ]]; then
    while IFS= read -r resolved_target; do
      resolved_targets+=("$resolved_target")
    done < <(all_jar_files)
  else
    for requested_target in "${requested_targets[@]}"; do
      if ! resolved_target="$(resolve_single_jar_target "$requested_target")"; then
        log "ERROR: Jar not found for target: $requested_target"
        exit 1
      fi
      resolved_targets+=("$resolved_target")
    done
  fi

  printf '%s\n' "${resolved_targets[@]}"
}

extract_single_jar() {
  local jar_file="$1"
  local jar_name target_dir folder_name legacy_folder legacy_dir

  jar_name="$(basename "$jar_file")"
  folder_name="$(derive_folder_name "$jar_name")"
  target_dir="$BASE_DIR/$folder_name"
  legacy_folder="$(derive_legacy_folder_name "$jar_name")"
  legacy_dir="$BASE_DIR/$legacy_folder"

  log "Processing: $jar_name"
  log "Target:     $target_dir"

  if [[ "$legacy_dir" != "$target_dir" && -d "$legacy_dir" ]]; then
    log "Cleaning:   $legacy_dir (legacy naming)"
    rm -rf "$legacy_dir"
  fi

  rm -rf "$target_dir"
  mkdir -p "$target_dir"

  # Mule apps are jar/zip archives; unzip extracts reliably.
  unzip -q "$jar_file" -d "$target_dir"
  redact_project_configurations "$target_dir"
}

extract_jars() {
  local requested_targets=("$@")
  local jars=()
  local jar_file

  while IFS= read -r jar_file; do
    jars+=("$jar_file")
  done < <(resolve_jar_targets "${requested_targets[@]}")

  for jar_file in "${jars[@]}"; do
    extract_single_jar "$jar_file"
  done

  log "Done. Extracted ${#jars[@]} jar(s)."
}

main() {
  local redact_only=false
  local redact_targets=()
  local extract_targets=()
  local has_redact_targets=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --redact-only)
        redact_only=true
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        if [[ "$redact_only" == true ]]; then
          redact_targets+=("$1")
          has_redact_targets=true
          shift
          continue
        fi

        extract_targets+=("$1")
        shift
        continue
        ;;
    esac
  done

  if [[ "$redact_only" == true ]]; then
    if [[ "$has_redact_targets" == true ]]; then
      redact_existing_projects "${redact_targets[@]}"
    else
      redact_existing_projects
    fi
    return
  fi

  extract_jars "${extract_targets[@]}"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
