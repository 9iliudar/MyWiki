# MyWiki

MyWiki is a personal knowledge evolution system.

It is not a generic note dump. Its purpose is to turn conversation, reading, and project thinking into a controlled personal knowledge network that can be searched, refined, and published.

## Core Idea

The project follows one simple principle:

`Chat = input, wiki = formalized knowledge, web = readable output`

The system is designed around "internalization", not "collection".

That means:

- A concept should enter the formal wiki only after the user has actually understood it.
- Mentioned concepts should not automatically explode into many pages.
- The knowledge network should grow slowly, deliberately, and by mastery.

This is the most important design decision in the whole repository.

## What Problem It Solves

Most note systems become warehouses:

- too many concepts
- too many shallow pages
- weak links between ideas
- no distinction between "mentioned" and "mastered"

MyWiki tries to solve that by separating:

- what the user has already mastered
- what the user has only touched
- what was merely mentioned in conversation

The result should be a smaller but higher-quality knowledge network.

## Knowledge Growth Philosophy

This repository now follows these rules:

- Prefer depth over breadth.
- Internalize one concept only when it is actually understood.
- Default to at most `1-2` formal concepts per conversation round.
- Keep derived concepts in a candidate layer until they are explicitly confirmed.
- Preserve overview pages when useful, but split independent concepts into their own pages only after mastery is clear.

In short:

`精不求多，消化一个，进一个。`

## System Architecture

The system has four main layers.

### 1. Input Layer

Raw material enters from:

- direct chat internalization
- markdown files placed in `sources/inbox/`
- future MCP or external tool calls

After ingest, source files are archived into `sources/archived/`.

### 2. Internalization Layer

The Python engine reads source material, asks the LLM to digest it, and decides:

- which concepts are formalized into wiki pages
- which concepts remain candidates
- which existing pages should be updated instead of duplicated

This logic lives mainly in:

- [engine/ingest.py](D:/project/mywiki/engine/ingest.py)
- [engine/prompts.py](D:/project/mywiki/engine/prompts.py)
- [engine/json_utils.py](D:/project/mywiki/engine/json_utils.py)
- [engine/wiki_io.py](D:/project/mywiki/engine/wiki_io.py)

### 3. Knowledge Storage Layer

Formal knowledge is stored as Markdown with frontmatter under:

- `wiki/MyWiki/<Category>/`

Candidate concepts are stored separately under:

- `wiki/candidates/<Category>/`

This separation is intentional:

- formal pages represent mastered knowledge
- candidate pages represent possible future knowledge

### 4. Retrieval and Publishing Layer

The project supports:

- semantic retrieval through local embeddings + Qdrant
- CLI query against the current wiki
- WebUI publishing through VitePress
- Obsidian browsing through the same Markdown files

Relevant modules:

- [engine/query.py](D:/project/mywiki/engine/query.py)
- [engine/embed.py](D:/project/mywiki/engine/embed.py)
- [web/scripts/prepare.js](D:/project/mywiki/web/scripts/prepare.js)

## Current Directory Layout

The current effective layout is:

```text
wiki/
  MyWiki/
    AI/
    Finance/
    IoT/
    Mechanical-Design/
    Management/
    Crypto/
    Digital-Transformation/
    Software-Engineering/
    Maker/
    General/
    Unsorted/
  candidates/
    <Category>/
  index.md
  log.md

sources/
  inbox/
  archived/

vectors/

web/
  pages/
  data/
  .vitepress/
```

## Category Model

Obsidian should point to exactly one vault root:

- `wiki/MyWiki`

Do not open one vault per category.

Use folders for primary classification and links/tags for cross-domain relationships.

Current top-level categories include:

- `AI`
- `IoT`
- `Finance`
- `Mechanical-Design`
- `Management`
- `Crypto`
- `Digital-Transformation`
- `Software-Engineering`
- `Maker`
- `General`
- `Unsorted`

Rules:

- each page has one primary category
- cross-domain meaning should be expressed via `[[links]]` and tags
- do not duplicate the same concept across multiple category folders

## Formal vs Candidate Knowledge

This is a core repository rule.

### Formal Knowledge

Formal knowledge means:

- the user has actually understood the concept
- the concept deserves a stable page in the main wiki
- it can safely participate in the main knowledge graph

Formal pages go into:

- `wiki/MyWiki/<Category>/`

### Candidate Knowledge

Candidate knowledge means:

- the concept appeared during conversation
- it may be useful later
- but the user has not clearly mastered it yet

Candidates go into:

- `wiki/candidates/<Category>/`

This prevents knowledge explosion.

## Standard Workflow

### 1. Chat and Clarify

The user discusses a concept until it is actually understood.

### 2. Internalize

Only mastered concepts are promoted into formal wiki pages.

If a concept is not yet mastered, it should stay in candidates or remain only in source material.

### 3. Archive

The original conversation snapshot or source material is archived under `sources/archived/`.

### 4. Rebuild Web Data

After wiki pages change, rebuild the WebUI data:

```powershell
node web\scripts\prepare.js
```

### 5. Review in Obsidian or WebUI

Obsidian reads the raw Markdown structure from `wiki/MyWiki`.

WebUI reads generated page metadata from `web/data` and generated markdown pages from `web/pages`.

## CLI Usage

All commands run from the repository root.

### Ingest

Digest one file:

```powershell
python -m engine.cli ingest --file sources\inbox\example.md --category AI
```

Digest all inbox files:

```powershell
python -m engine.cli ingest --category AI
```

### Query

```powershell
python -m engine.cli query "What do I already know about boundary design?"
```

### Lint

```powershell
python -m engine.cli lint
```

### Watch

```powershell
python -m engine.cli watch
```

## Web Publishing Flow

The WebUI is a published projection of the wiki, not the source of truth.

Source of truth:

- `wiki/MyWiki/`

Generated for web:

- `web/pages/`
- `web/data/wiki-meta.json`
- `web/data/route-map.json`
- `web/data/graph.json`

Rebuild command:

```powershell
node web\scripts\prepare.js
```

Then commit and push as needed.

## Important Operational Rules

If you are a future maintainer or AI agent, follow these rules:

- Do not create many pages from one conversation by default.
- Do not confuse "mentioned" with "mastered".
- Prefer updating an existing page over creating a duplicate page.
- Preserve category structure under `wiki/MyWiki/<Category>/`.
- Keep candidate concepts out of the main knowledge graph until confirmed.
- Rebuild web data after formal wiki changes.
- Treat Obsidian and WebUI as views over the same knowledge base, not separate systems.

## Key Outcomes Achieved So Far

This project has already established several important corrections:

- category-based wiki storage
- candidate-layer buffering to avoid concept explosion
- route-aware WebUI pages and graph navigation
- Obsidian-compatible single-vault structure
- a cleaner distinction between formal knowledge and overview pages

These are not minor implementation details. They are the current operating model of the repository.

## Recommended Next Principle

When in doubt, use this decision rule:

`If the user has not clearly understood it, do not promote it into the formal wiki yet.`

That rule protects the entire system.
