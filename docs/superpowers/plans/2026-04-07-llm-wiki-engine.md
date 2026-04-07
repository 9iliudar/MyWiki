# LLM Wiki Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-evolving personal knowledge engine that ingests raw sources, maintains interconnected wiki pages, and autonomously improves knowledge quality through LLM-driven lint — following Karpathy's LLM Wiki architecture.

**Architecture:** Three-layer system (Raw Sources → Wiki Pages → Schema) driven by three pipelines (Ingest, Query, Lint). Python engine with pluggable LLM backends, Qdrant for local vector search, Markdown files as the universal data format compatible with Obsidian.

**Tech Stack:** Python 3.11+, Qdrant (local persistence), PyYAML, python-frontmatter, anthropic/openai SDKs, watchdog (file monitoring)

---

## File Structure

```
MyWiki/
├── engine/
│   ├── __init__.py
│   ├── config.py          # Config loading from config.yaml
│   ├── config.yaml        # LLM/embedding/qdrant settings
│   ├── llm.py             # Pluggable LLM provider interface + implementations
│   ├── embed.py           # Embedding + Qdrant vector operations
│   ├── wiki_io.py         # Read/write wiki pages, parse frontmatter, manage log/index
│   ├── prompts.py         # All LLM prompt templates (ingest, query, lint)
│   ├── ingest.py          # Ingest pipeline: source → LLM → wiki pages
│   ├── query.py           # Query pipeline: question → search → LLM → answer + writeback
│   ├── lint.py            # Lint pipeline: review all pages → fix/enhance
│   ├── watch.py           # Folder watcher for sources/inbox/
│   └── cli.py             # CLI entry point: ingest/query/lint/watch commands
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_llm.py
│   ├── test_embed.py
│   ├── test_wiki_io.py
│   ├── test_ingest.py
│   ├── test_query.py
│   └── test_lint.py
├── sources/
│   ├── inbox/             # New sources land here
│   └── archived/          # Digested sources moved here
├── wiki/
│   ├── pages/             # LLM-maintained knowledge pages
│   ├── index.md           # Content navigation (LLM-maintained)
│   └── log.md             # Append-only operation log
├── vectors/               # Qdrant local storage
├── schema.md              # Wiki constitution
├── requirements.txt
└── pyproject.toml
```

---

## Task 1: Project Scaffold + Configuration

**Files:**
- Create: `engine/__init__.py`, `engine/config.py`, `engine/config.yaml`
- Create: `tests/__init__.py`, `tests/test_config.py`
- Create: `requirements.txt`, `pyproject.toml`
- Create: `sources/inbox/.gitkeep`, `sources/archived/.gitkeep`
- Create: `wiki/pages/.gitkeep`, `wiki/index.md`, `wiki/log.md`
- Create: `schema.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p sources/inbox sources/archived wiki/pages vectors engine tests
```

- [ ] **Step 2: Create requirements.txt**

Create `requirements.txt`:

```
anthropic>=0.40.0
openai>=1.50.0
qdrant-client>=1.12.0
python-frontmatter>=1.1.0
PyYAML>=6.0.2
watchdog>=5.0.0
pytest>=8.0.0
```

- [ ] **Step 3: Create pyproject.toml**

Create `pyproject.toml`:

```toml
[project]
name = "mywiki"
version = "0.1.0"
description = "LLM-driven personal knowledge evolution engine"
requires-python = ">=3.11"

[project.scripts]
wiki = "engine.cli:main"
```

- [ ] **Step 4: Create config.yaml**

Create `engine/config.yaml`:

```yaml
llm:
  provider: claude           # claude / openai / local
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY
  base_url: null             # Override for local/compatible APIs

embedding:
  provider: openai
  model: text-embedding-3-small
  api_key_env: OPENAI_API_KEY
  dimensions: 1536

qdrant:
  path: ./vectors

wiki:
  pages_dir: ./wiki/pages
  index_path: ./wiki/index.md
  log_path: ./wiki/log.md
  schema_path: ./schema.md

sources:
  inbox_dir: ./sources/inbox
  archive_dir: ./sources/archived

ingest:
  batch_interval_minutes: 60

lint:
  schedule: daily            # daily / weekly
```

- [ ] **Step 5: Write the failing test for config loading**

Create `tests/__init__.py` (empty) and `tests/test_config.py`:

```python
import os
import pytest
from engine.config import load_config


def test_load_config_returns_all_sections(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
llm:
  provider: claude
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY
  base_url: null
embedding:
  provider: openai
  model: text-embedding-3-small
  api_key_env: OPENAI_API_KEY
  dimensions: 1536
qdrant:
  path: ./vectors
wiki:
  pages_dir: ./wiki/pages
  index_path: ./wiki/index.md
  log_path: ./wiki/log.md
  schema_path: ./schema.md
sources:
  inbox_dir: ./sources/inbox
  archive_dir: ./sources/archived
""")
    config = load_config(str(config_file))
    assert config["llm"]["provider"] == "claude"
    assert config["embedding"]["dimensions"] == 1536
    assert config["qdrant"]["path"] == "./vectors"
    assert config["wiki"]["pages_dir"] == "./wiki/pages"
    assert config["sources"]["inbox_dir"] == "./sources/inbox"


def test_load_config_resolves_api_key(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
llm:
  provider: claude
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY
  base_url: null
embedding:
  provider: openai
  model: text-embedding-3-small
  api_key_env: OPENAI_API_KEY
  dimensions: 1536
qdrant:
  path: ./vectors
wiki:
  pages_dir: ./wiki/pages
  index_path: ./wiki/index.md
  log_path: ./wiki/log.md
  schema_path: ./schema.md
sources:
  inbox_dir: ./sources/inbox
  archive_dir: ./sources/archived
""")
    config = load_config(str(config_file))
    assert config["llm"]["api_key"] == "sk-test-123"
```

