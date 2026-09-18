#!/usr/bin/env bash
# Symlinks techabbr.py onto your PATH as `abbr`.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$HOME/.local/bin}"

mkdir -p "$TARGET_DIR"
chmod +x "$SCRIPT_DIR/techabbr.py"
ln -sf "$SCRIPT_DIR/techabbr.py" "$TARGET_DIR/abbr"

echo "Linked $TARGET_DIR/abbr -> $SCRIPT_DIR/techabbr.py"

case ":$PATH:" in
  *":$TARGET_DIR:"*)
    echo "Run 'abbr --help' to get started."
    ;;
  *)
    echo "$TARGET_DIR is not on your PATH."
    echo "Add this to your shell profile (~/.zshrc or ~/.bashrc):"
    echo "  export PATH=\"$TARGET_DIR:\$PATH\""
    ;;
esac
