---
name: task-tracking
description: Manage work as structured task files in tasks/pending/ and tasks/completed/. Use when planning a non-trivial piece of work, creating a task file, assigning a model to a task, executing a task, or marking a task complete. Triggers on "create a task", "write a task for", "what tasks are pending", "mark this task complete", or "update the task".
---

# Task Tracking

Tasks are Markdown files that capture a unit of work before it begins. They live in `tasks/pending/` while in progress and move to `tasks/completed/` when done. A corresponding entry is added to `development-log.md`.

## When to create a task

Write a task file when the work is substantial enough that:
- it touches multiple files or has distinct stages, **or**
- it requires a decision to be recorded before execution, **or**
- it will be handed off to a different model for execution

For small, self-contained edits, just do the work.

## Model assignment

Every task file must include a `model` field specifying which model should execute it.

**If a `topology.md` file exists in the project root, read it before assigning a model.** It describes the available models, their capabilities, and their intended use cases. Use it to make an informed assignment.

If no `topology.md` is present, use your best judgement and note the assumption in the task file.

General guidance (override with topology.md when present):

| Work type | Suggested assignment |
|---|---|
| Architecture, design, ambiguous problems | Cloud reasoning model (e.g. Claude Sonnet) |
| Mechanical execution: schema changes, renames, wiring | Local coding model (e.g. Qwen2.5-Coder 32B) |
| Small, self-contained edits | Either; skip the task file |

## Task file format

File name: `tasks/pending/<slug>.md` — lowercase, hyphenated, descriptive.

```markdown
# <Title>

**Model:** <model name and why, e.g. "Qwen2.5-Coder 32B — mechanical rename across known files">
**Status:** planned

## Goal
One sentence. What will be true when this task is done?

## Background
Optional. Link to design docs, prior decisions, or relevant context.
Omit if the goal is self-explanatory.

## Changes
Enumerate what will change. Be specific:
- Files to create or modify
- Schema changes
- Seed changes
- API / type changes
- Test changes

## Open questions
List anything that must be decided before or during execution.
If there are none, omit this section.

## Recommended approach
How to sequence the work. Note any non-obvious ordering constraints.

## Done when
- [ ] Specific, verifiable outcome
- [ ] Acceptance command that must pass, e.g. `pnpm jest --forceExit`
- [ ] Entry added to `development-log.md`
```

## Executing a task

1. Read the task file fully before starting.
2. If `topology.md` exists, confirm the assigned model matches what is currently available.
3. Work through the **Changes** section in the order given by **Recommended approach**.
4. Resolve any **Open questions** encountered during execution; note the decision in the file.
5. Verify every item in **Done when** before declaring the task complete.

## Completing a task

When all **Done when** items are checked:

1. Move the file: `mv tasks/pending/<slug>.md tasks/completed/<slug>.md`
2. Update its **Status** line to `completed`.
3. Append a concise summary to `development-log.md` covering what changed and any decisions made during execution.

## Directory structure

```
tasks/
  pending/    # tasks not yet complete
  completed/  # finished tasks, kept for reference
development-log.md
```

Create these if they do not exist.
