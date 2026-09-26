---
name: who
description: Say plainly which AIs answered, which did not, and which were never there - so the person knows how many opinions they actually got. Use it at the end of anything involving a second AI, and whenever they ask "кто отвечал", "это оба сказали?", "who said that", "сколько ИИ проверило".
argument-hint: "[nothing]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/second.py *) Read
---

# Duocall: who actually answered

The user said: $ARGUMENTS

Answer in the person's language. Three lines at most. This is the thing V1 guarantees in place of
"a better answer" (`V1/README.md:58-62`): not that the group was right, but that you can always see
what happened.

## 1. Four lines. Always four, always these, always in this order

This is a **form, not a suggestion**. Fill every line even when the answer is «никто» — an empty
line is information, and the line that gets dropped is always the one that mattered.

> **Отвечали:** я (Claude) и ChatGPT.
> **Не ответил:** никто.
> **Не спрашивали:** Gemini — его на этом компьютере нет.
> **Итого:** два мнения, из двух разных компаний.

And the same form when it went badly — note that nothing is omitted, only filled differently:

> **Отвечали:** только я (Claude).
> **Не ответил:** ChatGPT — у него на сегодня кончился запас, он вернётся через несколько часов.
> **Не спрашивали:** никого больше на этом компьютере нет.
> **Итого:** одно мнение, одна компания. Не два.

A program that timed out, ran out of allowance or failed is **«не ответил»**, never silently
dropped. A person who thinks three AIs checked something when one did is worse off than a person
who asked nobody. Leaving it out of the list is how «не ответил» becomes «не было» in the person's
memory by tomorrow.

## 2. The «Итого» line counts companies, not answers

Two answers from the same company are one opinion — including **your own two answers**: thinking
again is not a second opinion, it is the same opinion with more words. So the number on the «Итого»
line is families, and the word «компани…» is in it:

> **Итого:** два мнения, из двух разных компаний.
> **Итого:** одно мнение, одна компания. Не два.

Never write «Итого: два ответа» and leave the person to work out that both were yours.

Use `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/second.py" list` if you need to check what is on the
machine rather than remember it.

## 3. What this line is not

It is **not** a guarantee that the answer is right, and it must never be written so that it reads
like one. It says who was in the room. Whether they were right is the comparison's job, and often
nobody's.

If the person treats "два ИИ проверили" as a verdict, correct it once, gently:

> Два ИИ посмотрели — это не то же самое, что «проверено». Проверить можно только по бумаге или у
> того, кто отвечает за ответ.

**Only say this when two actually answered.** If the pair did not happen, this sentence is worse
than useless: the person reads past the correction and keeps the words «два ИИ посмотрели». When
only you answered, the line is:

> Смотрел один я. Это не «проверено» — проверить можно только по бумаге или у того, кто отвечает
> за ответ.

**This line goes *after* the four lines of §1 — it never stands in their place.** On its own it
reads like a complete answer and is not one: it does not say who was asked, it does not say that
ChatGPT ran out of allowance, and the person walks away thinking the second AI was never there
rather than that it is coming back in four hours. Form first, then this.

## If `python3` is not on this machine

On Windows it often is not. Try `py -3`, then `python`. If none runs, do not stop and do not show a
Python error: fall back to the browser path — hand the person the block to paste into a free chat
of another company, which needs no program at all.
