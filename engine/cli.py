import argparse
import sys

from engine.config import load_config
from engine.llm import create_llm_provider
from engine.embed import VectorStore, Embedder
from engine.wiki_io import WikiIO
from engine.ingest import IngestPipeline
from engine.query import QueryPipeline
from engine.lint import LintPipeline


def _safe_print(message: str):
    try:
        print(message)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        fallback = message.encode(encoding, errors="replace").decode(encoding, errors="replace")
        print(fallback)


def _build_components(config: dict):
    llm = create_llm_provider(config)
    embedder = Embedder(
        api_key=config["embedding"].get("api_key", ""),
        model=config["embedding"]["model"],
        base_url=config["embedding"].get("base_url"),
        provider=config["embedding"].get("provider", "local"),
    )
    vector_store = VectorStore(
        path=config["qdrant"]["path"],
        dimension=config["embedding"].get("dimensions", 1536),
    )
    wiki = WikiIO(
        pages_dir=config["wiki"]["pages_dir"],
        index_path=config["wiki"]["index_path"],
        log_path=config["wiki"]["log_path"],
        candidates_dir=config["wiki"].get("candidates_dir"),
    )
    wiki.default_category = config["wiki"].get("default_category", "AI")
    return llm, embedder, vector_store, wiki


def cmd_ingest(args, config):
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = IngestPipeline(
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        wiki=wiki,
        schema_path=config["wiki"]["schema_path"],
        inbox_dir=config["sources"]["inbox_dir"],
        archive_dir=config["sources"]["archive_dir"],
        max_auto_pages=config["ingest"].get("max_auto_pages", 2),
    )
    if args.file:
        result = pipeline.ingest_file(args.file, category_override=args.category)
        _safe_print(f"已消化: {args.file}")
        _safe_print(f"摘要: {result['summary']}")
        _safe_print(f"影响页面: {', '.join(result['pages_affected'])}")
        _safe_print(f"候选概念: {len(result.get('candidate_concepts', []))}")
        _safe_print(f"分类: {result.get('category', config['wiki'].get('default_category', 'AI'))}")
    else:
        results = pipeline.ingest_inbox(category_override=args.category)
        _safe_print(f"已消化 {len(results)} 份素材")
        for result in results:
            _safe_print(
                f"  - {result['summary'][:60]}... "
                f"({len(result['pages_affected'])} 页面, "
                f"{len(result.get('candidate_concepts', []))} 候选概念, "
                f"分类 {result.get('category', config['wiki'].get('default_category', 'AI'))})"
            )


def cmd_query(args, config):
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = QueryPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    result = pipeline.query(args.question)
    _safe_print(f"\n{result['answer']}\n")
    if result["saved_page"]:
        _safe_print(f"[已保存新页面: {result['saved_page']}]")
    if result["sources"]:
        _safe_print(f"[参考页面: {', '.join(result['sources'])}]")


def cmd_lint(args, config):
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = LintPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    result = pipeline.run()
    _safe_print(f"发现 {len(result['findings'])} 个问题")
    for finding in result["findings"]:
        _safe_print(f"  [{finding['type']}] {finding['description']}")
    _safe_print(f"已应用 {result['fixes_applied']} 个修复")


def cmd_watch(args, config):
    from engine.watch import start_watching

    _safe_print(f"开始监听 {config['sources']['inbox_dir']}...")
    _safe_print("按 Ctrl+C 停止")
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = IngestPipeline(
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        wiki=wiki,
        schema_path=config["wiki"]["schema_path"],
        inbox_dir=config["sources"]["inbox_dir"],
        archive_dir=config["sources"]["archive_dir"],
        max_auto_pages=config["ingest"].get("max_auto_pages", 2),
    )
    start_watching(config["sources"]["inbox_dir"], pipeline)


def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 知识进化引擎")
    parser.add_argument("--config", default=None, help="配置文件路径")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="消化新素材")
    ingest_parser.add_argument("--file", help="指定素材文件路径；不指定则处理整个 inbox")
    ingest_parser.add_argument("--category", help="正式知识写入的分类目录，例如 AI / Finance / Literature")

    query_parser = subparsers.add_parser("query", help="查询知识库")
    query_parser.add_argument("question", help="问题")

    subparsers.add_parser("lint", help="巡检知识库")
    subparsers.add_parser("watch", help="监听 inbox 文件夹")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config(args.config)
    commands = {
        "ingest": cmd_ingest,
        "query": cmd_query,
        "lint": cmd_lint,
        "watch": cmd_watch,
    }
    commands[args.command](args, config)


if __name__ == "__main__":
    main()
