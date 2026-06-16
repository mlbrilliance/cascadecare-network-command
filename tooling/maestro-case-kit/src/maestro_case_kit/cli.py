"""`maestro-case` CLI — agent-native, offline access to the knowledge layer.

v1 surface: `explain`. Validators (`lint`, `check-spawn`, `check-df`) attach to the
same parser in later slices. Every subcommand supports ``--json`` for agent/CI use
and exits non-zero when it has a finding to report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import IO

from . import __version__, contribution, knowledge, validators


def _print_human(entries: list[knowledge.KnowledgeEntry], stream: IO[str]) -> None:
    for e in entries:
        signals = ", ".join(e.error_signatures) or "(no error code — silent behavior)"
        resolved = f"  resolved_in: {e.resolved_in}" if e.resolved_in else ""
        print(f"[{e.id}] {e.title}", file=stream)
        print(f"  surface:   {e.surface}", file=stream)
        print(f"  signals:   {signals}", file=stream)
        print(f"  cause:     {e.cause}", file=stream)
        print(f"  fix:       {e.fix}", file=stream)
        print(f"  proven_on: {e.proven_on}{resolved}", file=stream)
        if e.references:
            print(f"  refs:      {', '.join(e.references)}", file=stream)
        print("", file=stream)


def _cmd_explain(args: argparse.Namespace) -> int:
    hits = knowledge.find(args.query, include_resolved=args.include_resolved)
    if args.json:
        print(json.dumps([e.to_dict() for e in hits], indent=2))
        return 0 if hits else 1
    if not hits:
        print(
            f"No known Maestro Case footgun matches {args.query!r}. "
            f"Try an error code (e.g. 400300) or a keyword (e.g. underscore, gate, deploy).",
            file=sys.stderr,
        )
        return 1
    _print_human(hits, sys.stdout)
    return 0


def _emit_findings(findings: list[validators.Finding], as_json: bool, ok_label: str) -> int:
    if as_json:
        print(json.dumps([f.to_dict() for f in findings], indent=2))
        return 1 if findings else 0
    if not findings:
        print(f"OK — {ok_label}")
        return 0
    for f in findings:
        suffix = f"  (explain: {f.entry_id})" if f.entry_id else ""
        where = f"  @ {f.location}" if f.location else ""
        print(f"[{f.severity.upper()}] {f.rule_id}: {f.message}{where}{suffix}")
    print(f"\n{len(findings)} finding(s).")
    return 1


def _cmd_lint(args: argparse.Namespace) -> int:
    findings = validators.lint_caseplan(args.caseplan_dir)
    return _emit_findings(findings, args.json, f"no Maestro Case footguns in {args.caseplan_dir}")


def _cmd_check_spawn(args: argparse.Namespace) -> int:
    findings = validators.check_spawn_fanout(args.caseplan_dir)
    return _emit_findings(findings, args.json, f"no qem spawn-fanout issues in {args.caseplan_dir}")


def _cmd_check_df(args: argparse.Namespace) -> int:
    findings = validators.validate_df_entity(args.spec)
    return _emit_findings(findings, args.json, f"no Data Fabric field-name traps in {args.spec}")


def _cmd_validate_knowledge(args: argparse.Namespace) -> int:
    denylist: list[str] = []
    if args.denylist_file:
        for line in Path(args.denylist_file).read_text(encoding="utf-8").splitlines():
            token = line.strip()
            if token and not token.startswith("#"):
                denylist.append(token)
    data: object = args.file or {"entries": [e.to_dict() for e in knowledge.load_entries()]}
    problems = contribution.validate_knowledge(data, denylist)
    if args.json:
        print(json.dumps(problems, indent=2))
        return 1 if problems else 0
    if not problems:
        print("OK — knowledge passes the contribution gate.")
        return 0
    for problem in problems:
        print(f"[GATE] {problem}")
    print(f"\n{len(problems)} problem(s).")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maestro-case",
        description="Knowledge + offline validators for UiPath Maestro Case footguns.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")

    explain = sub.add_parser(
        "explain",
        help="Explain a UiPath Maestro Case error code or footgun from the knowledge layer.",
    )
    explain.add_argument(
        "query",
        help="An error code/signature (e.g. 400300, 160009) or a keyword (e.g. underscore, deploy).",
    )
    explain.add_argument("--json", action="store_true", help="Emit structured JSON.")
    explain.add_argument(
        "--include-resolved",
        action="store_true",
        help="Include entries marked resolved in a later platform version.",
    )
    explain.set_defaults(func=_cmd_explain)

    lint = sub.add_parser(
        "lint",
        help="Statically lint a caseplan directory for known footguns (offline, no login).",
    )
    lint.add_argument(
        "caseplan_dir",
        help="Path to a directory containing caseplan.json (and ideally caseplan.json.bpmn).",
    )
    lint.add_argument("--json", action="store_true", help="Emit structured JSON findings.")
    lint.set_defaults(func=_cmd_lint)

    check_spawn = sub.add_parser(
        "check-spawn",
        help="Flag =datafabric.qem expressions in spawn inputs (fail at runtime, 400300).",
    )
    check_spawn.add_argument("caseplan_dir", help="Path to a directory containing caseplan.json.")
    check_spawn.add_argument("--json", action="store_true", help="Emit structured JSON findings.")
    check_spawn.set_defaults(func=_cmd_check_spawn)

    check_df = sub.add_parser(
        "check-df",
        help="Lint a Data Fabric entity/field spec for silent-drop and reserved-name traps.",
    )
    check_df.add_argument("spec", help="Path to a JSON entity spec ({\"fields\": [...]}).")
    check_df.add_argument("--json", action="store_true", help="Emit structured JSON findings.")
    check_df.set_defaults(func=_cmd_check_df)

    vk = sub.add_parser(
        "validate-knowledge",
        help="Validate a knowledge file against the schema + an optional IP-safety denylist.",
    )
    vk.add_argument("--file", help="Path to a knowledge JSON file (default: the bundled layer).")
    vk.add_argument(
        "--denylist-file",
        help="Optional newline-delimited file of forbidden tokens (# comments allowed).",
    )
    vk.add_argument("--json", action="store_true", help="Emit structured JSON problems.")
    vk.set_defaults(func=_cmd_validate_knowledge)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help(sys.stderr)
        return 2
    func = args.func
    assert callable(func)
    return int(func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
