#!/usr/bin/env python3
"""Generate a compact Boomi evidence pack from downloaded raw XML files.

The script preserves migration-relevant behavior while removing UI/layout metadata
that is not useful for implementation parity.

Outputs (default):
- boomi-integrations/<integrationName>/analysis/compactEvidence.json
- boomi-integrations/<integrationName>/analysis/compactEvidence.md
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "integration"


def _find_repo_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "package.json").exists():
            return candidate
    raise RuntimeError("Unable to locate repository root from script location.")


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _iter_descendants_by_local_name(node: ET.Element, name: str):
    for item in node.iter():
        if _local_name(item.tag) == name:
            yield item


def _first_descendant_by_local_name(node: ET.Element, name: str) -> ET.Element | None:
    for item in _iter_descendants_by_local_name(node, name):
        return item
    return None


def _read_xml(path: Path) -> ET.Element:
    return ET.fromstring(path.read_text(encoding="utf-8"))


@dataclass
class GraphComponent:
    component_id: str
    name: str
    component_type: str
    file_path: Path


def _resolve_graph_components(repo_root: Path, graph: dict) -> list[GraphComponent]:
    components: list[GraphComponent] = []
    for item in graph.get("components", []):
        raw_path = Path(item.get("file", ""))
        file_path = raw_path if raw_path.is_absolute() else repo_root / raw_path
        components.append(
            GraphComponent(
                component_id=item.get("componentId", ""),
                name=item.get("name", "unknown"),
                component_type=item.get("type", "unknown"),
                file_path=file_path,
            )
        )
    return components


def _extract_route_values(route_node: ET.Element) -> list[dict]:
    values: list[dict] = []
    route_values = _first_descendant_by_local_name(route_node, "routevalues")
    if route_values is None:
        return values

    for route_value in route_values:
        if _local_name(route_value.tag) != "routevalue":
            continue
        values.append(
            {
                "name": route_value.attrib.get("name"),
                "qualifier": route_value.attrib.get("qualifier"),
                "value": route_value.attrib.get("value"),
                "key": route_value.attrib.get("key"),
            }
        )
    return values


def _extract_business_rules(node: ET.Element) -> list[dict]:
    rules: list[dict] = []
    for rule in _iter_descendants_by_local_name(node, "rule"):
        error_message = _first_descendant_by_local_name(rule, "errorMessage")
        inputs = []
        for input_field in _iter_descendants_by_local_name(rule, "input"):
            input_name = input_field.attrib.get("name")
            if input_name:
                inputs.append(input_name)

        condition = _first_descendant_by_local_name(rule, "condition")
        nested_operators = [
            nested.attrib.get("operator")
            for nested in _iter_descendants_by_local_name(rule, "nestedExpression")
            if nested.attrib.get("operator")
        ]

        rules.append(
            {
                "name": rule.attrib.get("name"),
                "key": rule.attrib.get("key"),
                "conditionOperator": condition.attrib.get("operator") if condition is not None else None,
                "nestedOperators": nested_operators,
                "inputs": sorted(set(inputs)),
                "errorMessage": error_message.attrib.get("content") if error_message is not None else None,
            }
        )
    return rules


def _extract_shape_details(shape: ET.Element) -> dict:
    shape_type = shape.attrib.get("shapetype", "unknown")
    details: dict = {}
    configuration = _first_descendant_by_local_name(shape, "configuration")

    if configuration is None:
        return details

    if shape_type == "start":
        connector = _first_descendant_by_local_name(configuration, "connectoraction")
        if connector is not None:
            details = {
                "actionType": connector.attrib.get("actionType"),
                "connectorType": connector.attrib.get("connectorType"),
                "operationId": connector.attrib.get("operationId"),
            }

    elif shape_type == "map":
        map_node = _first_descendant_by_local_name(configuration, "map")
        if map_node is not None:
            details = {"mapId": map_node.attrib.get("mapId")}

    elif shape_type == "route":
        route_node = _first_descendant_by_local_name(configuration, "route")
        if route_node is not None:
            profile_element = _first_descendant_by_local_name(route_node, "profileelement")
            details = {
                "routeField": {
                    "elementName": profile_element.attrib.get("elementName") if profile_element is not None else None,
                    "profileId": profile_element.attrib.get("profileId") if profile_element is not None else None,
                },
                "values": _extract_route_values(route_node),
            }

    elif shape_type == "businessrules":
        business_rules = _first_descendant_by_local_name(configuration, "businessrules")
        if business_rules is not None:
            details = {
                "profileId": business_rules.attrib.get("profileId"),
                "profileName": business_rules.attrib.get("profileName"),
                "rules": _extract_business_rules(business_rules),
            }

    elif shape_type == "notify":
        notify = _first_descendant_by_local_name(configuration, "notify")
        if notify is not None:
            msg = _first_descendant_by_local_name(notify, "notifyMessage")
            level = _first_descendant_by_local_name(notify, "notifyMessageLevel")
            details = {
                "message": msg.text.strip() if msg is not None and msg.text else None,
                "level": level.text.strip() if level is not None and level.text else None,
            }

    elif shape_type == "exception":
        exception = _first_descendant_by_local_name(configuration, "exception")
        if exception is not None:
            message = _first_descendant_by_local_name(exception, "exMessage")
            details = {
                "title": exception.attrib.get("title"),
                "message": message.text.strip() if message is not None and message.text else None,
            }

    return details


def _extract_shape_connections(shape: ET.Element) -> list[dict]:
    connections: list[dict] = []
    dragpoints = _first_descendant_by_local_name(shape, "dragpoints")
    if dragpoints is None:
        return connections

    for dragpoint in dragpoints:
        if _local_name(dragpoint.tag) != "dragpoint":
            continue
        connections.append(
            {
                "toShape": dragpoint.attrib.get("toShape"),
                "identifier": dragpoint.attrib.get("identifier"),
                "text": dragpoint.attrib.get("text"),
            }
        )
    return connections


def _extract_process_summary(root_component_xml: Path) -> dict:
    root = _read_xml(root_component_xml)
    process = _first_descendant_by_local_name(root, "process")

    if process is None:
        return {
            "componentId": root.attrib.get("componentId"),
            "name": root.attrib.get("name"),
            "shapeCount": 0,
            "shapes": [],
            "warnings": ["No process node found in root component XML."],
        }

    shapes: list[dict] = []
    for shape in _iter_descendants_by_local_name(process, "shape"):
        shape_type = shape.attrib.get("shapetype", "unknown")
        shapes.append(
            {
                "shapeName": shape.attrib.get("name"),
                "shapeType": shape_type,
                "label": shape.attrib.get("userlabel") or None,
                "details": _extract_shape_details(shape),
                "connections": _extract_shape_connections(shape),
            }
        )

    return {
        "componentId": root.attrib.get("componentId"),
        "name": root.attrib.get("name"),
        "shapeCount": len(shapes),
        "shapes": shapes,
        "warnings": [],
    }


def _extract_document_properties(root_component_xml: Path, defined_prop_lookup: dict) -> dict:
    """Extract every <documentproperty> element from the main process XML.

    Each element is a runtime variable — either a Dynamic Process Property (DPP,
    scope=process) or a Dynamic Document Property (DDP, scope=document).

    defined_prop_lookup maps (componentId, propertyKey) -> isSecret so that
    variables sourced from a password-type Defined Process Property are flagged.
    """
    root = _read_xml(root_component_xml)
    process = _first_descendant_by_local_name(root, "process")
    if process is None:
        return {"dynamicProcessProperties": [], "dynamicDocumentProperties": []}

    dpps: dict[str, dict] = {}
    ddps: dict[str, dict] = {}

    for doc_prop in _iter_descendants_by_local_name(process, "documentproperty"):
        prop_id = doc_prop.attrib.get("propertyId", "")

        if prop_id.startswith("process."):
            scope = "process"
            short_name = prop_id[len("process."):]
        elif prop_id.startswith("dynamicdocument."):
            scope = "document"
            short_name = prop_id[len("dynamicdocument."):]
        else:
            continue

        source_type = "unknown"
        source_detail: str | None = None
        is_secret = False

        source_values = _first_descendant_by_local_name(doc_prop, "sourcevalues")
        if source_values is not None:
            for param_value in source_values:
                if _local_name(param_value.tag) != "parametervalue":
                    continue
                value_type = param_value.attrib.get("valueType")

                if value_type == "static":
                    static_param = _first_descendant_by_local_name(param_value, "staticparameter")
                    if static_param is not None:
                        source_type = "static"
                        source_detail = static_param.attrib.get("staticproperty")

                elif value_type == "definedparameter":
                    defined_param = _first_descendant_by_local_name(param_value, "definedprocessparameter")
                    if defined_param is not None:
                        source_type = "definedProcessProperty"
                        comp_id = defined_param.attrib.get("componentId", "")
                        prop_key = defined_param.attrib.get("propertyKey", "")
                        prop_label = defined_param.attrib.get("propertyLabel", "")
                        comp_name = defined_param.attrib.get("componentName", "")
                        source_detail = f"{prop_label!r} from {comp_name!r}"
                        is_secret = defined_prop_lookup.get((comp_id, prop_key), False)

                elif value_type == "profile":
                    profile_elem = _first_descendant_by_local_name(param_value, "profileelement")
                    if profile_elem is not None:
                        source_type = "profileField"
                        source_detail = profile_elem.attrib.get("elementName")

                elif value_type == "process":
                    process_param = _first_descendant_by_local_name(param_value, "processparameter")
                    if process_param is not None:
                        source_type = "dynamicProcessProperty"
                        source_detail = process_param.attrib.get("processproperty")

                elif value_type == "track":
                    track_param = _first_descendant_by_local_name(param_value, "trackparameter")
                    if track_param is not None:
                        source_type = "dynamicDocumentProperty"
                        source_detail = track_param.attrib.get("propertyName")

                elif value_type == "crossref":
                    crossref_param = _first_descendant_by_local_name(param_value, "crossrefparameter")
                    if crossref_param is not None:
                        source_type = "crossRefLookup"
                        source_detail = crossref_param.attrib.get("crossRefTableId")

                break  # only the first parametervalue determines source type

        entry = {
            "name": short_name,
            "propertyId": prop_id,
            "scope": scope,
            "sourceType": source_type,
            "sourceDetail": source_detail,
            "isSecret": is_secret,
        }

        if scope == "process":
            dpps[short_name] = entry
        else:
            ddps[short_name] = entry

    return {
        "dynamicProcessProperties": sorted(dpps.values(), key=lambda x: x["name"]),
        "dynamicDocumentProperties": sorted(ddps.values(), key=lambda x: x["name"]),
    }


def _extract_profile_fields(node: ET.Element, path_parts: list[str], output: list[dict]) -> None:
    local = _local_name(node.tag)

    if local in {"JSONRootValue", "JSONObject", "JSONObjectEntry"}:
        node_name = node.attrib.get("name")
        next_path_parts = path_parts + ([node_name] if node_name else [])

        if local == "JSONObjectEntry":
            output.append(
                {
                    "path": "/".join(next_path_parts),
                    "name": node_name,
                    "dataType": node.attrib.get("dataType"),
                    "required": node.attrib.get("required") == "true",
                    "allowEmpty": node.attrib.get("allowEmpty"),
                    "key": node.attrib.get("key"),
                }
            )

        for child in list(node):
            _extract_profile_fields(child, next_path_parts, output)
        return

    for child in list(node):
        _extract_profile_fields(child, path_parts, output)


def _extract_profile_summary(component: GraphComponent) -> dict:
    root = _read_xml(component.file_path)
    profile = _first_descendant_by_local_name(root, "JSONProfile")
    fields: list[dict] = []
    if profile is not None:
        _extract_profile_fields(profile, [], fields)

    return {
        "componentId": component.component_id,
        "name": component.name,
        "file": str(component.file_path),
        "fieldCount": len(fields),
        "fields": fields,
    }


def _extract_map_summary(component: GraphComponent) -> dict:
    root = _read_xml(component.file_path)
    map_node = _first_descendant_by_local_name(root, "Map")
    if map_node is None:
        return {
            "componentId": component.component_id,
            "name": component.name,
            "file": str(component.file_path),
            "fromProfile": None,
            "toProfile": None,
            "mappings": [],
            "scripts": [],
        }

    mappings = []
    mappings_node = _first_descendant_by_local_name(map_node, "Mappings")
    if mappings_node is not None:
        for mapping in mappings_node:
            if _local_name(mapping.tag) != "Mapping":
                continue
            mappings.append(
                {
                    "fromNamePath": mapping.attrib.get("fromNamePath"),
                    "toNamePath": mapping.attrib.get("toNamePath"),
                    "fromType": mapping.attrib.get("fromType"),
                    "toType": mapping.attrib.get("toType"),
                    "fromFunction": mapping.attrib.get("fromFunction"),
                    "toFunction": mapping.attrib.get("toFunction"),
                }
            )

    scripts = []
    for function_step in _iter_descendants_by_local_name(map_node, "FunctionStep"):
        script_node = _first_descendant_by_local_name(function_step, "ScriptToExecute")
        scripts.append(
            {
                "key": function_step.attrib.get("key"),
                "name": function_step.attrib.get("name"),
                "type": function_step.attrib.get("type"),
                "script": script_node.text.strip() if script_node is not None and script_node.text else None,
            }
        )

    return {
        "componentId": component.component_id,
        "name": component.name,
        "file": str(component.file_path),
        "fromProfile": map_node.attrib.get("fromProfile"),
        "toProfile": map_node.attrib.get("toProfile"),
        "mappings": mappings,
        "scripts": scripts,
    }


def _extract_connector_summary(component: GraphComponent) -> dict:
    root = _read_xml(component.file_path)
    operation = _first_descendant_by_local_name(root, "Operation")
    configuration = _first_descendant_by_local_name(operation, "Configuration") if operation is not None else None

    action = None
    if configuration is not None:
        for child in list(configuration):
            action = {
                "type": _local_name(child.tag),
                "attributes": dict(child.attrib),
            }
            break

    return {
        "componentId": component.component_id,
        "name": component.name,
        "file": str(component.file_path),
        "operation": action,
    }


def _extract_defined_process_properties(component: GraphComponent) -> dict:
    """Extract every property from a processproperty component.

    Each property has a type field; type='password' means the value is a secret
    and the defaultValue must never be included in output.
    """
    root = _read_xml(component.file_path)
    properties: list[dict] = []

    for prop in _iter_descendants_by_local_name(root, "definedProcessProperty"):
        label_el = _first_descendant_by_local_name(prop, "label")
        type_el = _first_descendant_by_local_name(prop, "type")
        default_el = _first_descendant_by_local_name(prop, "defaultValue")
        help_el = _first_descendant_by_local_name(prop, "helpText")

        label = label_el.text.strip() if label_el is not None and label_el.text else ""
        prop_type = type_el.text.strip() if type_el is not None and type_el.text else "string"
        default_value = default_el.text.strip() if default_el is not None and default_el.text else ""
        help_text = help_el.text.strip() if help_el is not None and help_el.text else ""
        is_secret = prop_type == "password"

        properties.append({
            "key": prop.attrib.get("key"),
            "label": label,
            "type": prop_type,
            "isSecret": is_secret,
            # Never include the actual default value for secrets
            "defaultValue": None if is_secret else (default_value or None),
            "helpText": help_text or None,
        })

    return {
        "componentId": component.component_id,
        "name": component.name,
        "file": str(component.file_path),
        "properties": properties,
    }


def _extract_connector_settings(component: GraphComponent) -> dict:
    """Extract connection configuration from a connector-settings component.

    Passwords are stored encrypted in <bns:encryptedValues>; they are detected
    and flagged but never included in output.
    """
    root = _read_xml(component.file_path)
    sub_type = root.attrib.get("subType", "")

    has_encrypted_password = any(
        "password" in ev.attrib.get("path", "").lower()
        and ev.attrib.get("isSet", "false").lower() == "true"
        for ev in _iter_descendants_by_local_name(root, "encryptedValue")
    )

    db_settings = _first_descendant_by_local_name(root, "DatabaseConnectionSettings")
    if db_settings is not None:
        return {
            "componentId": component.component_id,
            "name": component.name,
            "file": str(component.file_path),
            "subType": sub_type,
            "connectionType": "database",
            "driverClass": db_settings.attrib.get("className") or None,
            "host": db_settings.attrib.get("host") or None,
            "port": db_settings.attrib.get("port") or None,
            "dbName": db_settings.attrib.get("dbname") or None,
            "username": db_settings.attrib.get("username") or None,
            "connectionUrl": db_settings.attrib.get("urlFormat") or None,
            "hasEncryptedPassword": has_encrypted_password,
        }

    http_settings = _first_descendant_by_local_name(root, "HttpSettings")
    if http_settings is not None:
        return {
            "componentId": component.component_id,
            "name": component.name,
            "file": str(component.file_path),
            "subType": sub_type,
            "connectionType": "http",
            "url": http_settings.attrib.get("url") or None,
            "useBasicAuth": http_settings.attrib.get("useBasicAuth") or None,
            "hasEncryptedPassword": has_encrypted_password,
        }

    return {
        "componentId": component.component_id,
        "name": component.name,
        "file": str(component.file_path),
        "subType": sub_type,
        "connectionType": "unknown",
        "hasEncryptedPassword": has_encrypted_password,
    }


def _extract_crossref(component: GraphComponent) -> dict:
    """Extract all rows from a crossref lookup table component."""
    root = _read_xml(component.file_path)
    table = _first_descendant_by_local_name(root, "CrossRefTable")
    if table is None:
        return {
            "componentId": component.component_id,
            "name": component.name,
            "file": str(component.file_path),
            "columns": [],
            "rowCount": 0,
            "rows": [],
        }

    columns: list[str] = []
    headers = _first_descendant_by_local_name(table, "ColumnHeaders")
    if headers is not None:
        for header in headers:
            if _local_name(header.tag) == "columnHeader" and header.text:
                columns.append(header.text.strip())

    rows: list[dict] = []
    rows_node = _first_descendant_by_local_name(table, "Rows")
    if rows_node is not None:
        for row in rows_node:
            if _local_name(row.tag) != "row":
                continue
            row_data: dict = {}
            values_node = _first_descendant_by_local_name(row, "Values")
            if values_node is not None:
                for ref in values_node:
                    if _local_name(ref.tag) == "ref":
                        try:
                            col_idx = int(ref.attrib.get("colIdx", -1))
                        except ValueError:
                            continue
                        if 0 <= col_idx < len(columns):
                            row_data[columns[col_idx]] = ref.attrib.get("value")
            rows.append(row_data)

    return {
        "componentId": component.component_id,
        "name": component.name,
        "file": str(component.file_path),
        "columns": columns,
        "rowCount": len(rows),
        "rows": rows,
    }


def _build_compact_evidence(repo_root: Path, integration_name: str, raw_dir: Path) -> dict:
    graph_path = raw_dir / f"{_slugify(integration_name)}.componentGraph.json"
    if not graph_path.exists():
        raise FileNotFoundError(f"Graph index not found: {graph_path}")

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    components = _resolve_graph_components(repo_root, graph)

    root_component_file = Path(graph.get("rootComponentFile", ""))
    if not root_component_file.is_absolute():
        root_component_file = repo_root / root_component_file

    process_summary = _extract_process_summary(root_component_file)

    profiles = []
    maps = []
    connectors = []
    defined_process_properties = []
    connection_settings = []
    cross_reference_tables = []
    others = []
    warnings = process_summary.get("warnings", []).copy()

    for component in components:
        if component.component_id == graph.get("rootComponentId"):
            continue

        if not component.file_path.exists():
            warnings.append(
                f"Missing component file for {component.component_id}: {component.file_path}"
            )
            continue

        try:
            if component.component_type == "profile.json":
                profiles.append(_extract_profile_summary(component))
            elif component.component_type == "transform.map":
                maps.append(_extract_map_summary(component))
            elif component.component_type == "connector-action":
                connectors.append(_extract_connector_summary(component))
            elif component.component_type == "processproperty":
                defined_process_properties.append(_extract_defined_process_properties(component))
            elif component.component_type == "connector-settings":
                connection_settings.append(_extract_connector_settings(component))
            elif component.component_type == "crossref":
                cross_reference_tables.append(_extract_crossref(component))
            else:
                others.append(
                    {
                        "componentId": component.component_id,
                        "name": component.name,
                        "type": component.component_type,
                        "file": str(component.file_path),
                    }
                )
        except ET.ParseError as error:
            warnings.append(
                f"Failed to parse XML for component {component.component_id}: {error}"
            )

    # Build a lookup from (componentId, propertyKey) -> isSecret so that
    # document properties sourced from password-type defined process properties
    # can be flagged as secrets automatically.
    defined_prop_lookup: dict[tuple[str, str], bool] = {}
    for dpp_comp in defined_process_properties:
        for prop in dpp_comp.get("properties", []):
            key = (dpp_comp["componentId"], prop["key"])
            defined_prop_lookup[key] = prop["isSecret"]

    document_properties = _extract_document_properties(root_component_file, defined_prop_lookup)

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "integrationName": integration_name,
        "rawDirectory": str(raw_dir),
        "graph": {
            "rootComponentId": graph.get("rootComponentId"),
            "componentCount": graph.get("componentCount"),
            "edgeCount": graph.get("edgeCount"),
            "edges": graph.get("edges", []),
        },
        "process": process_summary,
        "dependencies": {
            "profiles": profiles,
            "maps": maps,
            "connectors": connectors,
            "definedProcessProperties": defined_process_properties,
            "connectionSettings": connection_settings,
            "crossReferenceTables": cross_reference_tables,
            "documentProperties": document_properties,
            "otherComponents": others,
        },
        "warnings": warnings,
    }


def _render_markdown(evidence: dict) -> str:
    process = evidence.get("process", {})
    dependencies = evidence.get("dependencies", {})
    profiles = dependencies.get("profiles", [])
    maps = dependencies.get("maps", [])
    connectors = dependencies.get("connectors", [])
    defined_process_properties = dependencies.get("definedProcessProperties", [])
    connection_settings = dependencies.get("connectionSettings", [])
    cross_reference_tables = dependencies.get("crossReferenceTables", [])
    document_properties = dependencies.get("documentProperties", {})

    lines = [
        f"# Compact Evidence - {evidence.get('integrationName')}",
        "",
        f"Generated: {evidence.get('generatedAt')}",
        f"Raw directory: {evidence.get('rawDirectory')}",
        "",
        "## Process",
        "",
        f"- Name: {process.get('name')}",
        f"- Component ID: {process.get('componentId')}",
        f"- Shape count: {process.get('shapeCount')}",
        "",
        "## Shapes",
        "",
    ]

    for shape in process.get("shapes", []):
        label = shape.get("label")
        label_suffix = f" ({label})" if label else ""
        lines.append(f"- {shape.get('shapeType')}: {shape.get('shapeName')}{label_suffix}")
        details = shape.get("details") or {}
        if details:
            details_json = json.dumps(details, ensure_ascii=True)
            lines.append(f"  - details: {details_json}")
        connections = shape.get("connections") or []
        if connections:
            targets = [item.get("toShape") for item in connections if item.get("toShape")]
            if targets:
                lines.append(f"  - routes to: {', '.join(targets)}")

    lines.extend(["", "## Profiles", ""])
    for profile in profiles:
        lines.append(
            f"- {profile.get('name')} ({profile.get('componentId')}) - fields: {profile.get('fieldCount')}"
        )
        for field in profile.get("fields", [])[:25]:
            lines.append(
                f"  - {field.get('path')} [{field.get('dataType')}] required={field.get('required')}"
            )

    lines.extend(["", "## Maps", ""])
    for map_item in maps:
        lines.append(
            f"- {map_item.get('name')} ({map_item.get('componentId')})"
        )
        lines.append(
            f"  - fromProfile: {map_item.get('fromProfile')} -> toProfile: {map_item.get('toProfile')}"
        )
        lines.append(f"  - mapping count: {len(map_item.get('mappings', []))}")
        for script in map_item.get("scripts", []):
            lines.append(f"  - script ({script.get('name')}):")
            script_text = script.get("script")
            if script_text:
                for row in script_text.splitlines():
                    lines.append(f"    {row}")

    lines.extend(["", "## Connectors", ""])
    for connector in connectors:
        lines.append(
            f"- {connector.get('name')} ({connector.get('componentId')}): {json.dumps(connector.get('operation'), ensure_ascii=True)}"
        )

    # Defined Process Properties
    if defined_process_properties:
        lines.extend(["", "## Defined Process Properties", ""])
        for group in defined_process_properties:
            lines.append(f"### {group.get('name')} ({group.get('componentId')})")
            lines.append("")
            lines.append("| Property | Type | Secret | Default Value | Help |")
            lines.append("|---|---|---|---|---|")
            for prop in group.get("properties", []):
                is_secret = prop.get("isSecret", False)
                default = "[secret]" if is_secret else (prop.get("defaultValue") or "")
                help_text = (prop.get("helpText") or "").replace("|", "/")
                lines.append(
                    f"| {prop.get('label')} | {prop.get('type')} | {is_secret} | {default} | {help_text} |"
                )
            lines.append("")

    # Document Properties (DPPs and DDPs)
    dpps = document_properties.get("dynamicProcessProperties", [])
    ddps = document_properties.get("dynamicDocumentProperties", [])

    if dpps or ddps:
        lines.extend(["## Document Properties", ""])

    if dpps:
        lines.extend(["### Dynamic Process Properties (DPP — process-scoped)", ""])
        lines.append("| Name | Source Type | Source Detail | Secret |")
        lines.append("|---|---|---|---|")
        for dpp in dpps:
            detail = (dpp.get("sourceDetail") or "").replace("|", "/")
            lines.append(
                f"| {dpp.get('name')} | {dpp.get('sourceType')} | {detail} | {dpp.get('isSecret')} |"
            )
        lines.append("")

    if ddps:
        lines.extend(["### Dynamic Document Properties (DDP — document-scoped)", ""])
        lines.append("| Name | Source Type | Source Detail | Secret |")
        lines.append("|---|---|---|---|")
        for ddp in ddps:
            detail = (ddp.get("sourceDetail") or "").replace("|", "/")
            lines.append(
                f"| {ddp.get('name')} | {ddp.get('sourceType')} | {detail} | {ddp.get('isSecret')} |"
            )
        lines.append("")

    # Connection Settings
    if connection_settings:
        lines.extend(["## Connection Settings", ""])
        for conn in connection_settings:
            lines.append(f"### {conn.get('name')} ({conn.get('componentId')})")
            lines.append("")
            conn_type = conn.get("connectionType", "unknown")
            lines.append(f"- Connection type: {conn_type}")
            if conn_type == "database":
                lines.append(f"- Driver class: {conn.get('driverClass') or 'n/a'}")
                lines.append(f"- Host: {conn.get('host') or 'n/a'}")
                lines.append(f"- Port: {conn.get('port') or 'n/a'}")
                lines.append(f"- Connection URL: {conn.get('connectionUrl') or 'n/a'}")
                lines.append(f"- Username: {conn.get('username') or 'n/a'}")
            elif conn_type == "http":
                lines.append(f"- URL: {conn.get('url') or 'n/a'}")
                lines.append(f"- Basic auth: {conn.get('useBasicAuth') or 'n/a'}")
            lines.append(f"- Has encrypted password: {conn.get('hasEncryptedPassword')}")
            lines.append("")

    # Cross-Reference Tables
    if cross_reference_tables:
        lines.extend(["## Cross-Reference Tables", ""])
        for table in cross_reference_tables:
            columns = table.get("columns", [])
            lines.append(f"### {table.get('name')} ({table.get('componentId')})")
            lines.append("")
            lines.append(f"- Columns: {', '.join(columns)}")
            lines.append(f"- Row count: {table.get('rowCount')}")
            rows = table.get("rows", [])
            if rows and columns:
                lines.append("")
                lines.append("| " + " | ".join(columns) + " |")
                lines.append("|" + "|".join(["---"] * len(columns)) + "|")
                for row in rows:
                    cells = [str(row.get(col, "")) for col in columns]
                    lines.append("| " + " | ".join(cells) + " |")
            lines.append("")

    warnings = evidence.get("warnings", [])
    lines.extend(["## Warnings", ""])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate compact evidence pack from downloaded Boomi XML components"
    )
    parser.add_argument(
        "--integration-name",
        required=True,
        help="Boomi integration/component name",
    )
    parser.add_argument(
        "--raw-dir",
        default=None,
        help="Raw XML directory (default: boomi-integrations/<integrationName>/raw)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: boomi-integrations/<integrationName>/analysis)",
    )
    parser.add_argument(
        "--json-file",
        default="compactEvidence.json",
        help="Output JSON filename (default: compactEvidence.json)",
    )
    parser.add_argument(
        "--markdown-file",
        default="compactEvidence.md",
        help="Output Markdown filename (default: compactEvidence.md)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = _find_repo_root(Path(__file__).resolve())
    safe_name = _slugify(args.integration_name)

    raw_dir = Path(args.raw_dir) if args.raw_dir else repo_root / "boomi-integrations" / safe_name / "raw"
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else repo_root / "boomi-integrations" / safe_name / "analysis"
    )

    if not raw_dir.exists():
        print(f"Raw directory does not exist: {raw_dir}")
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    evidence = _build_compact_evidence(repo_root=repo_root, integration_name=args.integration_name, raw_dir=raw_dir)

    json_path = output_dir / args.json_file
    markdown_path = output_dir / args.markdown_file

    json_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    markdown_path.write_text(_render_markdown(evidence), encoding="utf-8")

    print("Compact evidence generated.")
    print(f"JSON: {json_path}")
    print(f"Markdown: {markdown_path}")
    print(f"Warnings: {len(evidence.get('warnings', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
