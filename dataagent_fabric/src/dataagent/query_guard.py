"""Deterministic validation and canonicalization for LLM-created query plans."""

from __future__ import annotations

from datetime import date
from typing import Any

from dataagent.catalog import Dimension, SemanticCatalog
from dataagent.errors import QueryValidationError
from dataagent.schemas import Action, FilterOperator, FilterSpec, QueryPlan, SortSpec


class QueryGuard:
    def __init__(self, catalog: SemanticCatalog, max_result_rows: int) -> None:
        self.catalog = catalog
        self.max_result_rows = max_result_rows

    def validate(self, plan: QueryPlan) -> QueryPlan:
        if plan.action != Action.QUERY:
            return plan

        limits = self.catalog.policy
        if len(plan.measures) > int(limits.get("max_measures", 3)):
            raise QueryValidationError("Too many measures in one query")
        if len(plan.dimensions) > int(limits.get("max_dimensions", 2)):
            raise QueryValidationError("Too many dimensions in one query")
        if len(plan.filters) > int(limits.get("max_filters", 6)):
            raise QueryValidationError("Too many filters in one query")

        measure_names: list[str] = []
        for requested in plan.measures:
            measure = self.catalog.resolve_measure(requested)
            if measure.name not in measure_names:
                measure_names.append(measure.name)
        for requested in tuple(measure_names):
            for companion in self.catalog.measures[requested].companions:
                if companion not in measure_names:
                    measure_names.append(companion)

        dimension_keys: list[str] = []
        for requested in plan.dimensions:
            dimension = self.catalog.resolve_dimension(requested)
            if dimension.key not in dimension_keys:
                dimension_keys.append(dimension.key)

        high_cardinality = set(limits.get("high_cardinality_dimensions", []))
        high_cardinality_count = sum(key in high_cardinality for key in dimension_keys)
        max_high_cardinality = int(limits.get("max_high_cardinality_dimensions", 1))
        if high_cardinality_count > max_high_cardinality:
            raise QueryValidationError("Query combines too many high-cardinality dimensions")

        filters = [self._canonical_filter(item) for item in plan.filters]
        sort = [self._canonical_sort(item) for item in plan.sort]
        selected_fields = set(measure_names) | set(dimension_keys)
        if any(item.field not in selected_fields for item in sort):
            raise QueryValidationError("Sort field must be selected as a measure or dimension")
        limit = min(plan.limit, self.max_result_rows)

        return plan.model_copy(
            update={
                "measures": measure_names,
                "dimensions": dimension_keys,
                "filters": filters,
                "sort": sort,
                "limit": limit,
            }
        )

    def _canonical_filter(self, item: FilterSpec) -> FilterSpec:
        dimension = self.catalog.resolve_dimension(item.field)
        operator = item.operator
        value = item.value

        if operator == FilterOperator.IN:
            if not isinstance(value, list) or not value:
                raise QueryValidationError(f"Filter {dimension.key} requires a non-empty list")
            value = [self._coerce_scalar(dimension, part) for part in value]
        elif operator == FilterOperator.BETWEEN:
            if not isinstance(value, list) or len(value) != 2:
                raise QueryValidationError(f"Filter {dimension.key} requires exactly two values")
            value = [self._coerce_scalar(dimension, part) for part in value]
        else:
            if isinstance(value, (list, dict)):
                raise QueryValidationError(f"Filter {dimension.key} requires a scalar value")
            value = self._coerce_scalar(dimension, value)

        return FilterSpec(field=dimension.key, operator=operator, value=value)

    def _canonical_sort(self, item: SortSpec) -> SortSpec:
        try:
            field = self.catalog.resolve_measure(item.field).name
        except QueryValidationError:
            field = self.catalog.resolve_dimension(item.field).key
        return SortSpec(field=field, direction=item.direction)

    @staticmethod
    def _coerce_scalar(dimension: Dimension, value: Any) -> Any:
        try:
            if dimension.data_type == "integer":
                if isinstance(value, bool):
                    raise ValueError
                return int(value)
            if dimension.data_type in {"decimal", "number"}:
                if isinstance(value, bool):
                    raise ValueError
                return float(value)
            if dimension.data_type == "boolean":
                if isinstance(value, bool):
                    return value
                normalized = str(value).strip().casefold()
                if normalized in {"true", "1", "yes", "online", "có"}:
                    return True
                if normalized in {"false", "0", "no", "offline", "không"}:
                    return False
                raise ValueError
            if dimension.data_type == "date":
                return date.fromisoformat(str(value)).isoformat()
            return str(value)
        except (TypeError, ValueError) as exc:
            raise QueryValidationError(
                f"Invalid {dimension.data_type} value for {dimension.key}"
            ) from exc
