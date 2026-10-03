#!/usr/bin/env python3
"""End to end: a real Claude Code session opens a plugin skill and runs the script command written in it.

A stand-in for the Anthropic API on 127.0.0.1 plays a model that, in one `claude -p` run with the
default permission mode (nothing approved in advance, no --dangerously-skip-permissions):
  1. opens the skill /safecall:where through the Skill tool;
  2. copies the script command out of the skill text Claude Code sent it - with the plugin's real
     folder where the skill says ${CLAUDE_PLUGIN_ROOT} - and runs it with the shell tool it has:
     Bash as written, or, with only the PowerShell tool (Windows without Git Bash), with the start
     changed the way the skill says (E2E_SHELL_TOOL=PowerShell picks it where both tools exist);
  3. says it is done. A second session does the same for /chasecall:scout (`tracker.py stats`).
Checks: each command ran without a permission prompt (the skill's allowed-tools covered it - in
`-p` an unapproved command comes back as "This command requires approval"), and its output is the
script's own, not a Python error. When a command is asked about, Claude Code's own matcher decides whose
fault it is: the same command in a fresh session with only the skill's rules approved. Not covered there -
our skill is wrong, FAIL. Covered - Claude Code dropped the skill's grant (a known bug of 2.1.288, see
main()): a ::warning, and a 300 ms-pause probe at the end shows whether that bug is still there.

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
            args = rest.format(project=project)
            if "Bash" in names and os.environ.get("E2E_SHELL_TOOL", "Bash") == "Bash":
                tool, cmd = "Bash", 'sh "%s/hooks/python.sh" %s say %s' % (root, plugin, args)
            else:   # as the skill says: the bare path is what its PowerShell grant matches
                tool, cmd = "PowerShell", '%s/hooks/python.ps1 %s say %s' % (root, plugin, args)
            return [{"type": "tool_use", "id": "toolu_run_" + sid, "name": tool,
                     "input": {"command": cmd, "description": "Run the skill's script"}}], "tool_use"
    return [{"type": "text", "text": "Done."}], "end_turn"


def skill_rules(root, skill, tool):
    """The skill's own allowed-tools rules for this shell tool, with its plugin folder put in."""
    name = skill.split(":", 1)[1]
    text = open(os.path.join(root, "skills", name, "SKILL.md"), encoding="utf-8").read()
    line = next(l for l in text.split("---")[1].splitlines() if l.startswith("allowed-tools:"))
    return ["%s(%s)" % (t, r.replace("${CLAUDE_PLUGIN_ROOT}", root))
            for t, r in re.findall(r"\b(Bash|PowerShell)\((.*?)\)(?=\s|$)", line) if t == tool]


