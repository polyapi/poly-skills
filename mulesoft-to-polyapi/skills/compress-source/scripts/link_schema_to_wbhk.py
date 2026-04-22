#!/usr/bin/env python3
"""
Reads a RAML file to map HTTP routes -> schema files,
then enriches webhooks.jsonl with eventPayloadTypeSchema and responsePayload.
"""

import argparse
import json
import re
import sys
from pathlib import Path

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


def _make_path_loader():
    class PathLoader(yaml.SafeLoader):
        pass

    def include_constructor(loader, node):
        return {"$include": loader.construct_scalar(node)}

    PathLoader.add_constructor("!include", include_constructor)
    return PathLoader


def load_raml_shallow(raml_path: Path) -> dict:
    with open(raml_path, encoding="utf-8") as file_handle:
        return yaml.load(file_handle, Loader=_make_path_loader()) or {}


def _get_include(body_node) -> str | None:
    if not isinstance(body_node, dict):
        return None
    type_node = body_node.get("type")
    if isinstance(type_node, dict) and "$include" in type_node:
        return type_node["$include"]
    for value in body_node.values():
        if isinstance(value, dict):
            type_node = value.get("type")
            if isinstance(type_node, dict) and "$include" in type_node:
                return type_node["$include"]
    return None


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def collect_routes(node: dict, path: str = "") -> dict[tuple[str, str], dict]:
    routes: dict[tuple[str, str], dict] = {}
    if not isinstance(node, dict):
        return routes
    for key, value in node.items():
        if not isinstance(key, str):
            continue
        if key.startswith("/"):
            routes.update(collect_routes(value, path + key))
        elif key.lower() in HTTP_METHODS and isinstance(value, dict):
            body_inc = _get_include(value.get("body", {}))
            resp_inc = None
            responses = value.get("responses", {})
            for status, resp_val in (
                responses.items() if isinstance(responses, dict) else []
            ):
                if str(status).startswith("2") and isinstance(resp_val, dict):
                    resp_inc = _get_include(resp_val.get("body", {}))
                    break
            routes[(key.lower(), path)] = {"body": body_inc, "response": resp_inc}
    return routes


def include_to_schema(
    include_path: str, schemas_dir: Path, data_types_prefix: str = "data_types/"
) -> dict | None:
    normalized = include_path.replace("\\", "/")
    for prefix in (data_types_prefix, "dataTypes/"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
            break
    json_path = schemas_dir / Path(normalized).with_suffix(".json")
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))
    return None


def normalize_subpath(subpath: str) -> str:
    path = subpath.split("?")[0].strip("/")
    return "/" + path


def raml_path_to_regex(raml_path: str) -> re.Pattern:
    escaped = re.escape(raml_path)
    pattern = re.sub(r"\\\{[^}]+\\\}", r"[^/]+", escaped)
    return re.compile(f"^{pattern}$", re.IGNORECASE)


def convert_nullable(schema):
    if not isinstance(schema, dict):
        return schema
    result = {}
    for key, value in schema.items():
        if key == "nullable":
            continue
        result[key] = (
            convert_nullable(value)
            if isinstance(value, dict)
            else (
                [convert_nullable(item) for item in value]
                if isinstance(value, list)
                else value
            )
        )
    if schema.get("nullable") and "type" in schema:
        schema_type = schema["type"]
        result["type"] = [schema_type, "null"] if isinstance(schema_type, str) else schema_type
    return result


def _warn(message: str) -> None:
    print(message, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Enrich webhooks.jsonl with request and response schemas from RAML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/link_schema_to_wbhk.py --raml ./api/member-balance.raml --schemas-dir ./schemas --webhooks ./webhooks.jsonl --out ./webhooks.enriched.jsonl
""".strip(),
    )
    parser.add_argument(
        "--raml",
        type=Path,
        default=REPO_ROOT
        / "META-INF/mule-src/member_info/src/main/resources/api/member-balance.raml",
        help="RAML file that defines the public routes to enrich",
    )
    parser.add_argument(
        "--schemas-dir",
        type=Path,
        default=REPO_ROOT / "schemas",
        help="Directory containing JSON schemas generated from RAML data_types",
    )
    parser.add_argument(
        "--webhooks",
        type=Path,
        default=REPO_ROOT / "webhooks.jsonl",
        help="Input webhooks JSONL file to enrich",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "webhooks.jsonl",
        help="Output JSONL file to write after enrichment",
    )
    args = parser.parse_args()

    if yaml is None:
        parser.error(
            "PyYAML is required. Install PyYAML in the active Python environment."
        )
    if not args.raml.is_file():
        parser.error(f"--raml does not exist: {args.raml}")
    if not args.schemas_dir.is_dir():
        parser.error(f"--schemas-dir does not exist or is not a directory: {args.schemas_dir}")
    if not args.webhooks.is_file():
        parser.error(f"--webhooks does not exist: {args.webhooks}")

    args.out.parent.mkdir(parents=True, exist_ok=True)

    raml = load_raml_shallow(args.raml)
    routes = collect_routes(raml)

    _warn(f"Found {len(routes)} routes in RAML\n")

    webhooks = [
        json.loads(line)
        for line in args.webhooks.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    unmatched = []
    for hook in webhooks:
        method = hook["method"].lower()
        norm = normalize_subpath(hook["subpath"])

        matched_key = None
        if (method, norm) in routes:
            matched_key = (method, norm)
        else:
            for route_method, route_path in routes:
                if route_method != method:
                    continue
                if raml_path_to_regex(route_path).match(norm):
                    matched_key = (route_method, route_path)
                    break

        if matched_key is None:
            unmatched.append(hook["name"])
            continue

        route_info = routes[matched_key]

        if route_info["body"]:
            schema = include_to_schema(route_info["body"], args.schemas_dir)
            if schema:
                hook["eventPayloadType"] = "object"
                hook["eventPayloadTypeSchema"] = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    **convert_nullable(schema),
                }

        if route_info["response"]:
            schema = include_to_schema(route_info["response"], args.schemas_dir)
            if schema:
                hook["responsePayload"] = convert_nullable(schema)

        _warn(f"  ✓ {hook['method']} {norm}")

    with open(args.out, "w", encoding="utf-8") as file_handle:
        for hook in webhooks:
            file_handle.write(json.dumps(hook) + "\n")

    _warn(f"\nWritten to {args.out}")

    if unmatched:
        _warn(f"\nWARNING: {len(unmatched)} webhook(s) had no matching RAML route:")
        for name in unmatched:
            _warn(f"  !! {name}")


if __name__ == "__main__":
    main()
