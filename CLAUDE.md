# LLM Wiki - Knowledge Evolution Engine

This project is a personal knowledge digestion tracker — not a knowledge base organizer.

It does **not** assume the user already understands the material. The wiki should reflect what the user has actually digested through conversation, not what the AI has summarized for them. If a concept enters the wiki but the user can't explain it, the system has failed.

## Core Principle

**Only internalize what the user has actually understood.** Do not equate "mentioned" with "mastered". The wiki is a mirror of the user's real cognitive state.

## Recommended Workflow (Two-Step Confirmation)

1. **Preview first**: After a conversation covers new knowledge, call `wiki_preview` to generate a cognitive snapshot — this assesses what the user demonstrated understanding of, without writing anything.
2. **User confirms**: The user reviews the snapshot and decides what to ingest.
3. **Ingest on approval**: Only after confirmation, call `wiki_ingest` to write approved concepts into the wiki.

This ensures the wiki strictly reflects the user's actual cognitive state.

## MCP Tools

This project runs as an MCP server. Available tools:

- `wiki_preview(content)` — Cognitive assessment. Analyzes conversation content and returns a snapshot of mastered/likely/unconfirmed concepts. **Does not write anything.**
- `wiki_ingest(content, title?, category?)` — Digest confirmed knowledge into wiki pages.
- `wiki_query(question)` — Search existing knowledge and answer questions.
- `wiki_lint()` — Health check the wiki for contradictions, orphans, and gaps.

## CLI Commands

All commands run from the project root:

```bash
python -m engine.cli ingest --file <path>        # digest a specific file
python -m engine.cli ingest                       # digest all files in inbox
python -m engine.cli query "your question here"
python -m engine.cli lint
python -m engine.cli watch                        # watch inbox for new files
```

## Direct Ingest from Conversation

When the user wants to internalize chat content:

1. Save a markdown snapshot into `sources/inbox/`
2. Include `category` in frontmatter when possible
3. Run ingest

## Key Directories

- `wiki/MyWiki/<Category>/` — Formal wiki pages (Obsidian reads this directly)
- `wiki/candidates/<Category>/` — Candidate concepts not yet promoted
- `sources/inbox/` — New materials waiting to be digested
- `sources/archived/` — Already digested materials
- `engine/` — Core engine code
- `web/` — VitePress web UI (auto-deployed via Vercel)

## Mastery Tracking

Each wiki page has a `mastery` field in frontmatter:

- `deep` — Can explain to others, understands details and edge cases
- `solid` — Understands core principles, can use in practice
- `surface` — Knows what it is, but details are fuzzy

Mastery only goes up, never down. Query results are boosted by mastery level.

## After Knowledge Updates

When wiki pages are updated, publish to the web:

```bash
node web/scripts/prepare.js
git add wiki/ web/ && git commit -m "update wiki" && git push
```

This auto-deploys to wiki.aibc.fans via Vercel.

## Important

- The wiki uses `[[double brackets]]` for cross-page links
- Pages have YAML frontmatter (title, tags, related, mastery, evolution, etc.)
- Always prefer updating existing pages over creating duplicates
- Default to at most 1-2 formal concepts per conversation round
- Keep candidate concepts out of the formal wiki until confirmed
