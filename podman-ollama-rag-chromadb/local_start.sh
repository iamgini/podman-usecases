#!/usr/bin/env bash
# local_start.sh — first-run setup and start for podman-ollama-rag-chromadb (macOS)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/podman-compose.yml"
ENV_FILE="$SCRIPT_DIR/.env"
MCP_SERVER="$SCRIPT_DIR/mcp/server.py"
OLLAMA_CONTAINER="aap-rag-ollama"
LLM_MODEL="llama3.1:8b"
EMBED_MODEL="nomic-embed-text"
RAGDB_VOLUME="podman-ollama-rag-chromadb_ragdb"

# ── helpers ────────────────────────────────────────────────────────────────────
print_header() { echo ""; echo "━━━ $1 ━━━"; }
ok()   { echo "  ✓ $1"; }
warn() { echo "  ⚠ $1"; }
info() { echo "  → $1"; }
die()  { echo ""; echo "ERROR: $1"; exit 1; }

find_podman_compose() {
    if command -v podman-compose &>/dev/null; then
        echo "podman-compose"
        return
    fi
    # pip installs to version-specific bin dirs on macOS — search them
    local found
    found=$(find /Library/Frameworks/Python.framework -name "podman-compose" 2>/dev/null | head -1)
    if [ -n "$found" ]; then echo "$found"; return; fi
    found=$(find "$HOME/Library/Python" -name "podman-compose" 2>/dev/null | head -1)
    if [ -n "$found" ]; then echo "$found"; return; fi
    echo ""
}

# ── 1. check podman ────────────────────────────────────────────────────────────
print_header "1/7  Checking Podman"
if ! command -v podman &>/dev/null; then
    die "Podman not found. Install from https://podman.io/docs/installation"
fi
if ! podman info &>/dev/null 2>&1; then
    warn "Podman machine may not be running. Trying to start it..."
    podman machine start 2>/dev/null || die "Could not start Podman machine. Run 'podman machine init' first."
fi
ok "Podman $(podman --version | awk '{print $3}')"

# ── 2. check / install podman-compose ─────────────────────────────────────────
print_header "2/7  Checking podman-compose"
COMPOSE=$(find_podman_compose)
if [ -z "$COMPOSE" ]; then
    info "Not found — installing via pip3..."
    pip3 install --quiet podman-compose
    COMPOSE=$(find_podman_compose)
    [ -z "$COMPOSE" ] && die "podman-compose install failed. Try: pip3 install podman-compose"
fi
ok "podman-compose at $COMPOSE"

# ── 3. check / install MCP server deps ────────────────────────────────────────
print_header "3/7  Checking MCP server dependencies"
if ! python3 -c "import mcp, httpx" &>/dev/null; then
    info "Installing mcp + httpx for MCP server..."
    pip3 install --quiet mcp httpx
fi
ok "mcp + httpx ready"

# ── 4. configure .env ─────────────────────────────────────────────────────────
print_header "4/7  Checking .env"
if [ ! -f "$ENV_FILE" ]; then
    cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
    warn ".env created from .env.example — edit it to set AAP_DOCS_DIR before continuing."
    warn "  AAP_DOCS_DIR should point to the directory containing your AAP PDF files."
    echo ""
    echo "  Edit: $ENV_FILE"
    echo "  Then re-run: $0"
    exit 0
fi

source "$ENV_FILE"
AAP_DOCS_DIR="${AAP_DOCS_DIR:-}"
if [ -z "$AAP_DOCS_DIR" ] || [ ! -d "$AAP_DOCS_DIR" ]; then
    die "AAP_DOCS_DIR not set or directory not found in .env\n  Current value: '${AAP_DOCS_DIR:-unset}'"
fi
PDF_COUNT=$(find "$AAP_DOCS_DIR" -maxdepth 1 -name "*.pdf" | wc -l | tr -d ' ')
[ "$PDF_COUNT" -eq 0 ] && die "No PDFs found in AAP_DOCS_DIR: $AAP_DOCS_DIR"
ok ".env valid — AAP_DOCS_DIR has $PDF_COUNT PDF(s)"

