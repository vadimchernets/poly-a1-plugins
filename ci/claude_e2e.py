#!/usr/bin/env python3
"""End to end: a real Claude Code session fires the plugins' hooks by itself.

A stand-in for the Anthropic API on 127.0.0.1 plays a model that, in one `claude -p` run:
  1. asks to Write over an existing file with a non-English name  -> safecall's PreToolUse hook
  2. asks to run `stripe charges create ...` through Bash (PowerShell on a Windows without Git Bash)
                                                                    -> chasecall's PreToolUse hook
  3. says it is done                                                -> nightcall's Stop hook
Every request Claude Code sends is kept, so we can read what the hooks told the model:
  - SessionStart: safecall's "The real time on this computer" reached the model's context;
  - safecall made the copy before the write (a file under ~/.safecall/copies);
  - chasecall blocked the payment, and its reason came back to the model as the tool result.

  python claude_e2e.py --config <CLAUDE_CONFIG_DIR with the plugins installed> [--expect-shell powershell]

Exits 1 on any failed check.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REQUESTS = []
NOTE = "заметка.txt"


def text_of(body):
    return json.dumps(body, ensure_ascii=False)


def tool_results(body):
    out = []
    for m in body.get("messages", []):
        if isinstance(m.get("content"), list):
            for c in m["content"]:
                if c.get("type") == "tool_result":
                    out.append(c)
    return out


def plan(body, note_path):
    """What the stand-in model answers: a list of content blocks and a stop reason."""
    names = {t.get("name") for t in body.get("tools", []) or []}
    if "Write" not in names:
        return [{"type": "text", "text": "ok"}], "end_turn"
    done = {c.get("tool_use_id") for c in tool_results(body)}
    if "toolu_write_1" not in done:
        return [{"type": "tool_use", "id": "toolu_write_1", "name": "Write",
                 "input": {"file_path": note_path, "content": "новый текст\n"}}], "tool_use"
    if "toolu_bash_1" not in done:
        # Windows without Git Bash has no Bash tool: its command tool is PowerShell.
        shell_tool = "Bash" if "Bash" in names else "PowerShell"
        return [{"type": "tool_use", "id": "toolu_bash_1", "name": shell_tool,
                 "input": {"command": "stripe charges create --amount 4000 --currency usd",
                           "description": "Charge the card"}}], "tool_use"
    return [{"type": "text", "text": "Done."}], "end_turn"


class Handler(BaseHTTPRequestHandler):
    note_path = None

    def log_message(self, *a):
        pass

    def do_GET(self):
        self.send_json({"data": [], "has_more": False})

    def send_json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        n = int(self.headers.get("content-length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            body = {}
        if "/messages" not in self.path or "count_tokens" in self.path:
            return self.send_json({"input_tokens": 10})
        REQUESTS.append(body)
        blocks, stop = plan(body, self.note_path)
        msg = {"id": "msg_%d" % len(REQUESTS), "type": "message", "role": "assistant",
               "model": body.get("model", "claude"), "content": [], "stop_reason": None,
               "stop_sequence": None, "usage": {"input_tokens": 10, "output_tokens": 0}}
        if not body.get("stream"):
            msg.update(content=blocks, stop_reason=stop)
            return self.send_json(msg)
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.end_headers()

        def ev(name, data):
            self.wfile.write(("event: %s\ndata: %s\n\n" % (name, json.dumps(data, ensure_ascii=False))).encode())

        ev("message_start", {"type": "message_start", "message": msg})
        for i, b in enumerate(blocks):
            if b["type"] == "text":
                ev("content_block_start", {"type": "content_block_start", "index": i,
                                           "content_block": {"type": "text", "text": ""}})
                ev("content_block_delta", {"type": "content_block_delta", "index": i,
                                           "delta": {"type": "text_delta", "text": b["text"]}})
            else:
                ev("content_block_start", {"type": "content_block_start", "index": i,
                                           "content_block": {"type": "tool_use", "id": b["id"],
                                                             "name": b["name"], "input": {}}})
                ev("content_block_delta", {"type": "content_block_delta", "index": i,
                                           "delta": {"type": "input_json_delta",
                                                     "partial_json": json.dumps(b["input"], ensure_ascii=False)}})
            ev("content_block_stop", {"type": "content_block_stop", "index": i})
        ev("message_delta", {"type": "message_delta", "delta": {"stop_reason": stop, "stop_sequence": None},
                             "usage": {"output_tokens": 5}})
        ev("message_stop", {"type": "message_stop"})
        self.wfile.flush()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="CLAUDE_CONFIG_DIR with the plugins installed")
    ap.add_argument("--claude", default=shutil.which("claude") or "claude")
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="claude-e2e-")
    home = os.path.join(tmp, "дом пользователя")
    project = os.path.join(home, "проект")
    os.makedirs(project)
    note = os.path.join(project, NOTE)
    with open(note, "w", encoding="utf-8") as fh:
        fh.write("привет\n")

    Handler.note_path = note
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    env = dict(os.environ)
    env.update({"ANTHROPIC_BASE_URL": "http://127.0.0.1:%d" % server.server_port,
                "ANTHROPIC_API_KEY": "sk-ant-ci-stand-in", "CLAUDE_CONFIG_DIR": args.config,
                "HOME": home, "USERPROFILE": home, "CHASECALL_DB": os.path.join(tmp, "chasecall.db"),
                "DISABLE_TELEMETRY": "1", "DISABLE_ERROR_REPORTING": "1", "DISABLE_AUTOUPDATER": "1",
                "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"})
    env.pop("CLAUDECODE", None)
    p = subprocess.run([args.claude, "-p", "Please update the note.", "--output-format", "json",
                        "--dangerously-skip-permissions", "--debug-file", os.path.join(tmp, "debug.log")],
                       cwd=project, env=env, capture_output=True, timeout=300,
                       stdin=subprocess.DEVNULL)
    server.shutdown()
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    print("claude -p exit %d; %d model requests" % (p.returncode, len(REQUESTS)))

    problems = []
    tooled = [r for r in REQUESTS if any(t.get("name") == "Write" for t in r.get("tools", []) or [])]
    if not tooled:
        problems.append("the session never asked the model with tools: stdout=%r stderr=%r" % (out[-500:], err[-500:]))
    else:
        first = text_of(tooled[0])
        if "The real time on this computer" in first:
            print("ok   SessionStart: safecall's real time reached the model")
        else:
            problems.append("SessionStart: safecall's line is not in the first request")
        last = tooled[-1]
        results = {c["tool_use_id"]: c for c in tool_results(last)}
        w = results.get("toolu_write_1")
        copies = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(home, ".safecall")) for f in fs if f == NOTE]
        if copies:
            print("ok   PreToolUse Write: safecall copied %s before the write -> %s" % (NOTE, copies[0]))
        else:
            problems.append("PreToolUse Write: no copy under ~/.safecall (tool result %r)" % (w,))
        with open(note, encoding="utf-8") as fh:
            if fh.read() == "новый текст\n":
                print("ok   the write itself went through")
            else:
                problems.append("the Write did not go through: %r" % (w,))
        b = results.get("toolu_bash_1")
        btxt = text_of(b) if b else ""
        if "is not recognized" in btxt:
            problems.append("PowerShell's complaint about the sh line reached the model: %r" % btxt[:600])
        elif "[scriptblock]::Create" in btxt or "exec sh" in btxt:
            problems.append("the block shows the hook's own command in front of its reason: %r" % btxt[:600])
        elif b and b.get("is_error") and "chasecall" in btxt.lower():
            print("ok   PreToolUse %s: chasecall blocked" % ("Bash" if any(t.get("name") == "Bash" for t in last.get("tools", [])) else "PowerShell") + " the payment: %s" % btxt[:200])
        else:
            problems.append("PreToolUse Bash: payment not blocked by chasecall: %r" % (btxt[:400],))
    try:
        log = open(os.path.join(tmp, "debug.log"), encoding="utf-8", errors="replace").read()
    except OSError:
        log = ""
    for line in log.splitlines():
        low = line.lower()
        if ("hook" in low and ("powershell" in low or "pwsh" in low or "git bash" in low or "spawn" in low)) \
                or "non-blocking" in low or "hook error" in low:
            print("log  " + line[:240])
    for pr in problems:
        print("FAIL " + pr)
    if problems:
        print("--- stdout\n" + out[-2000:] + "\n--- stderr\n" + err[-2000:])
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
