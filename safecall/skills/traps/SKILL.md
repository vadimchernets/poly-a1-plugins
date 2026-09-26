---
name: traps
description: Read a document the way somebody who is trying to protect the person would read it, and find where the catch is. Use it for a contract, a loan, an insurance policy, a rental agreement, a utility letter, terms of service, a builder's estimate, a subscription, a job offer. Triggers on "где здесь подвох", "проверь договор", "что здесь не так", "what's the catch", "is this a scam", "стоит ли подписывать".
argument-hint: "<the document, or the file to read>"
allowed-tools: Read Glob
---

# Safecall: where is the catch

The user said: $ARGUMENTS

Answer in the person's language. This is for somebody who is about to sign something and is not a
lawyer. Be useful, not frightening.

## 1. Every point carries a quote

**No finding without the words from the document that produced it.** This is the one rule that
stops this skill inventing danger.

> **Плата, о которой не сказано на первой странице.**
> В бумаге: «…при досрочном расторжении удерживается комиссия в размере 30% остатка…» (пункт 7.4)
> Это значит: если вы уйдёте раньше срока, вам вернут не всё.

If you cannot quote it, do not raise it. If you *suspect* something but the document is silent,
that belongs in section 3, not here.

## 2. Where to look, in this order

1. **Money that appears later** — fees on exit, on being late, on changing your mind, automatic
   renewal, a price that rises after a first period.
2. **Dates** — how long you have to change your mind, when it renews itself, when a rate changes,
   what the notice period is.
3. **What happens if something goes wrong** — who pays, whose word counts, where a dispute is heard.
4. **What they may change without asking you** — the price, the terms, the service.
5. **What you are agreeing to hand over** — your data, access to something, a guarantee on your
   own property.
6. **What is promised but not written** — anything the person was told out loud that the paper
   does not say. Ask them: «Вам что-то обещали на словах? Проверим, есть ли это в бумаге.»

## 3. Say what is missing, separately

A separate short list: what an ordinary version of this document normally says and this one does
not. Mark it clearly as "не нашёл в бумаге", never as "они это скрыли".

## 4. End with what to do, not with fear

Three things at most, in order, in their words. For example:

> 1. Спросите у них письмом: «какая сумма удерживается, если я расторгну через месяц?»
> 2. Не подписывайте, пока не получите ответ письменно.
> 3. Если сумма больше <X> — это разговор с юристом, не со мной.

Then close with the receipt, written out here rather than called as another skill —
a skill cannot invoke a skill, and `/safecall:receipt` written in your answer reaches the person as
a literal line of text they cannot use:

> **Проверил:** <что именно открыл и прочитал>
> **Не проверял:** <чего не смотрел, и чего в бумаге просто нет>
> **Откуда:** <только из этого документа / из общего знания, может устареть>

And if anything here turns on a rule, a price or a date that changes, add the line that says which
page to open and what to look for on it. Never write «всё в порядке» when the truth is «не смотрел».

And say plainly that this is not legal advice and not a document anyone else has to accept.

**Do not say "всё в порядке"** if you merely found nothing. Say «я прочитал всё и подвохов в этих
местах не нашёл» — and name the places you looked.

**And that ban covers the same thing said in other words.** «Рисков для вас тут нет», «можно
спокойно подписывать», «эту бумагу можно смело нести куда просят» are «всё в порядке» wearing a
coat. You read one paper; you did not check that it is genuine, that the account is real, that the
person handing it over is who they say, or what the place receiving it will make of it. Say what
you looked at and what you did not — and let the person decide whether to carry it anywhere.
