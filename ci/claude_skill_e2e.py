#!/usr/bin/env python3
"""End to end: a real Claude Code session opens a plugin skill and runs the script command written in it.

A stand-in for the Anthropic API on 127.0.0.1 plays a model that, in one `claude -p` run with the
default permission mode (nothing approved in advance, no --dangerously-skip-permissions):
  1. opens the skill /safecall:where through the Skill tool;
  2. copies the script command out of the skill text Claude Code sent it - with the plugin's real
     folder where the skill says ${CLAUDE_PLUGIN_ROOT} - and runs it with the shell tool it has:
     Bash as written, or, with only the PowerShell tool (Windows without Git Bash), with the start
     changed the way the skill says;
  3. says it is done. A second session does the same for /chasecall:scout (`tracker.py stats`).
Checks: each command ran without a permission prompt (the skill's allowed-tools covered it - in
`-p` an unapproved command comes back as "This command requires approval"), and its output is the
script's own, not a Python error.

  python claude_skill_e2e.py --config <CLAUDE_CONFIG_DIR with the plugins installed>
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import claude_e2e  # noqa: E402  (the stand-in server: streaming, request log)

STEPS = [
    # (id, skill, plugin, script and arguments, what the script's output must contain)
    ("where", "safecall:where", "safecall", 'scripts/state.py show --folder "{project}"', "where we stopped"),
    ("stats", "chasecall:scout", "chasecall", "scripts/tracker.py stats", "tasks: 0"),
]


def all_text(body):
    out = []

    def walk(x):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, list):
            for y in x:
                walk(y)
        elif isinstance(x, dict):
            for y in x.values():
                walk(y)
    walk(body.get("messages", []))
    return "\n".join(out)


def plan(body, project):
    names = {t.get("name") for t in body.get("tools", []) or []}
    if "Skill" not in names:
        return [{"type": "text", "text": "ok"}], "end_turn"
    done = {c.get("tool_use_id") for c in claude_e2e.tool_results(body)}
    text = all_text(body)
    for sid, skill, plugin, rest, _ in STEPS:
        if "toolu_skill_" + sid not in done:
            return [{"type": "tool_use", "id": "toolu_skill_" + sid, "name": "Skill",
                     "input": {"skill": skill}}], "tool_use"
        if "toolu_run_" + sid not in done:
            m = re.search(r'sh "([^"\n]+)/hooks/python\.sh" %s say' % plugin, text)
            if not m:
                return [{"type": "text", "text": "NO-LAUNCHER-IN-SKILL-TEXT " + plugin}], "end_turn"
            root = m.group(1)
            # A real model takes seconds to answer. Answering in a few milliseconds raced Claude Code's own
            # update of the skill's allowed-tools grant (seen 3 times in 20 runs: "requires approval").
            time.sleep(2)
            args = rest.format(project=project)
            if "Bash" in names:
                tool, cmd = "Bash", 'sh "%s/hooks/python.sh" %s say %s' % (root, plugin, args)
            else:
                tool, cmd = "PowerShell", '& "%s/hooks/python.ps1" %s say %s' % (root, plugin, args)
            return [{"type": "tool_use", "id": "toolu_run_" + sid, "name": tool,
                     "input": {"command": cmd, "description": "Run the skill's script"}}], "tool_use"
    return [{"type": "text", "text": "Done."}], "end_turn"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--claude", default=shutil.which("claude") or "claude")
    ap.add_argument("--only", help="one step id; without it every step runs in a session of its own")
    args = ap.parse_args()
    global STEPS
    if not args.only:
        # One skill per session, as a person opens one per message. Two skills opened in one turn lost the
        # second one's allowed-tools now and then (Claude Code 2.1.288, about one run in two with the
        # stand-in): the command then asks for permission - a prompt, not a failure, for a person.
        codes = [subprocess.call([sys.executable, os.path.abspath(__file__), "--config", args.config,
                                  "--claude", args.claude, "--only", sid]) for sid, *_ in STEPS]
        return 1 if any(codes) else 0
    STEPS = [st for st in STEPS if st[0] == args.only]

    tmp = tempfile.mkdtemp(prefix="claude-skill-e2e-")
    home = os.path.join(tmp, "дом пользователя")
    project = os.path.join(home, "проект")
    os.makedirs(project)
    claude_e2e.plan = lambda body, _note: plan(body, project)
    server = ThreadingHTTPServer(("127.0.0.1", 0), claude_e2e.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    env = dict(os.environ)
    env.update({"ANTHROPIC_BASE_URL": "http://127.0.0.1:%d" % server.server_port,
                "ANTHROPIC_API_KEY": "sk-ant-ci-stand-in", "CLAUDE_CONFIG_DIR": args.config,
                "HOME": home, "USERPROFILE": home, "CHASECALL_DB": os.path.join(tmp, "chasecall.db"),
                "DISABLE_TELEMETRY": "1", "DISABLE_ERROR_REPORTING": "1", "DISABLE_AUTOUPDATER": "1",
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"})
    env.pop("CLAUDECODE", None)
    p = subprocess.run([args.claude, "-p", "Where did we stop?", "--output-format", "json",
                        "--permission-mode", "default",
                        # opening a skill is the one thing approved in advance (a person says yes to it once);
                        # its script then has to run on the skill's own allowed-tools
                        "--allowedTools", "Skill", "--debug-file", os.path.join(tmp, "debug.log")],
                       cwd=project, env=env, capture_output=True, timeout=300, stdin=subprocess.DEVNULL)
    server.shutdown()
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    reqs = claude_e2e.REQUESTS
    print("claude -p exit %d; %d model requests" % (p.returncode, len(reqs)))
    problems = []
    last = reqs[-1] if reqs else {}
    results = {c["tool_use_id"]: c for c in claude_e2e.tool_results(last)}
    shell = "Bash" if any(t.get("name") == "Bash" for t in last.get("tools", []) or []) else "PowerShell"
    for sid, skill, plugin, rest, want in STEPS:
        s = results.get("toolu_skill_" + sid)
        r = results.get("toolu_run_" + sid)
        st = claude_e2e.text_of(s) if s else ""
        rt = claude_e2e.text_of(r) if r else ""
        if not s or s.get("is_error"):
            problems.append("Skill %s did not open: %r" % (skill, st[:400]))
            continue
        if not r:
            problems.append("%s: the command from the skill text was never run (no launcher line in it?)" % skill)
            continue
        sent = [c.get("input", {}).get("command") for m in last.get("messages", []) if isinstance(m.get("content"), list)
                for c in m["content"] if c.get("type") == "tool_use" and c.get("id") == "toolu_run_" + sid]
        if "requires approval" in rt or "permission" in rt.lower():
            problems.append("%s: %s asked for permission - allowed-tools did not cover it: %r (command %r)"
                            % (skill, shell, rt[:400], sent))
        elif r.get("is_error") or want not in rt:
            problems.append("%s: %s ran, but not the script's answer: %r" % (skill, shell, rt[:400]))
        else:
            print("ok   %s via %s, no prompt: %s" % (skill, shell, rt[:160]))
    if not reqs:
        problems.append("no model requests: stdout=%r stderr=%r" % (out[-500:], err[-500:]))
    for pr in problems:
        print("FAIL " + pr)
    if problems:
        print("--- kept: " + tmp)
        print("--- stdout\n" + out[-2000:] + "\n--- stderr\n" + err[-2000:])
        try:
            log = open(os.path.join(tmp, "debug.log"), encoding="utf-8", errors="replace").read()
            print("--- debug (permission lines)\n" + "\n".join(
                l[:300] for l in log.splitlines() if "ermission" in l or "allowed" in l.lower())[-3000:])
        except OSError:
            pass
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
