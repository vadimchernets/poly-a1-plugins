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
NOTES = ROOT / "где-остановились"

MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня",
          "июля", "августа", "сентября", "октября", "ноября", "декабря"]
DAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def _slug(folder: Path) -> str:
    import hashlib
    import re
    name = re.sub(r"[^\wЀ-ӿ.-]+", "-", folder.name or "корень", flags=re.U).strip("-")
    return f"{name or 'папка'}-{hashlib.sha256(str(folder).encode()).hexdigest()[:8]}.json"


def _note_path(folder: Path) -> Path:
    return NOTES / _slug(folder)


def cmd_now(args):
    n = datetime.now().astimezone()
    print(f"Сейчас на этом компьютере: {DAYS[n.weekday()]}, {n.day} {MONTHS[n.month-1]} "
          f"{n.year} года, {n:%H:%M}. Часовой пояс {n:%Z} ({n:%z}).")
    print("Это настоящее время компьютера. Не здоровайся по времени суток наугад "
          "и не называй «вчера» то, что было час назад.")
    return 0


def cmd_show(args):
    folder = Path(args.folder or Path.cwd()).expanduser().resolve()
    p = _note_path(folder)
    if not p.exists():
        print("Заметки «где остановились» для этой папки нет — значит это первый раз.")
        return 0
    try:
        note = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print("Заметка есть, но прочитать её не смог.")
        return 1
    when = datetime.fromisoformat(note["когда"])
    print(f"В прошлый раз ({when.day} {MONTHS[when.month-1]}, {when:%H:%M}) остановились на этом:")
    print(f"  СДЕЛАНО: {note.get('сделано') or '—'}")
    print(f"  НЕ СДЕЛАНО: {note.get('не_сделано') or '—'}")
    print(f"  ДАЛЬШЕ: {note.get('дальше') or '—'}")
    if note.get("ловушки"):
        print(f"  ОСТОРОЖНО: {note['ловушки']}")
    return 0


def cmd_save(args):
    folder = Path(args.folder or Path.cwd()).expanduser().resolve()
    NOTES.mkdir(parents=True, exist_ok=True)
    note = {
        "когда": datetime.now().astimezone().isoformat(timespec="minutes"),
        "папка": str(folder),
        "сделано": args.done or "",
        "не_сделано": args.left or "",
        "дальше": args.next or "",
        "ловушки": args.traps or "",
    }
    _note_path(folder).write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Записал, где остановились. В следующий раз начнём отсюда.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safecall: время и «где остановились».")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("now", help="настоящее время этого компьютера")
    s.set_defaults(func=cmd_now)

    s = sub.add_parser("show", help="показать, где остановились")
    s.add_argument("--folder")
    s.set_defaults(func=cmd_show)

    s = sub.add_parser("save", help="записать, где остановились (только по слову человека)")
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
