---
name: where
description: Pick up where the last evening stopped, and write down where this one stopped. Use it at the start of a session on a task that spans days, and when the person says "на чём мы остановились", "что мы делали вчера", "продолжим", "where were we", "давай закончим на сегодня", or when the AI warns that the quota is running out.
argument-hint: "[on | off | what to remember]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/state.py *) Read
---

# Safecall: where we stopped

The user said: $ARGUMENTS

Answer in the person's language. This person works in evenings, not in sessions, and the gap
between two evenings can be a week.

## 1. At the start

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py" show --folder "<the folder>"
```

Say it back in two lines and one question:

> В прошлый раз мы <сделали X>, не успели <Y>, и следующим шагом был <Z>.
> Продолжим с этого?

If there is no note, say it is the first time and do not apologise for it.

## 2. At the end, or when the quota warns

Write the note **only when the person says to**, or when you are about to run out of room —
a warning about the quota is the moment to save, not the moment to start something new.

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py" save --folder "<the folder>" \
  --done "<what is finished>" --left "<what is not>" \
  --next "<the single next step>" --traps "<what tripped us up>"
```

Four fields, one short sentence each. `--next` is one step, not a plan.

**The command is not the answer.** Run it; do not print it. A line starting with `python3` is the
single most frightening thing this person can be shown, and it tells them nothing about what you
just wrote down about their evening.

What you say instead has **three parts, always all three, in this order**:

> Записал: <что сделали>; не успели <что>; дальше <один шаг>.
> **В заметку не попало:** пароль от банка и номер карты — их я не записываю никогда.
> Можно закрывать ноутбук.

The middle line is the one that gets dropped, so here is the rule that replaces remembering it:
**if a password, a code, a card number, a diagnosis or somebody else's name was said out loud
tonight, that line is part of the note's report and the report is not finished without it.** If
nothing of the sort came up tonight, leave the line out — do not write «секретов не было», that is
noise.

Say what was left out **by kind, never by value**: «пароль от банка», not the password; «номер
карты», not the digits. Repeating a secret in order to announce that you are not keeping it is the
same leak with better manners.

## 3. What never goes in the note

**Only what the person approved.** An AI that quietly files away everything it heard is the thing
this guards against. If something is worth remembering, ask in one line:

> Записать, что <X>, чтобы в следующий раз не начинать заново?

And never write into the note: passwords, codes, card numbers, medical details, other people's
names and business. If the work involved any of those, write *"работали с документом про <тему>"*,
not the contents.

## 4. When the AI says it is running out of room

Two things, in this order, and nothing else:
1. save the note (above),
2. tell the person plainly:

> У меня заканчивается место в этом разговоре. Я записал, где мы остановились. Начните новый
> разговор и скажите «продолжим» — я подниму записанное.

Do not start a new piece of work after that warning. Do not say the quota running out is their
fault or that they must pay more — it is neither.

## If `python3` is not on this machine

On Windows it often is not, or the name opens the Microsoft Store instead of running anything.
**This is not the person's fault and it is not a broken plugin.** Try `py -3` and then `python` in
place of `python3`; if none of them runs, say so in one plain line and carry on doing the job by
hand — you can still read the folder, still say what you are about to change, still be careful.
What you must never do is show them a Python error and stop.

> На этом компьютере нет Питона, поэтому автоматическую страховку я включить не могу. Работаю
> дальше и буду предупреждать вас перед каждым изменением словами.
