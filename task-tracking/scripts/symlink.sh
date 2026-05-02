#!/usr/bin/env bash
# symlink.sh — link ~/.agents/skills to this repo so pi can auto-discover skills.
#
# Usage: bash scripts/symlink.sh
#   Run from the root of the skills repo.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$HOME/.agents/skills"

echo "Repo:   $REPO_DIR"
echo "Target: $TARGET"

# Create ~/.agents if it doesn't exist
mkdir -p "$HOME/.agents"

# Remove an existing symlink or directory at the target path
if [ -L "$TARGET" ]; then
  echo "Removing existing symlink at $TARGET"
  rm "$TARGET"
elif [ -d "$TARGET" ]; then
  echo "ERROR: $TARGET exists as a real directory."
  echo "Move or remove it manually before running this script, e.g.:"
  echo "  rm -rf $TARGET"
  exit 1
fi

ln -s "$REPO_DIR" "$TARGET"
echo "Symlink created: $TARGET -> $REPO_DIR"
