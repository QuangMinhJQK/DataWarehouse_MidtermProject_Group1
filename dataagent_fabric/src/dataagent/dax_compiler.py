"""Compile a validated logical plan into a small, read-only DAX subset."""

from __future__ import annotations

from datetime import date
from typing import Any

from dataagent.catalog import Dimension, SemanticCatalog
from dataagent.schemas import FilterOperator, FilterSpec, QueryPlan, SortDirection, SortSpec


class DaxCompiler:
    def __init__(self, catalog: SemanticCatalog) -> None:
        self.catalog = catalog

    def compile(self, plan: QueryPlan) -> str:
        group_by = [self._column(self.catalog.dimensions[key]) for key in plan.dimensions]
        filters = [self._filter(item) for item in plan.filters]
        measures = [f"{self._string(name)}, {self._measure_ref(name)}" for name in plan.measures]
        summarize_args = group_by + filters + measures
        summarized = "SUMMARIZECOLUMNS(\n        " + ",\n        ".join(summarize_args) + "\n    )"

        if plan.sort:
            sort_items = plan.sort
        elif plan.dimensions:
            sort_items = [
                SortSpec(field=field, direction=SortDirection.ASC) for field in plan.dimensions
            ]
        else:
            sort_items = [SortSpec(field=plan.measures[0], direction=SortDirection.DESC)]

        sorted_fields = {item.field for item in sort_items}
        sort_items = [*sort_items]
        sort_items.extend(
            SortSpec(field=field, direction=SortDirection.ASC)
            for field in plan.dimensions
            if field not in sorted_fields
        )

        topn_sort = []
        for item in sort_items:
            expression = self._sort_expression(item.field)
            direction = item.direction.value.upper()
            topn_sort.append(f"    {expression}, {direction}")

        dax = (
            "EVALUATE\n"
            "TOPN(\n"
            f"    {plan.limit},\n"
            f"    {summarized},\n" + ",\n".join(topn_sort) + "\n"
            ")"
        )

        order_by = []
        for item in sort_items:
            order_by.append(f"{self._sort_expression(item.field)} {item.direction.value.upper()}")
        dax += "\nORDER BY " + ", ".join(order_by)
        return dax

    def _filter(self, item: FilterSpec) -> str:
        dimension = self.catalog.dimensions[item.field]
        column = self._column(dimension)
        if item.operator == FilterOperator.EQ:
            return f"TREATAS({{{self._literal(item.value, dimension)}}}, {column})"
        if item.operator == FilterOperator.IN:
            values = ", ".join(self._literal(value, dimension) for value in item.value)
            return f"TREATAS({{{values}}}, {column})"

        if item.operator == FilterOperator.BETWEEN:
            low = self._literal(item.value[0], dimension)
            high = self._literal(item.value[1], dimension)
            predicate = f"{column} >= {low} && {column} <= {high}"
        elif item.operator == FilterOperator.GTE:
            predicate = f"{column} >= {self._literal(item.value, dimension)}"
        else:
            predicate = f"{column} <= {self._literal(item.value, dimension)}"
        return f"FILTER(ALL({column}), {predicate})"

    def _sort_expression(self, field: str) -> str:
        if field in self.catalog.measures:
            return self._measure_ref(field)
        return self._column(self.catalog.dimensions[field])

    @staticmethod
    def _column(dimension: Dimension) -> str:
        table = dimension.table.replace("'", "''")
        column = dimension.column.replace("]", "]]")
        return f"'{table}'[{column}]"

    @staticmethod
    def _measure_ref(name: str) -> str:
        return f"[{name.replace(']', ']]')}]"

    @staticmethod
    def _string(value: str) -> str:
        return '"' + value.replace('"', '""') + '"'

    def _literal(self, value: Any, dimension: Dimension) -> str:
        if dimension.data_type == "boolean":
            return "TRUE()" if value else "FALSE()"
        if dimension.data_type == "date":
            parsed = date.fromisoformat(str(value))
            return f"DATE({parsed.year}, {parsed.month}, {parsed.day})"
        if dimension.data_type in {"integer", "decimal", "number"}:
            return str(value)
        return self._string(str(value))
