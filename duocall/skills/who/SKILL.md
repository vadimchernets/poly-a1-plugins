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

## 1. The three states, named

> **Отвечали:** я (Claude) и ChatGPT — двое, из двух разных компаний.
> **Не ответил:** никто.
> **Не спрашивали:** Gemini — его на этом компьютере нет.

A program that timed out, ran out of allowance or failed is **«не ответил»**, never silently
dropped. A person who thinks three AIs checked something when one did is worse off than a person
who asked nobody.

## 2. Say how many companies, not how many answers

Two answers from the same company are one opinion. So the count that matters is families:

> Это два мнения от двух разных компаний.

or

> Это одно мнение. Второй компании тут не было.

Use `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/second.py" list` if you need to check what is on the
machine rather than remember it.

## 3. What this line is not

It is **not** a guarantee that the answer is right, and it must never be written so that it reads
like one. It says who was in the room. Whether they were right is the comparison's job, and often
nobody's.

If the person treats "два ИИ проверили" as a verdict, correct it once, gently:

> Два ИИ посмотрели — это не то же самое, что «проверено». Проверить можно только по бумаге или у
> того, кто отвечает за ответ.

## If `python3` is not on this machine

On Windows it often is not. Try `py -3`, then `python`. If none runs, do not stop and do not show a
Python error: fall back to the browser path — hand the person the block to paste into a free chat
of another company, which needs no program at all.
