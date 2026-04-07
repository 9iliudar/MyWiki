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
