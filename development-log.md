# Development Log

Chronological record of completed tasks and decisions.

<!-- Append entries here as tasks are completed. -->

## 2026-05-26 — Extract tools into package

Moved the five inline tool functions out of `agent.py` into `ask-foreign-agent/tools/` (one file per tool). Shared `_cwd` state and `_run` helper live in `_context.py`. `agent.py` now imports from the package and sets `_context._cwd` in `main()`. Pond's output was not used — it discarded the agentic loop and had several spec deviations; files were written by Claude.
