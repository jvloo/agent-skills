"""Black-box checks of both installed helper copies using a fake CLI."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/fake_cli.py"


def is_running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # Linux containers can retain dead grandchildren as zombies until init reaps them.
    if sys.platform.startswith("linux"):
        try:
            state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].strip().split()[0]
            return state != "Z"
        except FileNotFoundError:
            return False
    return True


@unittest.skipUnless(sys.platform == "darwin" or sys.platform.startswith("linux"), "POSIX runner")
class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="worker-tests-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def launch(self, provider, scenario="success", prompt="fixture", structured=False, timeout=5, wait=True):
        case = self.directory / (provider + "-" + scenario)
        case.mkdir()
        args_file = case / "argv.json"
        child_file = case / "child.pid"
        args_file.write_text(json.dumps([sys.executable, str(FIXTURE), scenario, provider, str(child_file)]))
        out = case / "run"
        cmd = [sys.executable, str(ROOT / f"skills/meta-agent/use-{provider}/scripts/run_worker.py"),
               "--provider", provider, "--argv-file", str(args_file), "--cwd", str(case),
               "--timeout", str(timeout), "--output-dir", str(out)]
        if structured:
            cmd.append("--structured")
        if not wait:
            prompt_file = case / "prompt.txt"
            prompt_file.write_text(prompt)
            cmd.extend(["--prompt-file", str(prompt_file)])
            return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True), out, child_file
        result = subprocess.run(cmd, input=prompt, text=True, capture_output=True, timeout=15)
        self.assertTrue((out / "run.json").exists(), result.stderr + result.stdout)
        manifest = json.loads((out / "run.json").read_text())
        return result, manifest, out

    def test_literal_prompt_transport_and_private_logs(self):
        prompt = "quotes ' \" `touch unexpected` $(touch unexpected) $HOME\nUnicode: café 雪"
        for provider in ("claude", "codex"):
            with self.subTest(provider=provider):
                result, record, out = self.launch(provider, prompt=prompt)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(record["runtime_status"], "succeeded")
                self.assertEqual((out / "result.txt").read_text(), prompt)
                self.assertFalse((out.parent / "unexpected").exists())
                self.assertIn("fixture diagnostic", (out / "stderr.txt").read_text())
                self.assertNotIn(prompt, (out / "run.json").read_text())
                self.assertEqual(out.stat().st_mode & 0o777, 0o700)
                for file in out.iterdir():
                    self.assertEqual(file.stat().st_mode & 0o777, 0o600, str(file))

    def test_structured_blocked_is_successful_execution(self):
        for provider in ("claude", "codex"):
            with self.subTest(provider=provider):
                result, record, out = self.launch(provider, "structured", structured=True)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(record["runtime_status"], "succeeded")
                self.assertEqual(record["task_status"], "blocked")
                self.assertEqual(json.loads((out / "result.json").read_text())["status"], "blocked")

    def test_failed_or_incomplete_calls_are_never_accepted(self):
        for provider in ("claude", "codex"):
            for scenario in ("nonzero", "failure", "missing_completion", "truncated"):
                with self.subTest(provider=provider, scenario=scenario):
                    result, record, out = self.launch(provider, scenario)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotEqual(record["runtime_status"], "succeeded")
                    self.assertTrue((out / "stdout.txt").read_text())

    def test_invalid_handoffs_rejected(self):
        for provider in ("claude", "codex"):
            for scenario in ("structured_extra", "structured_missing", "structured_wrong_type", "success"):
                with self.subTest(provider=provider, scenario=scenario):
                    result, record, _ = self.launch(provider, scenario, structured=True)
                    self.assertEqual(result.returncode, 5, result.stderr + result.stdout)
                    self.assertEqual(record["runtime_status"], "invalid_output")

    def test_claude_stream_json(self):
        result, record, out = self.launch("claude", "stream")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(record["runtime_status"], "succeeded")

    def test_claude_prompt_suggestion_can_follow_result(self):
        for scenario in ("suggestion_tail", "idle_tail", "task_completed_tail", "completed"):
            with self.subTest(scenario=scenario):
                result, record, _ = self.launch("claude", scenario)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                self.assertEqual(record["runtime_status"], "succeeded")

    def test_claude_unfinished_or_failed_tail_is_incomplete(self):
        for scenario in ("running_tail", "requires_action_tail", "task_failed_tail", "task_stopped_tail"):
            with self.subTest(scenario=scenario):
                result, record, _ = self.launch("claude", scenario)
                self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                self.assertEqual(record["runtime_status"], "incomplete")

    def test_tool_activity_after_result_is_incomplete(self):
        for provider in ("claude", "codex"):
            with self.subTest(provider=provider):
                result, record, _ = self.launch(provider, "tool_tail")
                self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                self.assertEqual(record["runtime_status"], "incomplete")

    def test_claude_interrupted_success_envelope_is_incomplete(self):
        for reason in ("aborted_tools", "aborted_streaming", "tool_deferred", "hook_stopped", "background_requested", "max_tokens"):
            with self.subTest(reason=reason):
                result, record, _ = self.launch("claude", reason)
                self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
                self.assertEqual(record["runtime_status"], "incomplete")

    def test_timeout_stops_child_preserves_partial_output(self):
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            for provider in ("claude", "codex"):
                with self.subTest(provider=provider):
                    result, record, out = self.launch(provider, "timeout", timeout=0.5)
                    self.assertEqual(result.returncode, 3, result.stderr + result.stdout)
                    self.assertEqual(record["runtime_status"], "timed_out")
                    pid = int((out.parent / "child.pid").read_text())
                    self.assertFalse(is_running(pid), f"owned child {pid} still running")
                    self.assertIn("fixture.partial", (out / "stdout.txt").read_text())
                    self.assertIsNone(unrelated.poll())
        finally:
            unrelated.terminate()
            unrelated.wait(timeout=5)

    def test_successful_parent_with_live_child_is_incomplete(self):
        result, record, out = self.launch("codex", "leftover_child")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(record["runtime_status"], "incomplete")
        self.assertFalse(is_running(int((out.parent / "child.pid").read_text())))

    def test_cancellation_stops_owned_child(self):
        proc, out, child_file = self.launch("claude", "cancel", wait=False, timeout=10)
        try:
            until = time.monotonic() + 5
            while not child_file.exists() and time.monotonic() < until and proc.poll() is None:
                time.sleep(0.02)
            self.assertTrue(child_file.exists())
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=8)
            self.assertEqual(proc.returncode, 4, stderr + stdout)
            self.assertEqual(json.loads((out / "run.json").read_text())["runtime_status"], "cancelled")
            self.assertFalse(is_running(int(child_file.read_text())))
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()
            if child_file.exists() and is_running(int(child_file.read_text())):
                os.kill(int(child_file.read_text()), signal.SIGKILL)

    def test_invalid_launch_does_not_overwrite_existing_output(self):
        out = self.directory / "existing"
        out.mkdir()
        sentinel = out / "keep"
        sentinel.write_text("user data")
        args_file = self.directory / "argv.json"
        args_file.write_text(json.dumps([sys.executable, str(FIXTURE), "success", "codex"]))
        cmd = [sys.executable, str(ROOT / "skills/meta-agent/use-codex/scripts/run_worker.py"),
               "--provider", "codex", "--argv-file", str(args_file), "--cwd", str(self.directory),
               "--timeout", "5", "--output-dir", str(out)]
        result = subprocess.run(cmd, input="test", text=True, capture_output=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sentinel.read_text(), "user data")


if __name__ == "__main__":
    unittest.main()
