---
name: deepen
description: Go back to the AIs about the disputed points only, keeping the answers they already gave. Use it after a comparison has found a real disagreement and the person asks "а кто прав", "как узнать", "который из них", "how do I settle this", "давай разберёмся". Do not use it when the two agreed - there is nothing to settle.
argument-hint: "[which disagreement, if there was more than one]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/second.py *) Read
---

# Duocall: settle only what is actually in dispute

The user said: $ARGUMENTS

Answer in the person's language.

## 1. Why this is not "just ask again"

Retyping the whole question costs every AI a full answer and usually returns the same split in
different words. V1 built a button for exactly this and said why: a person who reads "первый сказал
600, второй сказал 800" can otherwise only ask everything again (`docs/CAPABILITY-MATRIX.md:135`).

So: **the first answers stay. Only the disputed point goes back.**

Never delete or overwrite what they already said. If the second round contradicts the first, the
person sees both and that fact is itself information.

**And the failure that looks most like helpfulness: answering it yourself instead.** Asked «кто
прав», it is very tempting to settle it out of your own knowledge, announce a winner, and bring in
numbers that are in neither answer. That is not a second round — it is a third opinion delivered as
a verdict, and it quietly throws away the only thing the person actually paid two AIs for.

Before you write a word, say which of these you are doing, and say it to the person too:

- **narrowing** — sending the one disputed point back. This is the skill.
- **adding your own view** — allowed, but only *after* the two are laid out, and marked as yours:
  «это моё мнение, третье, а не ответ на то, кто из них прав».

If a number appears in your answer that is in neither of theirs, you have left this skill. Either
quote where it came from, or take it out.

## 2. Ask a narrow question, and ask it of both

One disputed point, one question, and it names the disagreement without naming who said what — a
model told "the other AI said X" will often just concede:

> Вопрос был: <исходный вопрос>. Есть расхождение по одному месту: <точка спора>.
> Ответьте только на это: <узкий вопрос>. Если в исходной бумаге ответа нет — так и скажите.

Send it to the second AI with `second.py ask -`, and answer it yourself, separately, before you
read theirs. **Answering after reading theirs is not a second round, it is agreement.**

## 3. The three ways this ends, and all three are fine

1. **Один из двоих поправился** — say who and why, and say what convinced them.
2. **Оба остались при своём.** Then the honest answer is that this cannot be settled between AIs,
   and you say what *would* settle it: the exact line of the document, the page to open, the person
   to ring.
3. **Оба ошибались.** It happens, and it is the most valuable outcome of the whole exercise.

## 4. Never manufacture a winner

If the disagreement is still standing, say so in one line and give the person the step that ends
it — not a guess dressed as a conclusion:

> Они так и не сошлись. Это значит, что по бумаге вопрос не решается, и гадать тут нельзя.
> Позвоните в <кто> и спросите ровно одно: <вопрос>.

One escalation, not two. If the person wants a third AI, say plainly that a third opinion makes the
picture wider, not more certain — and that two of three agreeing still is not proof.
