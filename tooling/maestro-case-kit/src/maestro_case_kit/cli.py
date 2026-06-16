"""`maestro-case` CLI — agent-native, offline access to the knowledge layer.

v1 surface: `explain`. Validators (`lint`, `check-spawn`, `check-df`) attach to the
same parser in later slices. Every subcommand supports ``--json`` for agent/CI use
and exits non-zero when it has a finding to report.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import IO

from . import __version__, knowledge


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
