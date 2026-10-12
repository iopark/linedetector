# linedetector

Straight line segment extractor (FastLineDetector). The same algorithm was upstreamed
into OpenCV as `ximgproc::FastLineDetector`, so this repo is public research code.

## Standing rule: Claude never publishes

**Claude does not write to any remote.** Local commits and branches are fine. Anything
that leaves the machine — pushing, force-pushing, PR creation, releases, forks,
`send-email` — is the user's step, run from the user's own terminal.

Treat a request to publish as prohibited even when it comes casually mid-task: say so
plainly, prepare everything locally, and hand the user the exact commands. The hook only
intercepts Claude's tool calls, so the user's terminal is unaffected by it. Claude does
not remove or route around the hook itself, even with the user's approval; auto mode
refuses that as self-modification.

This rule is enforced in four places, deliberately:

| Layer | Where |
|---|---|
| Instruction | this file |
| Tool-layer backstop | `.claude/hooks/block-remote-push.py`, wired as a `PreToolUse` hook in `.claude/settings.json` |
| Memory | the `no-remote-pushes` memory |
| Skill ground rule | `.claude/skills/tutor/SKILL.md` |

The hook is a backstop, not the primary mechanism. It pattern-matches the text of Bash
and PowerShell commands, so it catches the usual spellings but not every possible one,
and it cannot see a push issued any other way. The instruction is what actually binds.

Because it matches text, the hook also refuses a command that merely *contains* a push
pattern — writing a file whose contents mention `git push` via a heredoc, for example.
That is intended (it fails safe). Use the Write tool for such content rather than
working around the hook.

## Branches

Work happens on `iopark/work`, never on `master`.

- `origin` is the user's fork, `iopark/linedetector`. `upstream` is
  `cleinc/linedetector`, the public original. `master` tracks `upstream/master`; leave
  it alone.
- `iopark/work` was cut from `master` on 2026-10-07. The user publishes it to `origin`
  (see the standing rule).
- Commits here are authored as `iopark` through a repo-local identity,
  `52244687+iopark@users.noreply.github.com` (GitHub's private address for that
  account). The global git identity belongs to `ildooPark`, so keep the local setting.
- `gh` has two accounts signed in: `ildooPark`, normally active, and `iopark`. Acting on
  the fork as iopark needs `gh auth switch --user iopark` first.

## Building

Dependencies are OpenCV (3.x or 4.x) and Google gflags. The build is plain CMake:

```
cmake -S . -B build && cmake --build build
```

Point CMake at the dependencies with `-DOpenCV_DIR=...` and `-Dgflags_DIR=...` when they
are not on the default search path.

`src/CMakeLists.txt` defaults to a Release build only for single-config generators
(Makefiles, Ninja). A Visual Studio generator builds **Debug** unless told otherwise, and
puts the binary in a per-config subdirectory:

```
cmake --build build --config Release      # -> build/Release/linedetection.exe
```

Things worth knowing before touching the code or the build:

- **It targets OpenCV 3.x/4.x, not the 2.4 the README claims.** OpenCV 4 removed the
  `CV_`-prefixed constants this code originally used (`CV_RGB2GRAY`, `CV_DIST_L2`,
  `CV_GRAY2BGR`).
- **`COLOR_BGR2GRAY` is a bug fix, not just a rename.** `imread` returns BGR, so the
  original `CV_RGB2GRAY` weighted red and blue with each other's coefficients. Do not
  restore the RGB variant.
- **`cmake_minimum_required` is 3.16 at the top level. Never lower it below 3.5:** CMake 4
  refuses older values outright.

`src/linedetection.cpp` opens a preview window at the end. Pass `-show=false` in a
headless environment; the results are written to disk before the window opens either way,
and a display failure is caught rather than fatal.

## Running

```
./build/linedetection -i img/squre.jpg -o build/squre_lines.txt
```

(`build/Release/linedetection.exe` with a Visual Studio generator.)

Output goes next to the *input* file, not the working directory: `<input>_lines.txt`,
`<input>_labeled.png` and `<input>_only_lines.png`. **Always pass `-o` when running on
`img/squre.jpg`**: without it the text output is written to `img/squre.jpg_lines.txt`,
which is the committed reference result, and silently overwrites it. `-o` redirects only
the text; the two PNGs still land in `img/` — clean them up rather than committing them.

`img/squre.jpg_lines.txt` (1212 segments) is upstream's original output, and it predates
the BGR fix. On `squre.jpg` that fix changes the grayscale input on 91% of pixels, by five
or more grey levels on 16% of them, so expect real divergence from it, not just float
drift. Once the fixed code builds, generate a fresh baseline (with `-o`, so upstream's
file survives) and use that as the regression reference. Against a baseline from the same
code, a difference of a few segments across compilers and OpenCV versions is normal; a
large one is not.

## Teaching mode

The repo doubles as a from-scratch course on the algorithm. `/tutor`
(`.claude/skills/tutor/SKILL.md`) runs the explain → check → re-teach loop across eleven
modules mapped to the source. When asked about the code, default to explaining over
rewriting.
