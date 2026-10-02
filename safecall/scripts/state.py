#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safecall: the real time, and where we stopped last time.

Two small things that together fix a whole class of confusion for a person who works with an AI
across several evenings.

1. THE TIME. A model does not feel the time of day: it says "good night" at ten in the morning and
   calls an hour ago "yesterday". V1 fixed this by computing the time in code and putting it into
   every call. Here the same, in the one place a plugin gets: the start of the session.

2. WHERE WE STOPPED. The person closes the laptop mid-task and comes back on Thursday. Without a
   note, the evening starts from nothing. With one, it starts from the sentence they left.
   The note is written ONLY when the person says so - an AI that files away whatever it heard is
   the failure this guards against, not the feature.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("SAFECALL_HOME", Path.home() / ".safecall"))
NOTES = ROOT / "notes"

# LEGACY (read-only): names written by safecall <= 0.1.0, before this was renamed from Russian
# to English. A note made by that version lives in `где-остановились/` and has Russian keys -
# we never write these names again, but we keep reading them so upgrading never loses the last
# note somebody already has on their machine.
LEGACY_NOTES_DIR_NAME = "где-остановились"
LEGACY_NOTE_KEYS = {"when": "когда", "folder": "папка", "done": "сделано",
                     "left": "не_сделано", "next": "дальше", "traps": "ловушки"}

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _tag(folder: Path) -> str:
    import hashlib
    return hashlib.sha256(str(folder).encode()).hexdigest()[:8]


def _slug(folder: Path) -> str:
    import re
    name = re.sub(r"[^\w.-]+", "-", folder.name or "root", flags=re.U).strip("-")
    return f"{name or 'folder'}-{_tag(folder)}.json"


def _note_path(folder: Path) -> Path:
    return NOTES / _slug(folder)


def _find_note(folder: Path):
    """The note file for this folder: the current one if there is one, else the legacy one
    (written by a version before the rename) for the SAME folder. Matched by the hash tag
    rather than the full file name, since the legacy name-sanitising regex differed slightly
    and must not be relied on to produce byte-identical names. Returns None if there is no
    note either way."""
    new = _note_path(folder)
    if new.exists():
        return new
    legacy_dir = ROOT / LEGACY_NOTES_DIR_NAME
    if not legacy_dir.exists():
        return None
    tag = _tag(folder)
    matches = sorted(legacy_dir.glob(f"*{tag}.json"))
    return matches[0] if matches else None


def _load_note(path: Path, legacy: bool) -> dict:
    """This note's fields, with English keys - translated from the legacy Russian ones first,
    if that is what this note has."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not legacy:
        return raw
    return {new: raw[old] for new, old in LEGACY_NOTE_KEYS.items() if old in raw}


def cmd_now(args):
    n = datetime.now().astimezone()
    print(f"The real time on this computer: {DAYS[n.weekday()]}, {MONTHS[n.month-1]} {n.day}, "
          f"{n.year}, {n:%H:%M}. Time zone {n:%Z} ({n:%z}).")
    print("This is the computer's real time. Do not greet by guessing the time of day, "
          "and do not call something that happened an hour ago \"yesterday\".")
    return 0


def cmd_show(args):
    folder = Path(args.folder or Path.cwd()).expanduser().resolve()
    p = _find_note(folder)
    if p is None:
        print("There is no \"where we stopped\" note for this folder — so this is the first time.")
        return 0
    try:
        note = _load_note(p, legacy=(p.parent.name == LEGACY_NOTES_DIR_NAME))
    except (OSError, ValueError, KeyError):
        print("The note exists, but it could not be read.")
        return 1
    when = datetime.fromisoformat(note["when"])
    print(f"Last time ({MONTHS[when.month-1]} {when.day}, {when:%H:%M}) this is where things stopped:")
    print(f"  DONE: {note.get('done') or '—'}")
    print(f"  NOT DONE: {note.get('left') or '—'}")
    print(f"  NEXT: {note.get('next') or '—'}")
    if note.get("traps"):
        print(f"  WATCH OUT: {note['traps']}")
    return 0


def cmd_save(args):
    folder = Path(args.folder or Path.cwd()).expanduser().resolve()
    NOTES.mkdir(parents=True, exist_ok=True)
    note = {
        "when": datetime.now().astimezone().isoformat(timespec="minutes"),
        "folder": str(folder),
        "done": args.done or "",
        "left": args.left or "",
        "next": args.next or "",
        "traps": args.traps or "",
    }
    _note_path(folder).write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Noted where things stopped. Next time, we will start from here.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safecall: the time, and \"where we stopped\".")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("now", help="the real time on this computer")
    s.set_defaults(func=cmd_now)

    s = sub.add_parser("show", help="show where things stopped")
    s.add_argument("--folder")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("save", help="note where things stopped (only when the person says so)")
    s.add_argument("--folder")
    s.add_argument("--done")
    s.add_argument("--left")
    s.add_argument("--next")
    s.add_argument("--traps")
    s.set_defaults(func=cmd_save)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
