# LLM Wiki - Knowledge Evolution Engine

This repository is a personal knowledge digestion tracker, not a knowledge base organizer.

It does **not** assume the user already understands the material. The wiki must reflect what the user has actually digested — not what the AI could summarize. If you ingest a batch of articles and produce pages the user can't explain, you have broken the system.

Read `README.md` first for the current system design.

## Core Operating Principle

Do not equate "mentioned" with "mastered". The wiki mirrors the user's real cognitive state.

Default behavior:

- Use `wiki_preview` before `wiki_ingest` to assess cognitive state
- Internalize only concepts the user has actually understood
- Keep growth controlled
- Avoid one conversation turning into many shallow wiki pages

Repository rule:

- formal knowledge goes into `wiki/MyWiki/<Category>/`
- candidate concepts go into `wiki/candidates/<Category>/`

## Two-Step Confirmation Workflow

1. Call `wiki_preview(content)` → returns cognitive snapshot (mastered / likely / unconfirmed)
2. User reviews and confirms which concepts to ingest
3. Call `wiki_ingest(content)` only for confirmed concepts

Never skip the preview step unless the user explicitly asks to ingest directly.

## Mastery Tracking

Every formal page has a `mastery` field:

- `deep` — can explain to others
- `solid` — understands core, can use in practice
- `surface` — knows what it is, details fuzzy

Mastery only goes up, never down. When updating existing pages, preserve or upgrade mastery.

## Commands

All commands run from the project root:

```powershell
python -m engine.cli ingest --file <path> --category AI
python -m engine.cli ingest --category AI
python -m engine.cli query "your question here"
python -m engine.cli lint
python -m engine.cli watch
node web\scripts\prepare.js
```

## MCP Tools

The engine also runs as an MCP server with these tools:

- `wiki_preview(content)` — Cognitive assessment, no writes
- `wiki_ingest(content, title?, category?)` — Digest into wiki
- `wiki_query(question)` — Search and answer from wiki
- `wiki_lint()` — Health check and auto-fix

## Key Directories

- `wiki/MyWiki/` - formal wiki pages, organized by category
- `wiki/candidates/` - candidate concepts not yet promoted into the formal graph
- `wiki/index.md` - human-readable navigation index
- `wiki/log.md` - operation history
- `sources/inbox/` - new source material waiting for ingest
- `sources/archived/` - archived source material after ingest
- `web/pages/` and `web/data/` - generated WebUI outputs
- `vectors/` - local Qdrant vector database

## Rules For Future AI Agents

- **Always preview before ingest** unless user explicitly skips.
- Prefer updating an existing page over creating a duplicate.
- Do not create many formal pages by default.
- A conversation may produce candidate concepts without promoting them.
- Only split a concept into standalone pages after the user clearly masters those sub-concepts.
- Preserve category routing and category folder structure.
- Preserve or upgrade mastery level when updating pages.
- Rebuild web data after formal wiki changes.

## Publishing

After formal wiki pages change:

```powershell
node web\scripts\prepare.js
git add wiki web
git commit -m "update wiki"
git push
```

Auto-deploys to wiki.aibc.fans via Vercel.
