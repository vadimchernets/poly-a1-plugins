#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for duocall. Run: python3 -m unittest discover tests

The load-bearing rule here is "never a second opinion from the same company", so that is what the
tests are built around. A plugin that quietly lets Claude be its own second opinion is worse than
no plugin: it hands a person false confidence exactly when they are about to act.
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECOND = HERE.parent / "scripts" / "second.py"


def fake_cli(folder: Path, name: str, body: str):
    """A stand-in for a vendor CLI, so the tests never call a real one or spend an allowance."""
    p = folder / name
    p.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="duocall-test-"))
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        # An empty PATH plus only what a test puts in it: no real vendor program can be reached.
        self.env = dict(os.environ, PATH=str(self.bin))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_second(self, *args, env=None):
        return subprocess.run([sys.executable, str(SECOND), *args],
                              capture_output=True, text=True, env=env or self.env)


class TestWhoCanBeAsked(unittest.TestCase):
    def test_claude_is_never_a_second_opinion(self):
        """Read the family table itself: claude must not be in it under any condition."""
        text = SECOND.read_text(encoding="utf-8")
        table = text.split("FAMILIES = [")[1].split("\n]")[0]
        self.assertNotIn('"claude"', table,
                         "claude in the list of second opinions is one opinion in two hats")
        self.assertIn('"openai"', table)
        self.assertIn('"google"', table)


class TestList(Base):
    def test_says_plainly_when_there_is_no_second_company(self):
        out = self.run_second("list")
        self.assertEqual(out.returncode, 1)
        self.assertIn("no second program", out.stdout.lower())
        self.assertIn("browser", out.stdout.lower(),
                      "no second program must still show the free path, not a dead end")

    def test_finds_an_installed_program(self):
        fake_cli(self.bin, "codex", 'echo "second answer"\n')
        out = self.run_second("list")
        self.assertEqual(out.returncode, 0)
        self.assertIn("ChatGPT", out.stdout)

    def test_one_seat_per_company(self):
        """agy and gemini are one company. Two seats of one company are not two opinions."""
        fake_cli(self.bin, "agy", 'echo x\n')
        fake_cli(self.bin, "gemini", 'echo x\n')
        out = self.run_second("list")
        self.assertEqual(out.stdout.count("Gemini"), 1,
                         "two Google programs were counted as two opinions")


class TestAsk(Base):
    def test_brings_the_answer_back(self):
        fake_cli(self.bin, "codex", 'echo "the deadline is fourteen days"\n')
        out = self.run_second("ask", "what is the deadline?")
        self.assertEqual(out.returncode, 0, out.stdout)
        got = json.loads(out.stdout)
        self.assertTrue(got["ok"])
        self.assertEqual(got["family"], "openai")
        self.assertIn("fourteen", got["answer"])

    def test_refuses_when_nobody_is_there(self):
        out = self.run_second("ask", "question")
        self.assertEqual(out.returncode, 1)
        self.assertFalse(json.loads(out.stdout)["ok"])

    def test_exhausted_allowance_is_said_in_plain_words(self):
        fake_cli(self.bin, "codex", 'echo "429 rate limit exceeded" >&2\nexit 1\n')
        out = self.run_second("ask", "question")
        got = json.loads(out.stdout)
        self.assertFalse(got["ok"])
        self.assertIn("allowance", got["why"],
                      "a used-up limit must be explained in plain words, not code 429")

    def test_a_silent_program_is_a_failure_not_an_empty_answer(self):
        fake_cli(self.bin, "codex", 'exit 0\n')       # success, but empty
        out = self.run_second("ask", "question")
        self.assertEqual(out.returncode, 1)
        self.assertFalse(json.loads(out.stdout)["ok"],
                         "an empty answer is 'did not answer', not agreement")

    def test_timeout_is_reported_not_waited_on(self):
        fake_cli(self.bin, "codex", '/bin/sleep 30\n')
        env = dict(self.env, DUOCALL_TIMEOUT="1")
        out = self.run_second("ask", "question", env=env)
        self.assertEqual(out.returncode, 1)
        self.assertIn("did not answer within", json.loads(out.stdout)["why"])

    def test_question_reaches_the_second_ai_unchanged(self):
        fake_cli(self.bin, "codex", 'printf "%s" "$*"\n')
        question = "what is the cancellation period under this contract?"
        out = self.run_second("ask", question)
        got = json.loads(out.stdout)
        self.assertIn(question, got["answer"],
                      "the question must go out unchanged: a paraphrased question is not a second opinion")

    def test_named_program_that_is_absent_is_refused_not_substituted(self):
        fake_cli(self.bin, "codex", 'echo x\n')
        out = self.run_second("ask", "question", "--who", "grok")
        self.assertEqual(out.returncode, 1)
        self.assertIn("is not on this computer", json.loads(out.stdout)["why"],
                      "grok was asked for - substituting another program for it is not allowed")


if __name__ == "__main__":
    unittest.main()
