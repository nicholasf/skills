# Write unit tests for all tools

**Created:** 2026-05-26 11:27:31
**Model:** qwen3-coder-30b on pond — mechanical test authoring
**Status:** planned

## Goal

Create a `tests/` directory under `ask-foreign-agent/` with a pytest unit test file for each tool.

## Background

Depends on both previous tasks being complete:
- `2026-05-26T11-26-50-extract-tools-package.md` (tools package exists)
- `2026-05-26T11-27-10-add-new-tools.md` (all nine tools exist)

pytest must be added to `pyproject.toml` before tests can run.

## Available tools

Read `ask-foreign-agent/TOOLS.md` for the full tool list and usage notes.

**Read all files listed in "Files to read" before writing anything.**

## Files to read

Read these to understand the existing code before writing tests:

- `ask-foreign-agent/pyproject.toml` — must be updated to add pytest as a dev dependency
- `ask-foreign-agent/tools/_context.py` — the `_cwd` variable that tests must set via fixture
- `ask-foreign-agent/tools/__init__.py` — the full list of tools
- `ask-foreign-agent/tools/read_file.py`
- `ask-foreign-agent/tools/write_file.py`
- `ask-foreign-agent/tools/bash.py`
- `ask-foreign-agent/tools/find_files.py`
- `ask-foreign-agent/tools/grep.py`
- `ask-foreign-agent/tools/edit_file.py`
- `ask-foreign-agent/tools/list_directory.py`
- `ask-foreign-agent/tools/git_diff.py`

## Changes

### `ask-foreign-agent/pyproject.toml`

Add `pytest>=8` as a dev dependency. Use `[project.optional-dependencies]` with key `dev`.

### `ask-foreign-agent/tests/__init__.py`

Empty file.

### `ask-foreign-agent/tests/conftest.py`

Provide a `set_working_directory` fixture (autouse=False, scope="function") that:
- Accepts `tmp_path` from pytest
- Sets `tools._context.working_directory` to `str(tmp_path)` before the test
- Resets `tools._context.working_directory` to `"."` after the test (via yield)

### Test files — one per tool

Each test file imports the tool function directly (e.g. `from tools.read_file import read_file`) and uses the `set_working_directory` fixture where file system access is needed.

**`tests/test_read_file.py`**
- Test: reading an existing file returns its content
- Test: reading a missing file returns a string starting with `"Error"`

**`tests/test_write_file.py`**
- Test: writing a file creates it with the correct content
- Test: writing with `executable=True` sets the executable bit on the file
- Test: writing to a path whose parent directory does not exist creates the parent directories

**`tests/test_bash.py`**
- Test: a simple command (`echo hello`) returns its output
- Test: a failing command (exit code != 0) returns output that includes `STDERR`

**`tests/test_find_files.py`**
- Test: creates two `.py` files in `tmp_path`, calls `find_files("*.py")`, and asserts both filenames appear in the output

**`tests/test_grep.py`**
- Test: creates a file containing a known string, calls `grep` with that string, and asserts the filename and line appear in the output
- Test: searching for a string that does not exist returns `"(no output)"`

**`tests/test_edit_file.py`**
- Test: replaces a unique string in a file; verifies the file content after the edit
- Test: attempting to edit a string not present in the file returns an error string
- Test: attempting to edit a string that appears more than once returns an error string mentioning the count

**`tests/test_list_directory.py`**
- Test: creates a nested directory structure in `tmp_path` and confirms expected paths appear in the output
- Test: `node_modules` directory is excluded from the output even when present

**`tests/test_git_diff.py`**
- Test: in a directory that is not a git repo, `git_diff` returns a string (does not raise an exception — error output is acceptable)
- Test: initialise a git repo in `tmp_path` (`git init`, `git commit --allow-empty -m init`), stage a new file, call `git_diff`, and assert the filename appears in the output

`typecheck` does not require a unit test — it is environment-specific (requires a pnpm workspace at `backend/saga`) and its behaviour is fully covered by the docstring.

## Recommended approach

1. Read all files listed above.
2. Update `pyproject.toml` to add pytest.
3. Write `tests/__init__.py` and `tests/conftest.py`.
4. Write each test file. The order does not matter.
5. Run the suite with `bash`: `cd ask-foreign-agent && ../.venv/bin/python3 -m pytest tests/ -v` or use `uv run pytest tests/ -v` if uv is available.

## Done when

- [ ] `ask-foreign-agent/tests/` exists with `__init__.py`, `conftest.py`, and one test file per tool (eight files, excluding typecheck)
- [ ] `cd ask-foreign-agent && python3 -m pytest tests/ -v` passes with no failures
- [ ] Entry added to `development-log.md`

## Handoff

Run from the skills repo root:

```bash
cd /home/nicholasf/code/github/nicholasf/skills/ask-foreign-agent && \
  .venv/bin/python3 agent.py \
  --cwd /home/nicholasf/code/github/nicholasf/skills \
  "Read the task file at tasks/pending/2026-05-26T11-27-31-write-tool-tests.md and execute it in full. Fill in the ## Results section when done."
```

## Results
<!-- Filled in by the executing model after completion -->
**Tests:**
**Files changed:**
**Summary:**
