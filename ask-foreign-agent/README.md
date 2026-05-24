# ask-foreign-agent

Runs qwen3-coder on pond as an interactive agent inside the Claude Code session. Claude acts as the display surface and mediator; qwen acts as a peer agent with access to the local codebase.

## Concept

Claude Code runs on Anthropic's infrastructure but has a local CLI process that executes tools (file reads, bash, etc.) on your machine. The ask-foreign-agent skill gives qwen3-coder on pond an analogous capability: a local Python agentic loop that executes tools on qwen's behalf, with the conversation appearing in the Claude Code session, prefixed with `[pond-qwen]`.

This means you can:
- Ask qwen a question directly in the Claude Code session
- Have Claude delegate a subtask to qwen and relay the result
- Have both models visible in the same conversation

## Tool architecture — Option A vs Option B

### Option A (current): Local Python tools

The `agent.py` loop defines tools as plain Python functions (`read_file`, `bash`, `find_files`, `grep`). When qwen calls a tool, the Python process executes it locally and returns the result. Claude is not involved in tool execution — it only relays the conversation.

```
you ──► Claude ──► agent.py ──► pond:9337 (qwen)
                      │              │
                      │◄─ tool call ◄┘
                      │
                      ├─ read_file() / bash() / grep() [runs locally]
                      │
                      └─► pond:9337 (tool result)
```

**Tradeoff:** qwen's tool set is limited to what `agent.py` defines. It cannot call Claude's full tool set (WebFetch, Write, Edit, etc.).

### Option B (future): Claude as tool relay

qwen requests a tool, `agent.py` surfaces the request to Claude, Claude executes it using its own CLI tools, and the result flows back. This would give qwen access to Claude's full tool set including WebFetch, Edit, and Write — but requires a two-way protocol between `agent.py` and the Claude Code CLI process, which doesn't exist yet.

We are starting with Option A. Option B is architecturally more interesting and may be revisited once the basic agent loop is proven.

## Implementation

Built with [LangGraph](https://github.com/langchain-ai/langgraph) and LangChain's OpenAI-compatible client. The agentic loop is a standard ReAct graph (`create_react_agent`) with SQLite checkpointing for multi-turn conversation persistence.

## Dependencies

```
pip install langgraph langchain-openai langchain-core
```

Or with uv:

```
uv pip install langgraph langchain-openai langchain-core
```

## Usage

See `SKILL.md` for how Claude invokes this skill.
