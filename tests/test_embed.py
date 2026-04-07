import pytest
from engine.embed import VectorStore


@pytest.fixture
def store(tmp_path):
    return VectorStore(path=str(tmp_path / "test_vectors"), dimension=4)


def test_upsert_and_search(store):
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "Alpha"})
    store.upsert("page2", [0.0, 1.0, 0.0, 0.0], {"title": "Beta"})
    results = store.search([1.0, 0.1, 0.0, 0.0], top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "page1"
    assert results[0]["metadata"]["title"] == "Alpha"


def test_upsert_overwrites(store):
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "Old"})
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "New"})
    results = store.search([1.0, 0.0, 0.0, 0.0], top_k=1)
    assert results[0]["metadata"]["title"] == "New"


def test_delete(store):
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "Alpha"})
    store.delete("page1")
    results = store.search([1.0, 0.0, 0.0, 0.0], top_k=1)
    assert len(results) == 0


def test_count(store):
    assert store.count() == 0
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "A"})
    store.upsert("page2", [0.0, 1.0, 0.0, 0.0], {"title": "B"})
    assert store.count() == 2
