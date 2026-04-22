#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


def _find_repo_root(start_dir: Path) -> Path:
    for candidate in (start_dir, *start_dir.parents):
        if (candidate / "AGENTS.md").exists():
            return candidate
    return start_dir


REPO_ROOT = _find_repo_root(Path(__file__).resolve().parent)
DATA_TYPES_DIR = REPO_ROOT / "data_types"
SCHEMAS_DIR = REPO_ROOT / "schemas"


def _display_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _make_raml_loader():
    class RamlLoader(yaml.SafeLoader):
        pass

    def include_constructor(loader, node):
        include_path = loader.construct_scalar(node)
        current_dir = Path(loader.name).parent
        resolved = (current_dir / include_path).resolve()
        return _load_raml(resolved)

    RamlLoader.add_constructor("!include", include_constructor)
    return RamlLoader


def _load_raml(raml_path: Path) -> Any:
    with open(raml_path, "r", encoding="utf-8") as file_handle:
        if raml_path.suffix == ".json":
            return json.load(file_handle)
        return yaml.load(file_handle, Loader=_make_raml_loader())


RAML_TYPE_MAP: dict[str, dict[str, Any]] = {
    "string": {"type": "string"},
    "number": {"type": "number"},
    "integer": {"type": "integer"},
    "boolean": {"type": "boolean"},
    "date-only": {"type": "string", "format": "date"},
    "datetime": {"type": "string", "format": "date-time"},
    "datetime-only": {"type": "string", "format": "date-time"},
    "time-only": {"type": "string", "format": "time"},
    "any": {},
}


def parse_raml_type(raw: str) -> dict[str, Any]:
    parts = [part.strip() for part in raw.split("|")]
    nullable = "nil" in parts
    types = [part for part in parts if part != "nil"]

    schemas = [RAML_TYPE_MAP.get(type_name, {"type": type_name}) for type_name in types]

    result: dict[str, Any]
    if len(schemas) == 1:
        result = dict(schemas[0])
    elif len(schemas) > 1:
        result = {"oneOf": [dict(schema) for schema in schemas]}
    else:
        result = {}

    if nullable:
        result["nullable"] = True

    return result


def dict_handler(content: dict):
    for key, value in list(content.items()):
        clean_key = key.replace("?", "")
        if "?" in key:
            content.pop(key)
            content[clean_key] = value
            key = clean_key

        if isinstance(value, dict):
            if key == "type":
                content.pop("type")
                content.update(value)
                dict_handler(content)
                return
            if key == "properties":
                required = [
                    prop.replace("?", "") for prop in value.keys() if "?" not in prop
                ]
                if required:
                    content["required"] = required
            dict_handler(content[key])
        elif isinstance(value, str) and ("|" in value or value in RAML_TYPE_MAP):
            if key == "type" and "|" not in value:
                mapped = RAML_TYPE_MAP.get(value, {})
                content["type"] = mapped.get("type", value)
                if "format" in mapped:
                    content["format"] = mapped["format"]
            else:
                content[key] = parse_raml_type(value)


def create_json_for_raml(raml_path: Path, schemas_dir: Path, base_dir: Path) -> None:
    rel = raml_path.relative_to(base_dir)
    json_path = schemas_dir / rel.with_suffix(".json")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    print(rel)
    result: Any = {"schema": {"type": "object"}}
    try:
        content = _load_raml(raml_path)
        if isinstance(content, dict):
            dict_handler(content)
        result = content
    except Exception as error:
        print(f"  ERROR: {error}")

    with open(json_path, "w", encoding="utf-8") as file_handle:
        json.dump(result, file_handle, indent=2)
    print(f"  -> {json_path}")
    print(f"  created: {_display_path(json_path, REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert RAML data type fragments into JSON Schema files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/create_schemas.py --data-types-dir ./data_types --schemas-dir ./schemas
""".strip(),
    )
    parser.add_argument(
        "--data-types-dir",
        type=Path,
        default=DATA_TYPES_DIR,
        help="Directory containing RAML data type fragments",
    )
    parser.add_argument(
        "--schemas-dir",
        type=Path,
        default=SCHEMAS_DIR,
        help="Output directory for generated JSON schemas",
    )

    args = parser.parse_args()
    data_types_dir: Path = args.data_types_dir
    schemas_dir: Path = args.schemas_dir
    if yaml is None:
        parser.error(
            "PyYAML is required. Install PyYAML in the active Python environment."
        )
    if not data_types_dir.is_dir():
        parser.error(f"--data-types-dir does not exist or is not a directory: {data_types_dir}")

    schemas_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning: {data_types_dir}\n")
    raml_files = sorted(data_types_dir.rglob("*.raml"))
    if not raml_files:
        parser.error(f"No .raml files found under: {data_types_dir}")

    for raml_path in raml_files:
        lines = raml_path.read_text(encoding="utf-8").splitlines()
        first_line = lines[0].strip() if lines else ""
        if "#%RAML 1.0 Library" in first_line:
            print(f"  skipped (Library): {raml_path.name}")
            continue
        create_json_for_raml(raml_path, schemas_dir, data_types_dir)


if __name__ == "__main__":
    main()