- [ ] **Step 6: Run test to verify it fails**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'engine'`

- [ ] **Step 7: Implement config.py**

Create `engine/__init__.py` (empty) and `engine/config.py`:

```python
import os
from pathlib import Path

import yaml


def load_config(config_path: str = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Resolve API keys from environment variables
    for section in ("llm", "embedding"):
        env_var = config[section].get("api_key_env")
        if env_var:
            config[section]["api_key"] = os.environ.get(env_var, "")

    return config
```

- [ ] **Step 8: Run test to verify it passes**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_config.py -v
```

Expected: 2 passed

- [ ] **Step 9: Create schema.md**

Create `schema.md`:

```markdown
# Wiki Schema（宪法）

本文件定义 Wiki 的运行规则，是所有 LLM 操作的指令依据。

## 语言规范

- Wiki 页面一律使用中文撰写
- 技术术语保留英文原文，首次出现时附中文翻译，如：RAG（检索增强生成）
- 原始素材语言不限，消化后的 wiki 页面统一为中文

## 页面 Frontmatter 规范

每个 wiki 页面必须包含以下 frontmatter：

---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - 关联的原始素材路径
related:
  - "[[相关页面名]]"
tags: [标签1, 标签2]
evolution:
  - "YYYY-MM-DD: 变更描述"
---

## Ingest 规则

当消化新素材时，LLM 必须：
1. 为素材生成一段 3-5 句话的摘要
2. 识别素材中涉及的所有核心概念和实体
3. 为每个核心概念创建新页面（如不存在）或更新已有页面
4. 目标：每次 ingest 创建或更新 10-15 个相关页面
5. 所有新页面必须至少有一个 [[双链]] 指向其他页面
6. 更新 index.md 的导航结构
7. 在 log.md 追加本次操作记录

## 页面创建 vs 更新规则

- 如果概念已有页面：更新内容，追加新信息来源到 sources，更新 evolution
- 如果概念没有页面：创建新页面，填充完整 frontmatter
- 合并判断：标题相同或语义高度相似（如 "LLM" 和 "大语言模型"）应合并为同一页面

## 页面内容规范

每个页面应包含：
- 一段简明定义（2-3 句话）
- 核心要点（要点列表）
- 与其他概念的关系说明
- 来源引用

## Lint 检查清单

定期巡检时，LLM 必须检查以下项目：
1. **矛盾检测**：不同页面对同一概念的描述是否矛盾
2. **孤岛检测**：是否有页面没有被任何其他页面引用（无入链）
3. **浅层检测**：是否有页面内容过于单薄（少于 100 字）
4. **重复检测**：是否有多个页面描述同一概念
5. **空白检测**：页面中提到但未创建的 [[链接]] 目标
6. **过时检测**：超过 30 天未更新且关联素材较新的页面

## Query 反哺规则

当用户提问并获得有价值的回答时：
1. 如果回答涉及新概念：创建新页面
2. 如果回答深化了已有概念：更新对应页面
3. 将对话本身作为素材存入 sources/archived/
4. 在 log.md 记录本次 query 及其影响

## index.md 格式

按知识领域组织的导航目录，格式：

## 领域名称

- [[页面名]] — 一句话描述
- [[页面名]] — 一句话描述

## log.md 格式

时间倒序的操作日志，格式：

## YYYY-MM-DD HH:MM

**操作**: ingest / query / lint
**素材**: （如适用）素材文件名
**影响页面**: 创建/更新的页面列表
**摘要**: 一句话总结本次操作
```

- [ ] **Step 10: Create initial wiki files**

Create `wiki/index.md`:

```markdown
# 知识导航

> 本目录由 LLM 引擎自动维护，按知识领域组织。

*Wiki 刚刚初始化，等待第一次 ingest 后自动生成导航。*
```

Create `wiki/log.md`:

```markdown
# 操作日志

> 按时间倒序记录每次 ingest / query / lint 操作。
```

- [ ] **Step 11: Commit**

```bash
git init
git add pyproject.toml requirements.txt engine/__init__.py engine/config.py engine/config.yaml tests/__init__.py tests/test_config.py schema.md sources/inbox/.gitkeep sources/archived/.gitkeep wiki/pages/.gitkeep wiki/index.md wiki/log.md docs/
git commit -m "feat: project scaffold with config, schema, and directory structure"
```

---

## Task 2: LLM Adapter Layer

**Files:**
- Create: `engine/llm.py`
- Create: `tests/test_llm.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_llm.py`:

```python
import pytest
from engine.llm import create_llm_provider, LLMProvider


class FakeLLMProvider(LLMProvider):
    def __init__(self, response: str = "fake response"):
        self._response = response

    def complete(self, prompt: str, context: str = "") -> str:
        return self._response


def test_llm_provider_interface():
    provider = FakeLLMProvider("hello")
    result = provider.complete("test prompt", "test context")
    assert result == "hello"


def test_create_llm_provider_claude(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    config = {
        "llm": {
            "provider": "claude",
            "model": "claude-sonnet-4-6",
            "api_key": "sk-test",
            "base_url": None,
        }
    }
    provider = create_llm_provider(config)
    assert provider.__class__.__name__ == "ClaudeProvider"


def test_create_llm_provider_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    config = {
        "llm": {
            "provider": "openai",
            "model": "gpt-4o",
            "api_key": "sk-test",
            "base_url": None,
        }
    }
    provider = create_llm_provider(config)
    assert provider.__class__.__name__ == "OpenAIProvider"


def test_create_llm_provider_local():
    config = {
        "llm": {
            "provider": "local",
            "model": "llama3",
            "api_key": "",
            "base_url": "http://localhost:11434/v1",
        }
    }
    provider = create_llm_provider(config)
    assert provider.__class__.__name__ == "LocalProvider"


def test_create_llm_provider_unknown_raises():
    config = {"llm": {"provider": "unknown"}}
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        create_llm_provider(config)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_llm.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement llm.py**

Create `engine/llm.py`:

```python
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, context: str = "") -> str:
        """Send prompt + context to LLM, return response text."""
        ...


class ClaudeProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, base_url: str = None):
        import anthropic

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = anthropic.Anthropic(**kwargs)
        self.model = model

    def complete(self, prompt: str, context: str = "") -> str:
        messages = []
        if context:
            messages.append({"role": "user", "content": context})
            messages.append({"role": "assistant", "content": "我已阅读上述内容，请告诉我需要做什么。"})
        messages.append({"role": "user", "content": prompt})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=messages,
        )
        return response.content[0].text


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str, base_url: str = None):
        import openai

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = openai.OpenAI(**kwargs)
        self.model = model

    def complete(self, prompt: str, context: str = "") -> str:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content


class LocalProvider(LLMProvider):
    """Uses OpenAI-compatible API (e.g., Ollama, vLLM)."""

    def __init__(self, model: str, base_url: str, api_key: str = ""):
        import openai

        self.client = openai.OpenAI(api_key=api_key or "not-needed", base_url=base_url)
        self.model = model

    def complete(self, prompt: str, context: str = "") -> str:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content


def create_llm_provider(config: dict) -> LLMProvider:
    llm_config = config["llm"]
    provider = llm_config["provider"]

    if provider == "claude":
        return ClaudeProvider(
            model=llm_config["model"],
            api_key=llm_config.get("api_key", ""),
            base_url=llm_config.get("base_url"),
        )
    elif provider == "openai":
        return OpenAIProvider(
            model=llm_config["model"],
            api_key=llm_config.get("api_key", ""),
            base_url=llm_config.get("base_url"),
        )
    elif provider == "local":
        return LocalProvider(
            model=llm_config["model"],
            base_url=llm_config.get("base_url", "http://localhost:11434/v1"),
            api_key=llm_config.get("api_key", ""),
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_llm.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add engine/llm.py tests/test_llm.py
git commit -m "feat: pluggable LLM adapter layer with Claude/OpenAI/local providers"
```

---

## Task 3: Embedding + Qdrant Vector Layer

**Files:**
- Create: `engine/embed.py`
- Create: `tests/test_embed.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_embed.py`:

```python
import pytest
from engine.embed import VectorStore


@pytest.fixture
def store(tmp_path):
    return VectorStore(path=str(tmp_path / "test_vectors"), dimension=4)


def test_upsert_and_search(store):
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "Alpha"})
    store.upsert("page2", [0.0, 1.0, 0.0, 0.0], {"title": "Beta"})

    results = store.search([1.0, 0.1, 0.0, 0.0], top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "page1"
    assert results[0]["metadata"]["title"] == "Alpha"


def test_upsert_overwrites(store):
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "Old"})
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "New"})

    results = store.search([1.0, 0.0, 0.0, 0.0], top_k=1)
    assert results[0]["metadata"]["title"] == "New"


def test_delete(store):
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "Alpha"})
    store.delete("page1")

    results = store.search([1.0, 0.0, 0.0, 0.0], top_k=1)
    assert len(results) == 0


def test_count(store):
    assert store.count() == 0
    store.upsert("page1", [1.0, 0.0, 0.0, 0.0], {"title": "A"})
    store.upsert("page2", [0.0, 1.0, 0.0, 0.0], {"title": "B"})
    assert store.count() == 2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_embed.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement embed.py**

Create `engine/embed.py`:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter


COLLECTION_NAME = "wiki_pages"


class VectorStore:
    def __init__(self, path: str, dimension: int = 1536):
        self.client = QdrantClient(path=path)
        self.dimension = dimension
        self._ensure_collection()

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
            )

    def upsert(self, page_id: str, vector: list[float], metadata: dict):
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=self._hash_id(page_id),
                    vector=vector,
                    payload={"page_id": page_id, **metadata},
                )
            ],
        )

    def search(self, query_vector: list[float], top_k: int = 10) -> list[dict]:
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
        ).points
        return [
            {
                "id": hit.payload["page_id"],
                "score": hit.score,
                "metadata": {k: v for k, v in hit.payload.items() if k != "page_id"},
            }
            for hit in results
        ]

    def delete(self, page_id: str):
        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[self._hash_id(page_id)],
        )

    def count(self) -> int:
        return self.client.count(collection_name=COLLECTION_NAME).count

    @staticmethod
    def _hash_id(page_id: str) -> int:
        """Convert string ID to integer hash for Qdrant."""
        import hashlib
        return int(hashlib.sha256(page_id.encode()).hexdigest()[:16], 16)


