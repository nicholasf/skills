# ask-foreign-agent — Improvements

This file is a carry-forward brief for a new Claude session. The skill lives at
`~/.agents/skills/ask-foreign-agent/` (symlinked from this repo). The main file to
edit is `agent.py`.

## Current state

Pond (qwen3-coder-30b on pond:9337) runs as an agentic loop via `ChatOpenAI.bind_tools()`.
It has five tools:

| Tool | What it does |
|---|---|
| `read_file` | Read a file by absolute or relative path |
| `bash` | Run a shell command in `--cwd` |
| `find_files` | Find files by name pattern, node_modules excluded |
| `grep` | Search file contents, node_modules excluded |
| `write_file` | Write (overwrite) a file; supports `executable=True` |

There is a fallback XML parser (`parse_xml_tool_calls`) for when qwen3's thinking mode
emits `<function=name>` XML instead of structured JSON `tool_calls`. This is working.

## Bug: `--thread` / history persistence is a no-op

`agent.py` accepts `--thread` and a `_thread_id` parameter but never uses it. `history.db`
exists on disk but no checkpoint/persistence logic reads or writes it. Multi-turn threads
across invocations are silently ignored — each call starts fresh.

Either implement persistence (e.g. write/load message history as JSON keyed by thread ID)
or remove the `--thread` flag to avoid confusion.

## Suggested new tools

### 1. `edit_file(path, old_string, new_string)` — highest priority

Pond currently can only overwrite entire files with `write_file`. For small targeted changes
this is risky — large files can have content silently dropped. An edit tool makes changes
reviewable as diffs rather than full rewrites.

```python
@tool
def edit_file(path: str, old_string: str, new_string: str) -> str:
    """
    Replace an exact string in a file. Fails if old_string is not found or
    matches more than once (use a larger context window to make it unique).
    """
    target = Path(path) if Path(path).is_absolute() else Path(_cwd) / path
    try:
        content = target.read_text()
    except Exception as e:
        return f"Error reading {path}: {e}"
    count = content.count(old_string)
    if count == 0:
        return f"Error: old_string not found in {path}"
    if count > 1:
        return f"Error: old_string matches {count} times in {path} — provide more context to make it unique"
    target.write_text(content.replace(old_string, new_string, 1))
    return f"Edited: {target}"
```

### 2. `list_directory(path, max_depth)` — quality of life

Pond uses `bash` with `find`/`ls` to explore structure, which works but can accidentally
generate massive output if exclusions are forgotten. A dedicated tool with sensible defaults
is safer.

```python
@tool
def list_directory(path: str = ".", max_depth: int = 3) -> str:
    """
    List directory tree, excluding node_modules, .git, __pycache__, .venv, dist.
    """
    excludes = "node_modules|.git|__pycache__|.venv|dist"
    return _run(
        f'find {path} -maxdepth {max_depth} '
        f'-not -path "*/{excludes}/*" -not -name "{excludes}" | sort'
    )
```

Note: the excludes pattern in `find` will need splitting into multiple `-not -path` clauses
since `find` doesn't accept `|` in path patterns — shown above for brevity.

### 3. `git_diff()` — self-review

Lets pond review its own working-tree changes before declaring done. Useful for writing
accurate Results sections in task files and for catching accidental deletions.

```python
@tool
def git_diff() -> str:
    """Show unstaged and staged changes in the working tree."""
    result = _run("git diff && git diff --cached")
    if len(result) > 6000:
        result = result[:6000] + "\n...[truncated]"
    return result or "(no changes)"
```


## Implementation notes

- All new tools follow the same pattern: use `_run()` for shell commands, `Path(_cwd)` for
  file paths, return a plain string (including errors).
- Add each new tool to the `TOOLS` list and `TOOL_MAP` dict at the bottom of the tool
  definitions section.
- The tool docstring is what the model sees — keep it short and include an example if the
  parameters need clarification.
- Result truncation (6000 chars) happens in the main loop, not in individual tools. No need
  to truncate inside the tool functions.

## Files to edit

- `agent.py` — all changes go here; the skill is a single file
- `SKILL.md` — update the Available tools table once new tools are added
