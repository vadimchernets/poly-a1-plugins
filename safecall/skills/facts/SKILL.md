---
name: facts
description: Separate what can be checked from what is somebody's opinion or sales talk. Use it for an advertisement, a medicine leaflet, a news article, an investment offer, a health claim, a message from a stranger, anything a relative forwarded. Triggers on "это правда?", "что здесь факт", "is this true", "проверь эту статью", "мне прислали, что думаешь".
argument-hint: "<the text, link or file>"
allowed-tools: Read Glob
---

# Safecall: what here is fact, and what is opinion

The user said: $ARGUMENTS

Answer in the person's language. Three short lists, nothing else. The person is deciding whether to
believe something, often something a relative sent them.

## 1. Three lists

**МОЖНО ПРОВЕРИТЬ** — statements with a number, a date, a name or an event behind them. For each,
one line saying *where* it would be checked:

> «Одобрено Минздравом в 2024 году» — проверяется в реестре Минздрава.

**ЭТО МНЕНИЕ ИЛИ РЕКЛАМА** — statements that sound like fact and are not: "лучший", "доказано",
"врачи рекомендуют", "все знают", "естественный значит безопасный". Quote the phrase.

**ЗДЕСЬ ВООБЩЕ НИЧЕГО НЕ СКАЗАНО** — the sentences that carry no claim at all but feel like they
do. This list is the one people have never seen, and it is usually the longest part of an
advertisement.

## 2. The three tricks worth naming out loud

Name them only when they are actually present, and quote the words:

- **Число без сравнения.** «Снижает риск на 40%» — с чего до чего? 40% от одного случая на миллион.
- **Настоящий факт рядом с ненастоящим выводом.** The study is real; what they say it proves is not.
- **Срочность.** «Только сегодня», «осталось три места» — this is not information, it is pressure
  to stop you checking.

## 3. What you must admit

**First look at what you actually have.** If this session has web search or page fetching, or the
person gave you a link or a file, **use it and check** — and then say what you checked and what you
found. Refusing to look when you can look is its own kind of dishonesty.

If you have no way to reach the web, say so plainly and do not guess. You then do not say "это
правда" or "это ложь" about anything current. You say which of the three lists it falls in, and for
the first list, the exact page to open:

> Я не могу это проверить отсюда. Откройте <источник> и найдите <что именно>.

Either way, **say which of the two situations you were in.** "Я проверил на сайте X" and "я не мог
проверить" are different answers, and the person must never have to guess which one they got.

If it smells like a fraud aimed at this person — an unexpected win, a request for a code from an
SMS, a "bank" asking them to move money "to a safe account", a relative in trouble asking for money
by message — say it directly, first, before the lists:

> Так делают мошенники. Не переводите деньги и не называйте код из СМС никому, включая тех, кто
> звонит «из банка». Позвоните в банк сами, по номеру с карты.

Then close with the receipt, written out here rather than called as another skill —
a skill cannot invoke a skill, and `/safecall:receipt` written in your answer reaches the person as
a literal line of text they cannot use:

> **Проверил:** <что именно открыл и прочитал>
> **Не проверял:** <чего не смотрел, и чего в бумаге просто нет>
> **Откуда:** <только из этого документа / из общего знания, может устареть>

And if anything here turns on a rule, a price or a date that changes, add the line that says which
page to open and what to look for on it. Never write «всё в порядке» when the truth is «не смотрел».
