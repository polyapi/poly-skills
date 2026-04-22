#!/usr/bin/env python3
import argparse
import json
import re
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
CLASSES_DIR = REPO_ROOT / "classes"


def _display_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _make_raml_loader():
    """Return a SafeLoader subclass that resolves !include relative to the file being parsed."""

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


RAML_TYPE_MAP: dict[str, str] = {
    "string": "str",
    "number": "float",
    "integer": "int",
    "boolean": "bool",
    "date-only": "str",
    "datetime": "str",
    "datetime-only": "str",
    "time-only": "str",
    "any": "Any",
    "nil": "None",
}


def to_class_name(stem: str) -> str:
    """Convert a file stem like 'match_decision' or 'matchDecision' to 'MatchDecision'."""
    normalized = re.sub(r"[-_](.)", lambda match: match.group(1).upper(), stem)
    return normalized[0].upper() + normalized[1:] if normalized else stem


def parse_raml_type_str(raw: str) -> str:
    """Parse a RAML type string like 'string | nil' into a Python type hint."""
    parts = [part.strip() for part in raw.split("|")]
    nullable = "nil" in parts
    types = [part for part in parts if part != "nil"]

    py_types = [RAML_TYPE_MAP.get(type_name, to_class_name(type_name)) for type_name in types]

    if not py_types:
        result = "Any"
    elif len(py_types) == 1:
        result = py_types[0]
    else:
        result = f"Union[{', '.join(py_types)}]"

    if nullable:
        result = f"Optional[{result}]"

    return result


def _cap(name: str) -> str:
    return name[0].upper() + name[1:] if name else name


class ClassWriter:
    def __init__(self):
        self.imports: set[str] = set()
        self.aux_blocks: list[str] = []

    def _resolve_field_type(self, prop_def: Any, parent_class: str, field_name: str) -> str:
        if isinstance(prop_def, str):
            return parse_raml_type_str(prop_def)

        if not isinstance(prop_def, dict):
            return "Any"

        raml_type = prop_def.get("type")

        if raml_type == "object" or (raml_type is None and "properties" in prop_def):
            nested_name = f"{parent_class}{_cap(field_name)}"
            self._emit_aux_class(nested_name, prop_def)
            return nested_name

        if raml_type == "array":
            items = prop_def.get("items")
            if isinstance(items, dict):
                items_raml_type = items.get("type")
                if items_raml_type == "object" or (
                    items_raml_type is None and "properties" in items
                ):
                    item_class = f"{parent_class}{_cap(field_name)}Item"
                    self._emit_aux_class(item_class, items)
                    item_type = item_class
                else:
                    item_type = self._resolve_field_type(items, parent_class, field_name)
            elif isinstance(items, str):
                item_type = parse_raml_type_str(items)
            else:
                item_type = "Any"
            self.imports.add("List")
            return f"List[{item_type}]"

        if isinstance(raml_type, dict):
            nested_name = f"{parent_class}{_cap(field_name)}"
            self._emit_aux_class(nested_name, raml_type)
            return nested_name

        if isinstance(raml_type, str):
            return parse_raml_type_str(raml_type)

        return "Any"

    def _collect_imports(self, type_str: str) -> None:
        if "Optional" in type_str:
            self.imports.add("Optional")
        if "List" in type_str:
            self.imports.add("List")
        if "Union" in type_str:
            self.imports.add("Union")
        if "Any" in type_str:
            self.imports.add("Any")

    def _emit_aux_class(self, class_name: str, content: dict) -> None:
        block_lines = self._render_class(class_name, content)
        self.aux_blocks.append("\n".join(block_lines))

    def _render_class(self, class_name: str, content: Any) -> list[str]:
        props: dict = content.get("properties", {}) if isinstance(content, dict) else {}

        required_fields: list[tuple[str, str]] = []
        optional_fields: list[tuple[str, str]] = []

        for raw_key, prop_def in props.items():
            is_optional = raw_key.endswith("?")
            field_name = raw_key.rstrip("?")
            py_type = self._resolve_field_type(prop_def, class_name, field_name)
            self._collect_imports(py_type)
            if is_optional:
                optional_fields.append((field_name, py_type))
            else:
                required_fields.append((field_name, py_type))

        lines: list[str] = []
        has_required = bool(required_fields)
        has_optional = bool(optional_fields)

        if has_required and has_optional:
            base_name = f"_{class_name}Required"
            lines.append(f"class {base_name}(TypedDict):")
            for field_name, py_type in required_fields:
                lines.append(f"    {field_name}: {py_type}")
            lines.append("")
            lines.append(f"class {class_name}({base_name}, total=False):")
            for field_name, py_type in optional_fields:
                lines.append(f"    {field_name}: {py_type}")
        elif has_required:
            lines.append(f"class {class_name}(TypedDict):")
            for field_name, py_type in required_fields:
                lines.append(f"    {field_name}: {py_type}")
        elif has_optional:
            lines.append(f"class {class_name}(TypedDict, total=False):")
            for field_name, py_type in optional_fields:
                lines.append(f"    {field_name}: {py_type}")
        else:
            lines.append(f"class {class_name}(TypedDict, total=False):")
            lines.append("    pass")

        return lines

    def build(self, class_name: str, content: Any) -> str:
        self.imports = set()
        self.aux_blocks = []

        if isinstance(content, dict):
            main_lines = self._render_class(class_name, content)
        else:
            main_lines = [f"class {class_name}(TypedDict, total=False):", "    pass"]

        header: list[str] = [
            "from __future__ import annotations",
            "from typing_extensions import TypedDict",
        ]
        typing_imports = sorted(self.imports)
        if typing_imports:
            header.append(f"from typing import {', '.join(typing_imports)}")

        parts = header + ["", ""]
        for block in self.aux_blocks:
            parts.append(block)
            parts.append("")
            parts.append("")
        parts.extend(main_lines)

        return "\n".join(parts) + "\n"


