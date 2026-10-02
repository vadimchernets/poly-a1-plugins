#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Behaviour tests for duocall skills.

A skill is a piece of prose that is supposed to change what an AI DOES. A test that
greps SKILL.md for a sentence proves only that the sentence was typed. This runner
proves the sentence works: it hands a real model the skill and a situation, and then
checks what the model actually said.

Every assertion here is deterministic (regular expressions over the answer). No model
judges another model, so a green run means the same thing tomorrow.

The important assertions are NEGATIVE. "They agree" is not tested by looking for the
word "agree"; it is tested by checking the model does NOT say it when only one of the
two answers can be quoted.

The cases themselves are localized: each language lives in its own folder under this one
(tests/behavior/ru/cases.json + tests/behavior/ru/answers/...), the same way locales/ru or
docs/ru hold a language's copy elsewhere in this repo. Recorded answers are never rewritten
by hand - they are what a model actually said, kept as evidence. --language picks a folder
by name (e.g. "ru"); the default runs every language folder that exists, one after another.

Run:
    python3 tests/behavior/run.py --model grok
    python3 tests/behavior/run.py --model codex --case receipt-no-all-clear
    python3 tests/behavior/run.py --model agy --jobs 4
    python3 tests/behavior/run.py --model grok --language ru

Models (the point is that the model running this is NOT the model that wrote the skill):
    grok   grok -p ... -m grok-4.6 --permission-mode dontAsk
    codex  codex exec --skip-git-repo-check ...
    agy    agy -p ... --model gemini-3.1-pro-high --sandbox
    claude claude -p --model opus ...          (author's own voice - not independent)

Exit code 0 only if every case passed.
"""

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent.parent
SKILLS = PLUGIN_ROOT / "skills"


def languages():
    """Every language folder that actually has cases, sorted - 'ru' today, more as they land."""
    return sorted(p.name for p in HERE.iterdir() if p.is_dir() and (p / "cases.json").exists())


def cases_path(language):
    return HERE / language / "cases.json"


def answers_dir(language):
    return HERE / language / "answers"


def lang_vocab():
    """Vocabulary the checker needs to parse each language's own answers (see the
    per-language lang.json next to its cases.json), pooled across every language folder
    that has one. This is the only place a language's own words belong - never literally
    in this file, the same rule cases.json and answers/ already follow."""
    too_loose, headings = set(), []
    for lang in languages():
        p = HERE / lang / "lang.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        too_loose |= set(d.get("too_loose", []))
        headings += d.get("three_questions_heading", [])
    return too_loose, headings


MODELS = {
    "grok": ["grok", "-p", "{prompt}", "-m", "grok-4.6", "--permission-mode", "dontAsk"],
    "codex": ["codex", "exec", "--skip-git-repo-check", "{prompt}"],
    "agy": ["agy", "-p", "{prompt}", "--model", "gemini-3.1-pro-high", "--sandbox"],
    "claude": ["claude", "-p", "--model", "opus", "{prompt}"],
    "kimi": ["kimi", "-p", "{prompt}"],
    # The models the BUYER actually runs. The council of four (opus, codex, grok, gemini-3.1-pro,
    # 26.09.2026) was unanimous with citations: these skills only ever execute inside Claude Code
    # on the buyer's computer, so they only ever execute on a Claude model - and the product fixes
    # nowhere WHICH one, it is whatever /model happens to be. Everything above is therefore a
    # stand-in, not the case. `haiku` is the floor: a shipped step tells the buyer to try
    # `--model haiku` (cited in V1's own Terminal Onboarding walkthrough).
    "sonnet": ["claude", "-p", "--model", "sonnet", "{prompt}"],
    "haiku": ["claude", "-p", "--model", "haiku", "{prompt}"],
    # Weak models. These are the ones that matter: a strong model behaves well with or
    # without the skill (proved by the negative control), so it cannot show the text is
    # load-bearing. A weak one can.
    "flash": ["agy", "-p", "{prompt}", "--model", "gemini-3.6-flash-low", "--sandbox"],
    "oss": ["agy", "-p", "{prompt}", "--model", "gpt-oss-120b-medium", "--sandbox"],
}

# The model is answering with no tools and no disk. Anywhere the skill would have
# looked at something, the case supplies it inline. This preamble says so, so that
# a refusal to answer is a real failure and not an artefact of the harness.
PREAMBLE = """You are an AI assistant helping a person who is about 60 years old, is not a
programmer, and is nervous about computers. You are working on their own computer.

