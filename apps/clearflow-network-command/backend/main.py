"""UiPath Coded App entry point for ClearFlow Network Command dashboard.

SPEC: register_handlers
Purpose: Wire Coded App HTTP handlers for GET /dashboard and POST /override
Inputs: UiPath Coded App runtime (invokes module on deploy)
Outputs: none (side effect: handlers registered with the UiPath App runtime)
Edge cases:
  - invalid OverrideAction value -> 422 (Pydantic validation raises automatically)
  - missing request body on POST -> 422
  - UIPATH_LIVE=true -> 501 Not Implemented (live reads not wired until Slice 014)
Side effects: none at import time; handlers registered when UiPath invokes start()
Test: test_dashboard.py covers payload shape; handler registration tested at
      Slice 014 deploy via uip coded-app invoke smoke test
"""
from __future__ import annotations

import json
import os

from dashboard import build_payload
from models import DashboardPayload, OverrideAction


def get_dashboard() -> dict:
    """GET /dashboard — returns the full DashboardPayload as a dict."""
    try:
        payload: DashboardPayload = build_payload()
        return payload.model_dump()
    except NotImplementedError:
        return {"error": "Live reads not yet wired. Unset UIPATH_LIVE.", "status": 501}


def post_override(body: dict) -> dict:
    """POST /override — accepts {action: OverrideAction} and acknowledges.

    Stub implementation: validates the action enum and echoes acceptance.
    Full wiring (actually firing the Maestro trigger) is done in Slice 014
    via the uipath SDK's process invocation API.
    """
    raw_action = body.get("action")
    if raw_action is None:
        return {"error": "Missing 'action' field", "status": 422}
    try:
        action = OverrideAction(raw_action)
    except ValueError:
        valid = [a.value for a in OverrideAction]
        return {"error": f"Invalid action '{raw_action}'. Valid: {valid}", "status": 422}

    return {"accepted": True, "action": action.value}


def handler(event: dict, context: object | None = None) -> dict:
    """UiPath Coded App universal handler dispatching by HTTP method + path.

    UiPath invokes this function with an event dict containing:
      event["httpMethod"]: "GET" | "POST"
      event["path"]: "/dashboard" | "/override"
      event["body"]: JSON string (POST only)
    """
    method = event.get("httpMethod", "GET").upper()
    path = event.get("path", "/dashboard")

    if method == "GET" and path == "/dashboard":
        return get_dashboard()

    if method == "POST" and path == "/override":
        raw_body = event.get("body", "{}")
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        return post_override(body)

    return {"error": f"Unknown route {method} {path}", "status": 404}
