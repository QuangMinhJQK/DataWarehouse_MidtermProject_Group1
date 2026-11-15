from types import SimpleNamespace

import httpx
import pyarrow as pa
import pyarrow.ipc as ipc
import pytest
import respx

from dataagent.errors import PermissionDeniedError, SemanticModelError
from dataagent.fabric_client import PowerBIRestClient


class FakeTokenProvider:
    def get_access_token(self):
        return "test-token"


def make_settings():
    return SimpleNamespace(
        powerbi_query_timeout_seconds=10,
        powerbi_api_base_url="https://api.powerbi.com/v1.0/myorg",
        powerbi_workspace_id="workspace-id",
        powerbi_semantic_model_id="model-id",
        max_result_rows=200,
    )


def arrow_response(rows, metadata=None):
    table = pa.Table.from_pylist(rows)
    if metadata:
        table = table.replace_schema_metadata(metadata)
    sink = pa.BufferOutputStream()
    with ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
    return sink.getvalue().to_pybytes()


@respx.mock
def test_execute_dax_returns_rows_and_warnings():
    settings = make_settings()
    url = "https://api.powerbi.com/v1.0/myorg/datasets/model-id/executeDaxQueries"
    respx.post(url).mock(
        return_value=httpx.Response(
            200,
            content=arrow_response([{"[Orders]": 10}]),
            headers={"Content-Type": "application/vnd.apache.arrow.stream"},
        )
    )
    client = PowerBIRestClient(settings, FakeTokenProvider())

    rows, warnings = client.execute_dax('EVALUATE ROW("Orders", [Orders])')

    assert rows == [{"[Orders]": 10}]
    assert warnings == []


@respx.mock
def test_health_check_finds_configured_model():
    settings = make_settings()
    url = "https://api.powerbi.com/v1.0/myorg/groups/workspace-id/datasets"
    query_url = "https://api.powerbi.com/v1.0/myorg/datasets/model-id/executeDaxQueries"
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            json={"value": [{"id": "model-id", "name": "sm_gold_sales_inventory"}]},
        )
    )
    respx.post(query_url).mock(
        return_value=httpx.Response(
            200,
            content=arrow_response([{"[Query Ready]": 1}]),
            headers={"Content-Type": "application/vnd.apache.arrow.stream"},
        )
    )
    client = PowerBIRestClient(settings, FakeTokenProvider())

    health = client.health_check()

    assert health["name"] == "sm_gold_sales_inventory"
    assert health["query_ready"] is True


@respx.mock
def test_execute_dax_explains_power_bi_authorization_failure():
    settings = make_settings()
    url = "https://api.powerbi.com/v1.0/myorg/datasets/model-id/executeDaxQueries"
    respx.post(url).mock(
        return_value=httpx.Response(
            401,
            json={"error": {"code": "PowerBINotAuthorizedException"}},
        )
    )
    client = PowerBIRestClient(settings, FakeTokenProvider())

    with pytest.raises(PermissionDeniedError, match="Execute Queries REST API"):
        client.execute_dax('EVALUATE ROW("Orders", [Orders])')


@respx.mock
def test_execute_dax_reads_arrow_error_rowset():
    settings = make_settings()
    url = "https://api.powerbi.com/v1.0/myorg/datasets/model-id/executeDaxQueries"
    respx.post(url).mock(
        return_value=httpx.Response(
            200,
            content=arrow_response(
                [{"ErrorCode": "1", "ErrorMessage": "Invalid DAX"}],
                metadata={b"IsError": b"true", b"FaultString": b"Invalid DAX"},
            ),
            headers={"Content-Type": "application/vnd.apache.arrow.stream"},
        )
    )
    client = PowerBIRestClient(settings, FakeTokenProvider())

    with pytest.raises(SemanticModelError, match="Invalid DAX"):
        client.execute_dax("EVALUATE INVALID()")
