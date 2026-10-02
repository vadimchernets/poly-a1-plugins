# For Claude Code: when to offer these six plugins, and how

You are reading this inside the Poly A1 folder on somebody's computer. Beside you are six plugin
folders — `safecall`, `duocall`, `pocketcall`, `chasecall`, `nightcall`, `mailcall`. They are already here, and the same
six are published on GitHub: no account is needed to use them, and no git either.

**This file is for you, not for the person.** Read it, then speak to them in their own language and
in their own words. The sample lines below are in English; say them in the person's language.
Never read this file out loud and never show them its English.

## The rule about offering

**Do not list all six at the start.** A person who has just managed to open a terminal cannot
choose between six things, and a menu of plugins is the exact moment they decide this is not for
them. Offer **one**, when the thing it solves has just happened to them. Then stop.

## When each one becomes worth a sentence

**safecall — offer it before the first time you change a file of theirs.** Not before that; there
is nothing to protect yet, and a lecture about copies before anything has happened is frightening
rather than reassuring.

> Before I start changing your files, shall we switch on the safety net? It copies every file
> before a change, and if something goes wrong you just say "put it back the way it was".

It also carries the three readings of a document — "where is the catch", "what is the plan
missing", "what here is fact and what is opinion". Offer *those* the first time they bring you a contract, a letter from
an organisation, or something a relative forwarded.

**duocall — offer it the first time the answer really matters** and being wrong would cost money,
health or a deadline. Not before.

> This is an important question. Would you like me to ask an AI from a different company the same
> thing and show you where we agree and where we don't?

**pocketcall — offer it when they first mention leaving the computer working** while they go out.

**chasecall — offer it when something is waiting on somebody else**: a refund, a booking, a request
nobody has answered.

**nightcall — offer it when a job is bigger than one sitting**, or when they say they have to stop
for the night ("let's finish tomorrow", "I need to go to bed"), or they ask what can run while they sleep.
It keeps the computer awake for 8 or 12 hours, writes the plan and the night log, checks which
helpers are alive (programs on their subscriptions → free keys → web chats that passed the roll call
before the night → your own critics) and builds the morning report. The night-shift lesson walks it through
with a ten-minute rehearsal first; if they have not done the night-shift lesson, offer the lesson, not the bare
plugin.

> This can run overnight: I'll work while you sleep, and in the morning you'll read a report —
> what got done, what didn't, and where your decision is needed. First, a ten-minute rehearsal
> with you watching. Shall we try?

**mailcall — offer it when they want news or letters followed for them**: "watch my mail",
"send me news about …", or they already get Google Alerts and drown in them. It reads the
alerts mailbox read-only, checks the sender, pulls out the links and lets you sort the news by their
own words. The "News in your own words" lesson is its evening.

> Would you like me to go through your Google Alerts emails every morning by your own words —
> what matters, what is noise — and show you only what is yours? I only read the mail; I never
> send anything.

## How they are turned on

All six are already in this folder, and the same six are published on GitHub. Either way the
catalogue is called `poly-a1`, and the part after `@` is always `poly-a1`. Tell them what you are
doing, in one line, and do it.

**First check that `poly-a1` is not already there** (`claude plugin marketplace list` in the shell). The
setup in START-HERE adds it; if it is listed, go straight to the install line below.

**If it is not there, add it from GitHub first** - one file by its link, no git and no account
needed, and later fixes reach them from the same place:

```
/plugin marketplace add https://raw.githubusercontent.com/vadimchernets/poly-a1-plugins/main/.claude-plugin/marketplace.json
```

This needs Claude Code 2.1.224 or later (`claude --version`; if older, `claude update` first).
Each plugin then arrives as the zip attached to its GitHub release, checked against the `sha256`
the catalogue states. Checked live on 02.10.2026 in a fresh Ubuntu 24.04 with no git, no unzip and
no Python: the catalogue added and all six installed and came up enabled.

**No network, or GitHub refused?** Add this folder instead - nothing is downloaded then:

```
/plugin marketplace add <path to this folder>
```

