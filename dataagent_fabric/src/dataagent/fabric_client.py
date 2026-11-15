"""Read-only Power BI REST client for semantic-model DAX queries."""

from __future__ import annotations

import time
from typing import Any

import httpx
import pyarrow as pa
import pyarrow.ipc as ipc

from dataagent.auth import EntraTokenProvider
from dataagent.config import Settings
from dataagent.errors import (
    AuthenticationError,
    PermissionDeniedError,
    SemanticModelError,
)


class PowerBIRestClient:
    def __init__(self, settings: Settings, token_provider: EntraTokenProvider) -> None:
        self.settings = settings
        self.token_provider = token_provider
        self._client = httpx.Client(timeout=settings.powerbi_query_timeout_seconds)

    @property
    def model_query_url(self) -> str:
        return (
            f"{self.settings.powerbi_api_base_url}"
            f"/datasets/{self.settings.powerbi_semantic_model_id}/executeDaxQueries"
        )

    def health_check(self) -> dict[str, Any]:
        url = (
            f"{self.settings.powerbi_api_base_url}/groups/{self.settings.powerbi_workspace_id}"
            "/datasets"
        )
        response = self._request("GET", url)
        for dataset in response.get("value", []):
            if dataset.get("id") == str(self.settings.powerbi_semantic_model_id):
                self.execute_dax('EVALUATE ROW("Query Ready", 1)')
                return {
                    "name": dataset.get("name", "unknown"),
                    "id": dataset.get("id"),
                    "is_refreshable": dataset.get("isRefreshable"),
                    "query_ready": True,
                }
        raise SemanticModelError("Configured semantic model is not visible in the workspace")

    def execute_dax(self, dax: str) -> tuple[list[dict[str, Any]], list[str]]:
        payload = {
            "query": dax,
            "queryTimeout": int(self.settings.powerbi_query_timeout_seconds),
            "resultSetRowCountLimit": self.settings.max_result_rows,
        }
        response = self._request_response("POST", self.model_query_url, json=payload)
        content_type = response.headers.get("Content-Type", "").casefold()
        if "application/vnd.apache.arrow.stream" not in content_type:
            raise SemanticModelError("Power BI returned an unexpected query response format")

        try:
            source = pa.BufferReader(response.content)
            reader = ipc.open_stream(source)
            table = reader.read_all()
        except (pa.ArrowException, OSError) as exc:
            raise SemanticModelError("Power BI returned an invalid Arrow query result") from exc

        metadata = {
            key.decode("utf-8", errors="replace").casefold(): value.decode(
                "utf-8", errors="replace"
            )
            for key, value in (reader.schema.metadata or {}).items()
        }
        rows = table.to_pylist()
        if metadata.get("iserror", "false").casefold() == "true":
            message = metadata.get("faultstring")
            if not message and rows:
                message = str(rows[0].get("ErrorMessage") or rows[0].get("ErrorDescription") or "")
            raise SemanticModelError(f"Power BI query failed: {(message or 'Unknown error')[:500]}")
        return rows, []

    def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self._request_response(method, url, **kwargs)
        try:
            parsed = response.json()
        except ValueError as exc:
            raise SemanticModelError("Power BI returned an invalid JSON response") from exc
        if not isinstance(parsed, dict):
            raise SemanticModelError("Power BI returned an unexpected response shape")
        return parsed

    def _request_response(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        attempts = 3
        for attempt in range(attempts):
            token = self.token_provider.get_access_token()
            try:
                response = self._client.request(
                    method,
                    url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    **kwargs,
                )
            except httpx.TimeoutException as exc:
                raise SemanticModelError("Power BI request timed out") from exc
            except httpx.HTTPError as exc:
                raise SemanticModelError("Could not connect to Power BI API") from exc

            if response.status_code == 401:
                if self._response_error_code(response) == "PowerBINotAuthorizedException":
                    raise PermissionDeniedError(
                        "Power BI denied Execute Queries. Enable tenant setting "
                        "'Semantic Model Execute Queries REST API' and verify dataset Read/Build "
                        "access"
                    )
                raise AuthenticationError("Power BI rejected the Microsoft Entra access token")
            if response.status_code == 403:
                raise PermissionDeniedError(
                    "Service principal lacks tenant, workspace, Read, or Build permission"
                )
            if response.status_code == 404:
                raise SemanticModelError("Workspace or semantic model was not found")
            if response.status_code == 429 or response.status_code >= 500:
                if attempt == attempts - 1:
                    raise SemanticModelError(
                        f"Power BI API unavailable after {attempts} attempts "
                        f"(HTTP {response.status_code})"
                    )
                retry_after = response.headers.get("Retry-After", "1")
                try:
                    delay = min(max(float(retry_after), 1.0), 8.0)
                except ValueError:
                    delay = 2.0**attempt
                time.sleep(delay)
                continue
            if response.is_error:
                raise SemanticModelError(
                    f"Power BI API rejected the request (HTTP {response.status_code})"
                )
            return response
        raise SemanticModelError("Power BI request failed")

    @staticmethod
    def _response_error_code(response: httpx.Response) -> str | None:
        try:
            payload = response.json()
        except ValueError:
            return None
        if not isinstance(payload, dict):
            return None
        error = payload.get("error")
        if not isinstance(error, dict):
            return None
        code = error.get("code")
        return str(code) if code else None
