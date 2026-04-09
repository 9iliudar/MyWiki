"""MCP Server exposing Wiki engine tools for VS Code integration."""
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from engine.config import load_config
from engine.llm import create_llm_provider
from engine.embed import VectorStore, Embedder
from engine.wiki_io import WikiIO
from engine.ingest import IngestPipeline
from engine.query import QueryPipeline
from engine.lint import LintPipeline

mcp = FastMCP("wiki-engine", instructions="LLM Wiki 知识进化引擎。提供知识消化(ingest)、查询(query)和巡检(lint)三个工具。当对话中出现新知识时调用 wiki_ingest，当用户询问已有知识时调用 wiki_query。")

_components = {}


def _get_components():
    if not _components:
        config = load_config()
        _components["config"] = config
        _components["llm"] = create_llm_provider(config)
        _components["embedder"] = Embedder(
            api_key=config["embedding"].get("api_key", ""),
            model=config["embedding"]["model"],
            base_url=config["embedding"].get("base_url"),
            provider=config["embedding"].get("provider", "local"),
        )
        _components["vector_store"] = VectorStore(
            path=config["qdrant"]["path"],
            dimension=config["embedding"].get("dimensions", 1536),
        )
        _components["wiki"] = WikiIO(
            pages_dir=config["wiki"]["pages_dir"],
            index_path=config["wiki"]["index_path"],
            log_path=config["wiki"]["log_path"],
            candidates_dir=config["wiki"].get("candidates_dir"),
        )
    return _components


def handle_ingest(content: str, title: str = "", llm=None, embedder=None, vector_store=None, wiki_env: dict = None) -> str:
    if wiki_env:
        wiki = WikiIO(
            wiki_env["pages_dir"],
            wiki_env["index_path"],
            wiki_env["log_path"],
            wiki_env.get("candidates_dir"),
        )
        pipeline = IngestPipeline(
            llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki,
            schema_path=wiki_env["schema_path"],
            inbox_dir=wiki_env["inbox_dir"],
            archive_dir=wiki_env["archive_dir"],
            max_auto_pages=wiki_env.get("max_auto_pages", 2),
        )
        inbox_dir = Path(wiki_env["inbox_dir"])
    else:
        c = _get_components()
        llm, embedder, vector_store = c["llm"], c["embedder"], c["vector_store"]
        wiki = c["wiki"]
        config = c["config"]
        pipeline = IngestPipeline(
            llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki,
            schema_path=config["wiki"]["schema_path"],
            inbox_dir=config["sources"]["inbox_dir"],
            archive_dir=config["sources"]["archive_dir"],
            max_auto_pages=config["ingest"].get("max_auto_pages", 2),
        )
        inbox_dir = Path(config["sources"]["inbox_dir"])

    if not title:
        title = f"conversation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    source_file = inbox_dir / f"{title}.md"
    source_file.write_text(
        f"---\ntitle: {title}\ndate_added: {datetime.now().strftime('%Y-%m-%d')}\ntype: conversation\nstatus: raw\n---\n\n{content}",
        encoding="utf-8",
    )

    result = pipeline.ingest_file(str(source_file))
    pages = ", ".join(result["pages_affected"])
    candidate_count = len(result.get("candidate_concepts", []))
    return f"已消化，更新了 {len(result['pages_affected'])} 个页面：{pages}\n候选概念：{candidate_count}\n摘要：{result['summary']}"


def handle_query(question: str, llm=None, embedder=None, vector_store=None, wiki_env: dict = None) -> str:
    if wiki_env:
        wiki = WikiIO(wiki_env["pages_dir"], wiki_env["index_path"], wiki_env["log_path"])
        pipeline = QueryPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    else:
        c = _get_components()
        pipeline = QueryPipeline(llm=c["llm"], embedder=c["embedder"], vector_store=c["vector_store"], wiki=c["wiki"])

    result = pipeline.query(question)
    answer = result["answer"]
    if result.get("saved_page"):
        answer += f"\n\n📝 已保存新页面：{result['saved_page']}"
    if result.get("sources"):
        answer += f"\n📖 参考页面：{', '.join(result['sources'])}"
    return answer


def handle_lint(llm=None, embedder=None, vector_store=None, wiki_env: dict = None) -> str:
    if wiki_env:
        wiki = WikiIO(wiki_env["pages_dir"], wiki_env["index_path"], wiki_env["log_path"])
        pipeline = LintPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    else:
        c = _get_components()
        pipeline = LintPipeline(llm=c["llm"], embedder=c["embedder"], vector_store=c["vector_store"], wiki=c["wiki"])

    result = pipeline.run()
    lines = [f"发现 {len(result['findings'])} 个问题，修正了 {result['fixes_applied']} 个。"]
    for f in result.get("findings", []):
        lines.append(f"  - [{f.get('type', '未知')}] {f.get('description', '')}")
    return "\n".join(lines)


@mcp.tool()
def wiki_ingest(content: str, title: str = "") -> str:
    """消化新知识到 Wiki。当对话中出现值得记录的新知识、概念或见解时调用此工具。

    Args:
        content: 要消化的知识内容（文本）
        title: 来源标题（可选，默认自动生成）
    """
    return handle_ingest(content, title)


@mcp.tool()
def wiki_query(question: str) -> str:
    """基于 Wiki 已有知识回答问题。当用户询问之前学过的内容、想查阅已有知识时调用此工具。

    Args:
        question: 自然语言问题
    """
    return handle_query(question)


@mcp.tool()
def wiki_lint() -> str:
    """Wiki 健康检查。检查知识库的矛盾、孤岛页面、缺失引用等问题并自动修复。"""
    return handle_lint()


if __name__ == "__main__":
    mcp.run(transport="stdio")
