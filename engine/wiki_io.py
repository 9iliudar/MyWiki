from datetime import datetime
from pathlib import Path

import frontmatter


class WikiIO:
    def __init__(self, pages_dir: str, index_path: str, log_path: str):
        self.pages_dir = Path(pages_dir)
        self.index_path = Path(index_path)
        self.log_path = Path(log_path)

    def write_page(self, name: str, fm: dict, content: str):
        path = self.pages_dir / f"{name}.md"
        post = frontmatter.Post(content, **fm)
        path.write_text(frontmatter.dumps(post), encoding="utf-8")

    def read_page(self, name: str) -> dict:
        path = self.pages_dir / f"{name}.md"
        post = frontmatter.load(str(path))
        return {"name": name, "frontmatter": dict(post.metadata), "content": post.content}

    def page_exists(self, name: str) -> bool:
        return (self.pages_dir / f"{name}.md").exists()

    def list_pages(self) -> list[str]:
        return [p.stem for p in self.pages_dir.glob("*.md")]

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

    def write_index(self, content: str):
        self.index_path.write_text(content, encoding="utf-8")

    def read_index(self) -> str:
        return self.index_path.read_text(encoding="utf-8")

    def get_page_full_text(self, name: str) -> str:
        page = self.read_page(name)
        fm = page["frontmatter"]
        lines = [f"# {fm.get('title', name)}", ""]
        if fm.get("tags"):
            lines.append(f"标签: {', '.join(fm['tags'])}")
        if fm.get("related"):
            lines.append(f"关联: {', '.join(fm['related'])}")
        lines.append("")
        lines.append(page["content"])
        return "\n".join(lines)
