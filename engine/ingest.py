import re
import shutil
from datetime import date
from pathlib import Path

import frontmatter

from engine.json_utils import parse_llm_json
from engine.llm import LLMProvider
from engine.prompts import INGEST_PROMPT, INGEST_REPAIR_PROMPT
from engine.wiki_io import WikiIO


MIN_CONTENT_CHARS = 180


class IngestPipeline:
    def __init__(
        self,
        llm: LLMProvider,
        embedder,
        vector_store,
        wiki: WikiIO,
        schema_path: str,
        inbox_dir: str,
        archive_dir: str,
        max_auto_pages: int = 2,
    ):
        self.llm = llm
        self.embedder = embedder
        self.vector_store = vector_store
        self.wiki = wiki
        self.schema = Path(schema_path).read_text(encoding="utf-8")
        self.inbox_dir = Path(inbox_dir)
        self.archive_dir = Path(archive_dir)
        self.max_auto_pages = max(1, max_auto_pages)

    def ingest_file(self, source_path: str, category_override: str | None = None) -> dict:
        source_path = Path(source_path)
        source_content = source_path.read_text(encoding="utf-8")
        source_post = frontmatter.load(str(source_path))
        source_category = self.wiki.normalize_category(
            category_override or source_post.metadata.get("category") or self.wiki.default_category
        )
        existing_pages = ", ".join(self.wiki.list_pages()) or "（暂无页面）"

        schema_short = self.schema[:800] if len(self.schema) > 800 else self.schema
        prompt = INGEST_PROMPT.format(
            source_content=source_content,
            existing_pages=existing_pages,
            schema=schema_short,
        )
        raw_response = self.llm.complete(prompt)
        response = self._parse_and_validate_response(raw_response, source_content)

        mastered_pages = self._get_mastered_pages(response)
        candidate_concepts = response.get("candidate_concepts", [])
        limited_mastered_pages = mastered_pages[: self.max_auto_pages]
        overflow_candidates = [
            self._to_candidate(page, "ready", "本轮正式内化名额已满，暂存为候选概念。")
            for page in mastered_pages[self.max_auto_pages :]
        ]
        candidate_concepts = candidate_concepts + overflow_candidates

        today = date.today().isoformat()
        pages_affected = []

        for page_data in limited_mastered_pages:
            name = page_data["name"]
            fm = {
                "title": page_data["title"],
                "created": today if page_data.get("is_new", True) else self._get_existing_created(name),
                "updated": today,
                "sources": [f"sources/archived/{source_path.name}"],
                "related": page_data.get("related", []),
                "tags": page_data.get("tags", []),
                "category": source_category,
                "evolution": [f"{today}: {'初始创建' if page_data.get('is_new', True) else '更新内容'}"],
            }

            if not page_data.get("is_new") and self.wiki.page_exists(name):
                existing = self.wiki.read_page(name)
                fm["created"] = existing["frontmatter"].get("created", today)
                fm["sources"] = list(set(existing["frontmatter"].get("sources", []) + fm["sources"]))
                fm["related"] = list(set(existing["frontmatter"].get("related", []) + fm["related"]))
                fm["tags"] = list(set(existing["frontmatter"].get("tags", []) + fm["tags"]))
                fm["evolution"] = existing["frontmatter"].get("evolution", []) + fm["evolution"]

            self.wiki.write_page(name, fm, page_data["content"], category=source_category)
            pages_affected.append(name)

            full_text = self.wiki.get_page_full_text(name)
            vector = self.embedder.embed(full_text)
            self.vector_store.upsert(name, vector, {"title": page_data["title"], "tags": page_data.get("tags", [])})

        self._backfill_related_links(pages_affected)

        if response.get("index_updates") and pages_affected:
            current_index = self.wiki.read_index()
            self.wiki.write_index(current_index + "\n" + response["index_updates"])

        if candidate_concepts:
            self.wiki.write_candidate_snapshot(
                source_name=source_path.name,
                summary=response.get("summary", ""),
                mastered_pages=pages_affected,
                candidates=candidate_concepts,
                category=source_category,
            )

        self.wiki.append_log(
            operation="ingest",
            source=source_path.name,
            affected_pages=pages_affected,
            summary=response.get("summary", ""),
        )
        self._archive_source(source_path)

        return {
            "summary": response.get("summary", ""),
            "pages_affected": pages_affected,
            "candidate_concepts": candidate_concepts,
            "category": source_category,
        }

    def ingest_inbox(self, category_override: str | None = None) -> list[dict]:
        results = []
        for source_file in sorted(self.inbox_dir.glob("*.md")):
            results.append(self.ingest_file(str(source_file), category_override=category_override))
        return results

    def _archive_source(self, source_path: Path):
        dest = self.archive_dir / source_path.name
        if source_path.resolve() != dest.resolve():
            shutil.move(str(source_path), str(dest))
        post = frontmatter.load(str(dest))
        post.metadata["status"] = "digested"
        dest.write_text(frontmatter.dumps(post), encoding="utf-8")

    def _backfill_related_links(self, pages_affected: list[str]):
        all_page_names = set(self.wiki.list_pages())
        title_to_name = {}
        for page_name in all_page_names:
            if self.wiki.page_exists(page_name):
                page = self.wiki.read_page(page_name)
                title_to_name[page["frontmatter"].get("title", page_name)] = page_name
                title_to_name[page_name] = page_name

        for page_name in pages_affected:
            if not self.wiki.page_exists(page_name):
                continue

            page = self.wiki.read_page(page_name)
            content = page["content"]
            links = re.findall(r"\[\[([^\]]+)\]\]", content)
            resolved = set()
            for link in links:
                target = title_to_name.get(link, link)
                if target in all_page_names and target != page_name:
                    resolved.add(f"[[{target}]]")

            existing_related = set(page["frontmatter"].get("related", []))
            merged = sorted(existing_related | resolved)
            if merged != sorted(existing_related):
                page["frontmatter"]["related"] = merged
                self.wiki.write_page(page_name, page["frontmatter"], content)

    def _get_existing_created(self, name: str) -> str:
        if self.wiki.page_exists(name):
            page = self.wiki.read_page(name)
            return page["frontmatter"].get("created", date.today().isoformat())
        return date.today().isoformat()

    def _parse_and_validate_response(self, raw_response: str, source_content: str) -> dict:
        response = self._parse_json(raw_response)
        issues = self._collect_page_issues(response)
        if not issues:
            return response

        repair_prompt = INGEST_REPAIR_PROMPT.format(
            source_content=source_content,
            raw_response=raw_response,
        )
        repaired_raw_response = self.llm.complete(repair_prompt)
        repaired_response = self._parse_json(repaired_raw_response)
        repaired_issues = self._collect_page_issues(repaired_response)
        if repaired_issues:
            issues_text = "; ".join(repaired_issues)
            raise ValueError(f"Ingest response remained invalid after repair: {issues_text}")
        return repaired_response

    @staticmethod
    def _parse_json(text: str) -> dict:
        return parse_llm_json(text)

    def _get_mastered_pages(self, response: dict) -> list[dict]:
        pages = response.get("mastered_pages")
        if pages is None:
            pages = response.get("pages", [])
        return pages or []

    def _collect_page_issues(self, response: dict) -> list[str]:
        issues = []
        pages = self._get_mastered_pages(response)
        if not pages:
            return ["response did not include any mastered pages"]

        for page in pages:
            name = page.get("name") or "<unknown>"
            content = (page.get("content") or "").strip()
            if len(content) < MIN_CONTENT_CHARS:
                issues.append(f"{name}: content too short ({len(content)} chars)")
            if len(content) < MIN_CONTENT_CHARS * 2 and self._looks_truncated(content):
                issues.append(f"{name}: content looks truncated")

        if "candidate_concepts" not in response:
            issues.append("response did not include candidate_concepts")

        return issues

    @staticmethod
    def _looks_truncated(content: str) -> bool:
        if not content:
            return True

        last_nonempty_line = ""
        for line in reversed(content.splitlines()):
            if line.strip():
                last_nonempty_line = line.strip()
                break

        if not last_nonempty_line:
            return True
        if last_nonempty_line in {"-", "*"}:
            return True
        if re.search(r"[:：,，、(（]$", last_nonempty_line):
            return True
        if re.match(r"^#+\s*$", last_nonempty_line):
            return True
        return not re.search(r"[。！？.!?）)】\]`\"]$", last_nonempty_line)

    @staticmethod
    def _to_candidate(page: dict, readiness: str, reason: str) -> dict:
        return {
            "name": page.get("name", ""),
            "title": page.get("title", page.get("name", "")),
            "readiness": readiness,
            "reason": reason,
        }
