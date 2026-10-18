#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    echo "Usage: $0 --pdf <path/to/file.pdf> --prompt <path/to/prompt.txt> --collection <name>"
    echo ""
    echo "  --pdf        Path to the PDF file to ingest"
    echo "  --prompt     Path to the system prompt file"
    echo "  --collection Collection name to store the ingested document"
    exit 1
}

PDF_SRC=""
PROMPT_SRC=""
COLLECTION=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pdf)        PDF_SRC="$2";    shift 2 ;;
        --prompt)     PROMPT_SRC="$2"; shift 2 ;;
        --collection) COLLECTION="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; usage ;;
    esac
done

# Validate
if [ -z "$PDF_SRC" ] || [ -z "$PROMPT_SRC" ] || [ -z "$COLLECTION" ]; then
    echo "ERROR: --pdf, --prompt, and --collection are all required."
    usage
fi

if [ ! -f "$PDF_SRC" ]; then
    echo "ERROR: PDF file not found: $PDF_SRC"
    exit 1
fi

if [ ! -f "$PROMPT_SRC" ]; then
    echo "ERROR: Prompt file not found: $PROMPT_SRC"
    exit 1
fi

PDF_NAME="$(basename "$PDF_SRC")"
PROMPT_NAME="$(basename "$PROMPT_SRC")"

echo ""
echo "================================================"
echo " podman-ollama-rag setup"
echo "================================================"
echo " PDF        : $PDF_NAME"
echo " Prompt     : $PROMPT_NAME"
echo " Collection : $COLLECTION"
echo "================================================"
echo ""

echo "[1/7] Creating local directories (docs, output, prompts)..."
mkdir -p "$SCRIPT_DIR/docs" "$SCRIPT_DIR/output" "$SCRIPT_DIR/prompts"
echo "      Done."
echo ""

echo "[2/7] Copying PDF to ./docs/ ..."
cp "$PDF_SRC" "$SCRIPT_DIR/docs/"
echo "      Copied: $PDF_NAME"
echo ""

echo "[3/7] Copying prompt file to ./prompts/ ..."
cp "$PROMPT_SRC" "$SCRIPT_DIR/prompts/"
echo "      Copied: $PROMPT_NAME"
echo ""

echo "[4/7] Starting Ollama container (this may pull the image if not cached)..."
podman-compose -f "$SCRIPT_DIR/podman-compose.yml" up -d ollama
echo "      Ollama container started. Waiting for it to be ready..."
until podman exec pdf-rag-ollama ollama list &>/dev/null; do
    echo -n "."
    sleep 2
done
echo ""
echo "      Ollama is ready."
echo ""

echo "[5/7] Pulling models (this may take a while on first run)..."
echo "      Pulling LLM model: llama3.1:8b ..."
podman exec pdf-rag-ollama ollama pull llama3.1:8b
echo "      Pulling embedding model: nomic-embed-text ..."
podman exec pdf-rag-ollama ollama pull nomic-embed-text
echo "      Models ready."
echo ""

echo "[6/7] Building ragapp container image..."
podman-compose -f "$SCRIPT_DIR/podman-compose.yml" build ragapp
echo "      Build complete."
echo ""

echo "[7/7] Ingesting PDF into collection '$COLLECTION' ..."
echo "      This chunks and embeds the document - may take a few minutes."
podman-compose -f "$SCRIPT_DIR/podman-compose.yml" run --rm ragapp ingest "$PDF_NAME" --collection "$COLLECTION"
echo "      Ingestion complete."
echo ""

echo "================================================"
echo " Stack is ready!"
echo "================================================"
echo ""
echo " Ask a question (plain):"
echo "    podman-compose run --rm ragapp ask \"What is this document about?\" --collection $COLLECTION"
echo ""
echo " Ask with your custom prompt:"
echo "    podman-compose run --rm ragapp ask \"Summarize the key points\" \\"
echo "        --collection $COLLECTION --system-file $PROMPT_NAME"
echo ""
echo " Generate a summary:"
echo "    podman-compose run --rm ragapp summarize --collection $COLLECTION"
echo "    # saved to ./output/$COLLECTION-summary.md"
echo ""
echo " Tip: Output files land in $SCRIPT_DIR/output/"
echo "================================================"
