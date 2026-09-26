#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safecall: a copy of a file before anything is written to it, and the way back.

Why this exists. The person this plugin is for has no git and never will. They have a folder of
documents, and the one sentence that stops them using an AI on it is "what if it deletes them".
V1 met the same wall and stopped requiring git for its own undo; this is the same idea, small
enough to live in a plugin and to be explained in one line to somebody who is sixty.

Where copies live. NOT in the person's folder. A copy dropped beside the documents gets read as
clutter and deleted by the very person it protects - so copies go to ~/.safecall/снимки/, outside
the work folder, with a README that says in their own words not to delete it.

No dependencies. Python 3.8+. Nothing here reaches the network.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
ROOT = Path(os.environ.get("SAFECALL_HOME", HOME / ".safecall"))
# ASCII on purpose. The buyer speaks one of five languages, and a folder called `снимки` cannot be
# typed by a person on an English or Spanish keyboard when support says "open the copies folder".
# Found by the round of criticism, 26.09.2026.
SHOTS = ROOT / "copies"

# Limits, so a snapshot can never fill the disk of a person who will not be watching it.
MAX_FILE = 5 * 1024 * 1024          # 5 MB per file
MAX_SNAPSHOT = 50 * 1024 * 1024     # 50 MB per snapshot
KEEP_DAYS = 14
KEEP_SNAPSHOTS = 20

# Files whose NAME says they hold a secret are never copied: a copy of a secret is a second secret,
# and this folder is not protected the way the original might be. Same rule V1 applies to rollback.
SECRET_NAME = re.compile(
    r"(^\.env|\.env$|\.env\.|secret|password|passwd|credential|\.pem$|\.key$|\.p12$|"
    r"\.keystore$|id_rsa|id_ed25519|\.netrc|\.htpasswd|token)", re.I)

README = """Это ваша страховка. Не удаляйте эту папку.

Здесь лежат копии ваших файлов, сделанные ДО того, как ИИ их изменил.
Если что-то пошло не так, скажите вашему ИИ на компьютере:

    верни, как было

и он возьмёт копию отсюда.

Копии старше 14 дней стираются сами. Ничего отсюда никуда не отправляется.

--
This is your safety net. Do not delete this folder.
It holds copies of your files made BEFORE the AI changed them.
To get them back, tell your AI: "put it back the way it was".
"""


def _say(msg):
    print(msg)


def _ensure_root():
    SHOTS.mkdir(parents=True, exist_ok=True)
    rd = ROOT / "README-ПРОЧТИ-МЕНЯ.txt"
    if not rd.exists():
        rd.write_text(README, encoding="utf-8")


def _slug(path: Path) -> str:
    """A short, readable folder name for the work folder a snapshot belongs to."""
    name = path.name or "корень"
    safe = re.sub(r"[^\wЀ-ӿ.-]+", "-", name, flags=re.U).strip("-")
    tag = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:8]
    return f"{safe or 'папка'}-{tag}"


def _stamp_dir(folder: Path) -> Path:
    """A fresh directory for this snapshot.

    The stamp is to the second, and two snapshots inside one second really happen: `restore` saves
    the current state before overwriting it, immediately after reading the snapshot it is about to
    restore from. Without the suffix below, that second save landed in the SAME directory and
    overwrote the very copy being restored - undo returned the damaged file. Found by
    test_save_and_restore_round_trip.
    """
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dest = folder / stamp
    n = 1
    while dest.exists():
        dest = folder / f"{stamp}-{n}"
        n += 1
    return dest


def _is_copyable(p: Path):
    """(ok, reason). Reason is in plain words - it gets shown to a person, not to a log."""
    if p.is_symlink():
        return False, "это ярлык на другой файл, а не сам файл"
    if not p.exists():
        return False, "файла ещё нет — значит и терять нечего"
    if not p.is_file():
        return False, "это папка, а не файл"
    if SECRET_NAME.search(p.name):
        return False, "в имени файла есть слово про пароль или ключ — копию такого не делаем"
    try:
        if p.stat().st_size > MAX_FILE:
            return False, f"файл больше {MAX_FILE // (1024*1024)} МБ"
    except OSError as e:
        return False, f"не смог прочитать размер: {e}"
    return True, ""


