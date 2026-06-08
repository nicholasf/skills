# Development Log

Chronological record of completed tasks and decisions.

<!-- Append entries here as tasks are completed. -->

## 2026-06-06 — load-topology-skill tests and GitHub Actions

24 pytest tests across test_discover_tailscale.py (8 tests: abstract base class, self/peer parsing, IPv6 skipping, error cases) and test_refresh_topology.py (16 tests: get_topology_path env resolution, parse_table, merge, build_table, update_last_refreshed). pyproject.toml and .github/workflows/test.yml already in place. Pond was cut off before test_refresh_topology.py; Claude wrote both files. All 24 pass.

## 2026-06-06 — load-topology-skill formalised

Rewrote SKILL.md (removed hardcoded paths and symlink script, uses $TOPOLOGY_PATH/$SSH_USER, adds refresh command). Wrote README.md with homelab framing, full topology format spec, LLM Node role, SSH_USER prerequisite, 9-test benchmark suite (Go/Python/React × simple/complex/reasoning), privacy section (.gitignore). Added .gitignore to load-topology-skill and local-system repos (topology.md and *-topology.md). Created scripts/discover_tailscale.py (NetworkProvider ABC + TailscaleProvider) and scripts/refresh_topology.py (archive, discover, merge, write). Pond had two bugs fixed: peer iteration used .values(), table_end defaulted to len(lines).

## 2026-06-06 — manage-skills-skill tests and GitHub Actions

19 pytest tests covering read_skill_list, write_skill_list, context_output, install_skill, sync_skill, and list_skills. pyproject.toml added with version, dev dependency, and pythonpath config. GitHub Actions workflow runs tests on push/PR to main. Pond's output had 5 bugs; tests rewritten by Claude.

## 2026-06-06 — manage-skills-skill context subcommand and load_at_startup

Added `load_at_startup` column to `skill-list.md` format, `--load-at-startup` flag to `install`, and `context` subcommand to `manage_skills.py`. `context` reads skills marked for startup, concatenates their `SKILL.md` content, and outputs the `SessionStart` JSON. `bootstrap.sh` updated to seed `skill-list.md` with the correct 4-column format and add the manage-skills-skill entry. `~/.claude/settings.json` `SessionStart` hook replaced with the single dynamic command. README updated. Pond lost existing functionality in its rewrite; Claude merged the additions manually.

## 2026-06-06 — manage-skills-skill README

Short README added to manage-skills-skill: cheesy meta joke opener followed by usage examples for install/sync/list and a setup pointer. Pond produced a longer doc but user redirected to keep detail in SKILL.md only.

## 2026-06-06 — manage-skills-skill core

Created the three files forming the `manage-skills-skill` repo: `manage_skills.py` (Python CLI with install/sync/list), `bootstrap.sh` (first-time setup), and `SKILL.md` (slash command routing). Pond produced the initial output; Claude applied a one-line bug fix (`sync` subcommand now accepts a bare positional name via `args.url or args.name`). Files written to `/home/nicholasf/code/github/nicholasf/manage-skills-skill/`.

## 2026-05-26 — Extract tools into package

Moved the five inline tool functions out of `agent.py` into `ask-foreign-agent/tools/` (one file per tool). Shared `_cwd` state and `_run` helper live in `_context.py`. `agent.py` now imports from the package and sets `_context._cwd` in `main()`. Pond's output was not used — it discarded the agentic loop and had several spec deviations; files were written by Claude.

## 2026-05-26 — Write unit tests

Created `ask-foreign-agent/tests/` with pytest and 17 tests covering all eight tools (typecheck excluded — environment-specific). LangChain `StructuredTool` objects require `.invoke({...})` rather than direct calls. `list_directory` exclusion bug fixed (single `|` pattern in `find` is silently broken — corrected to separate `-not -path` clauses). Added pytest as a dev dependency in `pyproject.toml`.

## 2026-05-26 — Add new tools

Added four new tools to `ask-foreign-agent/tools/`:
- `edit_file` - Replace exact string in file with error handling
- `list_directory` - List directory tree with exclusions
- `git_diff` - Show unstaged and staged working-tree changes
- `typecheck` - Run TypeScript compiler on backend/saga

All tools follow existing patterns and were wired into `TOOLS` and `TOOL_MAP` in `__init__.py`.