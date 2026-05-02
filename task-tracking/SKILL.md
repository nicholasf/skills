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

**Token economization:** A key reason to delegate a task to a local model (e.g. Qwen2.5-Coder) is to avoid spending cloud API tokens on work that does not require high-level reasoning. Cloud model tokens are expensive; local model inference is effectively free. A cloud model should design the task precisely and then hand off execution to a cheaper model, reserving its own involvement for architecture, ambiguous decisions, and review.

**If a `topology.md` file exists in the project root, read it before assigning a model.** It describes the available models, their capabilities, and their intended use cases. Use it to make an informed assignment.

If no `topology.md` is present, use your best judgement and note the assumption in the task file.

General guidance (override with topology.md when present):

| Work type | Suggested assignment |
|---|---|
| Architecture, design, ambiguous problems | Cloud reasoning model (e.g. Claude Sonnet) |
| Mechanical execution: schema changes, renames, wiring | Local coding model (e.g. Qwen2.5-Coder 32B) |
| Small, self-contained edits | Either; skip the task file |

## Task file format

File name: `tasks/pending/<timestamp>-<slug>.md` — timestamp in `YYYY-MM-DDTHH-MM-SS` format (using `-` as the time separator so it is shell-safe), followed by a lowercase, hyphenated, descriptive slug. Example: `2026-05-02T14-30-00-add-user-avatar.md`.

Generate the timestamp at the moment the file is created (use `date +%Y-%m-%dT%H-%M-%S` or the equivalent).

```markdown
# <Title>

**Created:** <YYYY-MM-DD HH:MM:SS>
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

## Results
<!-- Filled in by the executing model after completion -->
**Tests:** 
**Files changed:** 
**Summary:** 
```

## Handing off to pond

Pond receives tasks via the OpenAI-compatible chat completions API. The task file content **must be read and embedded in the request payload** — pond cannot access the filesystem directly.

Use Python to build the payload so the file content is safely interpolated:

```bash
python3 -c "
import json
task = open('tasks/pending/<slug>.md').read()
payload = {
  'model': 'qwen3-coder-30b.gguf',
  'stream': False,
  'max_tokens': 16000,
  'messages': [
    {
      'role': 'system',
      'content': 'You are an expert developer executing a precisely specified coding task. Read the task carefully, implement everything described, and fill in the ## Results section when done.'
    },
    {
      'role': 'user',
      'content': 'Working directory: /path/to/project\n\nExecute this task in full. Output the complete content of each file, clearly labelled with its path.\n\n' + task
    }
  ]
}
print(json.dumps(payload))
" > /tmp/task-payload.json

curl -s http://pond:9337/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d @/tmp/task-payload.json \
  | python3 -c "
import json, sys
resp = json.load(sys.stdin)
print(resp['choices'][0]['message']['content'])
usage = resp.get('usage', {})
print(f\"--- tokens: prompt={usage.get('prompt_tokens')}, completion={usage.get('completion_tokens')} ---\")
"
```

**Do not** use shell heredocs with `$(cat ...)` substitution — the file content will not be interpolated inside a heredoc and pond will receive an empty or literal string.

## Executing a task

1. Read the task file fully before starting.
2. If `topology.md` exists, confirm the assigned model matches what is currently available.
3. Work through the **Changes** section in the order given by **Recommended approach**.
4. Resolve any **Open questions** encountered during execution; note the decision in the file.
5. Verify every item in **Done when** before declaring the task complete.

## Reviewing a delegated task

When a task was executed by a delegated (local) model, the reviewing cloud model must **not** read the full changed files — doing so consumes the API tokens that delegation was intended to save. Instead:

1. Read only the **Results** section of the task file (filled in by the executing model).
2. Run or confirm the acceptance commands listed in **Done when** (test counts, typecheck). The test suite is the primary correctness signal.
3. Present a short summary to the user:
   - What changed (file list and counts, not contents)
   - Test results (suite count, pass/fail)
   - Any decisions made during execution
4. Wait for the user to confirm before marking the task complete. The user reviews the code directly if they wish.

The task file format includes a `## Results` section for the executing model to fill in. If it is absent or incomplete, ask the executing model to add it before proceeding.

## Completing a task

When all **Done when** items are checked and (for delegated tasks) the user has confirmed:

1. Move the file: `mv tasks/pending/<timestamp>-<slug>.md tasks/completed/<timestamp>-<slug>.md`
   The timestamp prefix is preserved so completed tasks are ordered chronologically in a directory listing.
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
