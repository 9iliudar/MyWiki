import pytest
from engine.wiki_io import WikiIO


@pytest.fixture
def wiki(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")
    return WikiIO(str(pages_dir), str(index_path), str(log_path))


def test_write_and_read_page(wiki):
    frontmatter = {"title": "RAG（检索增强生成）", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": ["AI"], "evolution": ["2026-04-07: 初始创建"]}
    wiki.write_page("RAG", frontmatter, "这是正文内容。")
    page = wiki.read_page("RAG")
    assert page["frontmatter"]["title"] == "RAG（检索增强生成）"
    assert page["content"] == "这是正文内容。"


def test_list_pages(wiki):
    fm = {"title": "A", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}
    wiki.write_page("A", fm, "Content A")
    wiki.write_page("B", {**fm, "title": "B"}, "Content B")
    assert set(wiki.list_pages()) == {"A", "B"}


def test_append_log(wiki):
    wiki.append_log("ingest", "test-source.md", ["RAG", "LLM"], "测试消化操作")
    log_content = wiki.read_log()
    assert "ingest" in log_content
    assert "RAG" in log_content
    assert "测试消化操作" in log_content


def test_page_exists(wiki):
    assert not wiki.page_exists("Nope")
    wiki.write_page("Nope", {"title": "Nope", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}, "x")
    assert wiki.page_exists("Nope")


def test_read_all_pages(wiki):
    fm = {"title": "X", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": ["[[Y]]"], "tags": [], "evolution": []}
    wiki.write_page("X", fm, "Content X")
    wiki.write_page("Y", {**fm, "title": "Y", "related": ["[[X]]"]}, "Content Y")
    all_pages = wiki.read_all_pages()
    assert len(all_pages) == 2
    titles = {p["frontmatter"]["title"] for p in all_pages}
    assert titles == {"X", "Y"}


def test_write_page_in_category(wiki):
    fm = {"title": "Finance Note", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}
    wiki.write_page("Finance-Note", fm, "Content", category="Finance")
    page = wiki.read_page("Finance-Note")
    assert page["frontmatter"]["category"] == "Finance"
    assert "Finance" in page["path"]