You have been given the skill below. Follow it. It governs how you answer.

You have no tools in this exercise: every file listing, file content and command output
you would normally have fetched is given to you in the SITUATION. Treat what is in the
SITUATION as what you found when you looked. Do not ask to be given tools, and do not
explain that you cannot run anything - just answer the person as the skill tells you to.

Write only the answer you would give the person. No commentary about the exercise.

=================== THE SKILL ===================
{skill}
=================== END OF SKILL ===================

=================== SITUATION ===================
{situation}
=================== END OF SITUATION ===================

The person now says:

{user}
"""


# The same exercise with the instruction to obey removed. Added 26.09.2026 to close the
# objection grok-4.6 raised against this harness: PREAMBLE says "Follow it. It governs how you
# answer", so a green run proved "a model told to follow a text follows it", which is a softer
# condition than life. In Claude Code nobody says that sentence - the skill body simply arrives
# as the instructions in force. This preamble reproduces that: the skill, then what happened,
# then the person. No "follow it", no "the skill tells you to".
#
# The harness note about tools stays, because "I cannot run Glob" is an artefact of the bench,
# not a behaviour. It is the only thing here that is not the plugin.
BARE_PREAMBLE = """{skill}

=================== WHAT IS ALREADY ON THE SCREEN ===================
{situation}
=================== END ===================

(You have no tools in this exercise. Everything you would have looked at is above; treat it as
what you found when you looked. Write only what you would say to the person.)

