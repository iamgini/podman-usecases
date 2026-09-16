# podman-ollama-rag

Disposable, fully offline RAG stack for querying PDF documents via Ollama in Podman. No cloud, no API keys.

## Stack

- `podman-compose.yml` — two services: `ollama` (persistent model volume) and `ragapp` (built from Containerfile)
- `Containerfile` — python:3.11-slim, installs requirements, runs app/rag.py
- `app/rag.py` — CLI with three subcommands: `ingest`, `ask`, `summarize`

## Subcommands

- `ingest <pdf> --collection <name>` — loads PDF from /data/docs, chunks, embeds via nomic-embed-text, stores in Chroma at /data/chroma
- `ask "<question>" --collection <name>` — similarity search + LLM answer
- `summarize --collection <name>` — broad retrieval + summary, saved to /data/output/<name>-summary.md

## Models

- LLM: `llama3.1:8b` via Ollama, CPU-only
- Embeddings: `nomic-embed-text`

## Volumes

- `ollama-models` — persistent, avoids re-pulling models
- `ragdb` — Chroma index, disposable: destroy with `podman-compose down -v`
- `./docs` — mounted read-only for input PDFs
- `./output` — generated summaries

## Git conventions

- No `Co-Authored-By` trailers for Claude or any AI assistant — all commits appear under the user's own git identity only.
