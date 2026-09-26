#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safecall guard: nothing is written to an existing file before a copy of it exists.

Runs as a PreToolUse hook on Write and Edit. Reads the tool call on stdin as JSON, finds the file
it is about to change, and makes sure a copy of that file exists before the write goes through.

IT MAKES THE COPY ITSELF. The first version blocked instead and told Claude to run the copy command
- the round of criticism on 26.09.2026 killed that design with two scenarios and both were right:

  (1) Poly A1's own coach writes a state file (`NEXT.md`, `СЕЙЧАС.md`, `ЗАРАЗ.md`) at the end of
      every evening. Second evening on, that file exists, so the guard stopped the one action that
      ends a person's evening well, and showed them a shell command instead of "готово".
  (2) blocking once and allowing afterwards meant that a frightened person who said "без копий"
      lost the protection permanently, at exactly the moment they were most afraid.

Making the copy keeps the promise absolutely and costs the person nothing, so there is nothing to
refuse and nothing to nag about.

What it does NOT do, deliberately:
  - it never blocks a NEW file. There is nothing to lose, and stopping the first `hello.txt` of a
    person's life to lecture them about backups is how you lose that person.
  - it never blocks reading. Read, Grep, Glob are untouched.
  - it fails OPEN on any trouble of its own - python missing, timeout, unreadable input. A guard
    must not be the thing that breaks somebody's session.

It blocks in exactly one case: the copy could not be made, so the write cannot be undone.

Exit 0 = allow. Exit 2 = block, and stderr is what Claude is told.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / "snapshot.py"

WRITERS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def _target(payload):
    ti = payload.get("tool_input") or {}
    for k in ("file_path", "notebook_path", "path"):
        if ti.get(k):
            return Path(str(ti[k])).expanduser()
    return None


def _run(args, timeout=15):
    return subprocess.run([sys.executable, str(SNAPSHOT), *args],
                          capture_output=True, text=True, timeout=timeout)


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0

    if payload.get("tool_name") not in WRITERS:
        return 0

    target = _target(payload)
    if target is None:
        return 0
    try:
        target = target.resolve()
    except OSError:
        return 0

    if not target.exists():
        return 0                                   # a new file: nothing to lose
    if _was_refused(target):
        return 0                                   # already asked about this one, person decided

    folder = str(Path.cwd())

    try:
        covered = _run(["covered", str(target), "--folder", folder, "--minutes", "120"])
        if covered.returncode == 0:
            return 0                               # a fresh copy already covers this file

        made = _run(["save", str(target), "--folder", folder])
    except (OSError, subprocess.SubprocessError):
        return 0                                   # our own trouble is never their problem

    if made.returncode == 0 and "Копия сделана" in made.stdout:
        # Allowed, with a line Claude can pass on in the person's own language.
        print(f"Safecall: сделал копию «{target.name}» перед правкой — вернуть можно словами "
              f"«верни, как было». / Safecall: copied \"{target.name}\" before editing — "
              f"say \"put it back the way it was\" to undo.")
        return 0

    # The one case worth stopping for: we could not protect this file, so the change is one-way.
    why = (made.stdout or made.stderr or "").strip().splitlines()
    why = why[0] if why else "причина неизвестна / reason unknown"
    sys.stderr.write(
        f"Safecall: не смог сделать копию «{target.name}», поэтому правка была бы без возврата.\n"
        f"Причина: {why}\n"
        f"Скажите человеку об этом ЕГО языком и спросите, менять ли файл без копии. Если он "
        f"скажет да — повторите правку, второй раз она пройдёт.\n"
        f"---\n"
        f"Safecall: could not copy \"{target.name}\", so this edit would be one-way.\n"
        f"Reason: {why}\n"
        f"Tell the person in THEIR language and ask whether to change the file with no copy. "
        f"If they say yes, repeat the edit - it will go through the second time.\n")
    _allow_next(target)
    return 2


# One override token per file: after we have blocked once and the person has been asked, the next
# attempt on that same file goes through. This is not the old "warn once then never again" - the
# copy is still attempted every time, and this only applies to a file that CANNOT be copied.
def _allow_next(target: Path):
    try:
        root = Path(os.environ.get("SAFECALL_HOME", Path.home() / ".safecall"))
        root.mkdir(parents=True, exist_ok=True)
        (root / "uncopyable.txt").open("a", encoding="utf-8").write(str(target) + "\n")
    except OSError:
        pass


def _was_refused(target: Path) -> bool:
    try:
        root = Path(os.environ.get("SAFECALL_HOME", Path.home() / ".safecall"))
        return str(target) in (root / "uncopyable.txt").read_text(encoding="utf-8").splitlines()
    except OSError:
        return False


if __name__ == "__main__":
    sys.exit(main())
