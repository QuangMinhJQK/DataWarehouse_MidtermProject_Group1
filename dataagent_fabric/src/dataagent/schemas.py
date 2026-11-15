"""Typed contracts exchanged by the planner, query engine, and UI."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Action(StrEnum):
    QUERY = "query"
    CLARIFY = "clarify"
    REJECT = "reject"


class FilterOperator(StrEnum):
    EQ = "eq"
    IN = "in"
    BETWEEN = "between"
    GTE = "gte"
    LTE = "lte"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class FilterSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    operator: FilterOperator
    value: Any


class SortSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str
    direction: SortDirection = SortDirection.DESC


class QueryPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Action
    title: str = Field(min_length=1, max_length=160)
    measures: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: list[FilterSpec] = Field(default_factory=list)
    sort: list[SortSpec] = Field(default_factory=list)
    limit: int = Field(default=100, ge=1, le=500)
    clarification_question: str | None = Field(default=None, max_length=300)
    rejection_reason: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def validate_action_payload(self) -> QueryPlan:
        if self.action == Action.QUERY and not self.measures:
            raise ValueError("A query plan requires at least one measure")
        if self.action == Action.CLARIFY and not self.clarification_question:
            raise ValueError("A clarification plan requires clarification_question")
        if self.action == Action.REJECT and not self.rejection_reason:
            raise ValueError("A rejected plan requires rejection_reason")
        return self


class NormalizedResult(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    warnings: list[str] = Field(default_factory=list)
    truncated: bool = False


class AgentResponse(BaseModel):
    request_id: str
    status: Literal["ok", "clarify", "rejected", "error", "empty"]
    text: str
    title: str | None = None
    rows: list[dict[str, Any]] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    dax: str | None = None
    query_plan: QueryPlan | None = None
