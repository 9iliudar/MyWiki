import json
from datetime import date

from engine.prompts import QUERY_PROMPT
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class QueryPipeline:
    def __init__(self, llm: LLMProvider, embedder, vector_store, wiki: WikiIO):
        self.llm = llm
        self.embedder = embedder
        self.vector_store = vector_store
        self.wiki = wiki

    def query(self, question: str) -> dict:
        query_vector = self.embedder.embed(question)
        search_results = self.vector_store.search(query_vector, top_k=10)

        context_pages = []
        for result in search_results:
            page_id = result["id"]
            if self.wiki.page_exists(page_id):
                full_text = self.wiki.get_page_full_text(page_id)
                context_pages.append(full_text)

        context_str = "\n\n---\n\n".join(context_pages) if context_pages else "（Wiki 中暂无相关内容）"

        prompt = QUERY_PROMPT.format(question=question, context_pages=context_str)
        raw_response = self.llm.complete(prompt)
        response = self._parse_json(raw_response)

        saved_page = None

        if response.get("should_save") and response.get("new_page"):
            page_data = response["new_page"]
            if page_data.get("name"):
                today = date.today().isoformat()
                fm = {
                    "title": page_data["title"],
                    "created": today, "updated": today,
                    "sources": [], "related": page_data.get("related", []),
                    "tags": page_data.get("tags", []),
                    "evolution": [f"{today}: 从 query 反哺创建"],
                }
                self.wiki.write_page(page_data["name"], fm, page_data["content"])
                full_text = self.wiki.get_page_full_text(page_data["name"])
                vector = self.embedder.embed(full_text)
                self.vector_store.upsert(page_data["name"], vector, {"title": page_data["title"], "tags": page_data.get("tags", [])})
                saved_page = page_data["name"]

        affected = [saved_page] if saved_page else []
        self.wiki.append_log(operation="query", source="", affected_pages=affected, summary=f"Q: {question[:50]}")

        return {"answer": response.get("answer", ""), "saved_page": saved_page, "sources": [r["id"] for r in search_results]}

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
