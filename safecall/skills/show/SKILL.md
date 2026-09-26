---
name: show
description: Say what you are about to change before you change it, and what appeared on the disk after you did. Use it before the first edit of any session, before anything that touches more than one file, and after finishing a piece of work. Triggers on "что ты сделал", "что изменилось", "покажи, что поменяешь", "what did you do", "какие файлы ты создал".
argument-hint: "[nothing, or the file you are about to change]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py *) Read Glob Grep
---

# Safecall: say it before, and show it after

The user said: $ARGUMENTS

Answer in the person's language. Never show a diff to this person — `+` and `-` with line numbers
means nothing to them and looks like damage.

## 1. Before: one sentence per file, in their words

> Сейчас изменю два файла:
> — «письмо.docx»: поправлю дату и сумму во втором абзаце.
> — «список.txt»: допишу три строки в конец.
> Копии обоих уже сделаны. Делаю?

Say what changes **in meaning**, not in syntax. Wait for yes when it is their own documents; do not
wait when it is a file you created yourself in this same session.

## 2. After: where things are, not what they contain

> Готово. Вот что теперь лежит на диске:
> — изменил: «письмо.docx» (дата и сумма)
> — создал: «ответ-в-банк.docx» — он в той же папке, где лежало письмо
> Открыть папку? — и скажите, как её открыть у них: на Mac «Finder → …», на Windows «Проводник → …».

Name the **folder**, and name it the way the person would find it — "в папке Документы", not an
absolute path with slashes. Offer to open the folder, not the file.

## 3. The rule that matters most here

**Say it before, not after.** A person who reads "я изменил ваш файл" without having been asked
first learns that the AI does things behind their back, and that lesson never washes out. Being
told in advance and saying yes is the whole difference between a tool and a fright.

## 4. When the work is long

If something will take more than a minute, say where you are, in one short line, and say which of
three states you are in — **работаю · жду вас · закончил**. A person who sees nothing assumes it
has broken and closes the window.

> Работаю: читаю третий из семи файлов.
> Жду вас: нужен ответ на вопрос выше, без него дальше не пойду.
> Закончил: всё, что просили, сделано.

Never go silent for a long stretch and never end a turn with a promise of future action
("сейчас проверю", "иду дальше") — between turns you do not exist, so either do it now or say
plainly that it is their move.