class Embedder:
    """Generate embeddings using OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small", base_url: str = None):
        import openai

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = openai.OpenAI(**kwargs)
        self.model = model

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_embed.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add engine/embed.py tests/test_embed.py
git commit -m "feat: Qdrant vector store and embedding layer"
```

---

## Task 4: Wiki I/O Layer

**Files:**
- Create: `engine/wiki_io.py`
- Create: `tests/test_wiki_io.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_wiki_io.py`:

```python
import pytest
from engine.wiki_io import WikiIO


@pytest.fixture
def wiki(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")
    return WikiIO(
        pages_dir=str(pages_dir),
        index_path=str(index_path),
        log_path=str(log_path),
    )


def test_write_and_read_page(wiki):
    frontmatter = {
        "title": "RAG（检索增强生成）",
        "created": "2026-04-07",
        "updated": "2026-04-07",
        "sources": [],
        "related": [],
        "tags": ["AI"],
        "evolution": ["2026-04-07: 初始创建"],
    }
    wiki.write_page("RAG", frontmatter, "这是正文内容。")

    page = wiki.read_page("RAG")
    assert page["frontmatter"]["title"] == "RAG（检索增强生成）"
    assert page["content"] == "这是正文内容。"


def test_list_pages(wiki):
    wiki.write_page("A", {"title": "A", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}, "Content A")
    wiki.write_page("B", {"title": "B", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}, "Content B")
    pages = wiki.list_pages()
    assert set(pages) == {"A", "B"}


def test_append_log(wiki):
    wiki.append_log("ingest", "test-source.md", ["RAG", "LLM"], "测试消化操作")
    log_content = wiki.read_log()
    assert "ingest" in log_content
    assert "RAG" in log_content
    assert "测试消化操作" in log_content


def test_page_exists(wiki):
    assert not wiki.page_exists("Nope")
    wiki.write_page("Nope", {"title": "Nope", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}, "x")
    assert wiki.page_exists("Nope")


def test_read_all_pages(wiki):
    wiki.write_page("X", {"title": "X", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": ["[[Y]]"], "tags": [], "evolution": []}, "Content X")
    wiki.write_page("Y", {"title": "Y", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": ["[[X]]"], "tags": [], "evolution": []}, "Content Y")
    all_pages = wiki.read_all_pages()
    assert len(all_pages) == 2
    titles = {p["frontmatter"]["title"] for p in all_pages}
    assert titles == {"X", "Y"}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_wiki_io.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement wiki_io.py**

Create `engine/wiki_io.py`:

```python
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
        return {
            "name": name,
            "frontmatter": dict(post.metadata),
            "content": post.content,
        }

    def page_exists(self, name: str) -> bool:
        return (self.pages_dir / f"{name}.md").exists()

    def list_pages(self) -> list[str]:
        return [p.stem for p in self.pages_dir.glob("*.md")]

    def read_all_pages(self) -> list[dict]:
        return [self.read_page(name) for name in self.list_pages()]

    def append_log(self, operation: str, source: str, affected_pages: list[str], summary: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## {now}\n\n"
        entry += f"**操作**: {operation}\n"
        if source:
            entry += f"**素材**: {source}\n"
        entry += f"**影响页面**: {', '.join(affected_pages)}\n"
        entry += f"**摘要**: {summary}\n"

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def read_log(self) -> str:
        return self.log_path.read_text(encoding="utf-8")

    def write_index(self, content: str):
        self.index_path.write_text(content, encoding="utf-8")

    def read_index(self) -> str:
        return self.index_path.read_text(encoding="utf-8")

    def get_page_full_text(self, name: str) -> str:
        """Return page content with frontmatter as readable text for LLM context."""
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_wiki_io.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add engine/wiki_io.py tests/test_wiki_io.py
git commit -m "feat: wiki I/O layer for reading/writing pages, log, and index"
```

---

## Task 5: Prompt Templates

**Files:**
- Create: `engine/prompts.py`

- [ ] **Step 1: Create prompts.py**

Create `engine/prompts.py`:

```python
INGEST_PROMPT = """你是一个知识管理引擎。你的任务是消化以下原始素材，并输出结构化的 wiki 页面。

## 原始素材

{source_content}

## 现有 Wiki 页面列表

{existing_pages}

## Wiki 规则

{schema}

## 你的任务

1. 为这份素材写一段 3-5 句话的摘要
2. 识别素材中的所有核心概念和实体
3. 为每个核心概念输出一个 wiki 页面（如果概念已有页面，输出更新内容）
4. 确保每个页面至少有一个 [[双链]] 关联到其他页面
5. 目标：输出 10-15 个页面

## 输出格式

严格按以下 JSON 格式输出，不要输出其他内容：

```json
{{
  "summary": "素材摘要",
  "pages": [
    {{
      "name": "页面文件名（英文，如 RAG）",
      "title": "页面标题（中文，如 RAG（检索增强生成））",
      "tags": ["标签1", "标签2"],
      "related": ["[[相关页面1]]", "[[相关页面2]]"],
      "content": "页面正文内容（Markdown 格式）",
      "is_new": true
    }}
  ],
  "index_updates": "需要添加到 index.md 的导航条目（Markdown 格式）"
}}
```"""


QUERY_PROMPT = """你是一个知识管理引擎。根据用户的问题和 Wiki 中的相关知识，给出准确的回答。

## 用户问题

{question}

## 相关 Wiki 页面

{context_pages}

## 回答要求

1. 基于 Wiki 中已有的知识回答，不要编造
2. 引用来源页面：使用 [[页面名]] 格式
3. 如果 Wiki 中没有足够信息，明确说明知识空白
4. 用中文回答

## 输出格式

严格按以下 JSON 格式输出：

```json
{{
  "answer": "回答正文（Markdown 格式，含 [[双链]] 引用）",
  "should_save": true,
  "save_reason": "为什么这个回答值得写回 wiki（如不需要保存则为空）",
  "new_page": {{
    "name": "新页面文件名（如不需要则为 null）",
    "title": "新页面标题",
    "tags": ["标签"],
    "related": ["[[相关页面]]"],
    "content": "页面正文"
  }}
}}
```"""


LINT_PROMPT = """你是一个知识管理引擎。你的任务是审视整个 Wiki，发现问题并提出修正。

