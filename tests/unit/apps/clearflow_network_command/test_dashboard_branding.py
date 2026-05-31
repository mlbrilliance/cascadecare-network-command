"""Offline branding gate for the ClearFlow Network Command UiPath App.

Asserts apps/clearflow-network-command/app.json carries an explicit ClearFlow
brand definition (palette → hex for the semantic tokens the components already
use, a logo asset reference, and typography) and that the screen spec is
IP-safe (zero forbidden real-company tokens). Pure offline file read — no tenant.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
APP_JSON = REPO_ROOT / "apps" / "clearflow-network-command" / "app.json"

# Semantic color tokens already referenced by app.json components
# (header badge, timeline active/inactive, agent statusColorMap, button variants).
REQUIRED_PALETTE_TOKENS = ("accent", "muted", "success", "warning", "danger")

HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

# IP-safety: forbidden real-company tokens (see CLAUDE.md / constitution §II).
FORBIDDEN_TOKENS = (
    "zelis", "aetna", "cigna", "unitedhealth", "bcbs", "hartley", "rivet",
    "zipp", "zapp", "change healthcare", "optum", "cotiviti", "wex",
)


def _app() -> dict:
    return json.loads(APP_JSON.read_text(encoding="utf-8"))


def test_app_json_is_valid_json() -> None:
    _app()  # raises on malformed JSON


def test_theme_block_exists() -> None:
    assert "theme" in _app(), "app.json must define a top-level 'theme' block"


def test_palette_defines_hex_for_semantic_tokens() -> None:
    palette = _app()["theme"].get("palette", {})
    for token in REQUIRED_PALETTE_TOKENS:
        assert token in palette, f"theme.palette missing token {token!r}"
        assert HEX.match(palette[token]), f"theme.palette.{token} must be a #RRGGBB hex, got {palette[token]!r}"


def test_logo_reference_present() -> None:
    logo = _app()["theme"].get("logo")
    assert isinstance(logo, str) and logo.strip(), "theme.logo must be a non-empty asset reference"


def test_typography_font_family_present() -> None:
    typo = _app()["theme"].get("typography", {})
    assert isinstance(typo.get("fontFamily"), str) and typo["fontFamily"].strip(), (
        "theme.typography.fontFamily must be a non-empty string"
    )


def test_brand_name_is_clearflow() -> None:
    assert _app()["theme"].get("brandName") == "ClearFlow Network Command", (
        "theme.brandName must be the committed fictional brand"
    )


def test_app_json_is_ip_safe() -> None:
    text = APP_JSON.read_text(encoding="utf-8").lower()
    hits = [t for t in FORBIDDEN_TOKENS if t in text]
    assert not hits, f"app.json contains forbidden real-company tokens: {hits}"
