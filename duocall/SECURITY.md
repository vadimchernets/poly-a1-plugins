# Security

## What Duocall touches

- It runs an AI program that is **already installed and already signed in** on this computer, and
  sends it the question the person asked. Nothing else.
- It never reads, copies, stores or forwards any credential, token or configuration of those
  programs. It calls them the way a person would from their own terminal.
- It writes no files and keeps no history of its own.

## Deliberate refusals

- **Never a second opinion from the same company.** Claude is not in the list of programs it will
  call, because Claude is the one asking. Same-vendor "diversity" is a lie told to a person who is
  about to act on it.
- **Never installs, signs in, or buys.** A program that is missing stays missing and the person is
  pointed at a free browser chat. A program out of allowance is reported as out of allowance, with
  the plain statement that it returns by itself and that nothing needs paying for.
- **The question goes out unchanged.** Claude's own answer is never attached to it — an AI shown
  somebody else's answer tends to agree with it, which destroys the only thing a second opinion is
  for.
- **A timeout is 180 seconds** (`DUOCALL_TIMEOUT`), after which the seat is reported as not having
  answered rather than waited on forever.

## What the person should know

The question — and any document text in it — goes to a second company as well as the first. That is
the point of a second opinion, and it doubles who has seen it. `/duocall:ask` says so before it
sends anything. For a document the person would not show a stranger, one opinion is the safer
choice, and the skill says that too.

## Reporting a problem

Write to polyhelper.ai@gmail.com with `duocall` in the subject.
