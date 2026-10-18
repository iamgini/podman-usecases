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
./local_prep.sh --pdf /path/to/your.pdf --prompt /path/to/your-prompt.txt --collection mydoc
```

All three arguments are required:

- `--pdf` — path to the PDF file you want to query (must be a file, not a directory)
- `--prompt` — path to your system prompt file
- `--collection` — name for the document collection (e.g. `mydoc`)

`local_prep.sh` does the following in one shot:

1. Creates `docs/`, `output/`, and `prompts/` directories
2. Copies the PDF into `./docs/` and the prompt into `./prompts/`
3. Starts Ollama via `podman-compose`
4. Pulls the LLM model (`llama3.1:8b`) and embedding model (`nomic-embed-text`)
5. Builds the `ragapp` container image
6. Ingests the PDF into the named collection (chunks, embeds, stores in Chroma)

Run it once on a fresh clone or after a full teardown. Model weights are cached in the `ollama-models` volume so subsequent runs skip the multi-GB download.

## Ask questions

```bash
podman-compose run --rm ragapp ask "What is this document about?" --collection mydoc
```

With a custom system prompt:

```bash
podman-compose run --rm ragapp ask "Summarize the key points" --collection mydoc --system-file myprompt.txt
```

Prompt files are copied into `./prompts/` by `local_prep.sh` via the `--prompt` argument.

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
