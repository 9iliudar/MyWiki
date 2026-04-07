import json
import pytest
from engine.ingest import IngestPipeline
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class MockLLM(LLMProvider):
    def complete(self, prompt: str, context: str = "") -> str:
        return json.dumps({
            "summary": "这是一篇关于知识管理的文章。",
            "pages": [
                {"name": "LLM_Wiki", "title": "LLM Wiki（LLM 知识库）", "tags": ["AI", "知识管理"], "related": ["[[知识图谱]]"], "content": "LLM Wiki 是一种利用大语言模型维护个人知识库的方法。", "is_new": True},
                {"name": "知识图谱", "title": "知识图谱", "tags": ["AI"], "related": ["[[LLM_Wiki]]"], "content": "知识图谱是一种结构化的知识表示方法。", "is_new": True},
            ],
            "index_updates": "## AI\n\n- [[LLM_Wiki]] — LLM 驱动的知识库\n- [[知识图谱]] — 结构化知识表示",
        })


class MockEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}
    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = {"vector": vector, "metadata": metadata}


@pytest.fixture
def pipeline(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    inbox = tmp_path / "sources" / "inbox"
    inbox.mkdir(parents=True)
    archive = tmp_path / "sources" / "archived"
    archive.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")
    schema_path = tmp_path / "schema.md"
    schema_path.write_text("测试 schema", encoding="utf-8")

    wiki = WikiIO(str(pages_dir), str(index_path), str(log_path))
    return IngestPipeline(llm=MockLLM(), embedder=MockEmbedder(), vector_store=MockVectorStore(), wiki=wiki, schema_path=str(schema_path), inbox_dir=str(inbox), archive_dir=str(archive))


def test_ingest_single_source(pipeline, tmp_path):
    source_file = tmp_path / "sources" / "inbox" / "test-article.md"
    source_file.write_text("---\ntitle: Test Article\nstatus: raw\n---\nArticle content here.", encoding="utf-8")
    result = pipeline.ingest_file(str(source_file))
    assert result["summary"] == "这是一篇关于知识管理的文章。"
    assert len(result["pages_affected"]) == 2
    assert pipeline.wiki.page_exists("LLM_Wiki")
    assert pipeline.wiki.page_exists("知识图谱")
    assert not source_file.exists()
    archived = tmp_path / "sources" / "archived" / "test-article.md"
    assert archived.exists()


def test_ingest_inbox(pipeline, tmp_path):
    f1 = tmp_path / "sources" / "inbox" / "a.md"
    f1.write_text("---\ntitle: A\nstatus: raw\n---\nContent A", encoding="utf-8")
    f2 = tmp_path / "sources" / "inbox" / "b.md"
    f2.write_text("---\ntitle: B\nstatus: raw\n---\nContent B", encoding="utf-8")
    results = pipeline.ingest_inbox()
    assert len(results) == 2
