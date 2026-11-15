from dataagent.dax_compiler import DaxCompiler
from dataagent.query_guard import QueryGuard
from dataagent.schemas import Action, FilterSpec, QueryPlan, SortSpec


def test_compiler_generates_bounded_grouped_query(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    compiler = DaxCompiler(catalog)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Sales by category",
        measures=["doanh thu"],
        dimensions=["danh mục"],
        filters=[FilterSpec(field="năm", operator="eq", value=2013)],
        sort=[SortSpec(field="doanh thu", direction="desc")],
        limit=5,
    )

    dax = compiler.compile(guard.validate(plan))

    assert dax.startswith("EVALUATE\nTOPN(")
    assert "SUMMARIZECOLUMNS" in dax
    assert "'product'[category_name]" in dax
    assert "TREATAS({2013}, 'date'[calendar_year])" in dax
    assert '"Net Sales", [Net Sales]' in dax
    assert "ORDER BY [Net Sales] DESC, 'product'[category_name] ASC" in dax


def test_compiler_escapes_string_literals(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    compiler = DaxCompiler(catalog)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Territory",
        measures=["Orders"],
        filters=[FilterSpec(field="territory.name", operator="eq", value='A "quoted" area')],
    )

    dax = compiler.compile(guard.validate(plan))

    assert '"A ""quoted"" area"' in dax


def test_compiler_defaults_grouped_query_to_dimension_order(catalog):
    guard = QueryGuard(catalog, max_result_rows=200)
    compiler = DaxCompiler(catalog)
    plan = QueryPlan(
        action=Action.QUERY,
        title="Daily trend",
        measures=["Net Sales"],
        dimensions=["date.full_date"],
        limit=100,
    )

    dax = compiler.compile(guard.validate(plan))

    assert "'date'[full_date], ASC" in dax
    assert dax.endswith("ORDER BY 'date'[full_date] ASC")
