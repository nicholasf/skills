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

# Register /load-topology as a Claude Code slash command
COMMANDS_DIR="$HOME/.claude/commands"
COMMAND_LINK="$COMMANDS_DIR/load-topology.md"
mkdir -p "$COMMANDS_DIR"
if [ -L "$COMMAND_LINK" ]; then
  echo "Removing existing command symlink at $COMMAND_LINK"
  rm "$COMMAND_LINK"
fi
ln -s "$REPO_DIR/load-topology/SKILL.md" "$COMMAND_LINK"
echo "Slash command registered: $COMMAND_LINK -> $REPO_DIR/load-topology/SKILL.md"

# Activate the pre-commit hook that keeps README.md in sync
git -C "$REPO_DIR" config core.hooksPath .git-hooks
echo "Git hook configured: .git-hooks/pre-commit will update README.md on each commit."
