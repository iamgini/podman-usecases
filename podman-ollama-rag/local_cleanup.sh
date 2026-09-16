#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Stopping and removing containers..."
podman-compose -f "$SCRIPT_DIR/podman-compose.yml" down -v 2>/dev/null || true

echo "==> Removing named volumes (if still present)..."
podman volume rm -f podman-ollama-rag_ollama-models 2>/dev/null || true
podman volume rm -f podman-ollama-rag_ragdb 2>/dev/null || true

echo "==> Removing pulled/built images..."
podman rmi -f docker.io/ollama/ollama:latest 2>/dev/null || true
podman rmi -f "$(podman images --filter 'label=io.buildah.version' --format '{{.Id}}' \
    --filter dangling=false 2>/dev/null | head -1)" 2>/dev/null || true
# remove the ragapp image by name if it was tagged
podman rmi -f localhost/podman-ollama-rag_ragapp 2>/dev/null || true

echo "==> Clearing local docs and output..."
rm -rf "$SCRIPT_DIR/docs/"* "$SCRIPT_DIR/output/"*

echo "==> Pruning any leftover dangling images..."
podman image prune -f 2>/dev/null || true

echo ""
echo "Done. ollama-models volume removed - next run will re-pull models."
echo "To keep models for next time, remove the 'podman volume rm' lines above."
