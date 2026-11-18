"""Curated semantic catalog used as both LLM context and an execution allow-list."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from dataagent.errors import ConfigurationError, QueryValidationError


@dataclass(frozen=True)
class Dimension:
    key: str
    table: str
    column: str
    label: str
    data_type: str
    synonyms: tuple[str, ...]


@dataclass(frozen=True)
class Measure:
    name: str
    table: str
    label: str
    format: str
    synonyms: tuple[str, ...]
    description: str = ""
    companions: tuple[str, ...] = ()


class SemanticCatalog:
    def __init__(self, path: Path) -> None:
        self.path = path
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise ConfigurationError(f"Cannot load semantic catalog: {path}") from exc
        if not isinstance(raw, dict):
            raise ConfigurationError("Semantic catalog root must be an object")

        self.version = str(raw.get("version", "unknown"))
        self.model = raw.get("semantic_model", {})
        self.policy = raw.get("policy", {})
        self.dimensions = self._load_dimensions(raw.get("dimensions", {}))
        self.measures = self._load_measures(raw.get("measures", {}))
        self._dimension_lookup = self._build_dimension_lookup()
        self._measure_lookup = self._build_measure_lookup()
        self._validate_companions()

    @staticmethod
    def _load_dimensions(raw: dict[str, Any]) -> dict[str, Dimension]:
        return {
            key: Dimension(
                key=key,
                table=str(value["table"]),
                column=str(value["column"]),
                label=str(value["label"]),
                data_type=str(value["data_type"]),
                synonyms=tuple(str(item) for item in value.get("synonyms", [])),
            )
            for key, value in raw.items()
        }

    @staticmethod
    def _load_measures(raw: dict[str, Any]) -> dict[str, Measure]:
        return {
            name: Measure(
                name=name,
                table=str(value["table"]),
                label=str(value["label"]),
                format=str(value.get("format", "decimal")),
                synonyms=tuple(str(item) for item in value.get("synonyms", [])),
                description=str(value.get("description", "")),
                companions=tuple(str(item) for item in value.get("companions", [])),
            )
            for name, value in raw.items()
        }

    def _build_dimension_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        for key, dimension in self.dimensions.items():
            for alias in (key, dimension.label, *dimension.synonyms):
                lookup[alias.casefold()] = key
        return lookup

    def _build_measure_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        for name, measure in self.measures.items():
            for alias in (name, measure.label, *measure.synonyms):
                lookup[alias.casefold()] = name
        return lookup

    def _validate_companions(self) -> None:
        missing = {
            companion
            for measure in self.measures.values()
            for companion in measure.companions
            if companion not in self.measures
        }
        if missing:
            raise ConfigurationError(f"Unknown companion measures: {sorted(missing)}")

    def validate_identity(self, workspace_id: object, model_id: object) -> None:
        expected_workspace = str(self.model.get("workspace_id", "")).strip().casefold()
        expected_model = str(self.model.get("id", "")).strip().casefold()
        if not expected_workspace or not expected_model:
            raise ConfigurationError("Semantic catalog is missing its workspace or model identity")
        if str(workspace_id).strip().casefold() != expected_workspace:
            raise ConfigurationError("Configured workspace does not match the semantic catalog")
        if str(model_id).strip().casefold() != expected_model:
            raise ConfigurationError(
                "Configured semantic model does not match the semantic catalog"
            )

    def resolve_dimension(self, value: str) -> Dimension:
        key = self._dimension_lookup.get(value.strip().casefold())
        if not key:
            raise QueryValidationError(f"Dimension is not allowed: {value}")
        return self.dimensions[key]

    def resolve_measure(self, value: str) -> Measure:
        name = self._measure_lookup.get(value.strip().casefold())
        if not name:
            raise QueryValidationError(f"Measure is not allowed: {value}")
        return self.measures[name]

    def prompt_context(self) -> str:
        payload = {
            "catalog_version": self.version,
            "limits": self.policy,
            "dimensions": [
                {
                    "key": item.key,
                    "label": item.label,
                    "type": item.data_type,
                    "synonyms": item.synonyms,
                }
                for item in self.dimensions.values()
            ],
            "measures": [
                {
                    "name": item.name,
                    "label": item.label,
                    "format": item.format,
                    "description": item.description,
                    "companions": item.companions,
                    "synonyms": item.synonyms,
                }
                for item in self.measures.values()
            ],
        }
        return json.dumps(payload, ensure_ascii=False)
