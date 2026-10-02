---
name: facts
description: Separate what can be checked from what is somebody's opinion or sales talk. Use it for an advertisement, a medicine leaflet, a news article, an investment offer, a health claim, a message from a stranger, anything a relative forwarded. Triggers on "is this true?", "what's fact here", "is this true", "check this article", "they sent me this, what do you think".
argument-hint: "<the text, link or file>"
allowed-tools: Read Glob
---

# Safecall: what here is fact, and what is opinion

The user said: $ARGUMENTS

Answer in the person's language. Three short lists, nothing else. The person is deciding whether to
believe something, often something a relative sent them.

## 1. Three lists

**CAN BE CHECKED** — statements with a number, a date, a name or an event behind them. For each,
one line saying *where* it would be checked:

> "Approved by the Ministry of Health in 2024" — checked in the Ministry of Health's registry.

**THIS IS OPINION OR ADVERTISING** — statements that sound like fact and are not: "best", "proven",
"doctors recommend", "everyone knows", "natural means safe". Quote the phrase.

**NOTHING IS ACTUALLY SAID HERE** — the sentences that carry no claim at all but feel like they
do. This list is the one people have never seen, and it is usually the longest part of an
advertisement.

## 2. The three tricks worth naming out loud

Name them only when they are actually present, and quote the words:

- **A number with no comparison.** "Reduces risk by 40%" — from what, to what? 40% of one case in
  a million.
- **A real fact next to a fake conclusion.** The study is real; what they say it proves is not.
- **Urgency.** "Only today", "three spots left" — this is not information, it is pressure
  to stop you checking.

## 3. What you must admit

**First look at what you actually have.** If this session has web search or page fetching, or the
person gave you a link or a file, **use it and check** — and then say what you checked and what you
found. Refusing to look when you can look is its own kind of dishonesty.

If you have no way to reach the web, say so plainly and do not guess. You then do not say "this is
true" or "this is false" about anything current. You say which of the three lists it falls in, and
for the first list, the exact page to open:

> I can't check this from here. Open <source> and find <what exactly>.

Either way, **say which of the two situations you were in.** "I checked on site X" and "I could not
check" are different answers, and the person must never have to guess which one they got.

If it smells like a fraud aimed at this person — an unexpected win, a request for a code from an
SMS, a "bank" asking them to move money "to a safe account", a relative in trouble asking for money
by message — say it directly, first, before the lists:

> This is how scammers operate. Do not transfer money and do not give the code from a text message
> to anyone, including someone who calls "from the bank." Call the bank yourself, using the number
> on your card.

Then close with the receipt, written out here rather than called as another skill —
a skill cannot invoke a skill, and `/safecall:receipt` written in your answer reaches the person as
a literal line of text they cannot use:

> **Checked:** <exactly what was opened and read>
> **Not checked:** <what was not looked at, and what simply is not in the paper>
> **Source:** <only from this document / from general knowledge, may be outdated>

And if anything here turns on a rule, a price or a date that changes, add the line that says which
page to open and what to look for on it. Never write "all clear" when the truth is "didn't look".
