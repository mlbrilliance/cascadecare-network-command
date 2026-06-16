"""Static, credential-free validators for a UiPath Maestro Case caseplan.

These run offline against a caseplan directory (caseplan.json + the compiled
caseplan.json.bpmn) and are safe in CI — no UiPath login. The rules generalize the
deterministic canvas-round-trip drops that bite Maestro Case authors; rule ids map
to knowledge-layer entries so `maestro-case explain <rule>` gives the full recipe.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

# Allowed V20 caseplan expression prefixes. Seeded from the documented conventions
# and reconciled against the prefixes that actually appear in live caseplans
# (=jsonString is real and was missing from the docs). =datafabric is a valid
# family even though the =datafabric.qem: spawn form fails at runtime — that
# runtime trap is caught by check_spawn_fanout, not by a prefix rule.
ALLOWED_EXPR_PREFIXES: tuple[str, ...] = (
    "=vars",
    "=js:",
    "=metadata",
    "=bindings",
    "=datafabric",
    "=response",
    "=string",
    "=jsonString",
)

_LEGACY_EXPR = re.compile(r"^\$\w")
_LOOKS_LIKE_EXPR = re.compile(r"^=[A-Za-z]")


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    location: str | None = None
    entry_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
            "entry_id": self.entry_id,
        }


def _walk_strings(node: object, path: str = "$"):
    """Yield (json_path, string_value) for every string leaf in the structure."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _walk_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk_strings(value, f"{path}[{index}]")


def _walk_output_lists(node: object, path: str = "$"):
    """Yield (json_path, outputs_list) for every list found under an 'outputs' key."""
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}"
            if key == "outputs" and isinstance(value, list):
                yield child_path, value
            yield from _walk_output_lists(value, child_path)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk_output_lists(value, f"{path}[{index}]")


