#!/usr/bin/env bash
# update-readme.sh — regenerates the Skills table in README.md from SKILL.md frontmatter.
# Run manually or via the pre-commit hook.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
README="$REPO_ROOT/README.md"

# Build the new table body by scanning every SKILL.md
table=""
for skill_file in "$REPO_ROOT"/*/SKILL.md; do
  dir="$(basename "$(dirname "$skill_file")")"

  # Extract the name field from YAML frontmatter (line starting with "name:")
  name="$(grep -m1 '^name:' "$skill_file" | sed 's/^name:[[:space:]]*//')"
  # Extract the description field (may span one line; take first match)
  description="$(grep -m1 '^description:' "$skill_file" | sed 's/^description:[[:space:]]*//')"

  # Fall back to directory name if frontmatter is missing
  name="${name:-$dir}"
  description="${description:-—}"

  table="${table}| [\`${name}\`](${dir}/SKILL.md) | ${description} |\n"
done

# Replace everything between the header row and the next blank line after the table
# Strategy: rewrite the block between "## Skills" and the next "##" section
python3 - "$README" "$table" <<'EOF'
import sys, re

readme_path = sys.argv[1]
new_rows = sys.argv[2]          # already \n-separated rows

with open(readme_path, "r") as f:
    content = f.read()

# Match the Skills table: header + separator + any number of rows
table_re = re.compile(
    r'(## Skills\n\n\| Skill \| Description \|\n\|---\|---\|\n)'  # header
    r'(?:\|.*\|\n)*',                                              # existing rows
    re.MULTILINE
)

replacement = r'\1' + new_rows.replace('\\n', '\n')

new_content, count = table_re.subn(replacement, content)
if count == 0:
    print("update-readme: could not find Skills table in README.md — no changes made.", file=sys.stderr)
    sys.exit(1)

with open(readme_path, "w") as f:
    f.write(new_content)

print(f"update-readme: Skills table updated ({count} replacement).")
EOF
