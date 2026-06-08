These skills have been given their own repos. 

See 

* [manage-skills-skill](https://github.com/nicholasf/manage-skills-skill)
* [load-topology](https://github.com/nicholasf/manage-skills-skill)
* [track-tasks-skill](https://github.com/nicholasf/track-tasks-skill)
* [ask-remote-llm-skill](https://github.com/nicholasf/ask-foreign-llm-skill)
* [ask-remote-agent-skill](https://github.com/nicholasf/ask-remote-agent-skill)



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
| [`ask-foreign-agent`](ask-foreign-agent/SKILL.md) | Run qwen3-coder on pond as an interactive agent inside the Claude Code session. qwen can read files, run bash commands, and reason about the codebase. Claude relays the conversation and prefixes qwen's output with [pond-qwen]. |
| [`load-topology`](load-topology/SKILL.md) | Read the local system topology to discover available machines and models. Use when the user wants to see what models can be run, load a model on a machine, or prepare for task delegation. Triggers on "load topology", "what models are available", "which machines are running", "start a model", "load a model on", or "show me the topology". |
| [`task-tracking`](task-tracking/SKILL.md) | Manage work as structured task files in tasks/pending/ and tasks/completed/. Use when planning a non-trivial piece of work, creating a task file, assigning a model to a task, executing a task, or marking a task complete. Triggers on "create a task", "write a task for", "what tasks are pending", "mark this task complete", or "update the task". |

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

## Keeping README.md in sync

The Skills table is auto-generated from each skill's `SKILL.md` frontmatter (`name` and `description` fields). A pre-commit hook regenerates and stages the table on every commit, so it never goes stale.

The hook is stored in `.git-hooks/pre-commit` and activated via:

```bash
git config core.hooksPath .git-hooks
```

This runs automatically after cloning if you use the symlink setup script (which calls `git config` for you). On a new machine, run it once manually if you skipped the setup script.

To regenerate the table without committing:

```bash
bash scripts/update-readme.sh
```

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
