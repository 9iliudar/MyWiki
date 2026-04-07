import json
import pytest
from engine.query import QueryPipeline
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class MockLLM(LLMProvider):
    def complete(self, prompt: str, context: str = "") -> str:
        return json.dumps({
            "answer": "RAG 是检索增强生成的缩写，详见 [[RAG]]。",
            "should_save": True,
            "save_reason": "对 RAG 的综合解释值得保留",
            "new_page": {"name": "RAG应用场景", "title": "RAG 应用场景", "tags": ["AI", "RAG"], "related": ["[[RAG]]"], "content": "RAG 常用于企业知识库问答系统。"},
        })


class MockEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}
    def search(self, query_vector, top_k=5):
        return [{"id": "RAG", "score": 0.95, "metadata": {"title": "RAG"}}]
    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = {"vector": vector, "metadata": metadata}


@pytest.fixture
def pipeline(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")
    wiki = WikiIO(str(pages_dir), str(index_path), str(log_path))
    wiki.write_page("RAG", {"title": "RAG（检索增强生成）", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": ["AI"], "evolution": []}, "RAG 是一种结合检索和生成的技术。")
    return QueryPipeline(llm=MockLLM(), embedder=MockEmbedder(), vector_store=MockVectorStore(), wiki=wiki)


def test_query_returns_answer(pipeline):
    result = pipeline.query("什么是 RAG？")
    assert "RAG" in result["answer"]


def test_query_creates_new_page_when_should_save(pipeline):
    result = pipeline.query("什么是 RAG？")
    assert result["saved_page"] == "RAG应用场景"
    assert pipeline.wiki.page_exists("RAG应用场景")


def test_query_logs_operation(pipeline):
    pipeline.query("什么是 RAG？")
    log = pipeline.wiki.read_log()
    assert "query" in log
