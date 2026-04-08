import json
import shutil
from datetime import date
from pathlib import Path

import frontmatter

from engine.prompts import INGEST_PROMPT
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider
from engine.json_utils import parse_llm_json


class IngestPipeline:
    def __init__(self, llm: LLMProvider, embedder, vector_store, wiki: WikiIO, schema_path: str, inbox_dir: str, archive_dir: str):
        self.llm = llm
        self.embedder = embedder
        self.vector_store = vector_store
        self.wiki = wiki
        self.schema = Path(schema_path).read_text(encoding="utf-8")
        self.inbox_dir = Path(inbox_dir)
        self.archive_dir = Path(archive_dir)

    def ingest_file(self, source_path: str) -> dict:
        source_path = Path(source_path)
        source_content = source_path.read_text(encoding="utf-8")
        existing_pages = ", ".join(self.wiki.list_pages()) or "（暂无页面）"

        # Truncate schema to essential rules to reduce prompt size
        schema_short = self.schema[:800] if len(self.schema) > 800 else self.schema
        prompt = INGEST_PROMPT.format(source_content=source_content, existing_pages=existing_pages, schema=schema_short)
        raw_response = self.llm.complete(prompt)
        response = self._parse_json(raw_response)

        today = date.today().isoformat()
        pages_affected = []

        for page_data in response.get("pages", []):
            name = page_data["name"]
            fm = {
                "title": page_data["title"],
                "created": today if page_data.get("is_new", True) else self._get_existing_created(name),
                "updated": today,
                "sources": [f"sources/archived/{source_path.name}"],
                "related": page_data.get("related", []),
                "tags": page_data.get("tags", []),
                "evolution": [f"{today}: {'初始创建' if page_data.get('is_new', True) else '更新内容'}"],
            }

            if not page_data.get("is_new") and self.wiki.page_exists(name):
                existing = self.wiki.read_page(name)
                fm["created"] = existing["frontmatter"].get("created", today)
                fm["sources"] = list(set(existing["frontmatter"].get("sources", []) + fm["sources"]))
                fm["related"] = list(set(existing["frontmatter"].get("related", []) + fm["related"]))
                fm["tags"] = list(set(existing["frontmatter"].get("tags", []) + fm["tags"]))
                fm["evolution"] = existing["frontmatter"].get("evolution", []) + fm["evolution"]

            self.wiki.write_page(name, fm, page_data["content"])
            pages_affected.append(name)

            full_text = self.wiki.get_page_full_text(name)
            vector = self.embedder.embed(full_text)
            self.vector_store.upsert(name, vector, {"title": page_data["title"], "tags": page_data.get("tags", [])})

        if response.get("index_updates"):
            current_index = self.wiki.read_index()
            self.wiki.write_index(current_index + "\n" + response["index_updates"])

        self.wiki.append_log(operation="ingest", source=source_path.name, affected_pages=pages_affected, summary=response.get("summary", ""))
        self._archive_source(source_path)

        return {"summary": response.get("summary", ""), "pages_affected": pages_affected}

    def ingest_inbox(self) -> list[dict]:
        results = []
        for source_file in sorted(self.inbox_dir.glob("*.md")):
            result = self.ingest_file(str(source_file))
            results.append(result)
        return results

    def _archive_source(self, source_path: Path):
        dest = self.archive_dir / source_path.name
        shutil.move(str(source_path), str(dest))
        post = frontmatter.load(str(dest))
        post.metadata["status"] = "digested"
        dest.write_text(frontmatter.dumps(post), encoding="utf-8")

    def _get_existing_created(self, name: str) -> str:
        if self.wiki.page_exists(name):
            page = self.wiki.read_page(name)
            return page["frontmatter"].get("created", date.today().isoformat())
        return date.today().isoformat()

    @staticmethod
    def _parse_json(text: str) -> dict:
        return parse_llm_json(text)
