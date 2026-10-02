#!/usr/bin/env python3
"""Run every hook of the installed Poly A1 plugins exactly the way Claude Code runs it, and check
what each one does - on Windows in all three shells Claude Code may pick, on Mac and Linux in sh.

How Claude Code (2.1.288) spawns a shell-form command hook, read from its own code:
  - macOS, Linux:          sh -c <command>                      (env CLAUDE_PLUGIN_ROOT, ...)
  - Windows with Git Bash: <Git>\\bin\\bash.exe -c <command>      (backslashes in the command and in
                           CLAUDE_PLUGIN_ROOT/DATA/PROJECT_DIR turned into forward slashes)
  - Windows without it:    pwsh|powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass
                           -Command <command>, with ${CLAUDE_PLUGIN_ROOT} (and _DATA, PROJECT_DIR)
                           rewritten to ${env:CLAUDE_PLUGIN_ROOT}
The hook's JSON goes to stdin as UTF-8 plus a newline. Exit 0 = go on, exit 2 = block.

Each hook runs twice: with a real Python on PATH, and with none - only stubs that fail `-c` the way
the Microsoft Store alias does - where the plugin must say its one step-0 line and never fail.

  python hooks_like_claude.py --installed <plugins/installed_plugins.json> --shells pwsh,powershell,gitbash
  python hooks_like_claude.py --root safecall=<dir> --root chasecall=<dir> --root nightcall=<dir> --shells sh

Prints one line per case and exits 1 if any case failed.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

WINDOWS = os.name == "nt"
GIT_BASH = r"C:\Program Files\Git\bin\bash.exe"
PLACEHOLDERS = ("CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_DATA")


def spawn(shell, command, env, stdin_text, cwd):
    """The argv Claude Code would use, and the command text after its rewrites."""
    if shell in ("pwsh", "powershell"):
        for name in PLACEHOLDERS:
            command = command.replace("${%s}" % name, "${env:%s}" % name)
        if not WINDOWS and "\n" in command:
            # PowerShell 7 on Mac and Linux has an `exec` of its own (Switch-Process) and would take the sh line;
            # on Windows there is none. Give it the PowerShell line alone, as Windows ends up running it.
            command = command.split("\n", 1)[1]
        argv = [shutil.which(shell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-Command", command]
    elif shell == "gitbash":
        command = command.replace("\\", "/")
        for name in PLACEHOLDERS:
            if name in env:
                env[name] = env[name].replace("\\", "/")
        argv = [GIT_BASH, "-c", command]
    else:
        argv = ["/bin/sh", "-c", command]
    p = subprocess.run(argv, input=(stdin_text + "\n").encode("utf-8"), capture_output=True,
                       env=env, cwd=cwd, timeout=60)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def no_python_path(tmp):
    """PATH with every real Python taken out and failing stubs in front of what is left."""
    stubs = os.path.join(tmp, "stubs")
    os.makedirs(stubs, exist_ok=True)
    if WINDOWS:
        # where.exe answers `python -c ...` with an error, just as the Store alias does (9009).
        for name in ("python.exe", "python3.exe", "py.exe"):
            shutil.copy(r"C:\Windows\System32\where.exe", os.path.join(stubs, name))
    else:
        for name in ("python3", "python", "py"):
            path = os.path.join(stubs, name)
            with open(path, "w") as fh:
                fh.write("#!/bin/sh\necho stub >&2\nexit 9009\n")
            os.chmod(path, 0o755)
    keep = os.environ["PATH"].split(os.pathsep)
    if WINDOWS:   # on Mac and Linux /usr/bin holds the shell's own tools too: the stubs in front are enough
        keep = [d for d in keep if d and not any(os.path.exists(os.path.join(d, n))
                                                 for n in ("python.exe", "python3.exe"))]
    return os.pathsep.join([stubs] + keep)


def commands(root):
    hooks = json.load(open(os.path.join(root, "hooks", "hooks.json"), encoding="utf-8"))["hooks"]
    out = []
    for event, groups in hooks.items():
        for group in groups:
            for i, hook in enumerate(group["hooks"]):
                out.append((event, group.get("matcher", ""), i, hook["command"]))
    return out


def cases(plugin, home, project):
    """(event, index) -> (stdin JSON, check(code, out, err, python) -> problem or None)."""
    note = os.path.join(project, "заметка.txt")

    def base(event, **extra):
        d = {"session_id": "ci", "transcript_path": os.path.join(home, "t.jsonl"), "cwd": project,
             "hook_event_name": event}
        d.update(extra)
        return json.dumps(d, ensure_ascii=False)

    def paused(code, out, err, py, speaks):
        if code != 0:
            return "exit %d (want 0) stderr=%r" % (code, err[-300:])
        if speaks:
            lines = [l for l in out.splitlines() if l.strip()]
            if len(lines) != 1 or ("%s is paused" % plugin) not in lines[0]:
                return "want one step-0 line, got %r" % out[-300:]
        elif out.strip():
            return "want silence, got %r" % out[-300:]
        return None

    if plugin == "safecall":
        def now(code, out, err, py):
            if not py:
                return paused(code, out, err, py, True)
            return None if code == 0 and "The real time on this computer" in out else \
                "exit %d out=%r err=%r" % (code, out[-300:], err[-300:])

        def show(code, out, err, py):
            if not py:
                return paused(code, out, err, py, False)
            return None if code == 0 and ("where we stopped" in out or out.strip()) else \
                "exit %d out=%r err=%r" % (code, out[-300:], err[-300:])

        def guard(code, out, err, py):
            copies = []
            for d, _, files in os.walk(os.path.join(home, ".safecall")):
                copies += [f for f in files if f == "заметка.txt"]
            if not py:
                if copies:
                    return "a copy was made with no Python?"
                return paused(code, out, err, py, False)
            if code != 0:
                return "exit %d stderr=%r" % (code, err[-300:])
            if not copies:
                return "no copy of заметка.txt under ~/.safecall (out=%r err=%r)" % (out[-300:], err[-300:])
            if "заметка.txt" not in out:
                return "the non-English file name came back garbled: %r" % out[-300:]
            return None

        return {
            ("SessionStart", 0): (base("SessionStart", source="startup"), now),
            ("SessionStart", 1): (base("SessionStart", source="startup"), show),
            ("PreToolUse", 0): (base("PreToolUse", tool_name="Write", tool_use_id="t1",
                                     tool_input={"file_path": note, "content": "новый текст"}), guard),
        }
    if plugin == "chasecall":
        def due(code, out, err, py):
            if not py:
                return paused(code, out, err, py, True)
            return None if code == 0 else "exit %d out=%r err=%r" % (code, out[-300:], err[-300:])

        def guard(code, out, err, py):
            if not py:
                return paused(code, out, err, py, False)
            if code != 2 or not err.strip():
                return "want exit 2 with a reason for a payment, got exit %d err=%r out=%r" % (code, err[-300:], out[-300:])
            return None

        return {
            ("SessionStart", 0): (base("SessionStart", source="startup"), due),
            ("PreToolUse", 0): (base("PreToolUse", tool_name="Bash", tool_use_id="t2",
                                     tool_input={"command": "stripe charges create --amount 4000 --currency usd"}), guard),
        }
    if plugin == "nightcall":
        def stop(code, out, err, py):
            if code != 0 or out.strip():
                return "want exit 0 and silence with no night run, got exit %d out=%r err=%r" % (code, out[-300:], err[-300:])
            return None

        return {("Stop", 0): (base("Stop", stop_hook_active=False), stop)}
    return {}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--installed", help="installed_plugins.json of a Claude Code config folder")
    ap.add_argument("--root", action="append", default=[], help="plugin=folder")
    ap.add_argument("--shells", default="pwsh,powershell,gitbash" if WINDOWS else "sh")
    args = ap.parse_args()

    roots = dict(r.split("=", 1) for r in args.root)
    if args.installed:
        data = json.load(open(args.installed, encoding="utf-8"))
        for key, entries in data.get("plugins", {}).items():
            name = key.split("@")[0]
            entry = entries[0] if isinstance(entries, list) else entries
            roots[name] = entry["installPath"]

    failed = 0
    ran = 0
    for plugin in sorted(roots):
        root = roots[plugin]
        if not os.path.exists(os.path.join(root, "hooks", "hooks.json")):
            print("%-10s no hooks - nothing to run (%s)" % (plugin, root))
            continue
        for shell in args.shells.split(","):
            for python in (True, False):
                tmp = tempfile.mkdtemp(prefix="hooks-ci-")
                home = os.path.join(tmp, "дом пользователя")
                project = os.path.join(home, "проект")
                os.makedirs(project)
                with open(os.path.join(project, "заметка.txt"), "w", encoding="utf-8") as fh:
                    fh.write("привет\n")
                env = dict(os.environ)
                env.update({"HOME": home, "USERPROFILE": home, "CLAUDE_PLUGIN_ROOT": root,
                            "CLAUDE_PLUGIN_DATA": os.path.join(tmp, "data"), "CLAUDE_PROJECT_DIR": project,
                            "CHASECALL_DB": os.path.join(tmp, "chasecall.db")})
                for k in ("PYTHONUTF8", "PYTHONIOENCODING"):
                    env.pop(k, None)
                if not python:
                    env["PATH"] = no_python_path(tmp)
                table = cases(plugin, home, project)
                for event, matcher, index, command in commands(root):
                    key = (event, index)
                    if key not in table:
                        print("FAIL %-10s %-10s %-6s %s[%d]: no check written for this hook" % (
                            plugin, shell, "python" if python else "none", event, index))
                        failed += 1
                        continue
                    stdin_text, check = table[key]
                    code, out, err = spawn(shell, command, dict(env), stdin_text, project)
                    problem = check(code, out, err, python)
                    if problem is None and "\ufffd" in out:
                        problem = "the output is not UTF-8 any more: %r" % out[-300:]
                    ran += 1
                    tag = "ok  " if problem is None else "FAIL"
                    first = (out.strip().splitlines() or [""])[0][:110]
                    print("%s %-10s %-10s %-6s %-12s[%d] exit=%d %s" % (
                        tag, plugin, shell, "python" if python else "none", event, index, code,
                        problem or first))
                    if problem:
                        failed += 1
                shutil.rmtree(tmp, ignore_errors=True)
    print("%d hook runs, %d failed" % (ran, failed))
    return 1 if failed or not ran else 0


if __name__ == "__main__":
    sys.exit(main())
