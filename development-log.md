# Development Log

Chronological record of completed tasks and decisions.

<!-- Append entries here as tasks are completed. -->

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