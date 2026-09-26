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
        """Читаем сам список семей: claude в нём быть не может ни при каких условиях."""
        text = SECOND.read_text(encoding="utf-8")
        table = text.split("FAMILIES = [")[1].split("\n]")[0]
        self.assertNotIn('"claude"', table,
                         "claude в списке вторых мнений — это одно мнение в двух шляпах")
        self.assertIn('"openai"', table)
        self.assertIn('"google"', table)


class TestList(Base):
    def test_says_plainly_when_there_is_no_second_company(self):
        out = self.run_second("list")
        self.assertEqual(out.returncode, 1)
        self.assertIn("нет", out.stdout.lower())
        self.assertIn("браузер", out.stdout.lower(),
                      "нет второй программы — обязан показать бесплатный путь, а не тупик")

    def test_finds_an_installed_program(self):
        fake_cli(self.bin, "codex", 'echo "второй ответ"\n')
        out = self.run_second("list")
        self.assertEqual(out.returncode, 0)
        self.assertIn("ChatGPT", out.stdout)

    def test_one_seat_per_company(self):
        """agy и gemini — одна компания. Два места одной компании — не два мнения."""
        fake_cli(self.bin, "agy", 'echo x\n')
        fake_cli(self.bin, "gemini", 'echo x\n')
        out = self.run_second("list")
        self.assertEqual(out.stdout.count("Gemini"), 1,
                         "две программы Google посчитаны как два мнения")


class TestAsk(Base):
    def test_brings_the_answer_back(self):
        fake_cli(self.bin, "codex", 'echo "срок четырнадцать дней"\n')
        out = self.run_second("ask", "какой срок?")
        self.assertEqual(out.returncode, 0, out.stdout)
        got = json.loads(out.stdout)
        self.assertTrue(got["ok"])
        self.assertEqual(got["семья"], "openai")
        self.assertIn("четырнадцать", got["ответ"])

    def test_refuses_when_nobody_is_there(self):
        out = self.run_second("ask", "вопрос")
        self.assertEqual(out.returncode, 1)
        self.assertFalse(json.loads(out.stdout)["ok"])

    def test_exhausted_allowance_is_said_in_plain_words(self):
        fake_cli(self.bin, "codex", 'echo "429 rate limit exceeded" >&2\nexit 1\n')
        out = self.run_second("ask", "вопрос")
        got = json.loads(out.stdout)
        self.assertFalse(got["ok"])
        self.assertIn("запас", got["почему"],
                      "кончившийся лимит обязан объясняться словами, а не кодом 429")

    def test_a_silent_program_is_a_failure_not_an_empty_answer(self):
        fake_cli(self.bin, "codex", 'exit 0\n')       # успех, но пусто
        out = self.run_second("ask", "вопрос")
        self.assertEqual(out.returncode, 1)
        self.assertFalse(json.loads(out.stdout)["ok"],
                         "пустой ответ — это «не ответил», а не согласие")

    def test_timeout_is_reported_not_waited_on(self):
        fake_cli(self.bin, "codex", '/bin/sleep 30\n')
        env = dict(self.env, DUOCALL_TIMEOUT="1")
        out = self.run_second("ask", "вопрос", env=env)
        self.assertEqual(out.returncode, 1)
        self.assertIn("не ответил за", json.loads(out.stdout)["почему"])

    def test_question_reaches_the_second_ai_unchanged(self):
        fake_cli(self.bin, "codex", 'printf "%s" "$*"\n')
        question = "какой срок расторжения по этому договору?"
        out = self.run_second("ask", question)
        got = json.loads(out.stdout)
        self.assertIn(question, got["ответ"],
                      "вопрос обязан уйти как есть: пересказанный вопрос — не второе мнение")

    def test_named_program_that_is_absent_is_refused_not_substituted(self):
        fake_cli(self.bin, "codex", 'echo x\n')
        out = self.run_second("ask", "вопрос", "--who", "grok")
        self.assertEqual(out.returncode, 1)
        self.assertIn("нет", json.loads(out.stdout)["почему"],
                      "просили grok — подсовывать вместо него другого нельзя")


if __name__ == "__main__":
    unittest.main()
