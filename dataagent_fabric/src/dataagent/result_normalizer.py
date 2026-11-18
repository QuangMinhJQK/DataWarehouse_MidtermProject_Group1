"""Normalize Power BI row keys and enforce application-level result caps."""

from __future__ import annotations

from typing import Any

from dataagent.catalog import SemanticCatalog
from dataagent.schemas import NormalizedResult


class ResultNormalizer:
    def __init__(self, catalog: SemanticCatalog, max_rows: int) -> None:
        self.catalog = catalog
        self.max_rows = max_rows
        self._column_labels = {
            f"{item.table}[{item.column}]".casefold(): item.label
            for item in catalog.dimensions.values()
        }

    def normalize(
        self, rows: list[dict[str, Any]], api_warnings: list[str] | None = None
    ) -> NormalizedResult:
        warnings = list(api_warnings or [])
        truncated = len(rows) > self.max_rows
        if truncated:
            rows = rows[: self.max_rows]
            warnings.append(f"Kết quả được giới hạn ở {self.max_rows} dòng.")

        normalized_rows: list[dict[str, Any]] = []
        for row in rows:
            normalized: dict[str, Any] = {}
            for raw_key, value in row.items():
                key = raw_key.strip()
                if key.startswith("[") and key.endswith("]"):
                    key = key[1:-1]
                label = self._column_labels.get(key.casefold())
                if not label and key in self.catalog.measures:
                    label = self.catalog.measures[key].label
                normalized[label or key] = value
            normalized_rows.append(normalized)

        columns = list(normalized_rows[0]) if normalized_rows else []
        return NormalizedResult(
            columns=columns,
            rows=normalized_rows,
            warnings=warnings,
            truncated=truncated,
        )
