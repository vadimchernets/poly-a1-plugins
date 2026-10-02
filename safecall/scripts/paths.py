#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Safecall: does every file the answer names actually exist?

The failure this catches is specific and common, and a person of sixty has no defence against it:
an AI writes "there is a contract-2024.pdf in your folder, and it says…" and there is no such
file. The sentence is fluent, the filename is plausible, and the person believes it — sometimes
about a document they then go looking for at the bank.

V1 meets the same problem in its folder council and answers it the same way: every path a seat
cites is checked against the disk, and a citation that does not resolve is not an answer
(`docs/ARCHITECTURE.md:183-185`, `docs/AGENT-MODE-CLI.md:1-7`).

This does the checking half. It reads text on standard input, pulls out everything that looks like
a file name or a path, and says which of them are really on the disk.

  python3 paths.py --folder <folder> < answer.txt

It deliberately does NOT judge the sentence around the name - it says what is there and what is
not, and the skill decides what to do about it.
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Extensions a person of this product actually deals with, plus the ones an AI invents about them.
EXT = (r"txt|md|pdf|docx?|xlsx?|pptx?|rtf|odt|ods|csv|tsv|json|ya?ml|xml|html?|zip|rar|7z|"
       r"jpe?g|png|heic|gif|webp|mp3|m4a|wav|mov|mp4|py|js|mjs|ts|tsx|sh|log|env|ini|cfg|conf")

# A path, or a bare file name. Quotes and « » are how both AIs and people fence a filename.
CANDIDATE = re.compile(
    r"""(?:[«"'`]\s*)?                      # optional opening fence
        (
          (?:~|\.{1,2})?/[^\s«»"'`,;:!?()\[\]{}]+   # something with a slash
          |
          [^\s«»"'`,;:!?()\[\]{}/\\]+\.(?:%s)\b     # or a bare name.ext
        )
    """ % EXT, re.X | re.I)

# Things that look like a file and are not one: URLs, versions, domains, money.
NOT_A_FILE = re.compile(
    r"^(?:https?:|mailto:|www\.)|^\d+\.\d+$|^v?\d+(?:\.\d+){1,}$", re.I)


def candidates(text: str):
    seen, out = set(), []
    for m in CANDIDATE.finditer(text):
        raw = m.group(1).rstrip(".,;:!?»\"'`)")
        if not raw or NOT_A_FILE.search(raw):
            continue
        if raw in seen:
            continue
        seen.add(raw)
        out.append(raw)
    return out


def resolve(name: str, base: Path):
    """Where this name really is, if anywhere. Returns (exists, where)."""
    p = Path(os.path.expanduser(name))
    tries = [p] if p.is_absolute() else [base / p, Path.cwd() / p]
    for t in tries:
        try:
            if t.exists():
                return True, str(t)
        except OSError:
            continue
    # Not at the named place - but maybe the same name lives somewhere under the folder. Saying
    # "there is no such file" when it is one folder down is its own kind of wrong answer.
    leaf = Path(name).name
    if leaf and leaf != name:
        try:
            for found in list(base.rglob(leaf))[:1]:
                return False, f"not at the named path, but a file by this name is here: {found}"
        except OSError:
            pass
    else:
        try:
            for found in list(base.rglob(leaf))[:1]:
                if found.parent != base:
                    return True, str(found)
        except OSError:
            pass
    return False, ""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safecall: check named files against the disk.")
    ap.add_argument("--folder", help="the person's folder; defaults to the current one")
    ap.add_argument("--text", help="text given directly as an argument; otherwise read from standard input")
    args = ap.parse_args(argv)

    base = Path(args.folder).expanduser().resolve() if args.folder else Path.cwd().resolve()
    text = args.text if args.text is not None else sys.stdin.read()

    names = candidates(text)
    if not names:
        print("No file was named in this text — nothing to check.")
        return 0

    good, bad = [], []
    for n in names:
        ok, where = resolve(n, base)
        (good if ok else bad).append((n, where))

    for n, where in good:
        print(f"  exists: {n}" + (f"  → {where}" if where and where != n else ""))
    for n, where in bad:
        print(f"  MISSING: {n}" + (f"  ({where})" if where else ""))

    print(f"\nfiles named: {len(names)} · found: {len(good)} · not found: {len(bad)}")
    if bad:
        print("Do NOT tell the person a file that was not found exists. Either fix the name, "
              "or say plainly that no such file is in the folder.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
