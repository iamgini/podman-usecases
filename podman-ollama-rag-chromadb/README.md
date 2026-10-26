# podman-ollama-rag-chromadb

A fully offline, local RAG (Retrieval-Augmented Generation) stack that gives AI agents a fast, private knowledge base of official Red Hat Ansible Automation Platform (AAP) documentation — no internet access required at query time.

## Why

AI agents and LLMs frequently need to reference AAP documentation for accurate, version-specific answers. Fetching pages from the internet on every query is slow, unreliable, and not possible in air-gapped environments. This stack ingests the full official AAP PDF documentation set once and serves it locally, so any AI agent can query it instantly without leaving the machine.

## Architecture

```
Claude Code (AI agent)
        │
        ▼
mcp/server.py  (host-side stdio process)     ← spawned by Claude Code on startup
  └── calls POST /ask on the API
        │
        ▼
local-rag-api container  (localhost:8000)
  ├── FastAPI HTTP API  ← any agent via POST /ask or curl
  ├── Query rewriting  ← LLM rephrases question before vector search
  ├── ChromaDB client  ← queries the persisted vector index
  └── LangChain + Ollama embeddings + LLM
        │
        ▼
local-rag-ollama container  (localhost:11434)
  ├── llama3.1:8b          ← LLM, CPU-only
  └── nomic-embed-text     ← embedding model
```

- **MCP server** — `mcp/server.py` runs on the host; Claude Code spawns it as a stdio process; it calls the HTTP API
- **Query rewriting** — the API rewrites questions into documentation terminology before vector search, improving retrieval accuracy
- **HTTP API** — FastAPI at `localhost:8000`; usable by any agent via `POST /ask`
- **CLI** — `podman-compose run --rm ragapp ask "..."` for ad-hoc queries
- All components run locally. No cloud, no API keys, no internet at query time.

## Stack

| Component | Technology |
|---|---|
| Container runtime | Podman + podman-compose |
| LLM | `llama3.1:8b` via Ollama (CPU, fully local) |
| Embeddings | `nomic-embed-text` via Ollama |
| Vector store | ChromaDB (persisted volume) |
| Orchestration | LangChain |
| HTTP API | FastAPI + uvicorn |
| Agent integration | MCP (Model Context Protocol) |

## Getting the AAP Documentation

Download the official AAP PDF documentation directly from [docs.redhat.com](https://docs.redhat.com) — no login required. Download all guides for the AAP versions you need and place them in the `docs/` directory (or set `DOCS_DIR` in `.env` to an existing folder).

Example for AAP 2.7:

```
docs/
  aap-administer-2-7-pdf.pdf
  aap-develop-2-7-pdf.pdf
  aap-install-2-7-pdf.pdf
  aap-plan-2-7-pdf.pdf
  aap-secure-2-7-pdf.pdf
  ...
```

You can mix multiple AAP versions in the same directory — all are ingested into one searchable collection.

## Quick Start (macOS)

Two scripts handle everything:

```bash
./local_start.sh          # first-run setup + start (safe to re-run)
./local_stop.sh           # stop containers, keep all data
./local_stop.sh --clean   # stop + wipe everything (full reset)
```

`local_start.sh` will:
1. Check Podman is installed and running
2. Install `podman-compose` via pip3 if missing
3. Create `.env` from `.env.example` on first run (then exit for you to fill it in)
4. Pull Ollama models on first run (~5 GB, skipped if already present)
5. Build container images
6. Ingest PDFs into ChromaDB (skipped if already done)
7. Start the HTTP API + MCP server at `localhost:8000`
8. Print MCP registration snippet if not yet registered in Claude Code

---

## Manual Setup

### 1. Configure paths

```bash
cp .env.example .env
# Edit .env and set your local paths:
#   DOCS_DIR=/path/to/your/aap-docs
```

### 2. Start Ollama

```bash
podman-compose up -d ollama
```

### 3. Pull models (first run only — ~5 GB)

```bash
podman exec local-rag-ollama ollama pull llama3.1:8b
podman exec local-rag-ollama ollama pull nomic-embed-text
```

### 4. Build the app images

```bash
podman-compose build ragapp ragapi
```

### 5. Ingest documentation (run once)

```bash
podman-compose run --rm ragapp ingest-dir
```

This chunks and embeds all PDFs into ChromaDB. The index persists across restarts — re-run only when you add new PDFs.

### 6. Start the HTTP API

```bash
podman-compose up -d ragapi
```

The API is now available at `http://localhost:8000`.

---

## Agent Integration

### Option A — MCP (native Claude Code tool)

`mcp/server.py` is a lightweight host-side stdio server that calls the HTTP API. Claude Code spawns it as a subprocess — no container ports or SSE connections involved.

**Register (one-time):**

```bash
claude mcp add --scope user local-rag /usr/local/bin/python3 \
  /path/to/podman-ollama-rag-chromadb/mcp/server.py
```

Replace `/path/to/` with the actual clone path. Requires `mcp` and `httpx` on the host:

```bash
pip3 install "mcp[cli]<2.0.0" httpx
```

Restart Claude Code and run `/mcp` to confirm `local-rag` is listed with an `ask_rag` tool. Claude will call it automatically — no Bash or curl needed.

### Option B — HTTP API (any agent)

```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Automation Gateway in AAP 2.7?"}'
```

Response:

```json
{
  "answer": "The Automation Gateway is ...",
  "sources": [
    {"file": "aap-whats-new-2-7-pdf.pdf", "page": 12}
  ],
  "collection": "aap-docs"
}
```

### Option C — CLI (ad-hoc queries)

```bash
podman-compose run --rm ragapp ask "What ports are required between execution nodes and the control plane?"

podman-compose run --rm ragapp ask "What changed in AAP 2.7 compared to 2.6?"
```

---

## CLI Reference

```bash
# Ingest all PDFs in the docs directory
podman-compose run --rm ragapp ingest-dir [--collection aap-docs]

# Ingest a single PDF
podman-compose run --rm ragapp ingest aap-plan-2-7-pdf.pdf [--collection aap-docs]

# Ask a question
podman-compose run --rm ragapp ask "your question" [--collection aap-docs] [--k 6]
```

All commands accept `--collection <name>` to segment by version or topic (e.g. `aap-26`, `aap-27`).

---

## After a Reboot

Models and the ChromaDB index persist in named volumes. Just restart the services — no re-ingestion needed:

```bash
./local_start.sh
```

---

## Volumes

| Volume | Purpose | Persistence |
|---|---|---|
| `ollama-models` | Pulled Ollama models | Persistent |
| `ragdb` | ChromaDB vector index | Persistent |

To wipe the vector index and start fresh:

```bash
podman-compose down -v
podman-compose run --rm ragapp ingest-dir   # re-ingest after wipe
```
