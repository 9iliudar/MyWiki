import json
from datetime import date

from engine.prompts import LINT_PROMPT
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class LintPipeline:
    def __init__(self, llm: LLMProvider, embedder, vector_store, wiki: WikiIO):
        self.llm = llm
        self.embedder = embedder
        self.vector_store = vector_store
        self.wiki = wiki

    def run(self) -> dict:
        all_pages = self.wiki.read_all_pages()
        if not all_pages:
            return {"findings": [], "fixes_applied": 0}

        pages_text = self._format_pages_for_prompt(all_pages)
        prompt = LINT_PROMPT.format(all_pages=pages_text)
        raw_response = self.llm.complete(prompt)
        response = self._parse_json(raw_response)

        findings = response.get("findings", [])
        fixes = response.get("fixes", [])
        today = date.today().isoformat()
        pages_affected = []

        for fix in fixes:
            action = fix.get("action")
            page_name = fix.get("page_name")

            if action == "update" and page_name and self.wiki.page_exists(page_name):
                page = self.wiki.read_page(page_name)
                fm = page["frontmatter"]
                content = page["content"]

                if fix.get("new_related"):
                    fm["related"] = list(set(fm.get("related", []) + fix["new_related"]))
                if fix.get("new_tags"):
                    fm["tags"] = list(set(fm.get("tags", []) + fix["new_tags"]))
                if fix.get("new_title"):
                    fm["title"] = fix["new_title"]
                if fix.get("new_content"):
                    content = fix["new_content"]

                fm["updated"] = today
                evolution = fm.get("evolution", [])
                evolution.append(f"{today}: Lint 修正 - {fix.get('action')}")
                fm["evolution"] = evolution

                self.wiki.write_page(page_name, fm, content)
                pages_affected.append(page_name)

                full_text = self.wiki.get_page_full_text(page_name)
                vector = self.embedder.embed(full_text)
                self.vector_store.upsert(page_name, vector, {"title": fm["title"], "tags": fm.get("tags", [])})

            elif action == "create" and page_name and not self.wiki.page_exists(page_name):
                fm = {"title": fix.get("new_title", page_name), "created": today, "updated": today, "sources": [], "related": fix.get("new_related", []), "tags": fix.get("new_tags", []), "evolution": [f"{today}: Lint 自动创建"]}
                self.wiki.write_page(page_name, fm, fix.get("new_content", ""))
                pages_affected.append(page_name)
                full_text = self.wiki.get_page_full_text(page_name)
                vector = self.embedder.embed(full_text)
                self.vector_store.upsert(page_name, vector, {"title": fm["title"], "tags": fm.get("tags", [])})

            elif action == "merge" and fix.get("merge_into"):
                if self.wiki.page_exists(page_name) and self.wiki.page_exists(fix["merge_into"]):
                    source_page = self.wiki.read_page(page_name)
                    target_page = self.wiki.read_page(fix["merge_into"])
                    merged_content = target_page["content"] + "\n\n" + source_page["content"]
                    target_fm = target_page["frontmatter"]
                    target_fm["updated"] = today
                    target_fm["evolution"] = target_fm.get("evolution", []) + [f"{today}: 合并自 {page_name}"]
                    self.wiki.write_page(fix["merge_into"], target_fm, merged_content)
                    pages_affected.append(fix["merge_into"])

        if response.get("index_updates"):
            self.wiki.write_index(response["index_updates"])

        self.wiki.append_log(operation="lint", source="", affected_pages=pages_affected, summary=f"发现 {len(findings)} 个问题，应用 {len(pages_affected)} 个修正")

        return {"findings": findings, "fixes_applied": len(pages_affected), "pages_affected": pages_affected}

    @staticmethod
    def _format_pages_for_prompt(pages: list[dict]) -> str:
        parts = []
        for page in pages:
            fm = page["frontmatter"]
            parts.append(f"### {fm.get('title', page['name'])}\n标签: {', '.join(fm.get('tags', []))}\n关联: {', '.join(fm.get('related', []))}\n\n{page['content']}")
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _parse_json(text: str) -> dict:
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()
        return json.loads(text)
