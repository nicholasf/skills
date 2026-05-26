# Extract tools into a package

**Created:** 2026-05-26 11:26:50
**Model:** qwen3-coder-30b on pond — mechanical extraction and wiring
**Status:** completed

## Goal

Move the five tool functions out of `agent.py` into a `tools/` package so each tool lives in its own file, while keeping `agent.py` as the entry point.

## Background

`agent.py` currently defines all tools inline. The plan is to add new tools and tests, which requires a proper package structure. `IMPROVEMENTS.md` in `ask-foreign-agent/` has the full context.

## Changes

- Create `ask-foreign-agent/tools/_context.py`
  - Module-level `_cwd: str = "."` (mutable shared state)
  - `_run(command: str, timeout: int = 30) -> str` function — identical logic to the current one in `agent.py`, but reads `_cwd` from this module
- Create `ask-foreign-agent/tools/bash.py` — `bash` tool, imports `_context._run`
- Create `ask-foreign-agent/tools/read_file.py` — `read_file` tool, uses `_context._cwd`
- Create `ask-foreign-agent/tools/write_file.py` — `write_file` tool, uses `_context._cwd`
- Create `ask-foreign-agent/tools/find_files.py` — `find_files` tool, imports `_context._run`
- Create `ask-foreign-agent/tools/grep.py` — `grep` tool, imports `_context._run`
- Create `ask-foreign-agent/tools/__init__.py`
  - Imports all five tools
  - Exports `TOOLS: list` and `TOOL_MAP: dict`
- Update `ask-foreign-agent/agent.py`
  - Remove the five `@tool` functions
  - Remove the inline `_run` function and `_cwd` global
  - Add `from tools import TOOLS, TOOL_MAP` and `from tools import _context`
  - Change the `global _cwd` assignment in `main()` to `_context._cwd = os.path.abspath(args.cwd)`
  - Remove the now-unused `_cwd` module-level variable

## Recommended approach

1. Write `_context.py` first — everything else imports from it.
2. Write each tool file, importing from `_context` as needed.
3. Write `__init__.py` last, importing from the individual files.
4. Update `agent.py`.

## Done when

- [ ] `ask-foreign-agent/tools/` directory exists with `_context.py`, `bash.py`, `read_file.py`, `write_file.py`, `find_files.py`, `grep.py`, `__init__.py`
- [ ] `agent.py` no longer defines `_cwd`, `_run`, or any `@tool` functions inline
- [ ] `python3 ask-foreign-agent/agent.py --cwd . "list the files in this directory"` runs without import errors (a live pond call is not required — just confirm it parses and imports cleanly with `python3 -c "import sys; sys.argv=['agent.py','x']; import ask_foreign_agent.agent"` or equivalent dry-run)
- [ ] Entry added to `development-log.md`

## Results
**Tests:** Import check passes — `from tools import TOOLS, TOOL_MAP` returns all five tool names.
**Files changed:** `tools/_context.py`, `tools/bash.py`, `tools/read_file.py`, `tools/write_file.py`, `tools/find_files.py`, `tools/grep.py`, `tools/__init__.py`, `agent.py`
**Summary:** Pond's output was discarded — it reduced `agent.py` to a stub and lost the agentic loop, `@tool` imports, `executable` param on `write_file`, and `node_modules` exclusions on `find_files`/`grep`. All files were written correctly by Claude. The `_cwd` global assignment in `main()` now goes through `_context._cwd`.
