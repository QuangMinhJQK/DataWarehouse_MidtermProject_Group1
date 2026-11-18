from types import SimpleNamespace

from dataagent.gemini_client import GeminiClient
from dataagent.schemas import Action, QueryPlan


class FakeModels:
    def __init__(self) -> None:
        self.config = None

    def generate_content(self, *, model, contents, config):
        self.config = config
        return SimpleNamespace(
            parsed=QueryPlan(
                action=Action.QUERY,
                title="Net sales",
                measures=["Net Sales"],
            ),
            text=None,
        )


class RetryableModelError(Exception):
    status_code = 503


class FallbackModels(FakeModels):
    def __init__(self) -> None:
        super().__init__()
        self.called_models = []

    def generate_content(self, *, model, contents, config):
        self.called_models.append(model)
        if len(self.called_models) == 1:
            raise RetryableModelError("temporarily unavailable")
        return super().generate_content(model=model, contents=contents, config=config)


def test_planner_uses_json_schema_supported_by_gemini(catalog):
    models = FakeModels()
    client = GeminiClient.__new__(GeminiClient)
    client.settings = SimpleNamespace(
        gemini_model_planner="gemini-test",
        max_result_rows=200,
    )
    client.catalog = catalog
    client._client = SimpleNamespace(models=models)
    client._planner_prompt = "Return a query plan."

    plan = client.plan("Doanh thu là bao nhiêu?")

    assert plan.measures == ["Net Sales"]
    assert models.config.response_schema is None
    assert models.config.response_json_schema == QueryPlan.model_json_schema()


def test_planner_falls_back_on_temporary_model_failure(catalog):
    models = FallbackModels()
    client = GeminiClient.__new__(GeminiClient)
    client.settings = SimpleNamespace(
        gemini_model_planner="gemini-primary",
        gemini_model_summarizer="gemini-fallback",
        max_result_rows=200,
    )
    client.catalog = catalog
    client._client = SimpleNamespace(models=models)
    client._planner_prompt = "Return a query plan."

    plan = client.plan("Doanh thu là bao nhiêu?")

    assert plan.action == Action.QUERY
    assert models.called_models == ["gemini-primary", "gemini-fallback"]
