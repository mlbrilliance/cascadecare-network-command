"""Agent-native tool registry — one definition of the tool surface, shared by the
CLI and the MCP server. Each tool has a JSON input schema and a handler that
returns a list of plain dicts (knowledge entries or lint findings).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from . import knowledge, validators


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict
    handler: Callable[[dict], list[dict]]


def _explain(args: dict) -> list[dict]:
    hits = knowledge.find(str(args["query"]), include_resolved=bool(args.get("include_resolved", False)))
    return [e.to_dict() for e in hits]


def _lint(args: dict) -> list[dict]:
    return [f.to_dict() for f in validators.lint_caseplan(str(args["caseplan_dir"]))]


def _check_spawn(args: dict) -> list[dict]:
    return [f.to_dict() for f in validators.check_spawn_fanout(str(args["caseplan_dir"]))]


def _check_df(args: dict) -> list[dict]:
    return [f.to_dict() for f in validators.validate_df_entity(str(args["spec_path"]))]


def _caseplan_dir_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "caseplan_dir": {
                "type": "string",
                "description": "Path to a directory containing caseplan.json.",
            }
        },
        "required": ["caseplan_dir"],
    }


TOOLS: list[Tool] = [
    Tool(
        "maestro_case_explain",
        "Explain a UiPath Maestro Case error code or footgun from the offline, "
        "version-stamped knowledge layer. Accepts an error code/signature or a keyword.",
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Error code/signature or keyword."},
                "include_resolved": {
                    "type": "boolean",
                    "description": "Include entries marked resolved in a later platform version.",
                },
            },
            "required": ["query"],
        },
        _explain,
    ),
    Tool(
        "maestro_case_lint",
        "Statically lint a caseplan directory for known footguns (stale .bpmn, missing "
        "start event, duplicate output vars, bad expression prefixes). Offline, no login.",
        _caseplan_dir_schema(),
        _lint,
    ),
    Tool(
        "maestro_case_check_spawn",
        "Flag =datafabric.qem expressions in spawn inputs, which fail at runtime (400300).",
        _caseplan_dir_schema(),
        _check_spawn,
    ),
    Tool(
        "maestro_case_check_df",
        "Lint a Data Fabric entity/field spec for the underscore silent-drop and the "
        "reserved 'id' field traps.",
        {
            "type": "object",
            "properties": {
                "spec_path": {"type": "string", "description": "Path to a JSON entity spec."}
            },
            "required": ["spec_path"],
        },
        _check_df,
    ),
]

_BY_NAME: dict[str, Tool] = {t.name: t for t in TOOLS}


def get_tool(name: str) -> Tool:
    return _BY_NAME[name]


def run_tool(name: str, args: dict) -> list[dict]:
    return get_tool(name).handler(args)
