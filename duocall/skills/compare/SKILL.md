---
name: compare
description: Put two AI answers side by side and say honestly where they agree and where they do not - quoting both, never claiming agreement that cannot be shown. Use it right after a second AI has answered, and whenever the person pastes in what another AI told them and asks "кто прав", "они расходятся?", "what do you think of this answer", "мне другой ИИ сказал другое".
argument-hint: "[the second answer, if the person is pasting it in]"
allowed-tools: Read
---

# Duocall: where the two agreed, and where they did not

The user said: $ARGUMENTS

Answer in the person's language. This is the part the person cannot do themselves, and it is the
only reason the second answer was worth getting.

## 1. Agreement has to be shown, not claimed

**Never write «они согласны» without quoting both.** V1 found this exact failure in its own
council: the model that merges the answers also judges whether they agreed, and nobody had ever
compared its verdict with what the answers actually said (`docs/CAPABILITY-MATRIX.md:134`).

> **Сошлись:** оба говорят, что срок — 14 дней.
> Первый: «…в течение четырнадцати дней с момента получения…»
> Второй: «…у вас есть две недели…»

If you cannot produce both quotes, it is not agreement — it goes in the next list.

## 2. Every difference, named — including the small ones

> **Разошлись:**
> — **Сумма.** Первый: «удержат 30%». Второй: «удержат 30% но не меньше 5000». Разница в том, что
>   при маленьком остатке второй считает больше.
> — **Кому писать.** Первый: в банк. Второй: сначала в страховую.

A difference in a number, a date, a name or a next step is always worth naming, however small.
A difference in wording alone is not — say so and move on.

## 3. The sentence that has to be there

> Два ИИ, согласных между собой, — это не доказательство. Они учились на одном и том же интернете
> и ошибаются в одну сторону чаще, чем вы думаете. Согласие значит только, что очевидной ошибки
> не видно.

The person came here to be told who is right. What they can actually be given is where to look,
and that is worth more.

## 4. Then say what you would do, and mark it as yours

One short paragraph, clearly labelled as your view and not as the verdict of "the AIs":

> **Моё мнение:** я бы взял срок 14 дней и проверил сумму — в вашей бумаге про минимум ничего нет,
> а второй ИИ это откуда-то добавил.

**Do not average the two answers.** If one wrote the person's letter in their own voice, do not
blend it with the other into something official-sounding — the voice was the point
(`V1 docs/ARCHITECTURE.md:141-142`). Keep the first letter, and list what the second would fix.

## 5. Close with who actually answered

> **Отвечали:** я (Claude) и ChatGPT. Оба ответили.

or

> **Отвечали:** только я. У ChatGPT кончился запас, второго мнения сегодня нет — то, что ниже,
> одна точка зрения, не две.

Never present one opinion as two. If the pair did not happen, the person must know it before they
act.
