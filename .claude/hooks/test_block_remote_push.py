#!/usr/bin/env python3
"""Check block-remote-push.py in both directions: what it must refuse, and what
it must leave alone. Runs the real hook as a subprocess with a PreToolUse
payload, exactly as Claude Code does. Nothing here executes git.

    python .claude/hooks/test_block_remote_push.py

Exits non-zero if any case comes out wrong.
"""
import json
import os
import subprocess
import sys

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "block-remote-push.py")

MUST_BLOCK = [
    "git push",
    "git push origin master",
    "git push --force",
    "git -C /tmp/x push",
    "git --no-pager push",
    "cd foo && git push",
    'bash -c "git push"',
    "sh -c 'git push origin master'",
    "echo $(git push)",
    'cmd /c "git push"',
    "Invoke-Expression 'git push'",
    "git.exe push",
    '"C:/Program Files/Git/cmd/git.exe" push',
    "& git push",
    "git --git-dir /repo/.git push",
    "git -P push",
    "git -c push.default=current push",
    "git subtree push --prefix=docs origin gh-pages",
    "git lfs push origin master",
    "git send-email x.patch",
    "gh pr create --title x",
    "gh.exe pr create",
    "gh pr merge 12",
    "gh repo fork cleinc/linedetector",
    "gh repo create mine/linedetector --public",
    "gh release create v1",
    "gh release upload v1 build.zip",
]

MUST_ALLOW = [
    "git status",
    "git commit -m x",
    "git log --grep push",
    "git log --oneline",
    "git --no-pager log --grep=push",
    "git branch -a",
    "git pull",
    "git fetch origin",
    "git remote -v",
    "git stash push -m wip",
    "git -C repo stash push",
    "git config push.default current",
    "git help push",
    "gh pr list",
    "gh repo view cleinc/linedetector",
    "pushd build",
    "echo pushing changes",
    "cmake --build build",
]


def blocks(cmd: str) -> bool:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    out = subprocess.run(
        [sys.executable, HOOK], input=payload, capture_output=True, text=True, timeout=10
    ).stdout
    return '"deny"' in out


def main() -> int:
    wrong = [("lets through", c) for c in MUST_BLOCK if not blocks(c)]
    wrong += [("wrongly blocks", c) for c in MUST_ALLOW if blocks(c)]
    for kind, cmd in wrong:
        print(f"FAIL {kind}: {cmd}")
    total = len(MUST_BLOCK) + len(MUST_ALLOW)
    print(f"{total - len(wrong)}/{total} cases correct")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
