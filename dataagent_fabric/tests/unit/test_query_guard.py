import pytest

from dataagent.errors import QueryValidationError
from dataagent.query_guard import QueryGuard
from dataagent.schemas import Action, FilterSpec, QueryPlan, SortSpec


def test_guard_canonicalizes_aliases_and_adds_companions(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Margin by year",
        measures=["estimated margin"],
        dimensions=["năm"],
        filters=[],
        limit=500,
    )

    validated = guard.validate(plan)

    assert validated.measures == ["Estimated Standard Margin", "Cost Coverage"]
    assert validated.dimensions == ["date.year"]
    assert validated.limit == 200


def test_guard_coerces_filter_types(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Sales in year",
        measures=["Net Sales"],
        filters=[FilterSpec(field="năm", operator="eq", value="2013")],
    )

    validated = guard.validate(plan)

    assert validated.filters[0].field == "date.year"
    assert validated.filters[0].value == 2013


def test_guard_rejects_invalid_boolean(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Channel",
        measures=["Orders"],
        filters=[FilterSpec(field="sales.channel", operator="eq", value="maybe")],
    )

    with pytest.raises(QueryValidationError):
        guard.validate(plan)


def test_guard_rejects_sort_field_not_selected(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Sales by year",
        measures=["Net Sales"],
        dimensions=["date.year"],
        sort=[SortSpec(field="Orders", direction="desc")],
    )

    with pytest.raises(QueryValidationError, match="Sort field must be selected"):
        guard.validate(plan)


def test_guard_rejects_high_cardinality_dimension_combination(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Daily sales by product",
        measures=["Net Sales"],
        dimensions=["date.full_date", "product.name"],
    )

    with pytest.raises(QueryValidationError, match="high-cardinality"):
        guard.validate(plan)
