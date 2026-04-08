import json
import pytest
from unittest.mock import MagicMock, patch
from engine.mcp_server import handle_ingest, handle_query, handle_lint


class MockLLM:
    def complete(self, prompt, context=""):
        return json.dumps({
            "summary": "测试摘要",
            "pages": [
                {"name": "Test-Page", "title": "测试页面", "tags": [], "related": [],
                 "content": "测试内容。", "is_new": True}
            ],
            "index_updates": "",
        })


class MockEmbedder:
    def embed(self, text):
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}
    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = {"vector": vector, "metadata": metadata}
    def search(self, query_vector, top_k=10):
        return []
    def count(self):
        return 0


@pytest.fixture
def wiki_env(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    inbox = tmp_path / "sources" / "inbox"
    inbox.mkdir(parents=True)
    archive = tmp_path / "sources" / "archived"
    archive.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 日志\n", encoding="utf-8")
    schema_path = tmp_path / "schema.md"
    schema_path.write_text("测试 schema", encoding="utf-8")
    return {
        "pages_dir": str(pages_dir),
        "index_path": str(index_path),
        "log_path": str(log_path),
        "schema_path": str(schema_path),
        "inbox_dir": str(inbox),
        "archive_dir": str(archive),
        "tmp_path": tmp_path,
    }


def test_handle_ingest(wiki_env):
    result = handle_ingest(
        content="RAG 是检索增强生成的缩写。",
        title="RAG 笔记",
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki_env=wiki_env,
    )
    assert "Test-Page" in result
    assert "测试摘要" in result


def test_handle_query(wiki_env):
    result = handle_query(
        question="什么是 RAG？",
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki_env=wiki_env,
    )
    assert isinstance(result, str)


def test_handle_lint(wiki_env):
    result = handle_lint(
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki_env=wiki_env,
    )
    assert "0" in result or "发现" in result
