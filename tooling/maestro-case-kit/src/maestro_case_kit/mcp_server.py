"""A dependency-free MCP server over stdio (newline-delimited JSON-RPC 2.0).

Implements the three methods an agent host needs — initialize, tools/list,
tools/call — over the shared tool registry. No third-party MCP SDK required, so
the server runs anywhere Python does and stays testable in CI. Register with a
Claude Code / OpenClaw host as: `maestro-case-mcp` (stdio).
"""

from __future__ import annotations

import json
import sys
from typing import IO

from . import __version__, tools

PROTOCOL_VERSION = "2025-06-18"
SERVER_NAME = "maestro-case-kit"


def _result(request_id: object, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: object, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_request(request: dict) -> dict | None:
    """Dispatch one JSON-RPC request. Returns None for notifications (no id)."""
    method = request.get("method")
    request_id = request.get("id")
    if request_id is None:
        return None  # notification — no response

    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": __version__},
            },
        )

    if method == "tools/list":
        listed = [
            {"name": t.name, "description": t.description, "inputSchema": t.input_schema}
            for t in tools.TOOLS
        ]
        return _result(request_id, {"tools": listed})

    if method == "tools/call":
        params = request.get("params") or {}
        name = params.get("name", "")
        arguments = params.get("arguments") or {}
        try:
            output = tools.run_tool(name, arguments)
            return _result(
                request_id,
                {"content": [{"type": "text", "text": json.dumps(output, indent=2)}], "isError": False},
            )
        except Exception as exc:  # tool-level failure -> isError, not a protocol error
            return _result(
                request_id,
                {"content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True},
            )

    return _error(request_id, -32601, f"method not found: {method}")


def serve(stdin: IO[str], stdout: IO[str]) -> None:
    """Read newline-delimited JSON-RPC from stdin; write responses to stdout."""
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle_request(request)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()


def main() -> int:
    serve(sys.stdin, sys.stdout)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
