# Shareable skills agent instructions

This git repo is symlinked to $HOME/.agents/skills so that it can be used generally by agents, such as Claude or pi, as needed.

## Code changes require explicit confirmation

**Before making any code change — no matter how small or mechanical — state what you intend to do and wait for the user to confirm.**

This applies to every Edit, Write, file deletion, and file-modifying Bash command. It applies even when the change was already discussed, is specified in a task file, or appears trivial. Do not act on pond's output without confirmation either.

If you catch yourself about to make a change without confirmation: stop, describe the change, and wait.

## Naming conventions

- **No abbreviations in identifiers.** Write full words: `initialise` not `init`, `authenticate` not `auth` as a prefix, `repository` not `repo`, `configuration` not `config`, etc.
- Abbreviations creep in when names start to feel long. Prefer the longer, unambiguous form consistently.
- Acronyms that are always written as acronyms are fine: `JWKS`, `JWT`, `URL`, `ID`, `GraphQL`, etc.
