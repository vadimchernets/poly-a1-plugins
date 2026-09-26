---
name: ask
description: Put the same question to an AI from a DIFFERENT company and bring back its answer word for word. Use it when the person says "спроси второй ИИ", "пусть кто-то ещё проверит", "ask another AI", "second opinion", "а другой что скажет" - and offer it yourself, once, when the stakes are real: money, health, a contract, a deadline, or a decision they cannot take back. Do not use it for ordinary questions; a second opinion on every sentence is noise.
argument-hint: "<the question, or nothing to reuse the last one>"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/second.py *) Read
---

# Duocall: ask the second AI

The user said: $ARGUMENTS

Answer in the person's language.

## 1. The rule you may not bend

**A second opinion has to come from a DIFFERENT company.** Two answers from the same company are
one opinion wearing two hats. If the only AI here is the one already answering — you — then there
is no pair, and you say so instead of inventing one.

## 2. Find out what is actually on this machine

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/second.py" list
```

**If a program is there**, say who it is in the person's words and what it will cost them — not
money, but their own monthly allowance with that company:

> У вас на компьютере есть ChatGPT. Спрошу его тем же вопросом. Это израсходует немного вашего
> месячного запаса у них — второй подписки не нужно.

Then ask it. Send the question **unchanged** — not your summary of it, and not your answer attached:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/second.py" ask -
```

and give it the question on standard input. Never paste your own answer into the question: an AI
shown somebody else's answer agrees with it. That is the whole reason this is worth doing.

**If there is no second program**, that is not a failure and you do not apologise. Say it plainly
and hand them the block to paste into a free chat in their browser:

> Второй программы на компьютере нет, и это не помеха: откройте в браузере любой бесплатный чат
> другой компании и вставьте туда вот это. Потом пришлите мне, что он ответит.
>
> ---
> <the question, exactly as they asked it, and nothing else>
> ---

Nothing else in the block. No "please analyse", no mention of Claude, no instructions — those
change the answer, and a changed answer is not a second opinion.

**Including the person's own framing.** They said «спроси второй ИИ, пусть он тоже посмотрит: …» —
the block gets what comes after the colon, not the sentence that was addressed to *you*. Anything
telling the other AI that it is second, or checking somebody, or confirming an answer, tilts it.
Read the block back to yourself before you hand it over: if it contains a single word that would not
have been there had the person asked this question first and of nobody else, take that word out.

## 3. Bring it back whole

Show the second answer **as it came**, marked as theirs:

> **ChatGPT ответил:**
> <their answer, unedited>

Do not fix it, do not shorten it, do not tidy its tone. If it is wrong, that belongs in the
comparison, not in a quiet edit.

## 4. If it did not answer

The script says why, and the commonest reason is the allowance running out. Say it without blame:

> ChatGPT сейчас не ответил — у него кончился месячный запас. Это не поломка и платить за это не
> надо: запас вернётся сам. Второе мнение можно взять в браузере, бесплатно.

Never hide a failed second opinion and never quietly answer twice yourself and call it a pair.
**A pair that did not happen is said out loud.**

## If `python3` is not on this machine

On Windows it often is not. Try `py -3`, then `python`. If none runs, do not stop and do not show a
Python error: fall back to the browser path — hand the person the block to paste into a free chat
of another company, which needs no program at all.
