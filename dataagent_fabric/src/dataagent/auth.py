"""Microsoft Entra client-credential authentication for Power BI APIs."""

from __future__ import annotations

from threading import Lock

import msal

from dataagent.config import Settings
from dataagent.errors import AuthenticationError


class EntraTokenProvider:
    def __init__(self, settings: Settings) -> None:
        self.scope = settings.powerbi_scope
        self._lock = Lock()
        self._application = msal.ConfidentialClientApplication(
            client_id=str(settings.azure_client_id),
            authority=f"https://login.microsoftonline.com/{settings.azure_tenant_id}",
            client_credential=settings.azure_client_secret.get_secret_value(),
        )

    def get_access_token(self) -> str:
        with self._lock:
            result = self._application.acquire_token_for_client(scopes=[self.scope])
        token = result.get("access_token")
        if token:
            return str(token)
        code = result.get("error", "authentication_failed")
        description = result.get("error_description", "No access token returned")
        safe_description = str(description).split("Trace ID:", maxsplit=1)[0].strip()
        raise AuthenticationError(
            f"Microsoft Entra authentication failed ({code}): {safe_description}"
        )
