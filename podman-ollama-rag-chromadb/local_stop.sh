#!/usr/bin/env bash
# local_stop.sh — stop the AAP RAG stack
#
# Usage:
#   ./local_stop.sh           stop containers, keep all data (models + ChromaDB)
#   ./local_stop.sh --clean   stop + remove containers + wipe all volumes (full reset)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/podman-compose.yml"

find_podman_compose() {
    if command -v podman-compose &>/dev/null; then echo "podman-compose"; return; fi
    local found
    found=$(find /Library/Frameworks/Python.framework -name "podman-compose" 2>/dev/null | head -1)
    if [ -n "$found" ]; then echo "$found"; return; fi
    found=$(find "$HOME/Library/Python" -name "podman-compose" 2>/dev/null | head -1)
    if [ -n "$found" ]; then echo "$found"; return; fi
    echo ""
}

COMPOSE=$(find_podman_compose)
[ -z "$COMPOSE" ] && { echo "ERROR: podman-compose not found."; exit 1; }

CLEAN=false
if [[ "${1:-}" == "--clean" ]]; then
    CLEAN=true
fi

if $CLEAN; then
    echo ""
    echo "━━━ Full clean — stopping containers and wiping all volumes ━━━"
    echo "  This will remove:"
    echo "    • aap-rag-ollama container"
    echo "    • aap-rag-api container"
    echo "    • ChromaDB vector index (ragdb volume)"
    echo "    • Ollama model cache (ollama-models volume)"
    echo ""
    read -r -p "  Are you sure? [y/N] " confirm
    case "$confirm" in
        [yY][eE][sS]|[yY])
            echo ""
            echo "  Stopping and removing containers..."
            "$COMPOSE" -f "$COMPOSE_FILE" down -v 2>/dev/null || true
            echo "  ✓ Containers stopped and volumes wiped"
            echo ""
            echo "  To start fresh: ./local_start.sh"
            ;;
        *)
            echo "  Cancelled."
            exit 0
            ;;
    esac
else
    echo ""
    echo "━━━ Stopping AAP RAG stack (data preserved) ━━━"
    "$COMPOSE" -f "$COMPOSE_FILE" stop 2>/dev/null || true
    echo "  ✓ Containers stopped"
    echo "  ✓ ChromaDB index and Ollama models preserved"
    echo ""
    echo "  To restart:   ./local_start.sh"
    echo "  To full clean: ./local_stop.sh --clean"
fi
echo ""
