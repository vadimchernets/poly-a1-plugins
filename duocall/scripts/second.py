#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Duocall: find a second AI of ANOTHER company on this computer, and ask it.

The rule that makes this worth anything is V1's, and it is not negotiable here either
(`V1/docs/leaders.manifest.json`, principles):

    "Pair (second opinion) = a DIFFERENT vendor, else the pair is honestly OFF
     (no same-vendor fake diversity)."

Two answers from the same company are one opinion wearing two hats. If the only program on this
machine is the one already answering, this script says so and offers nothing - the skill then hands
the person a block to paste into a free browser chat, which really is another company.

What it never does: install anything, sign anyone in, ask for a key, or spend money. It only drives
a program that is ALREADY installed and ALREADY signed in, which is the whole idea the product is
built on.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

# family -> (binary, args builder, human name). Claude is deliberately absent: it is the one asking.
FAMILIES = [
    ("openai", "codex",  lambda p: ["exec", "--skip-git-repo-check", "-s", "read-only", p],
     "ChatGPT (Codex)"),
    ("google", "agy",    lambda p: ["-p", p], "Gemini"),
    ("google", "gemini", lambda p: ["-p", p], "Gemini"),
    ("xai",    "grok",   lambda p: ["-p", p, "--permission-mode", "dontAsk",
                                    "--deny", "Write(**)", "--deny", "Edit(**)",
                                    "--deny", "Bash(*)", "--max-turns", "6"], "Grok"),
    ("moonshot", "kimi", lambda p: ["-p", p], "Kimi"),
    ("alibaba", "qwen",  lambda p: ["-p", p], "Qwen"),
]

TIMEOUT = int(os.environ.get("DUOCALL_TIMEOUT", "180"))


def available():
    seen, out = set(), []
    for family, binary, build, label in FAMILIES:
        if family in seen:
            continue
        path = shutil.which(binary)
        if path:
            seen.add(family)
            out.append({"семья": family, "программа": binary, "имя": label, "где": path})
    return out


def cmd_list(args):
    found = available()
    if not found:
        print("Второй программы другой компании на этом компьютере нет.")
        print("Это не поломка: второе мнение можно взять в браузере, бесплатно, "
              "в чате другой компании — так и сделайте.")
        return 1
    print(f"Нашёл {len(found)} программ(ы) другой компании, уже установленных и вошедших:")
    for f in found:
        print(f"  {f['имя']} — {f['программа']}")
    return 0


def cmd_ask(args):
    found = available()
    if not found:
        print(json.dumps({"ok": False, "почему": "нет второй программы другой компании"},
                         ensure_ascii=False))
        return 1

    pick = None
    if args.who:
        pick = next((f for f in found if args.who.lower() in (f["программа"], f["семья"])), None)
        if pick is None:
            print(json.dumps({"ok": False, "почему": f"{args.who} на этом компьютере нет"},
                             ensure_ascii=False))
            return 1
    else:
        pick = found[0]

    build = next(b for fam, bin_, b, _ in FAMILIES if bin_ == pick["программа"])
    prompt = args.prompt
    if prompt == "-":
        prompt = sys.stdin.read()

    try:
        done = subprocess.run([pick["программа"], *build(prompt)],
                              capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print(json.dumps({"ok": False, "кто": pick["имя"], "программа": pick["программа"],
                          "почему": f"не ответил за {TIMEOUT} секунд"}, ensure_ascii=False))
        return 1
    except OSError as e:
        print(json.dumps({"ok": False, "кто": pick["имя"], "почему": f"не запустился: {e}"},
                         ensure_ascii=False))
        return 1

    text = (done.stdout or "").strip()
    if done.returncode != 0 or not text:
        why = (done.stderr or "").strip().splitlines()
        why = why[-1] if why else f"код возврата {done.returncode}"
        # The single most common failure, and it is not the person's fault.
        if any(w in why.lower() for w in ("quota", "limit", "rate", "usage", "429")):
            why = "у этой программы кончился месячный или дневной запас"
        print(json.dumps({"ok": False, "кто": pick["имя"], "программа": pick["программа"],
                          "почему": why}, ensure_ascii=False))
        return 1

    print(json.dumps({"ok": True, "кто": pick["имя"], "программа": pick["программа"],
                      "семья": pick["семья"], "ответ": text}, ensure_ascii=False))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Duocall: второй ИИ другой компании.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="какие программы другой компании тут есть")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("ask", help="задать вопрос второму ИИ")
    s.add_argument("prompt", help="текст вопроса, или - чтобы прочитать со стандартного ввода")
    s.add_argument("--who", help="кого именно спросить (codex, agy, grok, kimi, qwen)")
    s.set_defaults(func=cmd_ask)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