## 当前 Wiki 所有页面

{all_pages}

## 检查清单

1. **矛盾检测**：不同页面对同一概念的描述是否矛盾
2. **孤岛检测**：是否有页面没有被任何其他页面引用
3. **浅层检测**：是否有页面内容过于单薄（少于 100 字）
4. **重复检测**：是否有多个页面描述同一概念
5. **空白检测**：页面中提到但未创建的 [[链接]] 目标
6. **关联缺失**：应该相互关联但没有链接的页面

## 输出格式

严格按以下 JSON 格式输出：

```json
{{
  "findings": [
    {{
      "type": "contradiction|orphan|shallow|duplicate|gap|missing_link",
      "description": "问题描述",
      "affected_pages": ["页面名1", "页面名2"]
    }}
  ],
  "fixes": [
    {{
      "action": "update|create|merge",
      "page_name": "页面名",
      "new_title": "新标题（如适用）",
      "new_tags": ["标签"],
      "new_related": ["[[关联]]"],
      "new_content": "新内容或追加内容",
      "merge_into": "合并目标页面名（仅 merge 时）"
    }}
  ],
  "index_updates": "更新后的完整 index.md 内容"
}}
```"""


INDEX_REBUILD_PROMPT = """你是一个知识管理引擎。根据以下所有 Wiki 页面，生成一份按知识领域组织的导航目录。

## 所有页面

{all_pages}

## 输出要求

- 按知识领域分组（如：AI 基础、架构模式、工具框架 等）
- 每个条目格式：`- [[页面名]] — 一句话描述`
- 用中文
- 开头加 `# 知识导航` 标题和说明

