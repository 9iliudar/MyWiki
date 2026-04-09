import json
import shutil
import tempfile
from pathlib import Path

from engine.ingest import IngestPipeline
from engine.llm import LLMProvider
from engine.wiki_io import WikiIO


class StaticLLM(LLMProvider):
    def __init__(self, response: str):
        self.response = response

    def complete(self, prompt: str, context: str = "") -> str:
        return self.response


class DummyEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.1, 0.1, 0.1]


class DummyVectorStore:
    def __init__(self):
        self.upserts = []

    def upsert(self, page_id, vector, metadata):
        self.upserts.append((page_id, metadata))


def test_ingest_limits_mastered_pages_and_stores_candidates():
    workspace_tmp = Path(tempfile.mkdtemp(dir=Path.cwd()))
    try:
        pages_dir = workspace_tmp / "wiki" / "pages"
        pages_dir.mkdir(parents=True)
        candidates_dir = workspace_tmp / "wiki" / "candidates"
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

        source_file = inbox_dir / "topic.md"
        source_file.write_text("---\ntitle: topic\nstatus: raw\n---\ncontent", encoding="utf-8")

        payload = {
            "summary": "summary",
            "mastered_pages": [
                {
                    "name": "Boundary-Design",
                    "title": "Boundary Design",
                    "tags": ["AI"],
                    "related": ["[[Constraint-Design]]"],
                    "content": ("边界设计。") * 80,
                    "is_new": True,
                },
                {
                    "name": "Permission-Boundary",
                    "title": "Permission Boundary",
                    "tags": ["AI"],
                    "related": ["[[Boundary-Design]]"],
                    "content": ("权限边界。") * 80,
                    "is_new": True,
                },
                {
                    "name": "Output-Boundary",
                    "title": "Output Boundary",
                    "tags": ["AI"],
                    "related": ["[[Boundary-Design]]"],
                    "content": ("输出边界。") * 80,
                    "is_new": True,
                },
            ],
            "candidate_concepts": [
                {
                    "name": "Quality-Boundary",
                    "title": "Quality Boundary",
                    "readiness": "partial",
                    "reason": "用户只接触到这个概念，还没真正掌握。",
                }
            ],
            "index_updates": "",
        }

        vector_store = DummyVectorStore()
        pipeline = IngestPipeline(
            llm=StaticLLM(json.dumps(payload, ensure_ascii=False)),
            embedder=DummyEmbedder(),
            vector_store=vector_store,
            wiki=WikiIO(str(pages_dir), str(index_path), str(log_path), str(candidates_dir)),
            schema_path=str(schema_path),
            inbox_dir=str(inbox_dir),
            archive_dir=str(archive_dir),
            max_auto_pages=2,
        )

        result = pipeline.ingest_file(str(source_file))

        assert result["pages_affected"] == ["Boundary-Design", "Permission-Boundary"]
        assert len(result["candidate_concepts"]) == 2
        assert (candidates_dir / "topic.md").exists()
        assert not (pages_dir / "Output-Boundary.md").exists()
        assert len(vector_store.upserts) == 2
    finally:
        shutil.rmtree(workspace_tmp, ignore_errors=True)
