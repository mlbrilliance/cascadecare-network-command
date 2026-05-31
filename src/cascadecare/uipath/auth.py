"""UiPath OAuth2 client credentials authentication.

Reads credentials from environment / .env and returns a bearer token
for the configured UiPath tenant (supports both cloud and staging).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import httpx

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class UiPathCredentials:
    base_url: str      # e.g. https://staging.uipath.com
    org: str           # e.g. hackathon26_042
    tenant: str        # e.g. DefaultTenant
    app_id: str
    app_secret: str

    @property
    def tenant_url(self) -> str:
        return f"{self.base_url}/{self.org}/{self.tenant}"

    @property
    def identity_url(self) -> str:
        return f"{self.base_url}/identity_/connect/token"

    @classmethod
    def from_env(cls, env_path: Path | None = None) -> UiPathCredentials:
        """Load credentials from environment + optional .env file."""
        env: dict[str, str] = dict(os.environ)
        if env_path and env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    k, _, v = stripped.partition("=")
                    env.setdefault(k.strip(), v.strip())

        uipath_url = env.get("UIPATH_URL", "")
        if not uipath_url:
            raise ValueError("UIPATH_URL is not set in environment or .env")

        parsed = urlparse(uipath_url)
        parts = parsed.path.strip("/").split("/")
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        org = parts[0] if len(parts) > 0 else ""
        tenant = parts[1] if len(parts) > 1 else ""

        return cls(
            base_url=base_url,
            org=org,
            tenant=tenant,
            app_id=env.get("UIPATH_APP_ID", ""),
            app_secret=env.get("UIPATH_APP_SECRET", ""),
        )


def get_access_token(creds: UiPathCredentials, scopes: list[str] | None = None) -> str:
    """Obtain a bearer token using the client credentials OAuth2 flow."""
    if scopes is None:
        scopes = ["OR.Cases", "OR.Folders", "OR.Assets", "OR.Queues"]

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            creds.identity_url,
            data={
                "grant_type": "client_credentials",
                "client_id": creds.app_id,
                "client_secret": creds.app_secret,
                "scope": " ".join(scopes),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if resp.status_code != 200:  # noqa: PLR2004
        raise RuntimeError(
            f"Authentication failed ({resp.status_code}): {resp.text[:500]}"
        )

    return str(resp.json()["access_token"])
