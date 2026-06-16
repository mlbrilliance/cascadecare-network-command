"""Tests for the dependency-free MCP stdio server (JSON-RPC dispatch)."""

from __future__ import annotations

import io
import json

from maestro_case_kit import mcp_server


def _req(method: str, params: dict | None = None, id_: int | None = 1) -> dict:
    msg: dict = {"jsonrpc": "2.0", "method": method}
    if id_ is not None:
        msg["id"] = id_
    if params is not None:
        msg["params"] = params
    return msg


def test_initialize_returns_server_info() -> None:
    resp = mcp_server.handle_request(_req("initialize", {"protocolVersion": "2025-06-18"}))
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"]
    assert "tools" in resp["result"]["capabilities"]


def test_tools_list_advertises_registry() -> None:
    resp = mcp_server.handle_request(_req("tools/list"))
    assert resp is not None
    listed = {t["name"] for t in resp["result"]["tools"]}
    assert "maestro_case_explain" in listed
    for t in resp["result"]["tools"]:
        assert "inputSchema" in t and "description" in t


def test_tools_call_explain() -> None:
    resp = mcp_server.handle_request(
        _req("tools/call", {"name": "maestro_case_explain", "arguments": {"query": "160009"}})
    )
    assert resp is not None
    result = resp["result"]
    assert result.get("isError") in (False, None)
    text = result["content"][0]["text"]
    payload = json.loads(text)
    assert any(r["id"] == "HITL-GATE-DELETE-160009" for r in payload)


def test_tools_call_unknown_tool_is_iserror() -> None:
    resp = mcp_server.handle_request(
        _req("tools/call", {"name": "nope", "arguments": {}})
    )
    assert resp is not None
    assert resp["result"]["isError"] is True


def test_unknown_method_is_jsonrpc_error() -> None:
    resp = mcp_server.handle_request(_req("frobnicate"))
    assert resp is not None
    assert resp["error"]["code"] == -32601


def test_notification_returns_no_response() -> None:
    resp = mcp_server.handle_request(_req("notifications/initialized", id_=None))
    assert resp is None


def test_serve_processes_a_line_stream() -> None:
    stdin = io.StringIO(json.dumps(_req("tools/list")) + "\n")
    stdout = io.StringIO()
    mcp_server.serve(stdin, stdout)
    out = stdout.getvalue().strip().splitlines()
    assert out
    resp = json.loads(out[0])
    assert resp["id"] == 1 and "result" in resp
