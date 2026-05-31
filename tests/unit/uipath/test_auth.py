"""Unit tests for UiPath OAuth2 client-credentials authentication.

All tests use a patched httpx layer — no real UiPath tenant is contacted.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from cascadecare.uipath.auth import UiPathCredentials, get_access_token

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

UIPATH_URL = "https://staging.uipath.com/hackathon26_042/DefaultTenant"


def _make_credentials() -> UiPathCredentials:
    return UiPathCredentials(
        base_url="https://staging.uipath.com",
        org="hackathon26_042",
        tenant="DefaultTenant",
        app_id="app-id-123",
        app_secret="app-secret-456",
    )


def _patch_httpx_client(response: MagicMock) -> tuple[MagicMock, MagicMock]:
    """Build a MagicMock that replaces ``httpx.Client`` as a context manager.

    Returns ``(factory, client)`` where ``factory`` stands in for
    ``httpx.Client`` and ``client`` is the inner mock whose ``.post``
    always yields ``response`` (for assertions on the request).
    """
    client = MagicMock()
    client.post.return_value = response
    ctx = MagicMock()
    ctx.__enter__.return_value = client
    ctx.__exit__.return_value = False
    factory = MagicMock(return_value=ctx)
    return factory, client


# ---------------------------------------------------------------------------
# Tests — UiPathCredentials URL derivation
# ---------------------------------------------------------------------------


class TestCredentialUrls:
    def test_tenant_url_is_composed(self) -> None:
        creds = _make_credentials()
        assert creds.tenant_url == "https://staging.uipath.com/hackathon26_042/DefaultTenant"

    def test_identity_url_is_composed(self) -> None:
        creds = _make_credentials()
        assert creds.identity_url == "https://staging.uipath.com/identity_/connect/token"


# ---------------------------------------------------------------------------
# Tests — from_env
# ---------------------------------------------------------------------------


class TestFromEnv:
    def test_splits_org_and_tenant_from_uipath_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("UIPATH_APP_ID", raising=False)
        monkeypatch.delenv("UIPATH_APP_SECRET", raising=False)
        monkeypatch.setenv("UIPATH_URL", UIPATH_URL)

        creds = UiPathCredentials.from_env()

        assert creds.base_url == "https://staging.uipath.com"
        assert creds.org == "hackathon26_042"
        assert creds.tenant == "DefaultTenant"
        assert creds.tenant_url == UIPATH_URL
        assert creds.identity_url == "https://staging.uipath.com/identity_/connect/token"

    def test_raises_value_error_when_url_unset(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("UIPATH_URL", raising=False)
        missing_env = tmp_path / "does-not-exist.env"

        with pytest.raises(ValueError, match="UIPATH_URL is not set"):
            UiPathCredentials.from_env(env_path=missing_env)

    def test_reads_app_id_and_secret_from_env_file(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("UIPATH_URL", raising=False)
        monkeypatch.delenv("UIPATH_APP_ID", raising=False)
        monkeypatch.delenv("UIPATH_APP_SECRET", raising=False)

        env_file = tmp_path / ".env"
        env_file.write_text(
            "# UiPath staging credentials\n"
            f"UIPATH_URL={UIPATH_URL}\n"
            "\n"
            "UIPATH_APP_ID=file-app-id\n"
            "UIPATH_APP_SECRET=file-app-secret\n",
            encoding="utf-8",
        )

        creds = UiPathCredentials.from_env(env_path=env_file)

        assert creds.app_id == "file-app-id"
        assert creds.app_secret == "file-app-secret"
        assert creds.org == "hackathon26_042"
        assert creds.tenant == "DefaultTenant"

    def test_os_environ_takes_precedence_over_env_file(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        # setdefault semantics: values already in os.environ win.
        monkeypatch.setenv("UIPATH_URL", UIPATH_URL)
        monkeypatch.setenv("UIPATH_APP_ID", "env-app-id")
        monkeypatch.delenv("UIPATH_APP_SECRET", raising=False)

        env_file = tmp_path / ".env"
        env_file.write_text(
            "UIPATH_APP_ID=file-app-id\n"
            "UIPATH_APP_SECRET=file-app-secret\n",
            encoding="utf-8",
        )

        creds = UiPathCredentials.from_env(env_path=env_file)

        # os.environ value preserved; .env value only fills the unset key.
        assert creds.app_id == "env-app-id"
        assert creds.app_secret == "file-app-secret"


# ---------------------------------------------------------------------------
# Tests — get_access_token
# ---------------------------------------------------------------------------


class TestGetAccessToken:
    def test_posts_client_credentials_with_default_scopes(self) -> None:
        creds = _make_credentials()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"access_token": "tok-abc-123"}
        factory, client = _patch_httpx_client(response)

        with patch("cascadecare.uipath.auth.httpx.Client", factory):
            token = get_access_token(creds)

        assert token == "tok-abc-123"

        post_kwargs = client.post.call_args.kwargs
        post_args = client.post.call_args.args
        # Endpoint is the identity URL.
        assert post_args[0] == creds.identity_url
        data = post_kwargs["data"]
        assert data["grant_type"] == "client_credentials"
        assert data["client_id"] == "app-id-123"
        assert data["client_secret"] == "app-secret-456"
        # Default scopes joined by spaces.
        assert data["scope"] == "OR.Cases OR.Folders OR.Assets OR.Queues"

    def test_uses_custom_scopes_when_provided(self) -> None:
        creds = _make_credentials()
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"access_token": "tok-xyz"}
        factory, client = _patch_httpx_client(response)

        with patch("cascadecare.uipath.auth.httpx.Client", factory):
            get_access_token(creds, scopes=["OR.Cases", "OR.Execution"])

        data = client.post.call_args.kwargs["data"]
        assert data["scope"] == "OR.Cases OR.Execution"

    def test_raises_runtime_error_on_non_200(self) -> None:
        creds = _make_credentials()
        response = MagicMock()
        response.status_code = 401
        response.text = "invalid_client"
        factory, _client = _patch_httpx_client(response)

        with (
            patch("cascadecare.uipath.auth.httpx.Client", factory),
            pytest.raises(RuntimeError, match="Authentication failed"),
        ):
            get_access_token(creds)
