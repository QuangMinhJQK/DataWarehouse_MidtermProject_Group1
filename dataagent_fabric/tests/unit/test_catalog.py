import pytest

from dataagent.errors import QueryValidationError


def test_catalog_resolves_vietnamese_aliases(catalog):
    assert catalog.resolve_measure("doanh thu").name == "Net Sales"
    assert catalog.resolve_dimension("năm").key == "date.year"


def test_catalog_blocks_unknown_detail_field(catalog):
    with pytest.raises(QueryValidationError):
        catalog.resolve_dimension("customer name")


def test_catalog_companions_exist(catalog):
    measure = catalog.resolve_measure("estimated margin")
    assert measure.companions == ("Cost Coverage",)
