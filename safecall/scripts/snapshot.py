#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safecall: a copy of a file before anything is written to it, and the way back.

Why this exists. The person this plugin is for has no git and never will. They have a folder of
documents, and the one sentence that stops them using an AI on it is "what if it deletes them".
V1 met the same wall and stopped requiring git for its own undo; this is the same idea, small
enough to live in a plugin and to be explained in one line to somebody who is sixty.

Where copies live. NOT in the person's folder. A copy dropped beside the documents gets read as
clutter and deleted by the very person it protects - so copies go to ~/.safecall/copies/, outside
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
# ASCII on purpose. The buyer speaks one of five languages, and a folder called `snapshots` cannot
# be mistyped the way a Cyrillic name could be on an English or Spanish keyboard when support says
# "open the copies folder". Found by the round of criticism, 26.09.2026.
SHOTS = ROOT / "copies"

# Limits, so a snapshot can never fill the disk of a person who will not be watching it.
MAX_FILE = 5 * 1024 * 1024          # 5 MB per file
MAX_SNAPSHOT = 50 * 1024 * 1024     # 50 MB per snapshot
KEEP_DAYS = 14
KEEP_SNAPSHOTS = 20

LANG_DIR = Path(__file__).resolve().parent.parent / "lang"


def _load_lang(code):
    try:
        return json.loads((LANG_DIR / f"{code}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _all_langs():
    """Every lang/<code>.json found, as {code: data}. Each language is read the same way -
    there is no "main" language file and no special-cased one."""
    if not LANG_DIR.is_dir():
        return {}
    return {p.stem: _load_lang(p.stem) for p in sorted(LANG_DIR.glob("*.json"))}


# Files whose NAME says they hold a secret are never copied: a copy of a secret is a second secret,
# and this folder is not protected the way the original might be. Same rule V1 applies to rollback.
# The word list was English-only until 26.09.2026, and that made it blind exactly where this
# plugin is used: the person it is written for does not know what an extension is and
# names the file in their own language. Caught by running it - a Russian-named password file
# was copied without a word. The words below are the ones such a person actually types, one
# list per language in lang/*.json (every language equal - none of them lives in this file).
# Over-matching costs a copy that is not made and IS announced; under-matching copies a secret
# into a second place and says nothing.
#
# Patterns here are technical conventions, not any one language's word, so they stay here
# rather than in a lang file: a dotfile or key-file name reads the same regardless of what
# language the person who typed it speaks.
_UNIVERSAL_SECRET_PATTERNS = (
    r"^\.env|\.env$|\.env\.|\.pem$|\.key$|\.p12$|\.keystore$|id_rsa|id_ed25519|\.netrc|\.htpasswd"
)


def _secret_name_pattern():
    parts = [_UNIVERSAL_SECRET_PATTERNS]
    for data in _all_langs().values():
        parts.extend(data.get("secret_words", []))
    return re.compile("(" + "|".join(parts) + ")", re.I)


SECRET_NAME = _secret_name_pattern()

# LEGACY (read-only): names written by safecall <= 0.1.0, before snapshot metadata was renamed
# from Russian to English. A copy made by that version has a metadata file whose name and keys
# are Russian too - we never write these names again, but we keep reading them so upgrading
# never drops or breaks a copy that already exists on somebody's machine. The names themselves
# live in lang/ru.json ("legacy"), not here - this file stays English-only.
_RU_LEGACY = _load_lang("ru").get("legacy", {})
# No lang/ru.json: no legacy name (None), never a guess that could collide with a current name.
LEGACY_META_NAME = _RU_LEGACY.get("meta_file_name")
LEGACY_META_KEYS = _RU_LEGACY.get("meta_keys", {})
LEGACY_ENTRY_KEYS = _RU_LEGACY.get("entry_keys", {})

README = """This is your safety net. Do not delete this folder.

It holds copies of your files, made BEFORE an AI changed them.
If something goes wrong, tell your AI on this computer:

    put it back the way it was

and it will take the copy from here.

Copies older than 14 days are deleted automatically. Nothing here is ever sent anywhere.
"""


def _say(msg):
    print(msg)


def _ensure_root():
    SHOTS.mkdir(parents=True, exist_ok=True)
    rd = ROOT / "README.txt"
    if not rd.exists():
        rd.write_text(README, encoding="utf-8")


def _slug(path: Path) -> str:
    """A short, readable folder name for the work folder a snapshot belongs to."""
    name = path.name or "root"
    safe = re.sub(r"[^\w.-]+", "-", name, flags=re.U).strip("-")
    tag = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:8]
    return f"{safe or 'folder'}-{tag}"


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
        return False, "this is a shortcut to another file, not the file itself"
    if not p.exists():
        return False, "the file does not exist yet — so there is nothing to lose"
    if not p.is_file():
        return False, "this is a folder, not a file"
    if SECRET_NAME.search(p.name):
        return False, "the file name has a word about a password or key — we do not copy that"
    try:
        if p.stat().st_size > MAX_FILE:
            return False, f"file is bigger than {MAX_FILE // (1024*1024)} MB"
    except OSError as e:
        return False, f"could not read the size: {e}"
    return True, ""


def cmd_save(args):
    _ensure_root()
    # abspath, NOT resolve: resolve() follows a symlink, and then the symlink check below can never
    # fire - the copy would silently be of the target. Found by test_symlink_is_not_copied.
    paths = [Path(os.path.abspath(os.path.expanduser(p))) for p in args.paths]
    if not paths:
        _say("Nothing to copy: no file was named.")
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
            skipped.append((str(p), "this snapshot already reached 50 MB"))
            continue
        try:
            rel = p.relative_to(base)
        except ValueError:
            rel = Path(p.name)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
        total += size
        entries.append({"file": str(p), "inside": str(rel), "bytes": size})

    if not entries:
        _say("Nothing here to copy. " + "; ".join(f"{f}: {w}" for f, w in skipped))
        return 0

    # Always written with the current (English) names - only reading looks back at the legacy
    # ones, for copies a previous version already made.
    (dest / "snapshot.json").write_text(json.dumps({
        "when": stamp, "folder": str(base), "files": entries, "skipped": skipped,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    _prune(SHOTS / _slug(base), keep=getattr(args, "keep", None))
    _say(f"Copy made: {len(entries)} file(s), {total // 1024} KB.")
    _say(f"It lives here: {dest}")
    if skipped:
        for f, w in skipped:
            _say(f"  not copied: {f} — {w}")
    _say('To get it back, say: "put it back the way it was".')
    return 0


def _prune(folder: Path, keep: Path = None):
    """Delete snapshots beyond the count/age limit.

    `keep` is never deleted even if it is old or over the count - it is the one `restore` is
    reading FROM right now. Without this, `restore` on an old snapshot deleted that very
    snapshot (via the "back up what is there now" save it does first, which prunes) before it
    could copy anything out of it - a silent "Restored 0 file(s)". Pre-existing bug, found while
    adding legacy-format reading; not specific to the rename. Covered by
    test_restore_of_an_old_snapshot_does_not_delete_it_first.
    """
    if not folder.exists():
        return
    shots = sorted([d for d in folder.iterdir() if d.is_dir()], reverse=True)
    cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
    for i, d in enumerate(shots):
        if keep is not None and d == keep:
            continue
        too_many = i >= KEEP_SNAPSHOTS
        try:
            too_old = datetime.strptime(d.name, "%Y-%m-%d_%H-%M-%S") < cutoff
        except ValueError:
            too_old = False
        if too_many or too_old:
            shutil.rmtree(d, ignore_errors=True)


def _meta_file(d: Path):
    """The metadata file inside this snapshot dir: the current name if it is there, else the
    legacy one, else None. A dir with neither is not a snapshot (e.g. mid-write, or foreign)."""
    new = d / "snapshot.json"
    if new.exists():
        return new
    legacy = d / LEGACY_META_NAME if LEGACY_META_NAME else None
    if legacy is not None and legacy.exists():
        return legacy
    return None


def _load_meta(d: Path) -> dict:
    """This snapshot's metadata, with English keys - translated from the legacy Russian ones
    first, if that is what this snapshot has."""
    f = _meta_file(d)
    if f is None:
        raise FileNotFoundError(f"no snapshot metadata in {d}")
    raw = json.loads(f.read_text(encoding="utf-8"))
    if f.name != LEGACY_META_NAME:
        return raw
    meta = {new: raw[old] for new, old in LEGACY_META_KEYS.items() if old in raw}
    meta["files"] = [{new: e[old] for new, old in LEGACY_ENTRY_KEYS.items() if old in e}
                      for e in meta.get("files", [])]
    return meta


def _shots_for(base: Path):
    folder = SHOTS / _slug(base)
    if not folder.exists():
        return []
    return sorted([d for d in folder.iterdir() if d.is_dir() and _meta_file(d) is not None],
                  reverse=True)


def cmd_list(args):
    base = Path(args.folder).expanduser().resolve() if args.folder else Path.cwd().resolve()
    shots = _shots_for(base)
    if not shots:
        _say("There are no copies for this folder yet.")
        return 0
    _say(f"Copies for folder {base}:")
    for i, d in enumerate(shots, 1):
        meta = _load_meta(d)
        when = datetime.strptime(meta["when"], "%Y-%m-%d_%H-%M-%S").strftime("%Y-%m-%d %H:%M")
        names = ", ".join(e["inside"] for e in meta["files"][:4])
        more = f" and {len(meta['files']) - 4} more" if len(meta["files"]) > 4 else ""
        _say(f"  {i}. {when} — {names}{more}")
    return 0


def cmd_restore(args):
    base = Path(args.folder).expanduser().resolve() if args.folder else Path.cwd().resolve()
    shots = _shots_for(base)
    if not shots:
        _say("Nothing to restore: there are no copies for this folder.")
        return 1
    pick = shots[0] if args.which in (None, "last") else None
    if pick is None:
        try:
            pick = shots[int(args.which) - 1]
        except (ValueError, IndexError):
            _say(f"There is no copy numbered {args.which}. Check the list: there are {len(shots)}.")
            return 1

    meta = _load_meta(pick)
    when = datetime.strptime(meta["when"], "%Y-%m-%d_%H-%M-%S").strftime("%Y-%m-%d %H:%M")

    if not args.yes:
        _say(f"Will restore {len(meta['files'])} file(s) to how they were at {when}:")
        for e in meta["files"]:
            _say(f"  {e['inside']}")
        _say("Nothing has been touched yet. To actually restore, add --yes.")
        return 0

    # Before overwriting, copy what is there NOW - so that "undo" itself can be undone.
    # `keep=pick`: this save must not prune away the very snapshot `restore` is reading from.
    now_paths = [Path(e["file"]) for e in meta["files"] if Path(e["file"]).exists()]
    if now_paths:
        cmd_save(argparse.Namespace(paths=[str(p) for p in now_paths], folder=str(base), keep=pick))

    back = 0
    for e in meta["files"]:
        src = pick / e["inside"]
        dst = Path(e["file"])
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        back += 1
    _say(f"Restored {back} file(s) to how they were at {when}.")
    _say("What was there before the restore was copied too — if you change your mind, that can "
         "be restored as well.")
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
            meta = _load_meta(d)
        except (OSError, ValueError):
            continue
        if any(Path(e["file"]) == p for e in meta["files"]):
            _say("yes")
            return 0
    _say("no")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safecall: copy a file before it is edited, and the way back.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("save", help="copy files before they are changed")
    s.add_argument("paths", nargs="+")
    s.add_argument("--folder")
    s.set_defaults(func=cmd_save)

    s = sub.add_parser("list", help="show the copies")
    s.add_argument("--folder")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("restore", help="put it back the way it was")
    s.add_argument("which", nargs="?")
    s.add_argument("--folder")
    s.add_argument("--yes", action="store_true")
    s.set_defaults(func=cmd_restore)

    s = sub.add_parser("covered", help="is there a fresh copy of this file")
    s.add_argument("path")
    s.add_argument("--folder")
    s.add_argument("--minutes", type=int, default=120)
    s.set_defaults(func=cmd_covered)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