def cmd_save(args):
    _ensure_root()
    # abspath, NOT resolve: resolve() follows a symlink, and then the symlink check below can never
    # fire - the copy would silently be of the target. Found by test_symlink_is_not_copied.
    paths = [Path(os.path.abspath(os.path.expanduser(p))) for p in args.paths]
    if not paths:
        _say("Нечего копировать: не названо ни одного файла.")
        return 0

    base = Path(args.folder).expanduser().resolve() if args.folder else Path.cwd().resolve()
    dest = _stamp_dir(SHOTS / _slug(base))
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    entries, skipped, total = [], [], 0

    for p in paths:
        ok, why = _is_copyable(p)
        if not ok:
            skipped.append((str(p), why))
            continue
        p = p.resolve()
        size = p.stat().st_size
        if total + size > MAX_SNAPSHOT:
            skipped.append((str(p), "снимок уже набрал 50 МБ"))
            continue
        try:
            rel = p.relative_to(base)
        except ValueError:
            rel = Path(p.name)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        total += size
        entries.append({"файл": str(p), "внутри": str(rel), "байт": size})

    if not entries:
        _say("Копию делать не из чего. " + "; ".join(f"{f}: {w}" for f, w in skipped))
        return 0

    (dest / "снимок.json").write_text(json.dumps({
        "когда": stamp, "папка": str(base), "файлы": entries, "пропущено": skipped,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    _prune(SHOTS / _slug(base))
    _say(f"Копия сделана: {len(entries)} файл(ов), {total // 1024} КБ.")
    _say(f"Лежит здесь: {dest}")
    if skipped:
        for f, w in skipped:
            _say(f"  не скопирован {f} — {w}")
    _say('Чтобы вернуть: скажите "верни, как было".')
    return 0


def _prune(folder: Path):
    if not folder.exists():
        return
    shots = sorted([d for d in folder.iterdir() if d.is_dir()], reverse=True)
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    for i, d in enumerate(shots):
        too_many = i >= KEEP_SNAPSHOTS
        try:
            too_old = datetime.strptime(d.name, "%Y-%m-%d_%H-%M-%S") < cutoff
        except ValueError:
            too_old = False
        if too_many or too_old:
            shutil.rmtree(d, ignore_errors=True)


def _shots_for(base: Path):
    folder = SHOTS / _slug(base)
    if not folder.exists():
        return []
    return sorted([d for d in folder.iterdir() if d.is_dir() and (d / "снимок.json").exists()],
                  reverse=True)


def cmd_list(args):
    base = Path(args.folder).expanduser().resolve() if args.folder else Path.cwd().resolve()
    shots = _shots_for(base)
    if not shots:
        _say("Копий для этой папки пока нет.")
        return 0
    _say(f"Копии для папки {base}:")
    for i, d in enumerate(shots, 1):
        meta = json.loads((d / "снимок.json").read_text(encoding="utf-8"))
        when = datetime.strptime(meta["когда"], "%Y-%m-%d_%H-%M-%S").strftime("%d.%m.%Y в %H:%M")
        names = ", ".join(e["внутри"] for e in meta["файлы"][:4])
        more = f" и ещё {len(meta['файлы']) - 4}" if len(meta["файлы"]) > 4 else ""
        _say(f"  {i}. {when} — {names}{more}")
    return 0


def cmd_restore(args):
    base = Path(args.folder).expanduser().resolve() if args.folder else Path.cwd().resolve()
    shots = _shots_for(base)
    if not shots:
        _say("Возвращать нечего: копий для этой папки нет.")
        return 1
    pick = shots[0] if args.which in (None, "last") else None
    if pick is None:
        try:
            pick = shots[int(args.which) - 1]
        except (ValueError, IndexError):
            _say(f"Нет копии под номером {args.which}. Посмотрите список: их {len(shots)}.")
            return 1

    meta = json.loads((pick / "снимок.json").read_text(encoding="utf-8"))
    when = datetime.strptime(meta["когда"], "%Y-%m-%d_%H-%M-%S").strftime("%d.%m.%Y в %H:%M")

    if not args.yes:
        _say(f"Верну {len(meta['файлы'])} файл(ов) в том виде, как они были {when}:")
        for e in meta["файлы"]:
            _say(f"  {e['внутри']}")
        _say("Ничего ещё не тронуто. Чтобы вернуть на самом деле, добавьте --yes.")
        return 0

    # Before overwriting, copy what is there NOW - so that "undo" itself can be undone.
    now_paths = [Path(e["файл"]) for e in meta["файлы"] if Path(e["файл"]).exists()]
    if now_paths:
        cmd_save(argparse.Namespace(paths=[str(p) for p in now_paths], folder=str(base)))

    back = 0
    for e in meta["файлы"]:
        src = pick / e["внутри"]
        dst = Path(e["файл"])
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        back += 1
    _say(f"Вернул {back} файл(ов), как было {when}.")
    _say("То, что лежало до возврата, тоже скопировано — если передумаете, вернуть можно и это.")
    return 0


def cmd_covered(args):
    """Is there a snapshot of this file from the last N minutes? Used by the hook."""
    p = Path(args.path).expanduser().resolve()
    base = Path(args.folder).expanduser().resolve() if args.folder else Path.cwd().resolve()
    fresh = time.time() - args.minutes * 60
    for d in _shots_for(base):
        try:
            if d.stat().st_mtime < fresh:
                break
            meta = json.loads((d / "снимок.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if any(Path(e["файл"]) == p for e in meta["файлы"]):
            _say("да")
            return 0
    _say("нет")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safecall: копия файла до правки и путь назад.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("save", help="скопировать файлы до того, как их изменят")
    s.add_argument("paths", nargs="+")
    s.add_argument("--folder")
    s.set_defaults(func=cmd_save)

    s = sub.add_parser("list", help="показать копии")
    s.add_argument("--folder")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("restore", help="вернуть, как было")
    s.add_argument("which", nargs="?")
    s.add_argument("--folder")
    s.add_argument("--yes", action="store_true")
    s.set_defaults(func=cmd_restore)

    s = sub.add_parser("covered", help="есть ли свежая копия этого файла")
    s.add_argument("path")
    s.add_argument("--folder")
    s.add_argument("--minutes", type=int, default=120)
    s.set_defaults(func=cmd_covered)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
