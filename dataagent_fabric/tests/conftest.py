from pathlib import Path

import pytest

from dataagent.catalog import SemanticCatalog


@pytest.fixture(scope="session")
def catalog() -> SemanticCatalog:
    root = Path(__file__).resolve().parents[1]
    return SemanticCatalog(root / "config" / "semantic_model.yaml")
