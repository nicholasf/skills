# skills

A personal collection of reusable, versioned [Agent Skills](https://agentskills.io/specification) for use with [pi](https://github.com/badlogic/pi-mono) and any other harness that implements the standard.

## Strategy

Skills encode repeatable workflows and conventions that are worth carrying across projects and machines — task tracking patterns, code generation pipelines, spec formats, and similar. Keeping them in a git repo means:

- **Versioned** — every change is tracked; you can see when a skill was introduced or why it changed
- **Portable** — clone once per machine, symlink, done
- **Composable** — skills stay small and focused; a project can load this repo alongside its own local skills

The rule of thumb for what belongs here: if a skill would be useful in more than one project and contains no project-specific detail, it lives here. Project-specific skills (e.g. a skill that knows about a particular schema or toolchain) stay in `.pi/skills/` or `.agents/skills/` inside the project repo.

## Skills

| Skill | Description |
|---|---|
| [`task-tracking`](task-tracking/SKILL.md) | Manage work as structured task files in `tasks/pending/` and `tasks/completed/`. Covers task format, model assignment, and the completion lifecycle. |

## Symlink setup (pi auto-discovery)

Pi auto-discovers skills from `~/.agents/skills/`. Rather than maintaining a copy there, symlink that path to this repo so the repo stays the single source of truth.

A helper script handles this for you:

```bash
# Clone the repo
git clone git@github.com:nicholasf/skills.git ~/code/github/nicholasf/skills
cd ~/code/github/nicholasf/skills

# Create the symlink
bash scripts/symlink.sh
```

The script will:
1. Resolve the repo root automatically (works regardless of where you cloned it).
2. Create `~/.agents/` if it doesn't exist.
3. Replace an existing symlink at `~/.agents/skills` if one is already there.
4. Exit with an error if `~/.agents/skills` is a real directory — move or remove it first in that case.

**Verify pi can see the skills:**

```bash
ls ~/.agents/skills/
```

Pi will pick up all skills in this directory at startup with no further configuration needed.

**Subsequent machines** — clone the repo, then run `bash scripts/symlink.sh` again.

## Adding a new skill

```
skills/
  my-skill/
    SKILL.md      # required — frontmatter + instructions
    scripts/      # optional helper scripts
    references/   # optional reference docs loaded on demand
```

The directory name must match the `name` field in `SKILL.md` frontmatter. See the [Agent Skills specification](https://agentskills.io/specification) for the full format.

Commit and push — all symlinked machines pick up the change on next `git pull`.