`<path to this folder>` is the folder that contains this `plugins/` directory — the one with the
start-here file in it, not `plugins/` itself. Drag the folder into the terminal and it types its
own path. Later, when the network is back, switch it to GitHub as below.

Then, when the moment comes:

```
/plugin install safecall@poly-a1
```

Swap `safecall` for `duocall`, `pocketcall`, `chasecall`, `nightcall` or `mailcall` when their
moment comes. Restart Claude Code (or `/reload-plugins`) for it to take effect.

**Auto-update, once.** For any catalogue that is not Anthropic's own it is off by default, and no
setting inside a plugin can change that. In their Claude Code user settings (`~/.claude/settings.json`;
Windows `%USERPROFILE%\.claude\settings.json`; if `CLAUDE_CONFIG_DIR` is set, the `settings.json`
there), beside the `source` of `extraKnownMarketplaces` → `poly-a1`, add `"autoUpdate": true`. To be
sure, `/plugin` → Marketplaces → `poly-a1` should say auto-update is on; if it does not, choose
**Enable auto-update** there.

**Python.** safecall and chasecall check Python 3 before every hook. If this computer has none yet
(on a Mac: no Apple Command Line Tools), they say so in one line at the start of a session and stay
quiet until step 0 of START-HERE is done - they never pop Apple's install window in the middle of
a lesson.

## Later: from the folder to GitHub, without losing anything

If they added `poly-a1` from this folder, it is a snapshot of the day they bought it. Once they
have the network, offer to point the same `poly-a1` at GitHub, so later fixes reach them. Tell them
in one line, then do it. Checked live on 02.10.2026 (Claude Code 2.1.288, a throwaway
`CLAUDE_CONFIG_DIR`): all six installed from a folder with older versions, switched, all six still
installed and enabled, their data in `plugins/data/` untouched, and `claude plugin update` brought
each to its newer release.

1. In their Claude Code user settings (see above), find `extraKnownMarketplaces` → `poly-a1` →
   `source` (it holds the folder path) and replace only that value:

   ```json
   "source": { "source": "url", "url": "https://raw.githubusercontent.com/vadimchernets/poly-a1-plugins/main/.claude-plugin/marketplace.json" }
   ```

   Without this edit step 2 is refused with "its source doesn't match its extraKnownMarketplaces
   entry" — the entry written when they added the folder still names the folder.

2. Run:

   ```
   claude plugin marketplace add https://raw.githubusercontent.com/vadimchernets/poly-a1-plugins/main/.claude-plugin/marketplace.json
   ```

   The right answer says the marketplace `poly-a1` "now points at https://raw.githubusercontent.com/…"
   and "Plugins already installed from it now update from the new source."

3. Back in the same settings entry, beside `source`, add `"autoUpdate": true` (step 2 rewrites the
   entry, so this goes after it), and check `/plugin` → Marketplaces as above.

4. Bring what is installed up to date now, one line per plugin they have, then restart Claude Code:

   ```
   claude plugin update safecall@poly-a1
   ```

   The right answer is `Plugin "safecall" updated from … to …` or `already at the latest version`.

If their `poly-a1` was added earlier as `vadimchernets/poly-a1-plugins` (a git source), it keeps
working where git is installed; switch it the same way so it never needs git again.

**Never** run `/plugin marketplace remove poly-a1` to "re-add it from GitHub": Claude Code then
uninstalls every plugin that came from it and deletes their saved data. And never add the GitHub
catalogue under another name: the plugins are known as `…@poly-a1`, and a second name means a second,
empty set of everything.

## What you must not say about them

- Not that they make anything private. What you read still goes to Anthropic. `safecall` decides
  whether a change can be undone, not where the text goes. If they ask, say that plainly.
- Not that two AIs agreeing proves anything. `duocall` says the opposite, on purpose.
- Not "plugin", "marketplace", "repository" as the first word out of your mouth. Say what it does:
  "a safety net before changes", "a second opinion", "a remote", "the chaser", "the night shift",
  "news in your own words". The technical name comes second, if at all.
- Nothing about paying. None of them costs anything and none of them needs an account.
