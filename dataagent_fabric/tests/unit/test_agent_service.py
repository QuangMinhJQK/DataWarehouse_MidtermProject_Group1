from types import SimpleNamespace

import pytest

from dataagent.agent_service import DataAgentService
from dataagent.errors import AuthenticationError, ConfigurationError
from dataagent.schemas import Action, QueryPlan


class FakeFabricClient:
    def health_check(self):
        return {"name": "sm_gold_sales_inventory", "id": "model-id"}

    def execute_dax(self, dax):
        assert dax.startswith("EVALUATE")
        return [{"[Net Sales]": 123.45}], []


class FakeGeminiClient:
    def plan(self, question, history=None):
        return QueryPlan(
            action=Action.QUERY,
            title="Net sales",
            measures=["Net Sales"],
            limit=10,
        )

    def summarize(self, question, plan, rows, warnings):
        assert rows == [{"Doanh thu thuần": 123.45}]
        return "Doanh thu thuần là 123,45."


def test_service_runs_end_to_end_with_injected_clients(catalog):
    settings = SimpleNamespace(
        max_result_rows=200,
        powerbi_workspace_id=catalog.model["workspace_id"],
        powerbi_semantic_model_id=catalog.model["id"],
    )
    service = DataAgentService(
        settings=settings,
        catalog=catalog,
        fabric_client=FakeFabricClient(),
        gemini_client=FakeGeminiClient(),
    )

    response = service.answer("Doanh thu là bao nhiêu?")

    assert response.status == "ok"
    assert response.rows == [{"Doanh thu thuần": 123.45}]
    assert response.dax is not None


def test_service_rejects_catalog_model_mismatch(catalog):
    settings = SimpleNamespace(
        max_result_rows=200,
        powerbi_workspace_id=catalog.model["workspace_id"],
        powerbi_semantic_model_id="00000000-0000-0000-0000-000000000000",
    )

    with pytest.raises(ConfigurationError, match="does not match"):
        DataAgentService(
            settings=settings,
            catalog=catalog,
            fabric_client=FakeFabricClient(),
            gemini_client=FakeGeminiClient(),
        )


def test_service_does_not_return_upstream_error_details(catalog):
    class FailingGeminiClient:
        def plan(self, question, history=None):
            raise AuthenticationError("upstream response contained fake-secret-value")

    settings = SimpleNamespace(
        max_result_rows=200,
        powerbi_workspace_id=catalog.model["workspace_id"],
        powerbi_semantic_model_id=catalog.model["id"],
    )
    service = DataAgentService(
        settings=settings,
        catalog=catalog,
        fabric_client=FakeFabricClient(),
        gemini_client=FailingGeminiClient(),
    )

    response = service.answer("Doanh thu là bao nhiêu?")

    assert response.status == "error"
    assert "fake-secret-value" not in response.text
    assert response.request_id
