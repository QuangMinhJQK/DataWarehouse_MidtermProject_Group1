"""Small Google Gen AI SDK adapter with structured planning."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from dataagent.catalog import SemanticCatalog
from dataagent.config import Settings
from dataagent.errors import LLMError
from dataagent.schemas import QueryPlan

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, settings: Settings, catalog: SemanticCatalog) -> None:
        self.settings = settings
        self.catalog = catalog
        self._client = genai.Client(
            api_key=settings.gemini_api_key.get_secret_value(),
            http_options=types.HttpOptions(
                timeout=settings.gemini_timeout_seconds * 1000,
                retry_options=types.HttpRetryOptions(
                    attempts=settings.gemini_retry_attempts,
                    initial_delay=0.5,
                    max_delay=2.0,
                    jitter=0.2,
                ),
            ),
        )
        self._planner_prompt = self._read_prompt(settings.planner_prompt_path)
        self._summarizer_prompt = self._read_prompt(settings.summarizer_prompt_path)

    def plan(self, question: str, history: list[dict[str, str]] | None = None) -> QueryPlan:
        compact_history = (history or [])[-6:]
        payload = {
            "question": question,
            "recent_conversation": compact_history,
            "semantic_catalog": json.loads(self.catalog.prompt_context()),
            "maximum_result_rows": self.settings.max_result_rows,
        }
        models = [self.settings.gemini_model_planner]
        fallback_model = getattr(self.settings, "gemini_model_summarizer", None)
        if fallback_model and fallback_model not in models:
            models.append(fallback_model)

        for index, model in enumerate(models):
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=json.dumps(payload, ensure_ascii=False),
                    config=types.GenerateContentConfig(
                        system_instruction=self._planner_prompt,
                        response_mime_type="application/json",
                        response_json_schema=QueryPlan.model_json_schema(),
                        temperature=0.1,
                        max_output_tokens=2048,
                    ),
                )
                if isinstance(response.parsed, QueryPlan):
                    return response.parsed
                if response.parsed is not None:
                    return QueryPlan.model_validate(response.parsed)
                if not response.text:
                    raise LLMError("Gemini planner returned an empty response")
                return QueryPlan.model_validate_json(response.text)
            except LLMError:
                raise
            except Exception as exc:
                has_fallback = index < len(models) - 1
                if self._is_retryable(exc) and has_fallback:
                    logger.warning("Gemini planner model unavailable; trying configured fallback")
                    continue
                raise LLMError("Gemini could not create a valid query plan") from exc

        raise LLMError("Gemini could not create a valid query plan")

    def summarize(
        self,
        question: str,
        plan: QueryPlan,
        rows: list[dict[str, Any]],
        warnings: list[str],
    ) -> str:
        payload = {
            "question": question,
            "query": plan.model_dump(mode="json"),
            "rows": rows[: self.settings.max_summary_rows],
            "warnings": warnings,
            "row_count_sent": min(len(rows), self.settings.max_summary_rows),
        }
        try:
            response = self._client.models.generate_content(
                model=self.settings.gemini_model_summarizer,
                contents=json.dumps(payload, ensure_ascii=False, default=str),
                config=types.GenerateContentConfig(
                    system_instruction=self._summarizer_prompt,
                    temperature=0.2,
                    max_output_tokens=1024,
                ),
            )
            if not response.text:
                raise LLMError("Gemini summarizer returned an empty response")
            return response.text.strip()
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError("Gemini could not summarize the semantic-model result") from exc

    @staticmethod
    def _read_prompt(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise LLMError(f"Cannot load prompt file: {path.name}") from exc

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
        return status_code in {429, 500, 502, 503, 504}
