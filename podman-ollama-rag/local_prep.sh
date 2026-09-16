#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Creating local directories..."
mkdir -p "$SCRIPT_DIR/docs" "$SCRIPT_DIR/output" "$SCRIPT_DIR/prompts"

echo "==> Copying prompt files from source..."
PROMPT_SRC="$HOME/community/workspace/rag-prompt.txt"
if [ -f "$PROMPT_SRC" ]; then
    cp "$PROMPT_SRC" "$SCRIPT_DIR/prompts/"
else
    echo "    WARNING: Prompt not found at $PROMPT_SRC - skipping"
fi

echo "==> Starting Ollama..."
podman-compose -f "$SCRIPT_DIR/podman-compose.yml" up -d ollama

echo "==> Waiting for Ollama to be ready..."
until podman exec pdf-rag-ollama ollama list &>/dev/null; do
    sleep 2
done

echo "==> Pulling LLM model (llama3.1:8b)..."
podman exec pdf-rag-ollama ollama pull llama3.1:8b

echo "==> Pulling embedding model (nomic-embed-text)..."
podman exec pdf-rag-ollama ollama pull nomic-embed-text

echo "==> Building RAG image..."
podman-compose -f "$SCRIPT_DIR/podman-compose.yml" build ragapp

echo ""
echo "================================================"
echo " Stack is ready. Next steps (manual):"
echo "================================================"
echo ""
echo " 1. Copy your PDF into the docs folder:"
echo "    cp /path/to/your.pdf $SCRIPT_DIR/docs/"
echo ""
echo " 2. Ingest the PDF:"
echo "    podman-compose run --rm ragapp ingest your.pdf --collection <name>"
echo ""
echo " 3. Ask a question:"
echo "    podman-compose run --rm ragapp ask \"your question\" --collection <name>"
echo "    podman-compose run --rm ragapp ask \"your question\" --collection <name> --system-file myprompt.txt"
echo ""
echo " 4. Summarize the document:"
echo "    podman-compose run --rm ragapp summarize --collection <name>"
echo ""
echo " Tip: output files land in $SCRIPT_DIR/output/"
echo "================================================"
