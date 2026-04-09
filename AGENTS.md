# LLM Wiki - Knowledge Evolution Engine

This repository is a personal knowledge evolution system.

Its goal is not to collect everything. Its goal is to internalize what the user has actually understood and turn that into a clean, searchable, publishable knowledge network.

Read `README.md` first for the current system design.

## Core Operating Principle

Do not equate "mentioned" with "mastered".

Default behavior:

- internalize only concepts the user has actually understood
- keep growth controlled
- avoid one conversation turning into many shallow wiki pages

Repository rule:

- formal knowledge goes into `wiki/MyWiki/<Category>/`
- candidate concepts go into `wiki/candidates/<Category>/`

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

## Direct Ingest from Conversation

When the user wants to internalize chat content:

1. Save a markdown snapshot into `sources/inbox/`
2. Include `category` in frontmatter when possible
3. Run ingest

Example:

```powershell
python -m engine.cli ingest --file sources\inbox\2026-04-09_topic.md --category AI
```

## Key Directories

- `wiki/MyWiki/` - formal wiki pages, organized by category
- `wiki/candidates/` - candidate concepts not yet promoted into the formal graph
- `wiki/index.md` - human-readable navigation index
- `wiki/log.md` - operation history
- `sources/inbox/` - new source material waiting for ingest
- `sources/archived/` - archived source material after ingest
- `web/pages/` and `web/data/` - generated WebUI outputs

## Rules For Future AI Agents

- Prefer updating an existing page over creating a duplicate.
- Do not create many formal pages by default.
- A conversation may produce candidate concepts without promoting them.
- Only split a concept into standalone pages after the user clearly masters those sub-concepts.
- Preserve category routing and category folder structure.
- Rebuild web data after formal wiki changes.

## Publishing Reminder

After formal wiki pages change:

```powershell
node web\scripts\prepare.js
git add wiki web
git commit -m "update wiki"
git push
```
