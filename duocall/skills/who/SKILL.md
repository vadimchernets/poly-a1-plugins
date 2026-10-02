---
name: who
description: Say plainly which AIs answered, which did not, and which were never there - so the person knows how many opinions they actually got. Use it at the end of anything involving a second AI, and whenever they ask "who answered", "did both say that?", "who said that", "how many AIs checked this".
argument-hint: "[nothing]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/second.py *) Read
---

# Duocall: who actually answered

The user said: $ARGUMENTS

Answer in the person's language. Three lines at most. This is the thing V1 guarantees in place of
"a better answer" (`V1/README.md:58-62`): not that the group was right, but that you can always see
what happened.

## 1. Four lines. Always four, always these, always in this order

This is a **form, not a suggestion**. Fill every line even when the answer is "nobody" — an empty
line is information, and the line that gets dropped is always the one that mattered.

> **Who answered:** me (Claude) and ChatGPT.
> **Did not answer:** nobody.
> **Not asked:** Gemini — it's not on this computer.
> **Total:** two opinions, from two different companies.

And the same form when it went badly — note that nothing is omitted, only filled differently:

> **Who answered:** only me (Claude).
> **Did not answer:** ChatGPT — it ran out of its allowance for today, it'll be back in a few hours.
> **Not asked:** nobody else is on this computer.
> **Total:** one opinion, one company. Not two.

A program that timed out, ran out of allowance or failed is **"did not answer"**, never silently
dropped. A person who thinks three AIs checked something when one did is worse off than a person
who asked nobody. Leaving it out of the list is how "did not answer" becomes "was never there" in
the person's memory by tomorrow.

## 2. The "Total" line counts companies, not answers

Two answers from the same company are one opinion — including **your own two answers**: thinking
again is not a second opinion, it is the same opinion with more words. So the number on the "Total"
line is families, and the word "compan..." is in it:

> **Total:** two opinions, from two different companies.
> **Total:** one opinion, one company. Not two.

Never write "Total: two answers" and leave the person to work out that both were yours.

Use `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/second.py" list` if you need to check what is on the
machine rather than remember it.

## 3. What this line is not

It is **not** a guarantee that the answer is right, and it must never be written so that it reads
like one. It says who was in the room. Whether they were right is the comparison's job, and often
nobody's.

If the person treats "two AIs checked it" as a verdict, correct it once, gently:

> Two AIs took a look — that's not the same as "verified." You can only verify against the document
> itself or with whoever is responsible for the answer.

**Only say this when two actually answered.** If the pair did not happen, this sentence is worse
than useless: the person reads past the correction and keeps the words "two AIs took a look." When
only you answered, the line is:

> Only I looked at this. That's not "verified" — you can only verify against the document itself or
> with whoever is responsible for the answer.

**This line goes *after* the four lines of §1 — it never stands in their place.** On its own it
reads like a complete answer and is not one: it does not say who was asked, it does not say that
ChatGPT ran out of allowance, and the person walks away thinking the second AI was never there
rather than that it is coming back in four hours. Form first, then this.

## If `python3` is not on this machine

On Windows it often is not. Try `py -3`, then `python`. If none runs, do not stop and do not show a
Python error: fall back to the browser path — hand the person the block to paste into a free chat
of another company, which needs no program at all.
