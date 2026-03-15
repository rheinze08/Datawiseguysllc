#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_FILE="$ROOT_DIR/index.html"

python3 "$ROOT_DIR/scripts/render_index.py"
echo "Generated: $OUTPUT_FILE"

if [[ "${1:-}" == "--deploy" ]]; then
  if ! git -C "$ROOT_DIR" remote get-url origin >/dev/null 2>&1; then
    echo "No git remote named 'origin' is configured. Skipping deploy." >&2
    exit 2
  fi

  CURRENT_BRANCH="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"
  git -C "$ROOT_DIR" add index.html
  if ! git -C "$ROOT_DIR" diff --cached --quiet; then
    git -C "$ROOT_DIR" commit -m "Build GitHub Pages index.html"
  fi

  git -C "$ROOT_DIR" push origin "$CURRENT_BRANCH":gh-pages
  echo "Deployed branch '$CURRENT_BRANCH' to 'gh-pages'."
fi