# ── 5. start Ollama and pull models ───────────────────────────────────────────
print_header "5/7  Starting Ollama"
"$COMPOSE" -f "$COMPOSE_FILE" up -d ollama 2>/dev/null
info "Waiting for Ollama to be ready..."
until podman exec "$OLLAMA_CONTAINER" ollama list &>/dev/null; do
    sleep 2; echo -n "."
done
echo ""

EXISTING_MODELS=$(podman exec "$OLLAMA_CONTAINER" ollama list 2>/dev/null)

if echo "$EXISTING_MODELS" | grep -q "$LLM_MODEL"; then
    ok "$LLM_MODEL already present"
else
    info "Pulling $LLM_MODEL (~5 GB, this takes a while)..."
    podman exec "$OLLAMA_CONTAINER" ollama pull "$LLM_MODEL"
    ok "$LLM_MODEL ready"
fi

if echo "$EXISTING_MODELS" | grep -q "$EMBED_MODEL"; then
    ok "$EMBED_MODEL already present"
else
    info "Pulling $EMBED_MODEL..."
    podman exec "$OLLAMA_CONTAINER" ollama pull "$EMBED_MODEL"
    ok "$EMBED_MODEL ready"
fi

# ── 6. build images ───────────────────────────────────────────────────────────
print_header "6/7  Building container images"
"$COMPOSE" -f "$COMPOSE_FILE" build ragapp ragapi 2>/dev/null | grep -E "^(STEP|Successfully|ERROR)" || true
ok "Images built"

# ── 7. ingest docs (skip if ChromaDB volume already has data) ─────────────────
print_header "7/7  Ingesting AAP documentation"
if podman volume inspect "$RAGDB_VOLUME" &>/dev/null; then
    ok "ChromaDB volume exists — skipping ingest (already done)"
    info "To re-ingest: podman volume rm $RAGDB_VOLUME && $0"
else
    info "Ingesting $PDF_COUNT PDF(s) into ChromaDB (this takes several minutes)..."
    "$COMPOSE" -f "$COMPOSE_FILE" run --rm ragapp ingest-dir 2>&1 | grep -v "telemetry"
    ok "Ingest complete"
fi

# ── start the API ─────────────────────────────────────────────────────────────
"$COMPOSE" -f "$COMPOSE_FILE" up -d ragapi 2>/dev/null
info "Waiting for API..."
sleep 4
until curl -sf http://localhost:8000/health &>/dev/null; do
    sleep 2; echo -n "."
done
echo ""
ok "HTTP API running at http://localhost:8000"

# ── MCP server registration check ─────────────────────────────────────────────
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
if [ -f "$CLAUDE_SETTINGS" ] && grep -q "aap-docs" "$CLAUDE_SETTINGS" 2>/dev/null; then
    ok "MCP server already registered in Claude Code"
else
    echo ""
    warn "MCP server not registered in Claude Code."
    warn "Add this to $CLAUDE_SETTINGS under \"mcpServers\":"
    echo ""
    cat <<MCP_SNIPPET
    "aap-docs": {
      "command": "$(command -v python3)",
      "args": ["$MCP_SERVER"],
      "description": "Local AAP documentation RAG"
    }
MCP_SNIPPET
    echo ""
    warn "Then restart Claude Code."
fi

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " AAP RAG stack is ready"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo " HTTP API:   http://localhost:8000/ask"
echo " Health:     http://localhost:8000/health"
echo " MCP tool:   ask_aap_docs  (in Claude Code after restart)"
echo ""
echo " Quick test:"
echo "   curl -s -X POST http://localhost:8000/ask \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"question\": \"What is the Automation Gateway in AAP 2.7?\"}'"
echo ""
echo " Stop:   ./local_stop.sh"
echo " Clean:  ./local_stop.sh --clean"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
