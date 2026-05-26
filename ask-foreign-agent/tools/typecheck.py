from langchain_core.tools import tool

from . import _context


@tool
def typecheck() -> str:
    """
    Run the TypeScript compiler on backend/saga (no emit).
    Use after making TypeScript changes to catch type errors before declaring done.
    """
    return _context.run_command("cd backend/saga && pnpm tsc --noEmit", timeout=60)