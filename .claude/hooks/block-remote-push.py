#!/usr/bin/env python3
"""PreToolUse guard: refuse shell commands that write to a git remote.

Standing rule for this repo (see CLAUDE.md and the "no-remote-pushes" memory):
local commits and branches are fine, anything that leaves the machine is not.
This is a backstop, not the primary mechanism -- it pattern-matches the text of
shell commands, so it cannot see a push issued some other way.

Reads the PreToolUse payload on stdin, prints a deny decision when the command
looks outward-writing, and stays silent otherwise. test_block_remote_push.py
next to this file checks both directions; run it after editing the patterns.
"""
import json
import re
import sys

# `git push`, however it is spelled:
#   - bare `git` or `git.exe`, optionally quoted or path-qualified;
#   - global options in front: `-C dir`, `-c k=v`, `--git-dir x`, `--no-pager`, `-P`;
#   - `subtree push` and `lfs push`, which also write to the remote;
#   - `push` followed by anything that ends a word (space, quote, paren, end of
#     string), so wrapped forms like `bash -c "git push"` and `$(git push)` match.
# `git stash push` and `git log --grep push` stay allowed: `stash` and `log` are
# not global options, so the chain breaks before it reaches `push`.
_GIT = r"""(?:^|[^\w.-])git(?:\.exe)?["']?"""
_GLOBAL_OPTS = (
    r"(?:\s+(?:"
    r"-[cC]\s+\S+"
    r"|--(?:git-dir|work-tree|namespace|exec-path|super-prefix|config-env)(?:=|\s+)\S+"
    r"|--[a-z][a-z-]*(?:=\S+)?"
    r"|-[a-zA-Z](?=\s)"
    r"))*"
)
_PUSH = r"\s+(?:(?:subtree|lfs)\s+)?push(?![\w-])"
GIT_PUSH = re.compile(_GIT + _GLOBAL_OPTS + _PUSH, re.IGNORECASE)

# Other ways to publish from the command line, including creating a fork.
OTHER_REMOTE_WRITES = re.compile(
    r"""(?:^|[^\w.-])(?:"""
    r"""gh(?:\.exe)?["']?\s+(?:pr\s+(?:create|merge)|repo\s+(?:create|fork)|release\s+(?:create|upload))"""
    r"""|git(?:\.exe)?["']?\s+(?:send-email|svn\s+dcommit)"""
    r""")(?![\w-])""",
    re.IGNORECASE,
)

REASON = (
    "Blocked by the project's no-remote-push rule: this repo is local-only "
    "(commits and branches are fine, anything that leaves the machine is not). "
    "Remove .claude/hooks/block-remote-push.py and its PreToolUse entry in "
    ".claude/settings.json if you genuinely want to publish."
)


def is_remote_write(command: str) -> bool:
    return bool(GIT_PUSH.search(command) or OTHER_REMOTE_WRITES.search(command))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # Never break the tool call over an unreadable payload.

    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") or ""
    if not isinstance(command, str):
        return 0

    if is_remote_write(command):
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": REASON,
                },
                "systemMessage": "Remote push blocked (repo is local-only).",
            },
            sys.stdout,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