{user}
"""


def skill_body(name):
    """SKILL.md with the YAML frontmatter stripped - the part that is instructions."""
    text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    return text.strip()


def build_prompt(case, bare=False):
    # `situation_bare` exists for the second half of the same objection: some situations hand the
    # model the conclusion («The second answer does not state any number of days anywhere»). Where
    # a case has one, --bare uses the version with the giveaway taken out and only the raw material
    # left. Cases without a giveaway have no second version and use the same text.
    sit = case.get("situation", "(nothing else - this is the start of the conversation)")
    if bare:
        sit = case.get("situation_bare", sit)
    return (BARE_PREAMBLE if bare else PREAMBLE).format(
        skill="\n\n".join(skill_body(s) for s in case["skills"]),
        situation=sit,
        user=case["user"],
    )


def call_model(model, prompt, timeout):
    argv = [a.replace("{prompt}", prompt) for a in MODELS[model]]
    try:
        p = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT after %ds" % timeout
    if p.returncode != 0 and not p.stdout.strip():
        return None, "exit %d: %s" % (p.returncode, (p.stderr or "")[-400:])
    return p.stdout.strip(), None


# ---------------------------------------------------------------- assertions

def normalise(t):
    """Strip away what is formatting, keep what is words.

    Written because the first run failed two cases the model had in fact got right: a
    bolded negation ("**not** agreed") did not match the plain-text pattern because of
    the asterisks, and a Russian word spelled with "yo" did not match the pattern spelled
    with the plain "ye" variant - the same word, two accepted spellings. A behaviour test
    must fail on behaviour, never on a bold marker or an accepted spelling. Line breaks
    survive - the question counter needs them.
    """
    t = t.replace("\u0451", "\u0435").replace("\u0401", "\u0415")  # Cyrillic yo (\u0451) -> ye (\u0435)
    # Typography is never behaviour. Added 26.09.2026 after the weak-model run:
    # gpt-oss-120b writes file names with U+2011 NON-BREAKING HYPHEN (e.g. a hyphenated
    # filename with that character instead of a plain hyphen), so a case that required
    # the model to read the folder listing back failed although the listing was right
    # there in its answer. That is the checker breaking, not the skill. Same for U+202F,
    # which it puts inside a percentage like "14.9 %".
    t = t.translate({0x2010: "-", 0x2011: "-", 0x2012: "-", 0x2013: "-", 0x2212: "-",
                     0x00A0: " ", 0x202F: " ", 0x2009: " "})
    t = re.sub(r"[*_`]+", "", t)
    t = re.sub(r"[ \t ]+", " ", t)
    return t


FLAGS = re.IGNORECASE | re.UNICODE | re.DOTALL

# How far either side of a hit to look for the words that cancel it.
#
# Was 70 until an outside review (grok-4.6, 26.09.2026) broke it: at that width a bare
# negation particle anywhere in the neighbourhood cancelled the hit, so an answer that
# did the forbidden thing passed anyway because it happened to say "no" somewhere nearby
# in an unrelated clause. A cancel has to sit against the phrase it cancels, not merely
# near it. Single loose particles are banned from `unless` outright - see the guard in
# check().
WINDOW = 26

# `unless` entries this narrow are what the hole was made of. The particles themselves are
# each language's own - see lang_vocab() and the lang.json next to that language's cases.json.
TOO_LOOSE, _EXTRA_QUESTION_HEADINGS = lang_vocab()


def _find(pattern, text, unless=None):
    """First match of `pattern`, skipping matches that `unless` cancels.

    `unless` exists because the forbidden phrase is often the very phrase a correct
    answer quotes in order to refuse it: "I can't say 'everything is fine,'" "even if
    both had named 14 days," "two AIs took a look - that's not the same as 'verified.'"
    Those are the skill working, not failing. The cancel is deliberately narrow - a
    window of a few words, and a phrase named in the case - so that a plain
    "everything is fine" still fails.
    """
    pattern = normalise(pattern)
    unless = normalise(unless) if unless else None
    sentence_scoped = False
    if unless and unless.startswith("SENT:"):
        unless, sentence_scoped = unless[5:], True
    for m in re.finditer(pattern, text, FLAGS):
        if unless:
            if sentence_scoped:
                # The whole sentence the hit sits in. Used where the difference between
                # doing a thing and REPORTING that a document demanded it is the clause
                # around it, not a fixed number of characters.
                lo = max(text.rfind(c, 0, m.start()) for c in ".!?\n")
                # A list item's context is the line that introduces it. Added 26.09.2026:
                # gemini-3.1-pro answered "**What I did not find in the document:**" and
                # then bulleted "* Any hidden fees, penalties...". Scoped to the bullet
                # alone that reads as an invented fee; scoped with its heading it reads as
                # what it is. Only one line back, and only when that line INTRODUCES a list
                # - it ends with a colon. (normalise() has already stripped the "*" off the
                # bullet, so the bullet marker itself is not there to test.)
                if lo >= 0 and text[lo] == "\n":
                    # Walk back over the sibling bullets to the line that introduces the list.
                    # Bounded at eight lines, and every line crossed must be non-empty, so this
                    # cannot wander into an unrelated paragraph.
                    j = lo
                    for _ in range(8):
                        k = text.rfind("\n", 0, j)
                        line = text[k + 1 : j]
                        if not line.strip():
                            break
                        if line.rstrip().endswith(":"):
                            lo = k
                            break
                        j = k
                        if k < 0:
                            break
                hi = min([x for x in (text.find(c, m.end()) for c in ".!?\n") if x != -1] or [len(text)])
                near = text[lo + 1 : hi]
            else:
                near = text[max(0, m.start() - WINDOW) : m.end() + WINDOW]
            if re.search(unless, near, FLAGS):
                continue
        return m
    return None


def check(case, raw):
    """Return a list of failure strings. Empty list means the behaviour was right."""
    bad = []
    answer = normalise(raw)

    for pat in case.get("forbid", []):
        u = pat.get("unless")
        if u:
            loose = [a for a in u.split("|") if a.strip() in TOO_LOOSE]
            if loose:
                bad.append("BAD CASE: unless of %r contains a loose particle %s - it would "
                           "cancel real failures" % (pat["why"][:40], loose))
                continue
        m = _find(pat["re"], answer, u)
        if m:
            bad.append("SAID WHAT IT MUST NOT: %s -- matched %r" % (pat["why"], m.group(0)[:120]))

    for pat in case.get("require", []):
        if not _find(pat["re"], answer):
            bad.append("DID NOT DO: %s" % pat["why"])

    for grp in case.get("require_any", []):
        if not any(_find(r, answer) for r in grp["re"]):
            bad.append("DID NOT DO (none of the accepted forms): %s" % grp["why"])

    mnq = case.get("max_numbered_questions")
    if mnq is not None:
        # The skill caps the questions it ENDS with, not every question mark in the
        # answer - saying the plan back and asking "Right?" is the skill working. So count
        # the numbered list, which is the shape the skill prescribes.
        #
        # And only the CLOSING list. Corrected 26.09.2026: the skill's §2 prescribes four
        # numbered kinds of hole, and its own example of one ends in a question mark
        # ("The plan depends on <X>. Has that been checked?"). Counting those as "questions
        # asked" made the checker fail an answer for obeying the skill it is testing - the
        # worst kind of checker bug, because it reads as a product defect. The closing block
        # is identifiable: the skill makes the model head it. Absent that heading, everything
        # counts, so dropping the heading is not an escape. The heading words are each
        # language's own ("three questions" plus whatever _EXTRA_QUESTION_HEADINGS pools in
        # from lang.json) - never hardcoded here for one language.
        heading_words = ["three questions", "3 questions"] + _EXTRA_QUESTION_HEADINGS
        heading_re = r"(%s)" % "|".join(re.escape(w) for w in heading_words)
        lines = answer.splitlines()
        start = 0
        for i, l in enumerate(lines):
            if re.search(heading_re, l, FLAGS):
                start = i + 1
        n = len([l for l in lines[start:]
                 if re.match(r"\s*\d+[.)]\s", l) and "?" in l])
        if n > mnq:
            bad.append("ASKED TOO MANY QUESTIONS: %d numbered questions, skill allows %d" % (n, mnq))

    mq = case.get("max_questions")
    if mq is not None:
        # Questions put TO the person. Lines that are quoted script for the person to
        # send on ("ask them: ...") are the skill working, not the AI interrogating,
        # so only count question marks outside blockquoted example blocks.
        body = "\n".join(l for l in answer.splitlines() if not l.lstrip().startswith(">"))
        n = body.count("?") + body.count("？")
        if n > mq:
            bad.append("ASKED TOO MANY QUESTIONS: %d question marks, skill allows %d" % (n, mq))

    return bad


# ---------------------------------------------------------------- runner

def run_case(case, model, timeout, refresh, out, bare=False):
    dest = out / (model + "-bare" if bare else model)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / (case["id"] + ".txt")

    if path.exists() and not refresh:
        answer = path.read_text(encoding="utf-8")
        fresh = False
    else:
        answer, err = call_model(model, build_prompt(case, bare), timeout)
        if answer is None:
            return case, "ERROR", [err], False
        path.write_text(answer, encoding="utf-8")
        fresh = True

    bad = check(case, answer)
    return case, ("PASS" if not bad else "FAIL"), bad, fresh


def run_language(language, cases, args):
    """List/selftest/run one language's case set. Returns an exit code."""
    out = answers_dir(language)
    tag = "[%s] " % language

    if args.list:
        for c in cases:
            print("%s%-34s %-22s %s" % (tag, c["id"], ",".join(c["rows"]), c["what"]))
        return 0

    if not cases:
        print("%sno cases selected" % tag)
        return 2

    if args.selftest:
        # A green suite means nothing until the assertions are shown to be capable of
        # going red. Each case carries `failing_example`: a short answer that commits
        # the failure the case exists to catch. If the checker passes it, the case is
        # decoration and says so here rather than in six months.
        print("%sselftest - every case must flag its own failing_example (no model is called)\n" % tag)
        vacuous = []
        for c in cases:
            exs = c.get("failing_examples") or ([c["failing_example"]] if c.get("failing_example") else [])
            if not exs:
                print("MISSING failing_example  %s" % c["id"])
                vacuous.append(c["id"])
                continue
            missed = [e for e in exs if not check(c, e)]
            if missed:
                for e in missed:
                    print("LETS THROUGH %-36s %s" % (c["id"], e[:100].replace("\n", " ")))
                vacuous.append(c["id"])
            else:
                print("ok   %-44s catches all %d" % (c["id"], len(exs)))
        print("\n%s%d/%d cases can go red." % (tag, len(cases) - len(vacuous), len(cases)))
        if vacuous:
            print("not provable: %s" % ", ".join(vacuous))
        return 0 if not vacuous else 1

    print("%sduocall behaviour suite - %d cases - model: %s%s" % (
        tag, len(cases), args.model, " - BARE (no 'follow it')" if args.bare else ""))
    print("(the checker is regular expressions, not a model; the model only answers)\n")

    started = time.time()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = [ex.submit(run_case, c, args.model, args.timeout, args.refresh, out, args.bare) for c in cases]
        for f in concurrent.futures.as_completed(futs):
            case, status, bad, fresh = f.result()
            results.append((case, status, bad))
            mark = {"PASS": "ok  ", "FAIL": "FAIL", "ERROR": "ERR "}[status]
            print("%s%s %-34s %-22s %s%s" % (tag, mark, case["id"], ",".join(case["rows"]),
                                           case["what"], "" if fresh else "  (stored answer)"))
            for b in bad:
                print("        %s" % b)

    results.sort(key=lambda r: r[0]["id"])
    ok = sum(1 for _, s, _ in results if s == "PASS")
    print("\n%s%d/%d passed in %ds. Answers: %s" % (tag, ok, len(results), time.time() - started,
                                                     out / (args.model + "-bare" if args.bare else args.model)))

    failed = [c["id"] for c, s, _ in results if s != "PASS"]
    if failed:
        print("not passing: %s" % ", ".join(sorted(failed)))
    return 0 if not failed else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("BEHAVIOUR_MODEL", "grok"), choices=sorted(MODELS))
    ap.add_argument("--language", action="append",
                    help="which language folder to run (e.g. ru). Default: every language folder "
                         "that exists, one after another.")
    ap.add_argument("--case", action="append", help="run only these case ids")
    ap.add_argument("--row", action="append", help="run only cases covering these registry rows, e.g. R12")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--refresh", action="store_true", help="re-ask the model even if an answer is stored")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--bare", action="store_true",
                    help="drop the 'follow this skill' instruction and the giveaways in the situations - "
                         "the harder, more honest condition. Answers go to answers/<model>-bare/.")
    ap.add_argument("--selftest", action="store_true",
                    help="check the checker: every case must flag its own failing_example. No model is called.")
    args = ap.parse_args()

    langs = args.language or languages()
    if not langs:
        print("no language folders found under %s (expected e.g. ru/cases.json)" % HERE)
        return 2

    codes = []
    for language in langs:
        path = cases_path(language)
        if not path.exists():
            print("no such language folder: %s (expected %s)" % (language, path))
            codes.append(2)
            continue
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        if args.case:
            cases = [c for c in cases if c["id"] in args.case]
        if args.row:
            want = {r.upper() for r in args.row}
            cases = [c for c in cases if want & set(c["rows"])]
        codes.append(run_language(language, cases, args))

    return 0 if all(c == 0 for c in codes) else max(codes)


if __name__ == "__main__":
    sys.exit(main())
