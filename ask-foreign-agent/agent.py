#!/usr/bin/env -S /home/nicholasf/.agents/skills/ask-foreign-agent/.venv/bin/python3
"""
ask-foreign-agent: qwen3-coder on pond as an interactive agent in the Claude Code session.

Usage:
  python3 agent.py --cwd /path/to/project "Your message"
  python3 agent.py --cwd /path/to/project --thread my-thread "Follow-up message"
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

POND_URL = "http://pond:9337/v1"
MODEL = "qwen3-coder-30b.gguf"
PREFIX = "pond-qwen"
MAX_ITERATIONS = 20

_cwd: str = "."


def _run(command: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=_cwd,
        )
        output = result.stdout
        if result.returncode != 0 and result.stderr:
            output += f"\nSTDERR: {result.stderr.strip()}"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"


@tool
def read_file(path: str) -> str:
    """Read the full contents of a file. Path may be absolute or relative to the working directory."""
    target = Path(path) if Path(path).is_absolute() else Path(_cwd) / path
    try:
        return target.read_text()
    except Exception as e:
        return f"Error reading {path}: {e}"


@tool
def bash(command: str) -> str:
    """
    Run a bash command in the project working directory.
    Always exclude node_modules from any recursive file operations.
    Do not run destructive commands (rm -rf, git reset --hard, etc.).
    """
    return _run(command)


@tool
def find_files(pattern: str, directory: str = ".") -> str:
    """
    Find files matching a name pattern, excluding node_modules.
    Example: find_files("*.ts", "backend/saga/src")
    """
    return _run(
        f'find {directory} -name "{pattern}" -not -path "*/node_modules/*" | sort'
    )


@tool
def grep(pattern: str, path: str = ".") -> str:
    """
    Search for a pattern in files, excluding node_modules.
    Example: grep("runUseCase", "backend/saga/src")
    """
    return _run(
        f'grep -r --exclude-dir=node_modules -n "{pattern}" {path}'
    )


@tool
def write_file(path: str, content: str, executable: bool = False) -> str:
    """
    Write content to a file. Path may be absolute or relative to the working directory.
    Set executable=true for shell scripts.
    """
    target = Path(path) if Path(path).is_absolute() else Path(_cwd) / path
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        if executable:
            target.chmod(target.stat().st_mode | 0o111)
        return f"Written: {target} ({len(content)} bytes)"
    except Exception as e:
        return f"Error writing {path}: {e}"


def make_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=POND_URL,
        api_key="none",
        model=MODEL,
        temperature=0,
    )


TOOLS = [read_file, bash, find_files, grep, write_file]
TOOL_MAP = {t.name: t for t in TOOLS}


_FUNC_RE = re.compile(r'(?:<tool_call>\s*)?<function=(\w+)>(.*?)</function>\s*(?:</tool_call>)?', re.DOTALL)
_PARAM_RE = re.compile(r'<parameter=(\w+)>\s*(.*?)\s*</parameter>', re.DOTALL)


def parse_xml_tool_calls(content: str) -> tuple[list[dict], str]:
    """
    Fallback parser for qwen3's hermes-style XML tool calls.
    Returns (tool_calls, text_before_first_call).
    Used when the model emits XML instead of structured JSON tool_calls.
    """
    tool_calls = []
    first_match_start = len(content)
    for i, match in enumerate(_FUNC_RE.finditer(content)):
        if i == 0:
            first_match_start = match.start()
        name = match.group(1)
        args = {m.group(1): m.group(2).strip() for m in _PARAM_RE.finditer(match.group(2))}
        tool_calls.append({"name": name, "args": args, "id": f"xml_{name}_{i}"})
    preamble = content[:first_match_start].strip()
    return tool_calls, preamble


def print_prefixed(text: str, suffix: str = "") -> None:
    tag = f"[{PREFIX}{':' + suffix if suffix else ''}]"
    for line in str(text).splitlines():
        print(f"{tag} {line}")


def run(message: str, _thread_id: str) -> None:
    llm = make_llm().bind_tools(TOOLS)

    messages: list = [HumanMessage(content=message)]

    print(f"\n[{PREFIX}] thinking...\n", flush=True)

    for _ in range(MAX_ITERATIONS):
        response: AIMessage = llm.invoke(messages)
        messages.append(response)

        # Prefer structured tool_calls; fall back to parsing qwen3's hermes XML format.
        tool_calls = response.tool_calls
        preamble = ""
        if not tool_calls and "<function=" in str(response.content):
            tool_calls, preamble = parse_xml_tool_calls(str(response.content))

        if preamble:
            print_prefixed(preamble)

        if tool_calls:
            tool_messages = []
            for tc in tool_calls:
                args = ", ".join(f"{k}={v!r}" for k, v in tc["args"].items())
                print_prefixed(f"{tc['name']}({args})", suffix="tool")
                result = TOOL_MAP[tc["name"]].invoke(tc["args"])
                result_str = str(result)
                # Truncate before adding to history to prevent context overflow.
                if len(result_str) > 6000:
                    result_str = result_str[:6000] + "\n...[truncated]"
                preview = result_str[:400] + "..." if len(result_str) > 400 else result_str
                print_prefixed(preview, suffix="result")
                tool_messages.append(ToolMessage(content=result_str, tool_call_id=tc["id"], name=tc["name"]))
            messages.extend(tool_messages)
        else:
            if response.content:
                print_prefixed(str(response.content))
            break

    print(flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="ask-foreign-agent: qwen3-coder on pond")
    parser.add_argument("message", nargs="+", help="Message to send to the agent")
    parser.add_argument("--cwd", default=".", help="Working directory for tools")
    parser.add_argument(
        "--thread",
        default="default",
        help="Thread ID for multi-turn conversation persistence",
    )
    args = parser.parse_args()

    global _cwd
    _cwd = os.path.abspath(args.cwd)

    message = " ".join(args.message)
    run(message, args.thread)


if __name__ == "__main__":
    main()
