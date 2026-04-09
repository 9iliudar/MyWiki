from datetime import datetime
from pathlib import Path

import frontmatter


class WikiIO:
    def __init__(self, pages_dir: str, index_path: str, log_path: str, candidates_dir: str | None = None):
        self.pages_dir = Path(pages_dir)
        self.index_path = Path(index_path)
        self.log_path = Path(log_path)
        self.candidates_dir = Path(candidates_dir) if candidates_dir else None
        self.default_category = "AI"

    def write_page(self, name: str, fm: dict, content: str, category: str | None = None):
        existing_path = self.get_page_path(name)
        page_category = self.normalize_category(
            category or fm.get("category") or (existing_path.parent.relative_to(self.pages_dir).as_posix() if existing_path else self.default_category)
        )
        path = self.pages_dir / page_category / f"{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        fm["category"] = page_category
        post = frontmatter.Post(content, **fm)
        path.write_text(frontmatter.dumps(post), encoding="utf-8")

    def read_page(self, name: str) -> dict:
        path = self.get_page_path(name)
        if path is None:
            raise FileNotFoundError(f"Page not found: {name}")
        post = frontmatter.load(str(path))
        metadata = dict(post.metadata)
        metadata.setdefault("category", path.parent.relative_to(self.pages_dir).as_posix())
        return {"name": name, "frontmatter": metadata, "content": post.content, "path": str(path)}

    def page_exists(self, name: str) -> bool:
        return self.get_page_path(name) is not None

    def list_pages(self) -> list[str]:
        return sorted(p.stem for p in self.pages_dir.rglob("*.md"))

    def read_all_pages(self) -> list[dict]:
        return [self.read_page(name) for name in self.list_pages()]

    def append_log(self, operation: str, source: str, affected_pages: list[str], summary: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## {now}\n\n**操作**: {operation}\n"
        if source:
            entry += f"**素材**: {source}\n"
        entry += f"**影响页面**: {', '.join(affected_pages)}\n**摘要**: {summary}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def read_log(self) -> str:
        return self.log_path.read_text(encoding="utf-8")

    def write_candidate_snapshot(
        self,
        source_name: str,
        summary: str,
        mastered_pages: list[str],
        candidates: list[dict],
        category: str | None = None,
    ):
        if not self.candidates_dir:
            return

        candidate_category = self.normalize_category(category or self.default_category)
        target_dir = self.candidates_dir / candidate_category
        target_dir.mkdir(parents=True, exist_ok=True)
        snapshot_name = Path(source_name).stem
        snapshot_path = target_dir / f"{snapshot_name}.md"
        created = datetime.now().strftime("%Y-%m-%d %H:%M")
        frontmatter_data = {
            "source": source_name,
            "created": created,
            "mastered_pages": mastered_pages,
            "candidate_count": len(candidates),
            "status": "pending_review",
            "category": candidate_category,
        }

        lines = ["# 候选概念", "", f"摘要：{summary}", ""]
        if mastered_pages:
            lines.append(f"已自动内化：{', '.join(mastered_pages)}")
            lines.append("")

        for candidate in candidates:
            title = candidate.get("title") or candidate.get("name") or "未命名概念"
            readiness = candidate.get("readiness", "candidate")
            reason = candidate.get("reason", "")
            lines.append(f"## {title}")
            lines.append("")
            lines.append(f"- readiness: {readiness}")
            if candidate.get("name"):
                lines.append(f"- name: {candidate['name']}")
            if reason:
                lines.append(f"- reason: {reason}")
            lines.append("")

        post = frontmatter.Post("\n".join(lines).rstrip() + "\n", **frontmatter_data)
        snapshot_path.write_text(frontmatter.dumps(post), encoding="utf-8")

    def write_index(self, content: str):
        self.index_path.write_text(content, encoding="utf-8")

    def read_index(self) -> str:
        return self.index_path.read_text(encoding="utf-8")

    def get_page_full_text(self, name: str) -> str:
        page = self.read_page(name)
        fm = page["frontmatter"]
        lines = [f"# {fm.get('title', name)}", ""]
        if fm.get("category"):
            lines.append(f"分类: {fm['category']}")
        if fm.get("tags"):
            lines.append(f"标签: {', '.join(fm['tags'])}")
        if fm.get("related"):
            lines.append(f"关联: {', '.join(fm['related'])}")
        lines.append("")
        lines.append(page["content"])
        return "\n".join(lines)

    def get_page_path(self, name: str) -> Path | None:
        direct = self.pages_dir / f"{name}.md"
        if direct.exists():
            return direct
        matches = list(self.pages_dir.rglob(f"{name}.md"))
        return matches[0] if matches else None

    @staticmethod
    def normalize_category(category: str | None) -> str:
        value = (category or "").strip().strip("/\\")
        return value or "AI"
