import argparse
import sys
from pathlib import Path

from engine.config import load_config
from engine.llm import create_llm_provider
from engine.embed import VectorStore, Embedder
from engine.wiki_io import WikiIO
from engine.ingest import IngestPipeline
from engine.query import QueryPipeline
from engine.lint import LintPipeline


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
    )
    return llm, embedder, vector_store, wiki


def cmd_ingest(args, config):
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = IngestPipeline(
        llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki,
        schema_path=config["wiki"]["schema_path"],
        inbox_dir=config["sources"]["inbox_dir"],
        archive_dir=config["sources"]["archive_dir"],
    )
    if args.file:
        result = pipeline.ingest_file(args.file)
        print(f"已消化: {args.file}")
        print(f"摘要: {result['summary']}")
        print(f"影响页面: {', '.join(result['pages_affected'])}")
    else:
        results = pipeline.ingest_inbox()
        print(f"已消化 {len(results)} 份素材")
        for r in results:
            print(f"  - {r['summary'][:60]}... ({len(r['pages_affected'])} 页面)")


def cmd_query(args, config):
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = QueryPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    result = pipeline.query(args.question)
    print(f"\n{result['answer']}\n")
    if result["saved_page"]:
        print(f"[已保存新页面: {result['saved_page']}]")
    if result["sources"]:
        print(f"[参考页面: {', '.join(result['sources'])}]")


def cmd_lint(args, config):
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = LintPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    result = pipeline.run()
    print(f"发现 {len(result['findings'])} 个问题")
    for f in result["findings"]:
        print(f"  [{f['type']}] {f['description']}")
    print(f"已应用 {result['fixes_applied']} 个修正")


def cmd_watch(args, config):
    from engine.watch import start_watching
    print(f"开始监听 {config['sources']['inbox_dir']}...")
    print("按 Ctrl+C 停止")
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = IngestPipeline(
        llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki,
        schema_path=config["wiki"]["schema_path"],
        inbox_dir=config["sources"]["inbox_dir"],
        archive_dir=config["sources"]["archive_dir"],
    )
    start_watching(config["sources"]["inbox_dir"], pipeline)


def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 知识进化引擎")
    parser.add_argument("--config", default=None, help="配置文件路径")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="消化新素材")
    ingest_parser.add_argument("--file", help="指定素材文件路径（不指定则处理整个 inbox）")

    query_parser = subparsers.add_parser("query", help="查询知识库")
    query_parser.add_argument("question", help="问题")

    subparsers.add_parser("lint", help="巡检知识库")
    subparsers.add_parser("watch", help="监听 inbox 文件夹")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config(args.config)
    commands = {"ingest": cmd_ingest, "query": cmd_query, "lint": cmd_lint, "watch": cmd_watch}
    commands[args.command](args, config)


if __name__ == "__main__":
    main()
