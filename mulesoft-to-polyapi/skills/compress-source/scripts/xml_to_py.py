#!/usr/bin/env python3
"""
Mule XML tree walker using lxml.
Parses eg.xml, prints a readable flow tree, resolves all config-refs
through _global.xml, lists every ${...} YAML property required, and
extracts scheduler flows into a target API job spec format.
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import lxml.etree as ET
except ModuleNotFoundError:
    ET = None


def _find_repo_root(start_dir: Path) -> Path:
    for candidate in (start_dir, *start_dir.parents):
        if (candidate / "AGENTS.md").exists():
            return candidate
    return start_dir


REPO_ROOT = _find_repo_root(Path(__file__).resolve().parent)

NS_MAP = {
    "http://www.mulesoft.org/schema/mule/core": "",
    "http://www.mulesoft.org/schema/mule/http": "http",
    "http://www.mulesoft.org/schema/mule/ee/core": "ee",
    "http://www.mulesoft.org/schema/mule/db": "db",
    "http://www.mulesoft.org/schema/mule/file": "file",
    "http://www.mulesoft.org/schema/mule/documentation": "doc",
}

DOC_NS = "http://www.mulesoft.org/schema/mule/documentation"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"


def short_tag(element):
    tag = element.tag
    if tag.startswith("{"):
        uri, local = tag[1:].split("}", 1)
        prefix = NS_MAP.get(uri) if uri in NS_MAP else uri.rsplit("/", 1)[-1]
        return f"{prefix}:{local}" if prefix else local
    return tag


def fmt_attribs(element):
    parts = []
    doc_name = None
    for key, value in element.attrib.items():
        if key.startswith("{"):
            uri, local = key[1:].split("}", 1)
            if uri == DOC_NS and local == "id":
                continue
            if uri == DOC_NS and local == "name":
                doc_name = value
                continue
            if uri == XSI_NS:
                continue
            prefix = NS_MAP.get(uri) if uri in NS_MAP else uri.rsplit("/", 1)[-1]
            label = f"{prefix}:{local}" if prefix else local
        else:
            label = key
        parts.append(f"{label}={value!r}")
    lead = f"[{doc_name}]  " if doc_name else ""
    rest = "  ".join(parts)
    return f"  {lead}{rest}" if (lead or rest) else ""


def print_text(text, indent):
    if not text or not text.strip():
        return
    pad = "  " * indent
    for line in text.strip().splitlines():
        print(f"{pad}  {line}")


def local_tag(el):
    if not isinstance(el.tag, str):
        return None
    return el.tag.split("}")[-1] if "}" in el.tag else el.tag


def walk(element, indent=0, flow_map=None, _visited=None):
    if not isinstance(element.tag, str):
        return
    if _visited is None:
        _visited = set()
    pad = "  " * indent
    tag = short_tag(element)
    attribs = fmt_attribs(element)
    print(f"{pad}{tag}{attribs}")
    print_text(element.text, indent)

    if flow_map is not None and local_tag(element) == "flow-ref":
        ref_name = element.attrib.get("name", "")
        target = flow_map.get(ref_name)
        if target is not None and id(target) not in _visited:
            _visited.add(id(target))
            print(f"{pad}  >>> expanding: {ref_name}")
            for child in target:
                walk(child, indent + 2, flow_map, _visited)
            return

    for child in element:
        walk(child, indent + 1, flow_map, _visited)


PROP_RE = re.compile(r"\$\{([^}]+)\}")
DW_PROP_RE = re.compile(r"p\('([^']+)'\)")


def all_text_in_subtree(element):
    for value in element.attrib.values():
        yield value
    if element.text:
        yield element.text
    for child in element.iter():
        for value in child.attrib.values():
            yield value
        if child.text:
            yield child.text


def build_global_index(global_tree):
    index = {}
    for el in global_tree.getroot().iter():
        name = el.attrib.get("name")
        if name:
            index[name] = el
    return index


def collect_config_refs(flow_tree):
    refs = set()
    for el in flow_tree.getroot().iter():
        ref = el.attrib.get("config-ref")
        if ref:
            refs.add(ref)
    return sorted(refs)


def collect_dw_props(flow_tree):
    props = set()
    for el in flow_tree.getroot().iter():
        if el.text:
            props.update(DW_PROP_RE.findall(el.text))
    return props


def report_variables(flow_tree, global_tree):
    config_refs = collect_config_refs(flow_tree)
    global_index = build_global_index(global_tree)
    dw_props = collect_dw_props(flow_tree)

    print()
    print("=" * 70)
    print("CONFIG-REFS -> VARIS REQUIRED")
    print("=" * 70)

    all_props = set()

    for ref in config_refs:
        el = global_index.get(ref)
        props = set()
        if el is not None:
            for text in all_text_in_subtree(el):
                props.update(PROP_RE.findall(text))
            tag = short_tag(el)
            print(f"\n  config-ref={ref!r}  ({tag})")
        else:
            print(f"\n  config-ref={ref!r}  (NOT FOUND in _global.xml)")
        for prop in sorted(props):
            print(f"    ${{{prop!s}}}")
        all_props.update(props)

    if dw_props:
        print("\n  DataWeave p('...') calls in flow logic")
        for prop in sorted(dw_props):
            print(f"    p('{prop}')")
        all_props.update(dw_props)

    print()
    print("-" * 60)
    print("  ALL VARIS NEEDED:")
    for prop in sorted(all_props):
        print(f"    {prop}")
    print("-" * 60)


TO_MINUTES = {
    "MILLISECONDS": lambda value: value / 60_000,
    "SECONDS": lambda value: value / 60,
    "MINUTES": lambda value: value,
    "HOURS": lambda value: value * 60,
    "DAYS": lambda value: value * 1440,
}


def parse_schedule(scheduler_el):
    for strategy in scheduler_el:
        for child in strategy:
            local = local_tag(child)
            if local is None:
                continue
            if local == "cron":
                return "periodical", child.attrib.get("expression", "")
            if local == "fixed-frequency":
                freq = int(child.attrib.get("frequency", 1))
                unit = child.attrib.get("timeUnit", "MINUTES").upper()
                minutes = TO_MINUTES.get(unit, lambda value: value)(freq)
                return "interval", int(minutes)
    return "interval", 0


def extract_schedulers(root):
    jobs = []
    for flow in root:
        if local_tag(flow) != "flow":
            continue

        children = [child for child in flow if isinstance(child.tag, str)]
        if not children:
            continue

        if local_tag(children[0]) != "scheduler":
            continue

        flow_name = flow.attrib.get("name", "")
        sched_type, sched_value = parse_schedule(children[0])

        event_payload = {}
        for child in children[1:]:
            child_local = local_tag(child)
            if child_local == "set-variable":
                var_name = child.attrib.get("variableName", "")
                var_value = child.attrib.get("value", "")
                if var_name:
                    event_payload[var_name] = var_value
            elif child_local == "flow-ref":
                break

        job = {
            "name": flow_name,
            "schedule": {
                "type": sched_type,
                "value": sched_value,
                "acceptableDelayTime": 30,
            },
            "functions": [
                {
                    "id": "",
                    "headersPayload": {},
                    "eventPayload": {},
                    "paramsPayload": {},
                }
            ],
            "enabled": True,
            "executionType": "sequential",
        }
        jobs.append(job)
    return jobs


def report_schedulers(root, out_file="jobs.jsonl"):
    jobs = extract_schedulers(root)
    if not jobs:
        return
    with open(out_file, "w", encoding="utf-8") as file_handle:
        for job in jobs:
            file_handle.write(json.dumps(job) + "\n")
    print(f"\nJobs written to {out_file}  ({len(jobs)} schedulers)")
    for job in jobs:
        print(
            f"  {job['schedule']['type']:<12} {job['schedule']['value']:<10} -> {job['name']}"
        )


def pascal_to_snake(name: str) -> str:
    snake = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", snake)
    return snake.lower()


def find_flow_ref_name(flow_el) -> str | None:
    for el in flow_el:
        if local_tag(el) == "flow-ref":
            return el.attrib.get("name")
    return None


APIKIT_RE = re.compile(
    r"^(get|post|put|patch|delete|head|options)"
    r":\\(.+?)"
    r"(?::application\\[^:]+)?"
    r":([^:]+)$",
    re.IGNORECASE,
)


def mule_path_to_subpath(mule_path: str) -> str:
    parts = mule_path.split("\\")
    converted = []
    for part in parts:
        if part.startswith("(") and part.endswith(")"):
            converted.append("{" + part[1:-1] + "}")
        elif part:
            converted.append(part)
    return "/".join(converted)


XML_PARSER_OPTIONS = {
    "enabled": False,
    "explicitArray": False,
    "normalizeTags": False,
    "trim": False,
}

QUERY_PARAM_RE = re.compile(r"attributes\.queryParams\.'?([a-zA-Z0-9_]+)'?")


def build_flow_map(mule_dir: str, extra_files: list[str] | None = None) -> dict:
    import glob as _glob

    paths = list(_glob.glob(f"{mule_dir}/**/*.xml", recursive=True))
    if extra_files:
        paths.extend(extra_files)

    flow_map = {}
    for path in paths:
        try:
            tree = ET.parse(path)
        except Exception:
            continue
        for el in tree.getroot().iter():
            if not isinstance(el.tag, str):
                continue
            if local_tag(el) in ("flow", "sub-flow"):
                name = el.attrib.get("name")
                if name:
                    flow_map[name] = el
    return flow_map


def scan_query_params(el, flow_map: dict, visited: set) -> set:
    found: set[str] = set()
    if id(el) in visited:
        return found
    visited.add(id(el))
    for node in el.iter():
        if not isinstance(node.tag, str):
            continue
        for value in node.attrib.values():
            found.update(QUERY_PARAM_RE.findall(value))
        if node.text:
            found.update(QUERY_PARAM_RE.findall(node.text))
        if local_tag(node) == "flow-ref":
            ref_name = node.attrib.get("name", "")
            target = flow_map.get(ref_name)
            if target is not None:
                found |= scan_query_params(target, flow_map, visited)
    return found


def build_subpath(base: str, query_params: list) -> str:
    if not query_params:
        return base
    query_string = "&".join(f"{param}={{{param}}}" for param in query_params)
    return f"{base}?{query_string}"


def load_filter(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def extract_webhooks(
    flow_map: dict, allowed: set[str] | None = None
) -> tuple[list, set[str]]:
    hooks = []
    matched: set[str] = set()
    for name, flow in flow_map.items():
        if local_tag(flow) != "flow":
            continue
        if allowed is not None and name not in allowed:
            continue
        match = APIKIT_RE.match(name)
        if not match:
            continue
        matched.add(name)
        method, mule_path = match.group(1), match.group(2)
        base_subpath = mule_path_to_subpath(mule_path)
        query_params = sorted(scan_query_params(flow, flow_map, set()))
        subpath = build_subpath(base_subpath, query_params)
        ref_name = find_flow_ref_name(flow)
        hook_name = pascal_to_snake(ref_name) if ref_name else name
        hooks.append(
            {
                "name": hook_name,
                "context": "",
                "description": "",
                "subpath": subpath,
                "method": method.upper(),
                "eventPayloadType": "",
                "eventPayloadTypeSchema": {},
                "responsePayload": {},
                "responseStatus": 200,
                "slug": "{{GHA_SLUG}}",
                "xmlParserOptions": XML_PARSER_OPTIONS,
            }
        )
    return hooks, matched


def report_webhooks(
    flow_map: dict, out_file="webhooks.jsonl", allowed: set[str] | None = None
):
    hooks, matched = extract_webhooks(flow_map, allowed)
    if not hooks:
        print("\nNo matching webhooks found.")
        return
    print(f"\nFound {len(hooks)} webhook(s).")
    with open(out_file, "w", encoding="utf-8") as file_handle:
        for hook in hooks:
            file_handle.write(json.dumps(hook) + "\n")
    print(f"Webhooks written to {out_file}")
    for hook in hooks:
        print(f"  {hook['method']:<7} {hook['subpath']}")
    if allowed is not None:
        missing = allowed - matched
        if missing:
            print(f"\n  WARNING: {len(missing)} filter line(s) had no matching flow:")
            for key in sorted(missing):
                print(f"    !! not found: {key}")


class _Tee:
    def __init__(self, file_handle):
        self._file = file_handle
        self._stdout = sys.stdout

    def write(self, data):
        self._stdout.write(data)
        self._file.write(data)

    def flush(self):
        self._stdout.flush()
        self._file.flush()


def main():
    parser = argparse.ArgumentParser(
        description="Mule XML flow walker that prints a readable flow tree, resolves flow-refs, and extracts webhooks and schedulers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with defaults (expects mule/ dir next to this script)
  python scripts/xml_to_py.py

  # Custom flow XML and global config
  python scripts/xml_to_py.py --flow-xml ./impl/my-flow.xml --global-xml ./my-global.xml

  # Also index flows from another XML for inline flow-ref expansion
  python scripts/xml_to_py.py --xml-files ./other/member_info.xml ./other/rates.xml

  # Only output webhooks listed in a filter file
  python scripts/xml_to_py.py --filter-file interested_hooks.txt

  # All options together
  python scripts/xml_to_py.py \\
    --flow-xml ./mule/implementation/ra.xml \\
    --global-xml ./mule/_global.xml \\
    --mule-dir ./mule \\
    --xml-files ./other/member_info.xml \\
    --filter-file interested_hooks.txt \\
    --out compressed.txt

Outputs:
  compressed.txt   Full print output (also echoed to stdout)
  webhooks.jsonl   One webhook JSON object per line, written next to --out
  jobs.jsonl       One scheduler job JSON object per line, written next to --out
""",
    )
    parser.add_argument(
        "--flow-xml",
        type=Path,
        default=REPO_ROOT / "mule/implementation/ra.xml",
        help="Main flow XML file (default: mule/implementation/ra.xml)",
    )
    parser.add_argument(
        "--global-xml",
        type=Path,
        default=REPO_ROOT / "mule/_global.xml",
        help="Global config XML file (default: mule/_global.xml)",
    )
    parser.add_argument(
        "--mule-dir",
        type=Path,
        default=None,
        help="Directory scanned recursively for flow-ref resolution (default: parent dir of --flow-xml)",
    )
    parser.add_argument(
        "--xml-files",
        type=Path,
        nargs="+",
        default=[],
        help="Extra XML files to index for flow-ref expansion (usually not needed when --mule-dir covers all flows)",
    )
    parser.add_argument(
        "--filter-file",
        type=Path,
        default=None,
        help="Text file of exact flow names to include in webhooks output (one per line)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("compressed.txt"),
        help="File to write full print output to (default: compressed.txt); webhooks.jsonl and jobs.jsonl are written alongside it",
    )
    args = parser.parse_args()
    if ET is None:
        parser.error(
            "lxml is required. Install lxml in the active Python environment."
        )
    if not args.flow_xml.is_file():
        parser.error(f"--flow-xml does not exist: {args.flow_xml}")
    if not args.global_xml.is_file():
        parser.error(f"--global-xml does not exist: {args.global_xml}")
    if args.mule_dir is not None and not args.mule_dir.is_dir():
        parser.error(f"--mule-dir does not exist or is not a directory: {args.mule_dir}")
    missing_xml_files = [path for path in args.xml_files if not path.is_file()]
    if missing_xml_files:
        missing = ", ".join(str(path) for path in missing_xml_files)
        parser.error(f"--xml-files contains missing paths: {missing}")
    if args.filter_file is not None and not args.filter_file.is_file():
        parser.error(f"--filter-file does not exist: {args.filter_file}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    output_dir = args.out.parent
    webhooks_out = output_dir / "webhooks.jsonl"
    jobs_out = output_dir / "jobs.jsonl"

    out_file = open(args.out, "w", encoding="utf-8")
    tee = _Tee(out_file)
    original_stdout = sys.stdout
    sys.stdout = tee

    try:
        flow_tree = ET.parse(str(args.flow_xml))
        global_tree = ET.parse(str(args.global_xml))
        root = flow_tree.getroot()

        print("=" * 70)
        print("MULE FLOW TREE")
        print("=" * 70)

        mule_dir = args.mule_dir if args.mule_dir is not None else args.flow_xml.parent
        all_extra = [str(path) for path in args.xml_files]
        flow_map = build_flow_map(str(mule_dir), all_extra or None)

        for child in root:
            tag = short_tag(child)
            name = child.attrib.get("name", "")
            print()
            print("-" * 60)
            print(f"  {tag}  name={name!r}")
            print("-" * 60)
            for step in child:
                walk(step, indent=1, flow_map=flow_map)
        report_variables(flow_tree, global_tree)
        report_schedulers(root, str(jobs_out))
        allowed = load_filter(args.filter_file) if args.filter_file else None
        report_webhooks(flow_map, out_file=str(webhooks_out), allowed=allowed)
        print()
        print("=" * 70)
        print("Done.")
    finally:
        sys.stdout = original_stdout
        out_file.close()

    print(f"Output saved to {args.out}")


if __name__ == "__main__":
    main()
