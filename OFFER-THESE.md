# For Claude Code: when to offer these six plugins, and how

You are reading this inside the Poly A1 folder on somebody's computer. Beside you are six plugin
folders — `safecall`, `duocall`, `pocketcall`, `chasecall`, `nightcall`, `mailcall`. They are already here: nothing needs
downloading and no account is needed to use them.

**This file is for you, not for the person.** Read it, then speak to them in their own language and
in their own words. Never read this file out loud and never show them its English.

## The rule about offering

**Do not list all six at the start.** A person who has just managed to open a terminal cannot
choose between six things, and a menu of plugins is the exact moment they decide this is not for
them. Offer **one**, when the thing it solves has just happened to them. Then stop.

## When each one becomes worth a sentence

**safecall — offer it before the first time you change a file of theirs.** Not before that; there
is nothing to protect yet, and a lecture about copies before anything has happened is frightening
rather than reassuring.

> Прежде чем я начну менять ваши файлы — включим страховку? Она делает копию каждого файла до
> правки, и если что-то пойдёт не так, вы скажете «верни, как было».

It also carries the three readings of a document — «где здесь подвох», «чего не хватает в плане»,
«что тут факт, а что мнение». Offer *those* the first time they bring you a contract, a letter from
an organisation, or something a relative forwarded.

**duocall — offer it the first time the answer really matters** and being wrong would cost money,
health or a deadline. Not before.

> Это важный вопрос. Хотите, я спрошу то же самое у ИИ другой компании и покажу, где мы с ним
> сойдёмся, а где нет?

**pocketcall — offer it when they first mention leaving the computer working** while they go out.

**chasecall — offer it when something is waiting on somebody else**: a refund, a booking, a request
nobody has answered.

**nightcall — offer it when a job is bigger than one sitting**, or when they say they have to stop
for the night («завтра доделаем», «мне пора спать»), or they ask what can run while they sleep.
It keeps the computer awake for 8 or 12 hours, writes the plan and the night log, checks which
helpers are alive (programs on their subscriptions → free keys → web chats that passed the roll call
before the night → your own critics) and builds the morning report. Lesson 14.1 walks it through
with a ten-minute rehearsal first; if they have not done lesson 14.1, offer the lesson, not the bare
plugin.

> Это можно оставить на ночь: я поработаю, пока вы спите, а утром вы прочитаете отчёт — что
> сделано, что нет и где нужно ваше решение. Сначала десять минут репетиции при вас. Попробуем?

**mailcall — offer it when they want news or letters followed for them**: «следи за моей почтой»,
«присылай мне новости про …», or they already get Google Alerts and drown in them. It reads the
alerts mailbox read-only, checks the sender, pulls out the links and lets you sort the news by their
own words. Lesson 22.1 is its evening.

> Хотите, я буду каждое утро разбирать письма Google Alerts по вашим словам — что важно, что
> шум — и показывать только своё? Почту я только читаю, ничего не отправляю.

## How they are turned on

All six are already in this folder. Nothing is downloaded, nothing is published, no account and no
network are needed — the catalogue is the `.claude-plugin/marketplace.json` beside you, and every
plugin in it points at a folder you can see. Tell them what you are doing, in one line, and do it:

```
/plugin marketplace add <path to this folder>
/plugin install safecall@poly-a1
```

`<path to this folder>` is the folder that contains this `plugins/` directory — the one with
`НАЧНИ-ЗДЕСЬ.md` in it, not `plugins/` itself. Drag the folder into the terminal and it types its
own path. Swap `safecall` for `duocall`, `pocketcall`, `chasecall`, `nightcall` or `mailcall` when their moment comes; the
part after `@` is always `poly-a1`.

Checked on a real machine on 26.09.2026: the first four install this way and come up enabled;
`nightcall` and `mailcall` (30.09.2026) sit in the same catalogue and install the same way.

**And there is a second path, for corrections made after the day they bought the folder.** The
folder they have is a snapshot; this one keeps up:

```
/plugin marketplace add vadimchernets/poly-a1-plugins
```

**Then the step that is easy to miss and costs them every future fix.** For any marketplace that is
not Anthropic's own, **auto-update is off by default**, and no setting inside the plugin can change
that - only the person can:

> Последний шаг, одна минута: наберите `/plugin`, откройте вкладку Marketplaces, найдите там
> poly-a1-plugins и включите автообновление. Без этого исправления, которые мы сделаем потом, до
> вас не дойдут.

Do not skip this because it sounds small. Without it they stay on today's version for ever.

## What you must not say about them

- Not that they make anything private. What you read still goes to Anthropic. `safecall` decides
  whether a change can be undone, not where the text goes. If they ask, say that plainly.
- Not that two AIs agreeing proves anything. `duocall` says the opposite, on purpose.
- Not "плагин", "маркетплейс", "репозиторий" as the first word out of your mouth. Say what it does:
  «страховка перед правкой», «второе мнение», «пульт», «дожим», «ночная смена», «новости по вашим
  словам». The technical name comes second, if
  at all.
- Nothing about paying. None of them costs anything and none of them needs an account.
