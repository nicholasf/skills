---
name: ask-foreign-agent
description: Run qwen3-coder on pond as an interactive agent inside the Claude Code session. qwen can read files, run bash commands, and reason about the codebase. Claude relays the conversation and prefixes qwen's output with [pond-qwen].
---

# Foreign Agent

Invoke qwen3-coder on pond as a peer agent. All of qwen's output appears in this session prefixed with `[pond-qwen]`.

## When to use

- Delegating a reasoning or research task to qwen that you want visible in this session
- Asking qwen a question directly ("What does X do?", "How should we approach Y?")
- Getting a second opinion on a design decision
- Letting the user speak to qwen interactively through you as mediator

## How to invoke

Run `agent.py` via the Bash tool. Always pass the working directory so tools resolve paths correctly.

**Single turn:**

```bash
~/.agents/skills/ask-foreign-agent/.venv/bin/python3 ~/.agents/skills/ask-foreign-agent/agent.py \
  --cwd /home/nicholasf/code/github/nicholasf/yggd \
  "Your message to qwen here"
```

**Multi-turn (continuing a conversation):**

```bash
~/.agents/skills/ask-foreign-agent/.venv/bin/python3 ~/.agents/skills/ask-foreign-agent/agent.py \
  --cwd /home/nicholasf/code/github/nicholasf/yggd \
  --thread my-thread-id \
  "Follow-up message"
```

Thread history is persisted to `~/.agents/skills/ask-foreign-agent/history.db`. Use the same `--thread` value to continue a conversation across multiple turns.

## Relaying user messages

When the user addresses qwen directly, pass their message verbatim as the agent message. When you are delegating a subtask, frame it clearly so qwen understands the context.

## Output format

qwen's text responses appear as `[pond-qwen] ...`.  
Tool calls appear as `[pond-qwen:tool:tool_name] ...`.  
Tool results appear as `[pond-qwen:result] ...` (truncated if long).

## Available tools

qwen can call these tools during its reasoning loop:

| Tool | Description |
|---|---|
| `read_file` | Read a file by absolute or relative path (relative to `--cwd`) |
| `bash` | Run a bash command; node_modules excluded from any recursive operations |
| `find_files` | Find files by name pattern, excluding node_modules |
| `grep` | Search for a pattern in files, excluding node_modules |

## Triggers

Invoke this skill when:
- The user says "ask qwen", "ask pond", "what does pond think", "let qwen look at this"
- You want a second agent's view on a design or code question
- The user wants to interact with qwen directly in this session
