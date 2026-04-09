# LLM Wiki - Knowledge Evolution Engine

This project is a personal knowledge evolution engine. When the user discusses knowledge topics, help them internalize knowledge into the wiki.

## Core Workflow

**Chat = Input, Wiki auto-evolves, user feels nothing.**

When the user shares new knowledge or reaches a conclusion worth preserving, proactively ingest it. When the user asks about something they've learned before, query the wiki first.

## Commands

All commands run from the project root:

```bash
# Ingest: digest new knowledge into wiki pages
python -m engine.cli ingest --file <path>        # digest a specific file
python -m engine.cli ingest                       # digest all files in inbox

# Query: search existing knowledge
python -m engine.cli query "your question here"

# Lint: health check the wiki
python -m engine.cli lint
```

## Direct Ingest from Conversation

When the user wants to internalize chat content, write the content to a temporary file in `wiki/sources/inbox/`, then run ingest:

```bash
# 1. Save conversation knowledge to a temp file
cat > wiki/sources/inbox/$(date +%Y-%m-%d)_topic.md << 'CONTENT'
<knowledge content here>
CONTENT

# 2. Ingest it
python -m engine.cli ingest
```

## Key Directories

- `wiki/pages/` — Wiki knowledge pages (Obsidian reads this directly)
- `wiki/sources/inbox/` — New materials waiting to be digested
- `wiki/sources/archived/` — Already digested materials
- `engine/` — Core engine code (do not modify unless asked)

## After Knowledge Updates

When wiki pages are updated, remind the user they can publish to the web:

```bash
git add wiki/pages/ && git commit -m "update wiki" && git push
```

## Important

- The wiki uses `[[double brackets]]` for cross-page links
- Pages have YAML frontmatter (title, tags, related, evolution, etc.)
- The engine uses LLM to extract, organize, and maintain knowledge automatically
- Always prefer updating existing pages over creating duplicates