def _check_bpmn(caseplan_path: Path, bpmn_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not bpmn_path.is_file():
        findings.append(
            Finding(
                "MC-NO-BPMN",
                "medium",
                "No compiled caseplan.json.bpmn next to caseplan.json — the engine "
                "runs the compiled .bpmn, so edits may be inert until the canvas "
                "regenerates it. Cannot verify compiled state.",
                location=str(bpmn_path),
                entry_id="MC-BPMN-STALE",
            )
        )
        return findings
    if caseplan_path.stat().st_mtime > bpmn_path.stat().st_mtime:
        findings.append(
            Finding(
                "MC-BPMN-STALE",
                "high",
                "caseplan.json is newer than its compiled caseplan.json.bpmn — edits "
                "are likely inert at runtime. Regenerate the .bpmn via the Studio Web "
                "canvas before pack/deploy.",
                location=str(bpmn_path),
                entry_id="MC-BPMN-STALE",
            )
        )
    if bpmn_path.read_text(encoding="utf-8").count("<bpmn:startEvent") == 0:
        findings.append(
            Finding(
                "MC-NO-START-EVENT",
                "high",
                "Compiled .bpmn has no <bpmn:startEvent> — the case will not auto-walk "
                "from its first stage. The canvas commonly drops the mainline start "
                "event on round-trip; restore it before deploy.",
                location=str(bpmn_path),
                entry_id="MC-BPMN-STALE",
            )
        )
    return findings


def _check_outputs(caseplan: object) -> list[Finding]:
    findings: list[Finding] = []
    for path, outputs in _walk_output_lists(caseplan):
        seen: set[str] = set()
        for output in outputs:
            if not isinstance(output, dict):
                continue
            var = output.get("var")
            if isinstance(var, str) and var:
                if var in seen:
                    findings.append(
                        Finding(
                            "MC-DUP-OUTPUT-VAR",
                            "high",
                            f"Duplicate output variable {var!r} on one task — V20 rejects "
                            f"duplicate output vars (the canvas auto-adds a dup 'error' "
                            f"output on round-trip). De-duplicate or suffix from 2.",
                            location=path,
                        )
                    )
                seen.add(var)
    return findings


# Output/variable binding keys hold =<FieldName> references (e.g. source="=Error",
# target="=reviewerId"), not value expressions — exempt them from the prefix rule.
_BINDING_KEYS = (".source", ".target")


def _check_expressions(caseplan: object) -> list[Finding]:
    findings: list[Finding] = []
    for path, value in _walk_strings(caseplan):
        if _LEGACY_EXPR.match(value):
            findings.append(
                Finding(
                    "MC-LEGACY-EXPR",
                    "medium",
                    f"Legacy $-prefixed expression {value!r} — V20 uses =-prefixed "
                    f"expressions (e.g. =js:vars.x), not $vars.x.",
                    location=path,
                )
            )
        elif path.endswith(_BINDING_KEYS):
            continue
        elif _LOOKS_LIKE_EXPR.match(value) and not value.startswith(ALLOWED_EXPR_PREFIXES):
            findings.append(
                Finding(
                    "MC-BAD-EXPR-PREFIX",
                    "medium",
                    f"Expression {value!r} does not start with an allowed V20 prefix "
                    f"({', '.join(ALLOWED_EXPR_PREFIXES)}).",
                    location=path,
                )
            )
    return findings


def _load_caseplan(caseplan_dir: Path | str) -> tuple[object, Path]:
    directory = Path(caseplan_dir)
    caseplan_path = directory / "caseplan.json"
    if not caseplan_path.is_file():
        raise FileNotFoundError(f"no caseplan.json in {directory}")
    return json.loads(caseplan_path.read_text(encoding="utf-8")), caseplan_path


def lint_caseplan(caseplan_dir: Path | str) -> list[Finding]:
    """Lint a caseplan directory. Raises FileNotFoundError if caseplan.json is absent."""
    caseplan, caseplan_path = _load_caseplan(caseplan_dir)
    bpmn_path = caseplan_path.parent / "caseplan.json.bpmn"
    findings: list[Finding] = []
    findings.extend(_check_bpmn(caseplan_path, bpmn_path))
    findings.extend(_check_outputs(caseplan))
    findings.extend(_check_expressions(caseplan))
    return findings


def check_spawn_fanout(caseplan_dir: Path | str) -> list[Finding]:
    """Flag =datafabric.qem expressions in spawn inputs — they fail at runtime (400300)."""
    caseplan, _ = _load_caseplan(caseplan_dir)
    findings: list[Finding] = []
    for path, value in _walk_strings(caseplan):
        if "=datafabric.qem" in value:
            findings.append(
                Finding(
                    "MC-SPAWN-QEM-400300",
                    "high",
                    f"=datafabric.qem expression {value!r} fails at runtime in spawn "
                    f"inputs (400300, 'Syntax error at index 4'). Resolve the value at "
                    f"authoring time and pass a literal slug instead.",
                    location=path,
                    entry_id="MC-SPAWN-QEM-400300",
                )
            )
    return findings


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:] if p)


def _extract_field_names(spec: object) -> list[str]:
    fields = spec.get("fields", []) if isinstance(spec, dict) else spec
    names: list[str] = []
    if isinstance(fields, list):
        for field in fields:
            if isinstance(field, str):
                names.append(field)
            elif isinstance(field, dict) and isinstance(field.get("name"), str):
                names.append(field["name"])
    return names


def validate_df_entity(spec_path: Path | str) -> list[Finding]:
    """Lint a Data Fabric entity/field spec for silent-drop and reserved-name traps."""
    path = Path(spec_path)
    if not path.is_file():
        raise FileNotFoundError(f"no spec file at {path}")
    spec = json.loads(path.read_text(encoding="utf-8"))
    findings: list[Finding] = []
    for name in _extract_field_names(spec):
        if name == "id":
            findings.append(
                Finding(
                    "DF-RESERVED-ID",
                    "medium",
                    "Field 'id' collides with the system Id primary key and is rejected; "
                    "use 'slug' (or another business-key name) instead.",
                    location=name,
                    entry_id="DF-RESERVED-ID",
                )
            )
        if "_" in name:
            findings.append(
                Finding(
                    "DF-UNDERSCORE-DROP",
                    "high",
                    f"Field {name!r} contains an underscore and is silently dropped on "
                    f"insert (no error surfaced). Use {_to_camel(name)!r} instead.",
                    location=name,
                    entry_id="DF-UNDERSCORE-DROP",
                )
            )
    return findings
