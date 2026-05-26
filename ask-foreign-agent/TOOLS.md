# Available tools

These are the tools available to qwen3-coder when executing a task via the ask-foreign-agent agentic loop. Each tool is a Python function registered with `@tool` and bound to the LLM via `bind_tools`.

**Read all files referenced in the task before writing or editing anything.**

## Tool reference

| Tool | Signature | What it does |
|---|---|---|
| `read_file` | `read_file(path)` | Read a file by absolute or relative path |
| `bash` | `bash(command)` | Run a shell command in the working directory |
| `find_files` | `find_files(pattern, directory=".")` | Find files by name pattern, node_modules excluded |
| `grep` | `grep(pattern, path=".")` | Search file contents, node_modules excluded |
| `write_file` | `write_file(path, content, executable=False)` | Write (overwrite) a file; set executable=True for scripts |
| `edit_file` | `edit_file(path, old_string, new_string)` | Replace an exact string in a file; fails if not found or not unique |
| `list_directory` | `list_directory(path=".", max_depth=3)` | List directory tree excluding node_modules, .git, __pycache__, .venv, dist |
| `git_diff` | `git_diff()` | Show unstaged and staged working-tree changes |

## Notes

- `edit_file` is preferred over `write_file` for targeted changes to existing files — it makes the change reviewable as a diff and avoids accidentally dropping content.
- `bash` can run any shell command, but avoid destructive operations (`rm -rf`, `git reset --hard`, etc.).
- All path-based tools resolve relative paths against the `--cwd` passed at invocation.
- There is no tool to call an external LLM. Qwen handles all execution independently using the tools above.
