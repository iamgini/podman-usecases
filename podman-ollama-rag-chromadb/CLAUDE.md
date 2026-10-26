# podman-ollama-rag-chromadb

Fully offline local RAG stack — ingests Red Hat AAP documentation PDFs into ChromaDB so AI agents can query the official docs locally without internet access.

## Stack

- `podman-compose.yml` — two services: `ollama` (persistent model volume) + `ragapp` (built from Containerfile)
- `Containerfile` — python:3.11-slim, installs requirements, runs app/rag.py
- `app/rag.py` — CLI: `ingest`, `ingest-dir`, `validate`, `ask`
- `app/prompts/validate.txt` — AAP-specific validation system prompt

## Subcommands

- `ingest-dir [--collection aap-docs]` — ingests all PDFs from /data/docs (drop all AAP version PDFs here)
- `ingest <pdf> [--collection]` — ingests a single PDF
- `validate <design-path> [--collection] [--k 5] [--max-chunks 25]` — validates a .adoc design doc against the AAP docs RAG; design-path is relative to /data/designs (= /Users/gmadappa/cers on host)
- `ask "<question>" [--collection]` — free-form Q&A against the RAG

## Models

- LLM: `llama3.1:8b` via Ollama, CPU-only
- Embeddings: `nomic-embed-text`

## Volumes (host paths)

- `./docs` → `/data/docs` — AAP PDF documentation (read-only)
- `./output` → `/data/output` — validation reports (markdown)
- `./app/prompts` → `/data/prompts` — system prompt files
- `ollama-models` — persistent Ollama model cache
- `ragdb` — ChromaDB vector store (disposable: `podman-compose down -v`)
- `/Users/gmadappa/cers` → `/data/designs` — CER design docs (read-only)

## Typical workflow

```bash
# 1. Start services
podman-compose up -d

# 2. Pull models (first run only)
podman exec aap-rag-ollama ollama pull llama3.1:8b
podman exec aap-rag-ollama ollama pull nomic-embed-text

# 3. Drop AAP PDFs into ./docs/ then ingest all
podman-compose run --rm ragapp ingest-dir

# 4. Validate a design doc
podman-compose run --rm ragapp validate sg-gic-aap-27-on-ocp-prod-uat-design/content/150_architecture.adoc

# 5. Report is saved to ./output/<filename>-validation.md
```

## Git conventions

- No `Co-Authored-By` trailers for Claude or any AI assistant.