def recheck_plan(body, tool, command):
    """The same command, asked for straight away, with no skill opened."""
    if "toolu_recheck" in {c.get("tool_use_id") for c in claude_e2e.tool_results(body)}:
        return [{"type": "text", "text": "Done."}], "end_turn"
    if tool not in {t.get("name") for t in body.get("tools", []) or []}:
        return [{"type": "text", "text": "ok"}], "end_turn"
    return [{"type": "tool_use", "id": "toolu_recheck", "name": tool,
             "input": {"command": command, "description": "Run the skill's script"}}], "tool_use"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--claude", default=shutil.which("claude") or "claude")
    ap.add_argument("--only", help="one step id; without it every step runs in a session of its own")
    ap.add_argument("--gap-ms", type=int, default=0,
                    help="pause the stand-in this long between a tool call and the end of its answer")
    ap.add_argument("--recheck", help=argparse.SUPPRESS)   # JSON {tool, command, rules}: see below
    args = ap.parse_args()
    global STEPS
    if not args.only:
        # One skill per session, as a person opens one per message.
        me = [sys.executable, os.path.abspath(__file__), "--config", args.config, "--claude", args.claude]
        codes = [subprocess.call(me + ["--only", sid]) for sid, *_ in STEPS]
        # A known Claude Code bug, kept in sight (not a failure of ours, and not hidden either). When the Skill
        # tool finishes while the model's answer is still streaming, Claude Code 2.1.288 drops the skill's
        # allowed-tools grant for the rest of the turn, and the skill's own command is asked about. The query
        # loop collects tool results mid-stream without the context they carry: in the binary, the mid-stream
        # drain reads only `message` from getCompletedResults(), while getRemainingResults() after the stream
        # also takes `newContext` - and the Skill tool is not concurrency-safe, so its permission layer travels
        # only in that `newContext`. A real API leaves such a pause now and then; the stand-in answered event by
        # event and so hit it in about 1 run in 6 (CI runs 37103036388, 37149272044). The stand-in now answers
        # in one write (claude_e2e.py), which checks our skills' allowed-tools exactly; this probe adds a 300 ms
        # pause and reports whether Claude Code still drops the grant. It turns into a note when that is fixed.
        out = subprocess.run(me + ["--only", STEPS[0][0], "--gap-ms", "300"], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT).stdout.decode("utf-8", "replace")
        if "Claude Code dropped" in out:
            print("::warning title=Claude Code drops a skill's allowed-tools::Known Claude Code bug still there: "
                  "the Skill tool finished while the answer was streaming (300 ms pause) and the skill's own "
                  "command was asked about. Our allowed-tools are right (the steps above); the fix is Claude Code's.")
        elif "no prompt" in out:
            print("note: with a 300 ms pause in the answer the skill's grant held - Claude Code may have fixed the "
                  "dropped allowed-tools; the comment in claude_skill_e2e.py main() can go.")
        else:
            print("note: the stream-pause probe gave no verdict:\n" + out[-1500:])
        return 1 if any(codes) else 0
    claude_e2e.STREAM_GAP_MS = args.gap_ms
    STEPS = [st for st in STEPS if st[0] == args.only]
    recheck = json.loads(args.recheck) if args.recheck else None

    tmp = tempfile.mkdtemp(prefix="claude-skill-e2e-")
    home = os.path.join(tmp, "дом пользователя")
    project = os.path.join(home, "проект")
    os.makedirs(project)
    if recheck:
        claude_e2e.plan = lambda body, _note: recheck_plan(body, recheck["tool"], recheck["command"])
    else:
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
                        "--debug-file", os.path.join(tmp, "debug.log"),
                        "--allowedTools"] + (recheck["rules"] if recheck else ["Skill"]),
                       cwd=project, env=env, capture_output=True, timeout=300, stdin=subprocess.DEVNULL)
    server.shutdown()
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    reqs = claude_e2e.REQUESTS
    print("claude -p exit %d; %d model requests" % (p.returncode, len(reqs)))
    problems = []
    last = reqs[-1] if reqs else {}
    results = {c["tool_use_id"]: c for c in claude_e2e.tool_results(last)}
    if recheck:
        rt = claude_e2e.text_of(results["toolu_recheck"]) if "toolu_recheck" in results else ""
        print("recheck %s: %s" % ("covered" if rt and "requires approval" not in rt else "NOT covered", rt[:300]))
        return 0 if rt and "requires approval" not in rt else 1
    shell = "Bash" if any(t.get("name") == "Bash" for t in last.get("tools", []) or []) \
        and os.environ.get("E2E_SHELL_TOOL", "Bash") == "Bash" else "PowerShell"
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
            # Asked. Either our allowed-tools rule does not cover the command (our bug), or Claude Code dropped
            # the skill's grant (its bug, see main()). Claude Code's own matcher tells which: a fresh session
            # with nothing but the skill's rules approved runs the very same command.
            root = re.search(r'^(?:sh ")?(.+?)/hooks/python\.(?:sh|ps1)', sent[0] if sent else "")
            rules = skill_rules(root.group(1), skill, shell) if root else []
            rc = subprocess.run([sys.executable, os.path.abspath(__file__), "--config", args.config, "--claude",
                                 args.claude, "--only", sid, "--recheck",
                                 json.dumps({"tool": shell, "command": sent[0], "rules": rules})],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT) if rules else None
            if rc is not None and rc.returncode == 0:
                print("::warning title=Claude Code dropped %s's allowed-tools::%s's command was asked about in the "
                      "turn that opened the skill, yet the skill's own rule %r covers it (rechecked by Claude Code "
                      "itself). The known Claude Code bug in main(); our skill is right." % (skill, skill, rules))
                print("ok   %s rule covers the command (Claude Code dropped the grant this time)" % skill)
            else:
                problems.append("%s: %s asked for permission - allowed-tools did not cover it: %r (command %r, "
                                "rules %r)\n%s" % (skill, shell, rt[:400], sent, rules,
                                                    rc.stdout.decode("utf-8", "replace")[-800:] if rc else ""))
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
