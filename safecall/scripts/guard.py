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
import time
from datetime import datetime
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

    folder = str(Path.cwd())

    # THE COPY IS TRIED FIRST, ALWAYS. The pass list is consulted only after it has failed - see
    # the note above `_has_pass`. Until 26.09.2026 this order was reversed, and one failed copy
    # took a file out of protection for good.
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

    # The copy did not happen. Only NOW does the pass matter: has this person already been asked
    # about this file in this same conversation and said yes?
    if _has_pass(target, payload):
        return 0

    # The one case worth stopping for: we could not protect this file, so the change is one-way.
    why = (made.stdout or made.stderr or "").strip().splitlines()
    why = why[0] if why else "причина неизвестна / reason unknown"
    if not _give_pass(target, payload):
        # We cannot even remember that we asked. Blocking now would block this file FOREVER, with
        # no way through - the person repeats the edit and is refused again, every time. That is
        # the guard breaking the session, which this file forbids at the top. So: let it through
        # and say so. Our own broken home is never their problem.
        print(f"Safecall: не смог сделать копию «{target.name}» и не смог запомнить вопрос о нём "
              f"— скорее всего папка копий недоступна. Правка прошла БЕЗ копии. "
              f"Скажите это человеку его языком. / Safecall: could not copy \"{target.name}\" and "
              f"could not remember asking about it - the copies folder is probably unavailable. "
              f"The edit went through WITH NO COPY. Tell the person in THEIR language.")
        return 0
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
    return 2


# ── The pass: how long "yes, change it without a copy" lasts ────────────────────────────────
#
# Until 26.09.2026 this was a file called `uncopyable.txt`, it was consulted BEFORE the copy was
# tried, and nothing ever removed a line from it. One failed copy - a full disk, a file held open
# by Word, a path too long - put that file outside the plugin's promise for good, silently, and
# the person was never told. The council of AIs was asked on 26.09.2026 (Claude Opus, Codex, the
# Google seat; Kimi was out of quota, Grok did not finish) and all three said: fix it.
#
# TWO THINGS CHANGED, AND THE FIRST ONE IS WHAT ACTUALLY FIXES IT:
#
#   1. THE ORDER. The copy is now tried every single time, before the pass is even looked at
#      (`main`). That alone makes a random failure heal itself: next time the disk has room, the
#      copy succeeds and the file is protected again, with no pass involved. No code has to guess
#      WHY the copy failed - the retry answers that for free, which is why there is no
#      "kind of failure" field anywhere here.
#
#   2. THE LIFETIME. A pass now belongs to the conversation the person answered in, and to that
#      file. A secret (`SECRET_NAME` in snapshot.py) can never be copied, so it keeps failing and
#      keeps using its pass - which is the intended behaviour, and it still ends with the
#      conversation. A new conversation asks again, because the person who answered may not even
#      be the one sitting there now.
#
# Claude Code hands a PreToolUse hook the `session_id` of the conversation. If it is ever absent,
# the day is used instead: still an end, just a blunter one. Never "forever" again.

PASSES = "passes.json"
PASS_HOURS = 24


def _pass_key(target: Path, payload) -> str:
    who = str(payload.get("session_id") or "")
    if not who:
        who = "день-" + datetime.now().strftime("%Y-%m-%d")
    return f"{who}\n{target}"


def _pass_root() -> Path:
    return Path(os.environ.get("SAFECALL_HOME", Path.home() / ".safecall"))


def _read_passes():
    """Live passes only. Stale ones are dropped on the way in, so the file cannot grow forever."""
    try:
        raw = json.loads((_pass_root() / PASSES).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    edge = time.time() - PASS_HOURS * 3600
    return {k: v for k, v in raw.items() if isinstance(v, (int, float)) and v > edge}


def _has_pass(target: Path, payload) -> bool:
    return _pass_key(target, payload) in _read_passes()


def _give_pass(target: Path, payload) -> bool:
    """Remember that we asked. False = we could not, and the caller must NOT block."""
    try:
        root = _pass_root()
        root.mkdir(parents=True, exist_ok=True)
        live = _read_passes()
        live[_pass_key(target, payload)] = time.time()
        (root / PASSES).write_text(json.dumps(live, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError:
        return False


if __name__ == "__main__":
    sys.exit(main())
