#!/usr/bin/env python3
"""Download Boomi integration XMLs by integration name.

Flow:
1) Query ComponentMetadata by integration name to resolve root componentId.
2) Download root component XML (manifest file).
3) Recursively discover referenced component IDs and download each component XML.
4) Persist a graph index for analysis.

Outputs (default base dir: boomi-integrations/<integrationName>/raw):
- <integrationName>.componentMetadata.xml
- <integrationName>.component.xml
- dependencies/<componentId>.component.xml
- <integrationName>.componentGraph.json
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT_SECONDS = 30.0
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
ENV_ENTRY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "integration"


def _basic_auth_header(username: str, token: str) -> str:
    raw = f"{username}:{token}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def _find_repo_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "package.json").exists():
            return candidate
    raise RuntimeError("Unable to locate repository root from script location.")


def _strip_optional_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _parse_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        match = ENV_ENTRY_RE.match(line)
        if not match:
            continue

        key, raw_value = match.groups()
        value = raw_value.strip()
        if value and value[0] not in {'"', "'"}:
            value = value.split("#", 1)[0].strip()

        values[key] = _strip_optional_quotes(value)

    return values


def _request_text(
    url: str,
    method: str,
    headers: dict[str, str],
    body: bytes | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[str, str]:
    req = Request(url=url, data=body, method=method)
    for key, value in headers.items():
        req.add_header(key, value)

    try:
        with urlopen(req, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            content_type = (resp.headers.get("Content-Type") or "").lower()
            return raw, content_type
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} calling {url}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc}") from exc


def _xml_or_fail(raw: str, content_type: str, source_label: str) -> str:
    if "xml" in content_type or raw.lstrip().startswith("<"):
        return raw
    raise RuntimeError(f"{source_label} response is not XML (content-type={content_type or 'unknown'}).")


def _find_component_ids_from_metadata_xml(metadata_xml: str) -> list[str]:
    try:
        root = ET.fromstring(metadata_xml)
    except ET.ParseError:
        return []

    component_ids: list[str] = []
    for elem in root.iter():
        if not elem.tag.endswith("result"):
            continue
        component_id = elem.attrib.get("componentId")
        if component_id:
            component_ids.append(component_id)
    return component_ids


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _is_uuid(value: str) -> bool:
    return bool(UUID_RE.match(value.strip()))


def _extract_referenced_component_ids(component_xml: str, current_component_id: str) -> set[str]:
    refs: set[str] = set()

    try:
        root = ET.fromstring(component_xml)
    except ET.ParseError:
        return refs

    for elem in root.iter():
        for attr_name, attr_value in elem.attrib.items():
            attr_name_lower = attr_name.lower()
            if not _is_uuid(attr_value):
                continue

            # Boomi references often use *Id, but profile links commonly use
            # names like responseProfile / toProfile.
            if attr_name_lower.endswith("id") or attr_name_lower.endswith("profile"):
                refs.add(attr_value)

        # Some Boomi structures can keep IDs in element text under tags ending with "Id".
        if elem.text:
            text_value = elem.text.strip()
            if text_value and _is_uuid(text_value):
                tag_name_lower = _local_name(elem.tag).lower()
                if tag_name_lower.endswith("id") or tag_name_lower.endswith("profile"):
                    refs.add(text_value)

    refs.discard(current_component_id)
    return refs


def _extract_component_identity(component_xml: str, fallback_component_id: str) -> tuple[str, str, str]:
    try:
        root = ET.fromstring(component_xml)
    except ET.ParseError:
        return fallback_component_id, "unknown", "unknown"

    component_id = root.attrib.get("componentId") or fallback_component_id
    component_name = root.attrib.get("name") or "unknown"
    component_type = root.attrib.get("type") or "unknown"
    return component_id, component_name, component_type


@dataclass
class ComponentNode:
    component_id: str
    name: str
    component_type: str
    file_path: str


@dataclass
class FileStats:
    created: int = 0
    updated: int = 0
    deleted: int = 0


def _write_text_file(path: Path, content: str, stats: FileStats) -> None:
    if path.exists():
        stats.updated += 1
    else:
        stats.created += 1
    path.write_text(content, encoding="utf-8")


def _resolve_env_path(raw_env_path: str | None, repo_root: Path) -> Path:
    selected = raw_env_path or os.environ.get("ENVPATH") or str(repo_root / "workflows" / "dev.env")
    path = Path(selected).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def parse_args() -> tuple[argparse.Namespace, Path]:
    repo_root = _find_repo_root(Path(__file__).resolve())

    env_parser = argparse.ArgumentParser(add_help=False)
    env_parser.add_argument(
        "--env-file",
        default=None,
        help="Env file path to load at runtime. Defaults to ENVPATH or workflows/dev.env.",
    )
    env_args, _ = env_parser.parse_known_args(sys.argv[1:])

    env_path = _resolve_env_path(env_args.env_file, repo_root)
    env_values = _parse_dotenv(env_path)
    timeout_default = DEFAULT_TIMEOUT_SECONDS
    timeout_from_env = env_values.get("BOOMI_API_TIMEOUT_SECONDS")
    if timeout_from_env:
        try:
            timeout_default = float(timeout_from_env)
        except ValueError as exc:
            raise SystemExit(
                f"Invalid BOOMI_API_TIMEOUT_SECONDS in {env_path}: must be a number."
            ) from exc

    parser = argparse.ArgumentParser(description="Download full Boomi component dependency graph")
    parser.add_argument(
        "--env-file",
        default=env_args.env_file,
        help="Env file path to load at runtime. Defaults to ENVPATH or workflows/dev.env.",
    )
    parser.add_argument(
        "--account-id",
        default=env_values.get("BOOMI_ACCOUNT_ID"),
        help=f"Boomi account id (or set BOOMI_ACCOUNT_ID in {env_path})",
    )
    parser.add_argument("--integration-name", required=True, help="Boomi integration/component name")
    parser.add_argument(
        "--username",
        default=env_values.get("BOOMI_USERNAME"),
        help=f"Boomi API username (or set BOOMI_USERNAME in {env_path})",
    )
    parser.add_argument(
        "--token",
        default=env_values.get("BOOMI_API_TOKEN"),
        help=f"Boomi API token (or set BOOMI_API_TOKEN in {env_path})",
    )
    parser.add_argument(
        "--api-base",
        default=env_values.get("BOOMI_API_URL"),
        help=f"Boomi API base URL (or set BOOMI_API_URL in {env_path})",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Default: boomi-integrations/<integrationName>/raw",
    )
    parser.add_argument(
        "--folder-name",
        required=True,
        help="Boomi folder name filter for metadata lookup (e.g. 'Submit Order').",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=timeout_default,
        help=(
            f"HTTP timeout per request in seconds (or set BOOMI_API_TIMEOUT_SECONDS in {env_path}; "
            f"default: {DEFAULT_TIMEOUT_SECONDS})"
        ),
    )
    parser.add_argument(
        "--clean-first",
        action="store_true",
        help="Delete the integration output directory before downloading.",
    )
    parser.add_argument(
        "--no-prune",
        action="store_true",
        help="Do not delete stale dependency files from previous runs.",
    )

    argv = sys.argv[1:]
    while argv and argv[0] == "--":
        argv = argv[1:]
    return parser.parse_args(argv), env_path


def main() -> int:
    args, env_path = parse_args()

    if not args.account_id:
        print(
            f"Missing account id. Provide --account-id or set BOOMI_ACCOUNT_ID in {env_path}.",
            file=sys.stderr,
        )
        return 2
    if not args.username or not args.token:
        print(
            "Missing credentials. Provide --username/--token or set "
            f"BOOMI_USERNAME and BOOMI_API_TOKEN in {env_path}.",
            file=sys.stderr,
        )
        return 2
    if not args.api_base:
        print(
            f"Missing API base URL. Provide --api-base or set BOOMI_API_URL in {env_path}.",
            file=sys.stderr,
        )
        return 2
    if args.timeout_seconds <= 0:
        print("--timeout-seconds must be greater than 0.", file=sys.stderr)
        return 2
    if not args.folder_name.strip():
        print("--folder-name must not be empty.", file=sys.stderr)
        return 2

    safe_name = _slugify(args.integration_name)
    repo_root = _find_repo_root(Path(__file__).resolve())

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser()
        if not output_dir.is_absolute():
            output_dir = repo_root / output_dir
        output_dir = output_dir.resolve()
    else:
        output_dir = repo_root / "boomi-integrations" / safe_name / "raw"
    if args.clean_first and output_dir.exists():
        shutil.rmtree(output_dir)

    dependencies_dir = output_dir / "dependencies"
    output_dir.mkdir(parents=True, exist_ok=True)
    dependencies_dir.mkdir(parents=True, exist_ok=True)

    file_stats = FileStats()

    auth_header = _basic_auth_header(args.username, args.token)

    # 1) Resolve root componentId from metadata XML.
    metadata_url = f"{args.api_base}/{args.account_id}/ComponentMetadata/query"
    nested_expression = [
        {
            "property": "name",
            "operator": "EQUALS",
            "argument": [args.integration_name],
        },
        {
            "property": "type",
            "operator": "EQUALS",
            "argument": ["process"],
        },
        {
            "property": "currentVersion",
            "operator": "EQUALS",
            "argument": ["true"],
        },
        {
            "property": "folderName",
            "operator": "EQUALS",
            "argument": [args.folder_name],
        },
    ]

    metadata_payload = {
        "QueryFilter": {
            "expression": {
                "operator": "and",
                "nestedExpression": nested_expression,
            }
        }
    }

    print(f"[1/3] Querying metadata for '{args.integration_name}'...")
    metadata_raw, metadata_content_type = _request_text(
        url=metadata_url,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": auth_header,
        },
        body=json.dumps(metadata_payload).encode("utf-8"),
        timeout_seconds=args.timeout_seconds,
    )
    metadata_xml = _xml_or_fail(metadata_raw, metadata_content_type, "Metadata")

    metadata_path = output_dir / f"{safe_name}.componentMetadata.xml"
    _write_text_file(metadata_path, metadata_xml, file_stats)

    metadata_component_ids = _find_component_ids_from_metadata_xml(metadata_xml)
    if not metadata_component_ids:
        print(f"Metadata saved: {metadata_path}", file=sys.stderr)
        print("Could not resolve root componentId from metadata XML.", file=sys.stderr)
        return 1

    if len(metadata_component_ids) > 1:
        print(
            "Warning: metadata query returned multiple component IDs. "
            "Using the first result from the filtered response.",
            file=sys.stderr,
        )

    root_component_id = metadata_component_ids[0]

    print(f"Resolved root componentId: {root_component_id}")

    # 2) BFS download of root and all referenced component IDs.
    print("[2/3] Downloading component dependency graph...")
    queue: deque[str] = deque([root_component_id])
    visited: set[str] = set()
    nodes: dict[str, ComponentNode] = {}
    edges: list[dict[str, str]] = []

    while queue:
        component_id = queue.popleft()
        if component_id in visited:
            continue
        visited.add(component_id)

        component_url = f"{args.api_base}/{args.account_id}/Component/{component_id}"
        component_raw, component_content_type = _request_text(
            url=component_url,
            method="GET",
            headers={"Authorization": auth_header},
            timeout_seconds=args.timeout_seconds,
        )
        component_xml = _xml_or_fail(component_raw, component_content_type, f"Component/{component_id}")

        node_component_id, node_name, node_type = _extract_component_identity(component_xml, component_id)
        root_file_path = output_dir / f"{safe_name}.component.xml"
        if node_component_id == root_component_id:
            file_path = root_file_path
            _write_text_file(file_path, component_xml, file_stats)

            # Clean up legacy duplicate from previous runs.
            legacy_root_copy = dependencies_dir / f"{node_component_id}.component.xml"
            if legacy_root_copy.exists():
                legacy_root_copy.unlink()
                file_stats.deleted += 1
        else:
            file_path = dependencies_dir / f"{node_component_id}.component.xml"
            _write_text_file(file_path, component_xml, file_stats)

        nodes[node_component_id] = ComponentNode(
            component_id=node_component_id,
            name=node_name,
            component_type=node_type,
            file_path=str(file_path),
        )

        discovered_refs = _extract_referenced_component_ids(component_xml, node_component_id)
        for ref_component_id in sorted(discovered_refs):
            edges.append({"from": node_component_id, "to": ref_component_id})
            if ref_component_id not in visited:
                queue.append(ref_component_id)

        print(f"  downloaded {node_component_id} ({node_type}) -> {len(discovered_refs)} reference(s)")

    # 3) Save graph index.
    print("[3/3] Writing graph index...")
    graph = {
        "integrationName": args.integration_name,
        "accountId": args.account_id,
        "rootComponentId": root_component_id,
        "metadataFile": str(metadata_path),
        "rootComponentFile": str(output_dir / f"{safe_name}.component.xml"),
        "componentCount": len(nodes),
        "edgeCount": len(edges),
        "components": [
            {
                "componentId": node.component_id,
                "name": node.name,
                "type": node.component_type,
                "file": node.file_path,
            }
            for node in sorted(nodes.values(), key=lambda n: n.component_id)
        ],
        "edges": edges,
    }

    graph_path = output_dir / f"{safe_name}.componentGraph.json"
    _write_text_file(graph_path, json.dumps(graph, indent=2), file_stats)

    if not args.no_prune:
        valid_dependency_files = {
            f"{component.component_id}.component.xml"
            for component in nodes.values()
            if component.component_id != root_component_id
        }
        for existing_file in dependencies_dir.glob("*.component.xml"):
            if existing_file.name not in valid_dependency_files:
                existing_file.unlink()
                file_stats.deleted += 1

    print("Graph download completed.")
    print(f"Metadata XML: {metadata_path}")
    print(f"Root component XML: {output_dir / f'{safe_name}.component.xml'}")
    print(f"Dependency files dir: {dependencies_dir}")
    print(f"Graph index: {graph_path}")
    print(
        "File summary: "
        f"created={file_stats.created}, "
        f"updated={file_stats.updated}, "
        f"deleted={file_stats.deleted}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