def create_class_for_raml(raml_path: Path, classes_dir: Path, base_dir: Path) -> None:
    rel = raml_path.relative_to(base_dir)
    py_path = classes_dir / rel.with_suffix(".py")
    py_path.parent.mkdir(parents=True, exist_ok=True)

    class_name = to_class_name(raml_path.stem)
    print(rel)

    content: Any = {"properties": {}}
    try:
        content = _load_raml(raml_path)
    except Exception as error:
        print(f"  ERROR loading: {error}")

    writer = ClassWriter()
    source = writer.build(class_name, content)

    py_path.write_text(source, encoding="utf-8")
    print(f"  -> {py_path}")
    print(f"  created: {_display_path(py_path, REPO_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert RAML data type fragments into Python TypedDict files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/create_classes_from_raml.py --data-types-dir ./data_types --classes-dir ./classes
""".strip(),
    )
    parser.add_argument(
        "--data-types-dir",
        type=Path,
        default=DATA_TYPES_DIR,
        help="Directory containing RAML data type fragments",
    )
    parser.add_argument(
        "--classes-dir",
        type=Path,
        default=CLASSES_DIR,
        help="Output directory for generated Python TypedDict files",
    )

    args = parser.parse_args()
    data_types_dir: Path = args.data_types_dir
    classes_dir: Path = args.classes_dir

    if yaml is None:
        parser.error(
            "PyYAML is required. Install PyYAML in the active Python environment."
        )
    if not data_types_dir.is_dir():
        parser.error(f"--data-types-dir does not exist or is not a directory: {data_types_dir}")

    classes_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning: {data_types_dir}\n")
    raml_files = sorted(data_types_dir.rglob("*.raml"))
    if not raml_files:
        parser.error(f"No .raml files found under: {data_types_dir}")

    for raml_path in raml_files:
        create_class_for_raml(raml_path, classes_dir, data_types_dir)


if __name__ == "__main__":
    main()