直接输出 Markdown 内容，不需要 JSON 包装。"""
```

- [ ] **Step 2: Commit**

```bash
git add engine/prompts.py
git commit -m "feat: LLM prompt templates for ingest, query, lint operations"
```

---

## Task 6: Ingest Pipeline

**Files:**
- Create: `engine/ingest.py`
- Create: `tests/test_ingest.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_ingest.py`:

```python
import json
import pytest
from engine.ingest import IngestPipeline
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class MockLLM(LLMProvider):
    def complete(self, prompt: str, context: str = "") -> str:
        return json.dumps({
            "summary": "这是一篇关于知识管理的文章。",
            "pages": [
                {
                    "name": "LLM_Wiki",
                    "title": "LLM Wiki（LLM 知识库）",
                    "tags": ["AI", "知识管理"],
                    "related": ["[[知识图谱]]"],
                    "content": "LLM Wiki 是一种利用大语言模型维护个人知识库的方法。",
                    "is_new": True,
                },
                {
                    "name": "知识图谱",
                    "title": "知识图谱",
                    "tags": ["AI"],
                    "related": ["[[LLM_Wiki]]"],
                    "content": "知识图谱是一种结构化的知识表示方法。",
                    "is_new": True,
                },
            ],
            "index_updates": "## AI\n\n- [[LLM_Wiki]] — LLM 驱动的知识库\n- [[知识图谱]] — 结构化知识表示",
        })


class MockEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}

    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = {"vector": vector, "metadata": metadata}


@pytest.fixture
def pipeline(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    inbox = tmp_path / "sources" / "inbox"
    inbox.mkdir(parents=True)
    archive = tmp_path / "sources" / "archived"
    archive.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")
    schema_path = tmp_path / "schema.md"
    schema_path.write_text("测试 schema", encoding="utf-8")

    wiki = WikiIO(str(pages_dir), str(index_path), str(log_path))
    vector_store = MockVectorStore()

    return IngestPipeline(
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=vector_store,
        wiki=wiki,
        schema_path=str(schema_path),
        inbox_dir=str(inbox),
        archive_dir=str(archive),
    )


def test_ingest_single_source(pipeline, tmp_path):
    source_file = tmp_path / "sources" / "inbox" / "test-article.md"
    source_file.write_text("---\ntitle: Test Article\nstatus: raw\n---\nArticle content here.", encoding="utf-8")

    result = pipeline.ingest_file(str(source_file))

    assert result["summary"] == "这是一篇关于知识管理的文章。"
    assert len(result["pages_affected"]) == 2
    assert pipeline.wiki.page_exists("LLM_Wiki")
    assert pipeline.wiki.page_exists("知识图谱")
    # Source should be moved to archived
    assert not source_file.exists()
    archived = tmp_path / "sources" / "archived" / "test-article.md"
    assert archived.exists()


def test_ingest_inbox(pipeline, tmp_path):
    f1 = tmp_path / "sources" / "inbox" / "a.md"
    f1.write_text("---\ntitle: A\nstatus: raw\n---\nContent A", encoding="utf-8")
    f2 = tmp_path / "sources" / "inbox" / "b.md"
    f2.write_text("---\ntitle: B\nstatus: raw\n---\nContent B", encoding="utf-8")

    results = pipeline.ingest_inbox()
    assert len(results) == 2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_ingest.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement ingest.py**

Create `engine/ingest.py`:

```python
import json
import shutil
from datetime import date
from pathlib import Path

import frontmatter

from engine.prompts import INGEST_PROMPT
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


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
    ):
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

        prompt = INGEST_PROMPT.format(
            source_content=source_content,
            existing_pages=existing_pages,
            schema=self.schema,
        )

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

            # Embed the page
            full_text = self.wiki.get_page_full_text(name)
            vector = self.embedder.embed(full_text)
            self.vector_store.upsert(name, vector, {"title": page_data["title"], "tags": page_data.get("tags", [])})

        # Update index
        if response.get("index_updates"):
            current_index = self.wiki.read_index()
            self.wiki.write_index(current_index + "\n" + response["index_updates"])

        # Log the operation
        self.wiki.append_log(
            operation="ingest",
            source=source_path.name,
            affected_pages=pages_affected,
            summary=response.get("summary", ""),
        )

        # Archive the source
        self._archive_source(source_path)

        return {
            "summary": response.get("summary", ""),
            "pages_affected": pages_affected,
        }

    def ingest_inbox(self) -> list[dict]:
        results = []
        for source_file in sorted(self.inbox_dir.glob("*.md")):
            result = self.ingest_file(str(source_file))
            results.append(result)
        return results

    def _archive_source(self, source_path: Path):
        dest = self.archive_dir / source_path.name
        shutil.move(str(source_path), str(dest))
        # Update status in frontmatter
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
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()
        return json.loads(text)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_ingest.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add engine/ingest.py tests/test_ingest.py
git commit -m "feat: ingest pipeline - digest sources into wiki pages"
```

---

## Task 7: Query Pipeline

**Files:**
- Create: `engine/query.py`
- Create: `tests/test_query.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_query.py`:

```python
import json
import pytest
from engine.query import QueryPipeline
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class MockLLM(LLMProvider):
    def complete(self, prompt: str, context: str = "") -> str:
        return json.dumps({
            "answer": "RAG 是检索增强生成的缩写，详见 [[RAG]]。",
            "should_save": True,
            "save_reason": "对 RAG 的综合解释值得保留",
            "new_page": {
                "name": "RAG应用场景",
                "title": "RAG 应用场景",
                "tags": ["AI", "RAG"],
                "related": ["[[RAG]]"],
                "content": "RAG 常用于企业知识库问答系统。",
            },
        })


class MockEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}

    def search(self, query_vector, top_k=5):
        return [
            {"id": "RAG", "score": 0.95, "metadata": {"title": "RAG"}},
        ]

    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = {"vector": vector, "metadata": metadata}


@pytest.fixture
def pipeline(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")

    wiki = WikiIO(str(pages_dir), str(index_path), str(log_path))

    # Pre-create a page for search results to reference
    wiki.write_page("RAG", {
        "title": "RAG（检索增强生成）",
        "created": "2026-04-07",
        "updated": "2026-04-07",
        "sources": [],
        "related": [],
        "tags": ["AI"],
        "evolution": [],
    }, "RAG 是一种结合检索和生成的技术。")

    return QueryPipeline(
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki=wiki,
    )


def test_query_returns_answer(pipeline):
    result = pipeline.query("什么是 RAG？")
    assert "RAG" in result["answer"]


def test_query_creates_new_page_when_should_save(pipeline):
    result = pipeline.query("什么是 RAG？")
    assert result["saved_page"] == "RAG应用场景"
    assert pipeline.wiki.page_exists("RAG应用场景")


def test_query_logs_operation(pipeline):
    pipeline.query("什么是 RAG？")
    log = pipeline.wiki.read_log()
    assert "query" in log
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_query.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement query.py**

Create `engine/query.py`:

```python
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
        # Semantic search for relevant pages
        query_vector = self.embedder.embed(question)
        search_results = self.vector_store.search(query_vector, top_k=10)

        # Build context from search results
        context_pages = []
        for result in search_results:
            page_id = result["id"]
            if self.wiki.page_exists(page_id):
                full_text = self.wiki.get_page_full_text(page_id)
                context_pages.append(full_text)

        context_str = "\n\n---\n\n".join(context_pages) if context_pages else "（Wiki 中暂无相关内容）"

        # Ask LLM
        prompt = QUERY_PROMPT.format(
            question=question,
            context_pages=context_str,
        )
        raw_response = self.llm.complete(prompt)
        response = self._parse_json(raw_response)

        saved_page = None

        # Write back if valuable
        if response.get("should_save") and response.get("new_page"):
            page_data = response["new_page"]
            if page_data.get("name"):
                today = date.today().isoformat()
                fm = {
                    "title": page_data["title"],
                    "created": today,
                    "updated": today,
                    "sources": [],
                    "related": page_data.get("related", []),
                    "tags": page_data.get("tags", []),
                    "evolution": [f"{today}: 从 query 反哺创建"],
                }
                self.wiki.write_page(page_data["name"], fm, page_data["content"])

                # Embed the new page
                full_text = self.wiki.get_page_full_text(page_data["name"])
                vector = self.embedder.embed(full_text)
                self.vector_store.upsert(
                    page_data["name"], vector,
                    {"title": page_data["title"], "tags": page_data.get("tags", [])},
                )
                saved_page = page_data["name"]

        # Log
        affected = [saved_page] if saved_page else []
        self.wiki.append_log(
            operation="query",
            source="",
            affected_pages=affected,
            summary=f"Q: {question[:50]}",
        )

        return {
            "answer": response.get("answer", ""),
            "saved_page": saved_page,
            "sources": [r["id"] for r in search_results],
        }

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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_query.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add engine/query.py tests/test_query.py
git commit -m "feat: query pipeline with semantic search and wiki writeback"
```

---

## Task 8: Lint Pipeline

**Files:**
- Create: `engine/lint.py`
- Create: `tests/test_lint.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_lint.py`:

```python
import json
import pytest
from engine.lint import LintPipeline
from engine.wiki_io import WikiIO
from engine.llm import LLMProvider


class MockLLM(LLMProvider):
    def complete(self, prompt: str, context: str = "") -> str:
        return json.dumps({
            "findings": [
                {
                    "type": "orphan",
                    "description": "Orphan 页面没有被任何页面引用",
                    "affected_pages": ["Orphan"],
                },
                {
                    "type": "shallow",
                    "description": "Shallow 页面内容过于单薄",
                    "affected_pages": ["Shallow"],
                },
            ],
            "fixes": [
                {
                    "action": "update",
                    "page_name": "Orphan",
                    "new_title": None,
                    "new_tags": None,
                    "new_related": ["[[Connected]]"],
                    "new_content": None,
                    "merge_into": None,
                },
                {
                    "action": "update",
                    "page_name": "Shallow",
                    "new_title": None,
                    "new_tags": None,
                    "new_related": None,
                    "new_content": "Shallow 是一个概念，用于描述内容不够深入的状态。它与深度学习形成对比。",
                    "merge_into": None,
                },
            ],
            "index_updates": "# 知识导航\n\n## 测试\n\n- [[Connected]] — 已连接\n- [[Orphan]] — 不再孤立\n- [[Shallow]] — 已深化",
        })


class MockEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}

    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = True


@pytest.fixture
def pipeline(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 知识导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 操作日志\n", encoding="utf-8")

    wiki = WikiIO(str(pages_dir), str(index_path), str(log_path))

    fm = {"title": "t", "created": "2026-04-07", "updated": "2026-04-07", "sources": [], "related": [], "tags": [], "evolution": []}
    wiki.write_page("Connected", {**fm, "title": "Connected", "related": ["[[Orphan]]"]}, "A well-connected page.")
    wiki.write_page("Orphan", {**fm, "title": "Orphan"}, "An orphan page with no inbound links except from Connected.")
    wiki.write_page("Shallow", {**fm, "title": "Shallow"}, "Thin.")

    return LintPipeline(
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki=wiki,
    )


def test_lint_returns_findings(pipeline):
    result = pipeline.run()
    assert len(result["findings"]) == 2
    types = {f["type"] for f in result["findings"]}
    assert "orphan" in types
    assert "shallow" in types


def test_lint_applies_fixes(pipeline):
    pipeline.run()
    orphan = pipeline.wiki.read_page("Orphan")
    assert "[[Connected]]" in orphan["frontmatter"]["related"]


def test_lint_updates_shallow_content(pipeline):
    pipeline.run()
    shallow = pipeline.wiki.read_page("Shallow")
    assert len(shallow["content"]) > 10  # No longer just "Thin."


def test_lint_logs_operation(pipeline):
    pipeline.run()
    log = pipeline.wiki.read_log()
    assert "lint" in log
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_lint.py -v
```

Expected: FAIL

- [ ] **Step 3: Implement lint.py**

Create `engine/lint.py`:

```python
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
        # Gather all pages
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
                    existing_related = fm.get("related", [])
                    fm["related"] = list(set(existing_related + fix["new_related"]))
                if fix.get("new_tags"):
                    existing_tags = fm.get("tags", [])
                    fm["tags"] = list(set(existing_tags + fix["new_tags"]))
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

                # Re-embed
                full_text = self.wiki.get_page_full_text(page_name)
                vector = self.embedder.embed(full_text)
                self.vector_store.upsert(page_name, vector, {"title": fm["title"], "tags": fm.get("tags", [])})

            elif action == "create" and page_name and not self.wiki.page_exists(page_name):
                fm = {
                    "title": fix.get("new_title", page_name),
                    "created": today,
                    "updated": today,
                    "sources": [],
                    "related": fix.get("new_related", []),
                    "tags": fix.get("new_tags", []),
                    "evolution": [f"{today}: Lint 自动创建"],
                }
                self.wiki.write_page(page_name, fm, fix.get("new_content", ""))
                pages_affected.append(page_name)

                full_text = self.wiki.get_page_full_text(page_name)
                vector = self.embedder.embed(full_text)
                self.vector_store.upsert(page_name, vector, {"title": fm["title"], "tags": fm.get("tags", [])})

            elif action == "merge" and fix.get("merge_into"):
                # Merge page into target - append content, delete original
                if self.wiki.page_exists(page_name) and self.wiki.page_exists(fix["merge_into"]):
                    source_page = self.wiki.read_page(page_name)
                    target_page = self.wiki.read_page(fix["merge_into"])

                    merged_content = target_page["content"] + "\n\n" + source_page["content"]
                    target_fm = target_page["frontmatter"]
                    target_fm["updated"] = today
                    target_fm["evolution"] = target_fm.get("evolution", []) + [f"{today}: 合并自 {page_name}"]

                    self.wiki.write_page(fix["merge_into"], target_fm, merged_content)
                    pages_affected.append(fix["merge_into"])

        # Update index
        if response.get("index_updates"):
            self.wiki.write_index(response["index_updates"])

        # Log
        self.wiki.append_log(
            operation="lint",
            source="",
            affected_pages=pages_affected,
            summary=f"发现 {len(findings)} 个问题，应用 {len(pages_affected)} 个修正",
        )

        return {
            "findings": findings,
            "fixes_applied": len(pages_affected),
            "pages_affected": pages_affected,
        }

    @staticmethod
    def _format_pages_for_prompt(pages: list[dict]) -> str:
        parts = []
        for page in pages:
            fm = page["frontmatter"]
            parts.append(
                f"### {fm.get('title', page['name'])}\n"
                f"标签: {', '.join(fm.get('tags', []))}\n"
                f"关联: {', '.join(fm.get('related', []))}\n\n"
                f"{page['content']}"
            )
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd D:/Project/MyWiki && python -m pytest tests/test_lint.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add engine/lint.py tests/test_lint.py
git commit -m "feat: lint pipeline for self-evolving knowledge quality checks"
```

---

## Task 9: CLI Entry Point

**Files:**
- Create: `engine/cli.py`

- [ ] **Step 1: Implement cli.py**

Create `engine/cli.py`:

```python
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
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        wiki=wiki,
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
    pipeline = QueryPipeline(
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        wiki=wiki,
    )

    result = pipeline.query(args.question)
    print(f"\n{result['answer']}\n")
    if result["saved_page"]:
        print(f"[已保存新页面: {result['saved_page']}]")
    if result["sources"]:
        print(f"[参考页面: {', '.join(result['sources'])}]")


def cmd_lint(args, config):
    llm, embedder, vector_store, wiki = _build_components(config)
    pipeline = LintPipeline(
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        wiki=wiki,
    )

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
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        wiki=wiki,
        schema_path=config["wiki"]["schema_path"],
        inbox_dir=config["sources"]["inbox_dir"],
        archive_dir=config["sources"]["archive_dir"],
    )
    start_watching(config["sources"]["inbox_dir"], pipeline)


def main():
    parser = argparse.ArgumentParser(description="LLM Wiki 知识进化引擎")
    parser.add_argument("--config", default=None, help="配置文件路径")
    subparsers = parser.add_subparsers(dest="command")

    # ingest
    ingest_parser = subparsers.add_parser("ingest", help="消化新素材")
    ingest_parser.add_argument("--file", help="指定素材文件路径（不指定则处理整个 inbox）")

    # query
    query_parser = subparsers.add_parser("query", help="查询知识库")
    query_parser.add_argument("question", help="问题")

    # lint
    subparsers.add_parser("lint", help="巡检知识库")

    # watch
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
```

- [ ] **Step 2: Verify CLI help works**

```bash
cd D:/Project/MyWiki && python -m engine.cli --help
```

Expected: Shows usage with ingest/query/lint/watch subcommands

- [ ] **Step 3: Commit**

```bash
git add engine/cli.py
git commit -m "feat: CLI entry point with ingest/query/lint/watch commands"
```

---

## Task 10: File Watcher (Phase 2)

**Files:**
- Create: `engine/watch.py`

- [ ] **Step 1: Implement watch.py**

Create `engine/watch.py`:

```python
import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class InboxHandler(FileSystemEventHandler):
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return

        # Wait a moment for file to be fully written
        time.sleep(1)
        path = Path(event.src_path)
        if not path.exists():
            return

        print(f"检测到新素材: {path.name}")
        try:
            result = self.pipeline.ingest_file(str(path))
            print(f"  已消化: {result['summary'][:60]}")
            print(f"  影响页面: {', '.join(result['pages_affected'])}")
        except Exception as e:
            print(f"  消化失败: {e}")


def start_watching(inbox_dir: str, pipeline):
    handler = InboxHandler(pipeline)
    observer = Observer()
    observer.schedule(handler, inbox_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

- [ ] **Step 2: Commit**

```bash
git add engine/watch.py
git commit -m "feat: file watcher for auto-ingesting new sources from inbox"
```

---

## Task 11: Install Dependencies and Integration Test

- [ ] **Step 1: Install dependencies**

```bash
cd D:/Project/MyWiki && pip install -r requirements.txt
```

- [ ] **Step 2: Run all tests**

```bash
cd D:/Project/MyWiki && python -m pytest tests/ -v
```

Expected: All tests pass (16 total)

- [ ] **Step 3: Verify CLI launches**

```bash
cd D:/Project/MyWiki && python -m engine.cli --help
cd D:/Project/MyWiki && python -m engine.cli ingest --help
cd D:/Project/MyWiki && python -m engine.cli query --help
```

Expected: All show help text without errors

- [ ] **Step 4: Create .gitignore**

Create `.gitignore`:

```
__pycache__/
*.pyc
vectors/
.env
*.egg-info/
dist/
build/
.pytest_cache/
```

- [ ] **Step 5: Final commit**

```bash
git add .gitignore
git commit -m "chore: add gitignore and verify full test suite passes"
```

---

## Task 12: End-to-End Smoke Test with Real LLM

This task is manual — requires actual API keys configured.

- [ ] **Step 1: Set up environment**

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

- [ ] **Step 2: Create a test source and ingest it**

Create `sources/inbox/2026-04-07_karpathy-llm-wiki.md`:

```markdown
---
title: Karpathy - LLM Wiki
source_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
date_added: 2026-04-07
type: article
status: raw
---

LLM Wiki 是 Andrej Karpathy 提出的一种个人知识管理方法...
（粘贴原文内容）
```

```bash
cd D:/Project/MyWiki && python -m engine.cli ingest
```

Expected: 素材被消化，wiki/pages/ 下出现 10+ 个 .md 文件

- [ ] **Step 3: Query the wiki**

```bash
cd D:/Project/MyWiki && python -m engine.cli query "什么是 LLM Wiki 的三层架构？"
```

Expected: 返回基于 wiki 内容的回答

- [ ] **Step 4: Run lint**

```bash
cd D:/Project/MyWiki && python -m engine.cli lint
```

Expected: 发现一些 findings 并应用修正

- [ ] **Step 5: Open wiki/ in Obsidian and verify**

Open Obsidian → Open folder as vault → select `wiki/`

Expected: 页面可浏览，双链可点击，图谱视图可见

- [ ] **Step 6: Commit the first batch of wiki content**

```bash
git add wiki/ sources/archived/
git commit -m "feat: first wiki ingest - Karpathy LLM Wiki article"
```
