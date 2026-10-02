#!/bin/sh
# Keeps this catalogue pinned to what each plugin has actually released.
#
# Since 02.10.2026 every entry in `.claude-plugin/marketplace.json` is an `archive` source: the zip
# attached to that plugin's GitHub release, with its sha256.
#
#   {"source": "archive",
#    "url": "https://github.com/vadimchernets/<plugin>/releases/download/v<version>/<plugin>-<version>.zip",
#    "sha256": "<64 hex>"}
#
# Why archives and not git. A `url`/`github` plugin source makes Claude Code run `git clone` on the
# person's machine. A beginner's Linux has no git ("Premature close", seen 02.10.2026), and on a Mac
# without Apple's Command Line Tools `git` is a stub that pops Apple's install window. An archive
# needs only HTTPS, and the catalogue itself is read the same way - as one file, by its raw link:
#
#   claude plugin marketplace add https://raw.githubusercontent.com/vadimchernets/poly-a1-plugins/main/.claude-plugin/marketplace.json
#
# so a person needs neither git nor a GitHub account (Claude Code 2.1.224 or later). A release asset
# never changes after upload (the zip GitHub builds on the fly from a tag may), so the sha256 holds.
# Each plugin's `.github/workflows/release.yml` builds and attaches the zip on every `v*` tag
# (`scripts/release-zip.sh` in that repository).
#
# This repository holds no plugin code: one copy of each plugin in the world, one catalogue. The paid
# Poly A1 kit generates its own catalogue from this very file (`poly-a1/site/kit-marketplace.py`),
# with the sources turned into the folders that ride inside it - same name `poly-a1`, same versions.
# That sameness is what lets a buyer switch from the kit folder to this catalogue without losing a
# plugin (OFFER-THESE.md). `metadata.commit` of each entry is the released commit, for that check.
#
#   ./sync.sh          - pin every entry to the release of its working repository's plugin.json version
#   ./sync.sh --check  - change nothing, fail if any pin, version or sha256 is not what is published
#
# For every plugin both modes require: the working repository is clean and pushed, its HEAD is the
# commit tagged v<version> (an unreleased commit would put into the kit something no zip holds), the
# release zip is downloadable, has the one top folder <plugin>-<version>/, and its plugin.json says
# that name and version. The sha256 is taken from the downloaded bytes, never computed locally.

set -u
HERE=$(cd "$(dirname "$0")" && pwd)
SRC_ROOT=${SRC_ROOT:-"$HOME/Developer"}
mode=write
[ "${1:-}" = "--check" ] && mode=check

python3 - "$HERE/.claude-plugin/marketplace.json" "$SRC_ROOT" "$mode" <<'PY'
import hashlib, io, json, os, subprocess, sys, zipfile

path, src_root, mode = sys.argv[1:4]
OWNER = "vadimchernets"
with open(path, encoding="utf-8") as fh:
    m = json.load(fh)

def git(repo, *args):
    try:
        return subprocess.check_output(["git", "-C", repo] + list(args), text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None

def fetch(url):
    # curl, not urllib: python.org's Python on a Mac ships without root certificates.
    try:
        return subprocess.check_output(["curl", "-fsSL", "--retry", "3", url], stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return None

bad = 0
changed = 0
for e in m["plugins"]:
    name = e["name"]
    work = os.path.join(src_root, name)
    def no(why):
        global bad
        print("BAD: %s - %s" % (name, why)); bad += 1
    if not os.path.isdir(os.path.join(work, ".git")):
        no("working repository %s is missing" % work); continue
    if git(work, "status", "--porcelain"):
        no("%s has unpublished edits" % work); continue
    head = git(work, "rev-parse", "HEAD")
    if not head or head != git(work, "rev-parse", "@{upstream}"):
        no("HEAD of %s is not what GitHub has (push it first)" % work); continue
    with open(os.path.join(work, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
        version = json.load(fh).get("version")
    tag = "v%s" % version
    remote = git(work, "ls-remote", "origin", "refs/tags/%s^{}" % tag, "refs/tags/%s" % tag) or ""
    tagged = [l.split()[0] for l in remote.splitlines() if l.endswith("^{}")] or \
             [l.split()[0] for l in remote.splitlines()]
    if not tagged:
        no("plugin.json says %s, but GitHub has no tag %s (cut the release: git tag -a %s && git push origin %s)"
           % (version, tag, tag, tag)); continue
    if tagged[0] != head:
        no("HEAD %s is not the released commit %s of %s - release the new commit first"
           % (head[:7], tagged[0][:7], tag)); continue
    url = "https://github.com/%s/%s/releases/download/%s/%s-%s.zip" % (OWNER, name, tag, name, version)
    data = fetch(url)
    if data is None:
        no("%s does not download (did the release workflow attach the zip?)" % url); continue
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        tops = {n.split("/", 1)[0] for n in z.namelist()}
        inner = json.loads(z.read("%s-%s/.claude-plugin/plugin.json" % (name, version)))
    except (zipfile.BadZipFile, KeyError, ValueError) as err:
        no("%s is not a plugin zip with %s-%s/.claude-plugin/plugin.json (%s)" % (url, name, version, err)); continue
    if tops != {"%s-%s" % (name, version)} or inner.get("name") != name or inner.get("version") != version:
        no("%s: top folders %s, manifest %s %s" % (url, sorted(tops), inner.get("name"), inner.get("version"))); continue
    sha = hashlib.sha256(data).hexdigest()
    want = {"source": "archive", "url": url, "sha256": sha}
    meta = dict(e.get("metadata") or {}, commit=head, tag=tag)
    if e.get("source") == want and e.get("version") == version and e.get("metadata") == meta:
        print("  %s %s - %s, sha256 %s, in step" % (name, version, tag, sha[:12]))
        continue
    if mode == "check":
        no("catalogue says %s %s, the release is %s sha256 %s" % (
            e.get("version"), json.dumps(e.get("source")), url, sha[:12]))
    else:
        e["source"] = want; e["version"] = version; e["metadata"] = meta; changed += 1
        print("  %s %s - pinned to %s, sha256 %s" % (name, version, url, sha[:12]))

if mode == "write" and changed and not bad:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2); fh.write("\n")
print("  catalogue: %d plugin(s)" % len(m["plugins"]))
sys.exit(1 if bad else 0)
PY
rc=$?

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$HERE" >/dev/null 2>&1 || { echo "BAD: claude plugin validate fails on this catalogue"; rc=1; }
fi

echo
[ "$rc" -eq 0 ] && { echo "sync: 0 problems"; exit 0; }
echo "sync: problems found"
exit 1
