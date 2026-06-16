"""Tests for the `maestro-case explain` CLI surface (R2, R7)."""

from __future__ import annotations

import json

from maestro_case_kit import cli


def test_explain_known_code_exits_zero(capsys) -> None:
    rc = cli.main(["explain", "400300"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "400300" in out
    assert "qem" in out.lower()


def test_explain_json_is_valid_and_structured(capsys) -> None:
    rc = cli.main(["explain", "160009", "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert isinstance(payload, list) and payload
    first = payload[0]
    assert first["id"] == "HITL-GATE-DELETE-160009"
    for key in ("id", "title", "cause", "fix", "error_signatures", "proven_on"):
        assert key in first


def test_explain_unknown_exits_nonzero(capsys) -> None:
    rc = cli.main(["explain", "no-such-signature-xyz"])
    err = capsys.readouterr().err
    assert rc == 1
    assert err.strip()


def test_explain_unknown_json_is_empty_list_and_nonzero(capsys) -> None:
    rc = cli.main(["explain", "no-such-signature-xyz", "--json"])
    out = capsys.readouterr().out
    assert rc == 1
    assert json.loads(out) == []


def test_explain_keyword_fallback(capsys) -> None:
    rc = cli.main(["explain", "underscore"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "DF-UNDERSCORE-DROP" in out


def test_no_subcommand_shows_help_nonzero(capsys) -> None:
    rc = cli.main([])
    assert rc != 0
