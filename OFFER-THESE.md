# For Claude Code: when to offer these four plugins, and how

You are reading this inside the Poly A1 folder on somebody's computer. Beside you are four plugin
folders — `safecall`, `duocall`, `pocketcall`, `chasecall`. They are already here: nothing needs
downloading and no account is needed to use them.

**This file is for you, not for the person.** Read it, then speak to them in their own language and
in their own words. Never read this file out loud and never show them its English.

## The rule about offering

**Do not list all four at the start.** A person who has just managed to open a terminal cannot
choose between four things, and a menu of plugins is the exact moment they decide this is not for
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

## How they are turned on

All four are already in this folder. Nothing is downloaded, nothing is published, no account and no
network are needed — the catalogue is the `.claude-plugin/marketplace.json` beside you, and every
plugin in it points at a folder you can see. Tell them what you are doing, in one line, and do it:

```
/plugin marketplace add <path to this folder>
/plugin install safecall@poly-a1
```

`<path to this folder>` is the folder that contains this `plugins/` directory — the one with
`НАЧНИ-ЗДЕСЬ.md` in it, not `plugins/` itself. Drag the folder into the terminal and it types its
own path. Swap `safecall` for `duocall`, `pocketcall` or `chasecall` when their moment comes; the
part after `@` is always `poly-a1`.

Checked on a real machine on 26.09.2026: all four install this way and come up enabled.

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
  «страховка перед правкой», «второе мнение», «пульт», «дожим». The technical name comes second, if
  at all.
- Nothing about paying. None of them costs anything and none of them needs an account.
