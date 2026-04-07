import json
import pytest
from engine.lint import LintPipeline
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class MockLLM(LLMProvider):
    def complete(self, prompt: str, context: str = "") -> str:
        return json.dumps({
            "findings": [
                {"type": "orphan", "description": "Orphan 页面没有被任何页面引用", "affected_pages": ["Orphan"]},
                {"type": "shallow", "description": "Shallow 页面内容过于单薄", "affected_pages": ["Shallow"]},
            ],
            "fixes": [
                {"action": "update", "page_name": "Orphan", "new_title": None, "new_tags": None, "new_related": ["[[Connected]]"], "new_content": None, "merge_into": None},
                {"action": "update", "page_name": "Shallow", "new_title": None, "new_tags": None, "new_related": None, "new_content": "Shallow 是一个概念，用于描述内容不够深入的状态。它与深度学习形成对比。", "merge_into": None},
            ],
            "index_updates": "# 知识导航\n\n## 测试\n\n- [[Connected]] — 已连接\n- [[Orphan]] — 不再孤立\n- [[Shallow]] — 已深化",
        })


class MockEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}
    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = True


@pytest.fixture
def pipeline(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")
    wiki = WikiIO(str(pages_dir), str(index_path), str(log_path))

    fm = {"title": "t", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}
    wiki.write_page("Connected", {**fm, "title": "Connected", "related": ["[[Orphan]]"]}, "A well-connected page.")
    wiki.write_page("Orphan", {**fm, "title": "Orphan"}, "An orphan page.")
    wiki.write_page("Shallow", {**fm, "title": "Shallow"}, "Thin.")

    return LintPipeline(llm=MockLLM(), embedder=MockEmbedder(), vector_store=MockVectorStore(), wiki=wiki)


def test_lint_returns_findings(pipeline):
    result = pipeline.run()
    assert len(result["findings"]) == 2
    types = {f["type"] for f in result["findings"]}
    assert "orphan" in types
    assert "shallow" in types


def test_lint_applies_fixes(pipeline):
    pipeline.run()
    orphan = pipeline.wiki.read_page("Orphan")
    assert "[[Connected]]" in orphan["frontmatter"]["related"]


def test_lint_updates_shallow_content(pipeline):
    pipeline.run()
    shallow = pipeline.wiki.read_page("Shallow")
    assert len(shallow["content"]) > 10


def test_lint_logs_operation(pipeline):
    pipeline.run()
    log = pipeline.wiki.read_log()
    assert "lint" in log
