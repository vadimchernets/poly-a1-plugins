# Poly A1 plugins

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23107737.svg)](https://doi.org/10.5281/zenodo.23107737)

**Pay $5 once — that's it: two AIs from different companies work together right on your phone. ChatGPT answers, Claude checks. No paid keys, no servers, no computer, nothing more to pay.**

Have ChatGPT and Claude? Start right away. Have one? It helps you install the other. Have neither? Gemini (Google) or Meta AI (WhatsApp, Facebook) helps you install both, free.

<details>
<summary><b>How it works</b></summary>

The orchestration runs on the phone itself. iPhone: a Shortcut calls Ask ChatGPT, then Ask Claude — actions the apps publish themselves; answers pass between your own apps, with no server of ours and no API keys, on your own accounts — free ones are enough. Android: the phone calls free AIs (Groq, OpenRouter, Google AI Studio) directly with your free key — no card, no server of ours; or by hand with your ChatGPT and Claude. Nothing like it exists anywhere else.

</details>

The phone part is [Duo and Trio](https://github.com/vadimchernets/c1m-duo); this repository is the computer part of Poly A1.

Six small additions to [Claude Code](https://claude.com/claude-code) for a person who is not a
programmer.

## Installing

Add the catalogue by its link - one file, no git and no GitHub account needed - and corrections made
later reach you from the same place:

```
/plugin marketplace add https://raw.githubusercontent.com/vadimchernets/poly-a1-plugins/main/.claude-plugin/marketplace.json
/plugin install safecall@poly-a1
/plugin install duocall@poly-a1
/plugin install pocketcall@poly-a1
/plugin install chasecall@poly-a1
/plugin install nightcall@poly-a1
/plugin install mailcall@poly-a1
```

Needs Claude Code 2.1.224 or later (`claude update`). With git installed, the short form
`/plugin marketplace add vadimchernets/poly-a1-plugins` works too.

This repository holds only the catalogue. Each plugin lives in its own public repository, and every
release of it carries `<plugin>-<version>.zip`; the catalogue installs that zip as an `archive`
source pinned by its `sha256`. So there is one copy of every plugin in the world, a release file
never changes after it is published, and the person's machine needs nothing but HTTPS. Checked live
on 02.10.2026 in a fresh Ubuntu 24.04 with no git, no unzip and no Python: all six installed and came
up enabled.

## The step everybody misses

**Auto-update is OFF by default for any marketplace that is not Anthropic's own**, and no field in
`marketplace.json` can turn it on. Do it once, either in `/plugin` → **Marketplaces** → `poly-a1` →
**Enable auto-update**, or in `~/.claude/settings.json`, beside the `source` of the
`extraKnownMarketplaces.poly-a1` entry:

```json
"autoUpdate": true
```

Without it, every correction made here after that day never reaches that machine.

## What is in it

| | |
|---|---|
| **[safecall](https://github.com/vadimchernets/safecall)** | Nothing is written before a copy exists; nothing is read before you have seen the list; no answer ends without saying what nobody checked. Plus three ready readings of a document - where the catch is, what a plan is missing, what here is fact and what is opinion. |
| **[duocall](https://github.com/vadimchernets/duocall)** | A second opinion from a **different company's** AI, and an honest account of where the two disagreed. Two AIs agreeing is not proof, and it says so. Works through a free browser chat when there is no second program. |
| **[pocketcall](https://github.com/vadimchernets/pocketcall)** | Leave the computer working and take the phone - the seven silent reasons an evening away never works, checked before you go out of the door. |
| **[chasecall](https://github.com/vadimchernets/chasecall)** | Something nobody is answering - a refund, a booking, a request. It keeps the task between sessions, writes the next letter, counts the attempts, and says when the call is yours to make. |
| **[nightcall](https://github.com/vadimchernets/nightcall)** | Claude Code working through the night: the computer kept awake for 8 or 12 hours, a plan and a progress file, other AIs checked alive and replaced when they die, and a morning report. |
| **[mailcall](https://github.com/vadimchernets/mailcall)** | Reads your mailbox, read-only: a morning summary of what matters, and Google Alerts and newsletters boiled down by the words you watch. Drafts only - nothing is sent without your yes. |

## What none of them do

No account. No API key. No second subscription. Nothing bought, and nothing that suggests buying.
They drive only what is already installed and already signed in on the machine. Python 3.8+ and the
standard library, no dependencies. Without Python, safecall's and chasecall's hooks say so in one line
and stay quiet - on a Mac without Apple's Command Line Tools they never start the `/usr/bin/python3`
stub that pops Apple's install window.

None of them makes Claude Code private: what Claude Code reads still goes to Anthropic. These
plugins decide whether a change can be undone and whether an answer can be trusted — not where the
text goes.

## For the buyer of Poly A1

All six also ride **inside** the Poly A1 folder for the computer, with a catalogue generated from
this one: the same name `poly-a1`, the same plugins, the same versions, only the sources point at the
folders beside it - so they install with no network and no account. The setup in START-HERE adds
`poly-a1` from the link above first and uses the folder only when that fails. Later, to get
corrections, point the same `poly-a1` at the link instead of removing anything: the steps are in
[`OFFER-THESE.md`](OFFER-THESE.md) (Claude Code reads that file and does it for you). Checked live on
02.10.2026 (Claude Code 2.1.288): installed from a folder with older versions, switched to the link,
all six stayed installed with their data, and `claude plugin update` brought each to its new release.
Do **not** remove the `poly-a1` marketplace to re-add it - Claude Code then uninstalls its plugins and
deletes their data.

## Keeping this repository in step

A plugin is released by tagging it: `git tag -a v<version>` and `git push origin v<version>` in its
repository, where `<version>` is the one in its `plugin.json`. Its `.github/workflows/release.yml`
then builds `<plugin>-<version>.zip` (`scripts/release-zip.sh`: one top folder
`<plugin>-<version>/`, committed files only, no tests) and publishes the release with the zip
attached; Zenodo archives the release and mints its DOI.

`./sync.sh` then pins every entry of this catalogue to that release: it checks the working repository
is clean, pushed and exactly at the tag, downloads the zip, checks its top folder and manifest, and
writes the url, the `sha256` of the published bytes, the version and `metadata.commit`.
`./sync.sh --check` changes nothing and fails if anything is behind or if `claude plugin validate`
rejects the catalogue. Run the check before publishing. The Poly A1 kit build refuses to ship a
catalogue that disagrees with the folders it ships.

## Licence

Apache-2.0 for all six. Each plugin carries its own `LICENSE` and `NOTICE`.

---

<sub>Free Claude has a daily limit. Ran out and you like Claude? Claude Pro ($20/month, $17 billed yearly; paid to Anthropic, not us) lifts it. While you wait, a free AI on a key does the checking (Trio).</sub>
