#!/usr/bin/env python3
"""Run every script the plugins' skills name, the way Claude Code's shell tools run a skill's command,
and check what comes back - on Windows through the Bash tool (Git Bash) and the PowerShell tool
(PowerShell 7 and Windows PowerShell 5.1), on Mac and Linux through bash.

A skill never calls `python3` itself. Its command is written for the Bash tool,
    sh "${CLAUDE_PLUGIN_ROOT}/hooks/python.sh" <plugin> say scripts/<name>.py ...
and the skill tells Claude that with the PowerShell tool only the start changes - the bare path,
    ${CLAUDE_PLUGIN_ROOT}/hooks/python.ps1 <plugin> say scripts/<name>.py ...
or `& "<path>"` when the path has a space (the probe below lives in such a folder).
Claude Code puts the plugin's real folder in place of ${CLAUDE_PLUGIN_ROOT} in the skill's text, so the
command Claude sends carries the path itself (on Windows with backslashes). Here:
  - Bash tool:       bash -c <command>   (Git Bash's bash.exe on Windows)
  - PowerShell tool: pwsh|powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand <command>

Cases, each with a real Python on PATH and with none (only stubs that fail `-c` like the Store alias):
  - every script a skill names, with --help: exit 0 and argparse's "usage:" - or, with no Python,
    exit 0 and exactly one "<plugin> is paused" line;
  - a probe script dropped into a copy of a plugin: arguments with spaces, a non-English word piped
    to standard input (<<'EOF' in bash, @'...'@ | in PowerShell, UTF-8 with no BOM), and a failing exit code.

  python skills_like_claude.py --installed <plugins/installed_plugins.json>
Prints one line per case and exits 1 if any case failed.
"""
import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hooks_like_claude import GIT_BASH, WINDOWS, no_python_path  # noqa: E402

WORD = "привет"


def bash_form(root, plugin, rest, stdin=None):
    cmd = 'sh "%s/hooks/python.sh" %s say %s' % (root, plugin, rest)
    if stdin is not None:
        cmd += " <<'EOF'\n%s\nEOF" % stdin
    return cmd


def ps_form(root, plugin, rest, stdin=None):
    # the bare path, as the skills say (their PowerShell grant matches it); `& "..."` when the path has a space
    launcher = "%s/hooks/python.ps1" % root
    cmd = '%s %s say %s' % ('& "%s"' % launcher if " " in launcher else launcher, plugin, rest)
    if stdin is not None:
        cmd = "@'\n%s\n'@ | %s" % (stdin, cmd)
    return cmd


def run(shell, command, env, cwd):
    if shell in ("pwsh", "powershell"):
        enc = base64.b64encode(command.encode("utf-16-le")).decode()
        argv = [shutil.which(shell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-EncodedCommand", enc]
    elif shell == "gitbash":
        argv = [GIT_BASH, "-c", command]
    else:
        argv = [shutil.which("bash") or "/bin/sh", "-c", command]
    p = subprocess.run(argv, capture_output=True, env=env, cwd=cwd, timeout=120, stdin=subprocess.DEVNULL)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def skill_scripts(root, plugin):
    found = set()
    for d in sorted(os.listdir(os.path.join(root, "skills"))):
        path = os.path.join(root, "skills", d, "SKILL.md")
        if os.path.exists(path):
            text = open(path, encoding="utf-8").read()
            found |= set(re.findall(r'hooks/python\.sh" %s say (scripts/[\w.-]+\.py)' % plugin, text))
    return sorted(found)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--installed", required=True)
    ap.add_argument("--shells", default="gitbash,pwsh,powershell" if WINDOWS else "bash")
    args = ap.parse_args()
    data = json.load(open(args.installed, encoding="utf-8"))
    roots = {}
    for key, entries in data.get("plugins", {}).items():
        entry = entries[0] if isinstance(entries, list) else entries
        roots[key.split("@")[0]] = entry["installPath"]

    failed = ran = 0
    for plugin in sorted(roots):
        root = roots[plugin]
        scripts = skill_scripts(root, plugin)
        print("%-10s %d scripts named by its skills: %s" % (plugin, len(scripts), " ".join(scripts)))
        if not scripts:
            continue
        for shell in args.shells.split(","):
            for python in (True, False):
                tmp = tempfile.mkdtemp(prefix="skills-ci-")
                home = os.path.join(tmp, "дом пользователя")
                project = os.path.join(home, "проект")
                os.makedirs(project)
                # the probe: a copy of the plugin's launchers next to a script that echoes what it got
                probe_root = os.path.join(tmp, "plugin copy")
                os.makedirs(os.path.join(probe_root, "scripts"))
                shutil.copytree(os.path.join(root, "hooks"), os.path.join(probe_root, "hooks"))
                with open(os.path.join(probe_root, "scripts", "probe.py"), "w", encoding="utf-8") as fh:
                    fh.write("import sys\nsys.stdout.reconfigure(encoding='utf-8')\n"
                             "print('args=' + '|'.join(sys.argv[1:]) + ' stdin=' + sys.stdin.read().strip())\n"
                             "sys.exit(3)\n")
                env = dict(os.environ)
                env.update({"HOME": home, "USERPROFILE": home, "CHASECALL_DB": os.path.join(tmp, "chasecall.db")})
                for k in ("PYTHONUTF8", "PYTHONIOENCODING", "CLAUDE_PLUGIN_ROOT"):
                    env.pop(k, None)
                if not python:
                    env["PATH"] = no_python_path(tmp)
                form = ps_form if shell in ("pwsh", "powershell") else bash_form
                todo = [(s, form(root, plugin, s + " --help"), None) for s in scripts]
                todo.append(("probe", form(probe_root, plugin, 'scripts/probe.py list --folder "a b"', WORD),
                             "args=list|--folder|a b stdin=" + WORD))
                for name, command, want in todo:
                    code, out, err = run(shell, command, env, project)
                    lines = [l for l in out.splitlines() if l.strip()]
                    if not python:
                        ok = code == 0 and len(lines) == 1 and ("%s is paused" % plugin) in lines[0]
                    elif want:
                        # bash hands back the script's own 3; `powershell -Command` ends with 1 for any failed
                        # last command, so there "not 0" is what a failing script can promise
                        ok = (code == 3 if shell in ("bash", "gitbash") else code != 0) and out.strip() == want
                    else:
                        ok = code == 0 and "usage:" in out
                    if ok and "�" in out:
                        ok = False
                    ran += 1
                    failed += not ok
                    print("%s %-10s %-10s %-6s %-22s exit=%d %s" % (
                        "ok  " if ok else "FAIL", plugin, shell, "python" if python else "none", name, code,
                        (lines[0][:100] if lines else "") if ok else "out=%r err=%r cmd=%r" % (out[-300:], err[-300:], command)))
                shutil.rmtree(tmp, ignore_errors=True)
    print("%d skill command runs, %d failed" % (ran, failed))
    return 1 if failed or not ran else 0


if __name__ == "__main__":
    sys.exit(main())
