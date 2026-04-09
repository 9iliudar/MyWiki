import json
import shutil
import tempfile
from pathlib import Path

from engine.ingest import IngestPipeline
from engine.llm import LLMProvider
from engine.wiki_io import WikiIO


class RepairingLLM(LLMProvider):
    def __init__(self, repaired_response: str):
        self.repaired_response = repaired_response
        self.calls = []

    def complete(self, prompt: str, context: str = "") -> str:
        self.calls.append(prompt)
        return self.repaired_response


class DummyEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.1, 0.1, 0.1]


class DummyVectorStore:
    def upsert(self, page_id, vector, metadata):
        return None


def test_ingest_repairs_truncated_pages():
    workspace_tmp = Path(tempfile.mkdtemp(dir=Path.cwd()))
    try:
        pages_dir = workspace_tmp / "wiki" / "pages"
        pages_dir.mkdir(parents=True)
        inbox_dir = workspace_tmp / "sources" / "inbox"
        inbox_dir.mkdir(parents=True)
        archive_dir = workspace_tmp / "sources" / "archived"
        archive_dir.mkdir(parents=True)
        index_path = workspace_tmp / "wiki" / "index.md"
        index_path.write_text("# index\n", encoding="utf-8")
        log_path = workspace_tmp / "wiki" / "log.md"
        log_path.write_text("# log\n", encoding="utf-8")
        schema_path = workspace_tmp / "schema.md"
        schema_path.write_text("schema", encoding="utf-8")

        repaired_response = json.dumps(
            {
                "summary": "fixed",
                "pages": [
                    {
                        "name": "Boundary-Design",
                        "title": "Boundary Design",
                        "tags": ["AI"],
                        "related": ["[[Constraint-Design]]", "[[Output-Boundary]]"],
                        "content": (
                            "## 定义\n\n"
                            "边界设计用于明确 AI 系统允许做什么、依赖什么、以什么格式交付结果。"
                            "它不是一句空泛的不要乱来，而是把目标、权限、数据、流程和质量全部提前设定清楚。"
                            "这样即使模型发挥一般，系统也能在护栏内给出可用结果。"
                            "\n\n## 落地方式\n\n"
                            "一个可运行的边界设计，通常会同时约束权限范围、输出结构、异常处理和验收标准。"
                            "只有当这些约束能被程序检查，而不是只写在口头共识里，系统才会真正稳定。"
                        ),
                        "is_new": True,
                    }
                ],
                "candidate_concepts": [],
                "index_updates": "",
            },
            ensure_ascii=False,
        )

        pipeline = IngestPipeline(
            llm=RepairingLLM(repaired_response),
            embedder=DummyEmbedder(),
            vector_store=DummyVectorStore(),
            wiki=WikiIO(str(pages_dir), str(index_path), str(log_path)),
            schema_path=str(schema_path),
            inbox_dir=str(inbox_dir),
            archive_dir=str(archive_dir),
        )

        broken_response = json.dumps(
            {
                "summary": "broken",
                "pages": [
                    {
                        "name": "Boundary-Design",
                        "title": "Boundary Design",
                        "tags": [],
                        "related": [],
                        "content": "## 核心理念\n\n边界设计的核心不是",
                        "is_new": True,
                    }
                ],
                "candidate_concepts": [],
                "index_updates": "",
            },
            ensure_ascii=False,
        )

        response = pipeline._parse_and_validate_response(
            broken_response,
            source_content="Boundary Design discussion",
        )

        assert response["summary"] == "fixed"
        assert len(pipeline.llm.calls) == 1
        assert response["pages"][0]["content"].endswith("系统才会真正稳定。")
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)
