# podman-ollama-rag

Disposable, local RAG stack for asking questions about PDF documents.
Runs fully offline via Ollama in Podman - no cloud, no API keys. CPU-only
works fine (slower, but functional).

Designed to be ephemeral: spin up, ingest a document, query it, tear it
down. The Ollama model cache persists across runs so you don't re-pull
multi-GB models each time; everything else is disposable.

## Setup

```bash
git clone <this-repo>
cd podman-ollama-rag
./local_prep.sh
```

`local_prep.sh` starts Ollama, pulls both models, builds the RAG image,
and creates the `docs/`, `output/`, and `prompts/` directories.

## Ingest a document

Drop your PDF into `./docs/` first, then:

```bash
podman-compose run --rm ragapp ingest mydoc.pdf --collection mydoc
```

## Ask questions

```bash
podman-compose run --rm ragapp ask "What is this document about?" --collection mydoc
```

With a custom system prompt:

```bash
podman-compose run --rm ragapp ask "Summarize the key points" --collection mydoc --system-file myprompt.txt
```

Drop your prompt files in `./prompts/`. `local_prep.sh` can copy them in automatically.

## Generate a summary

```bash
podman-compose run --rm ragapp summarize --collection mydoc
# saved to ./output/mydoc-summary.md
```

## Tear down

```bash
./local_cleanup.sh
```

Or manually:

```bash
podman-compose down -v      # wipes the ragdb volume
rm -rf docs/* output/*
```

## Swapping models

Edit `LLM_MODEL` in `podman-compose.yml` (e.g. `qwen2.5:14b`), pull it
once via `podman exec -it pdf-rag-ollama ollama pull <model>`, then re-run.
No rebuild needed - model is set via env var.

## Stack

- Ollama - local LLM + embedding server
- LangChain - document loading, chunking, retrieval orchestration
- Chroma - local vector store, no external DB needed
- pypdf - text extraction (text-layer PDFs; scanned PDFs need OCR first)
