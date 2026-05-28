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
import sys

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI

from tools import TOOL_MAP, TOOLS
from tools import _context

POND_URL = "http://pond:9337/v1"
MODEL = "qwen3-coder-30b.gguf"
PREFIX = "pond-qwen"
MAX_ITERATIONS = 400


def make_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=POND_URL,
        api_key="none",
        model=MODEL,
        temperature=0,
    )


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

    _context.working_directory = os.path.abspath(args.cwd)

    message = " ".join(args.message)
    run(message, args.thread)


if __name__ == "__main__":
    main()
