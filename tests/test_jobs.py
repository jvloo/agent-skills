"""Black-box restart/recovery tests. All provider calls use explicit local test doubles."""
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == 'darwin' or sys.platform.startswith('linux'), 'POSIX jobs')
class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='recoverable-jobs-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, CLAUDE_CONFIG_DIR=str(self.root/'claude-state'),
                        CODEX_HOME=str(self.root/'codex-state'), JOB_TEST_DISPATCHES=str(self.root/'dispatches.jsonl'))
        for key in ('ANTHROPIC_API_KEY', 'ANTHROPIC_BASE_URL', 'CLAUDE_CODE_USE_BEDROCK',
                    'CLAUDE_CODE_USE_VERTEX', 'CLAUDE_CODE_USE_FOUNDRY', 'OPENAI_BASE_URL', 'OPENAI_API_KEY', 'CODEX_API_KEY'):
            self.env.pop(key, None)
        for provider in ('claude', 'codex'):
            cli = self.root/('fake-'+provider)
            shutil.copyfile(ROOT/'tests/fixtures/fake_job_cli.py', cli)
            cli.chmod(0o700)
        self.workspace = self.root/'workspace'
        self.workspace.mkdir()
        (self.workspace/'notes.txt').write_text('user edit\n')

    def command(self, provider, *args):
        return [sys.executable, str(ROOT/f'meta-agent/use-{provider}/scripts/jobs.py'), *map(str, args)]

    def call(self, provider, *args, ok=True):
        result = subprocess.run(self.command(provider, *args), env=self.env, capture_output=True, text=True, timeout=20)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result

    def prompt(self, name, **data):
        path = self.root/(name+'.json')
        path.write_text(json.dumps(data))
        return path

    def start_args(self, provider, name, prompt, timeout=5, edit=False, wait=False):
        args = ['start', '--provider', provider, '--cli', self.root/('fake-'+provider),
                '--cwd', self.workspace, '--model', 'fixture-model', '--timeout', timeout,
                '--store', self.root/'jobs', '--name', name,
                '--prompt-file', prompt, '--structured']
        if edit:
            args += ['--profile', 'edit', '--write-file', 'notes.txt']
        if provider == 'claude':
            args += ['--budget-usd', 1]
        if wait:
            args += ['--wait']
        return args

    def status(self, provider, name):
        return json.loads(self.call(provider, 'status', self.root/'jobs'/name).stdout)

    def until(self, predicate, seconds=12):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(0.04)
        self.fail('condition did not become true')

    def finished(self, provider, name):
        return self.until(lambda: (s if not s['active'] and s['phase'] not in ('queued', 'prepared', 'running', 'interrupted') else None)
                          if (s := self.status(provider, name)) else None)

    def dispatches(self):
        path = self.root/'dispatches.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_profile_rules_and_exact_resume(self):
        for provider in ('claude', 'codex'):
            with self.subTest(provider=provider):
                name = provider+'-resume'
                self.call(provider, *self.start_args(provider, name, self.prompt(name, marker='original'), edit=True))
                first = self.finished(provider, name)
                self.assertEqual(first['runtime_status'], 'succeeded')
                self.assertTrue(first['session_available'])
                self.call(provider, 'resume', first['job'], '--expected-state', first['expected_state'],
                          '--prompt-file', self.prompt(name+'-next', answer='must not replay'))
                second = self.finished(provider, name)
                self.assertEqual(second['session_id'], first['session_id'])
                result = json.loads((Path(first['job'])/'attempt-002/run/result.json').read_text())
                self.assertEqual(result['summary'], 'original')
                argv = self.dispatches()[-1]['argv']
                if provider == 'claude':
                    self.assertIn('Edit(/'+str((self.workspace/'notes.txt').resolve())+')', argv)
                    self.assertIn('--resume', argv)
                else:
                    self.assertIn('sandbox_mode="workspace-write"', argv)
                    self.assertIn('--skip-git-repo-check', argv)
                    disabled = {argv[i + 1] for i, value in enumerate(argv) if value == '--disable'}
                    self.assertTrue({'plugins', 'apps', 'hooks', 'browser_use', 'multi_agent'} <= disabled)
                self.assertEqual((self.workspace/'notes.txt').read_text(), 'user edit\n')

    def test_client_death_does_not_lose_completion_or_deadline(self):
        for provider in ('claude', 'codex'):
            name = provider+'-client'
            client = subprocess.Popen(self.command(provider, *self.start_args(provider, name,
                                      self.prompt(name, sleep=1), wait=True)), env=self.env,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                line = client.stdout.readline()
                self.assertIn('job', json.loads(line))
                client.kill()
                client.wait(timeout=3)
                result = self.finished(provider, name)
                self.assertEqual(result['runtime_status'], 'succeeded')
            finally:
                if client.poll() is None:
                    client.kill()
                    client.wait()
                client.stdout.close()
                client.stderr.close()

    def test_supervisor_death_retains_worker_lease_and_timeout(self):
        for provider in ('claude', 'codex'):
            name = provider+'-guardian'
            self.call(provider, *self.start_args(provider, name, self.prompt(name, sleep=20), timeout=1.5))
            self.until(lambda: self.status(provider, name).get('session_id'))
            job = self.root/'jobs'/name
            state = json.loads((job/'state.json').read_text())
            os.kill(state['supervisor_pid'], signal.SIGKILL)
            self.assertTrue(self.status(provider, name)['active'])
            result = self.finished(provider, name)
            self.assertEqual(result['runtime_status'], 'timed_out')
            self.assertEqual(result['cleanup'], 'stopped')

    def test_stale_workspace_and_missing_session_block_dispatch(self):
        provider, name = 'codex', 'guarded-resume'
        self.call(provider, *self.start_args(provider, name, self.prompt(name)))
        status = self.finished(provider, name)
        (self.workspace/'notes.txt').write_text('new user edit')
        next_prompt = self.prompt('next')
        result = self.call(provider, 'resume', status['job'], '--expected-state', status['expected_state'],
                           '--prompt-file', next_prompt, ok=False)
        self.assertNotEqual(result.returncode, 0)
        fresh = self.status(provider, name)
        self.assertIn('notes.txt', fresh['changes_since_completion'])
        for file in (self.root/'codex-state/sessions').glob('*.jsonl'):
            file.unlink()
        result = self.call(provider, 'resume', status['job'], '--expected-state', fresh['expected_state'],
                           '--prompt-file', next_prompt, ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.dispatches()), 1)

    def test_resume_checks_its_own_cli_interface(self):
        provider, name = 'codex', 'resume-interface'
        self.call(provider, *self.start_args(provider, name, self.prompt(name)))
        status = self.finished(provider, name)
        self.env['JOB_TEST_RESUME_UNSUPPORTED'] = '1'
        result = self.call(provider, 'resume', status['job'], '--expected-state', status['expected_state'],
                           '--prompt-file', self.prompt('interface-next'), ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.dispatches()), 1)

    def test_concurrent_resume_never_duplicates_dispatch(self):
        provider, name = 'claude', 'race'
        self.call(provider, *self.start_args(provider, name, self.prompt(name)))
        state = self.finished(provider, name)
        args = ['resume', state['job'], '--expected-state', state['expected_state'], '--prompt-file', self.prompt('followup', sleep=0.5)]
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda _: self.call(provider, *args, ok=False), range(2)))
        self.assertEqual(sum(r.returncode == 0 for r in results), 1)
        self.finished(provider, name)
        self.assertEqual(len(self.dispatches()), 2)

    def test_cancel_is_attempt_specific_and_preserves_logs(self):
        for provider in ('claude', 'codex'):
            name = provider+'-cancel'
            self.call(provider, *self.start_args(provider, name, self.prompt(name, sleep=20)))
            self.until(lambda: self.status(provider, name).get('session_id'))
            self.call(provider, 'cancel', self.root/'jobs'/name, '--attempt', 1)
            state = self.finished(provider, name)
            self.assertEqual(state['runtime_status'], 'cancelled')
            self.assertEqual(state['cleanup'], 'stopped')
            self.assertTrue((Path(state['job'])/'attempt-001/run/stdout.txt').read_text())
            self.call(provider, 'resume', state['job'], '--expected-state', state['expected_state'],
                      '--prompt-file', self.prompt(name+'-again'))
            resumed = self.finished(provider, name)
            self.assertEqual(resumed['runtime_status'], 'succeeded')
            stale = self.call(provider, 'cancel', state['job'], '--attempt', 1, ok=False)
            self.assertNotEqual(stale.returncode, 0)

    def test_same_workspace_writers_are_serialized(self):
        provider = 'codex'
        self.call(provider, *self.start_args(provider, 'one', self.prompt('one', sleep=1.5), edit=True))
        self.until(lambda: self.status(provider, 'one').get('session_id'))
        self.call(provider, *self.start_args(provider, 'two', self.prompt('two'), edit=True))
        result = self.finished(provider, 'two')
        self.assertEqual(result['phase'], 'launch_failed')
        self.finished(provider, 'one')
        self.assertEqual(len(self.dispatches()), 1)

    def test_cancelling_one_reader_preserves_the_other_job(self):
        provider = 'codex'
        for name, delay in [('cancel-one', 20), ('keep-one', 1.5)]:
            self.call(provider, *self.start_args(provider, name, self.prompt(name, sleep=delay)))
            self.until(lambda: self.status(provider, name).get('session_id'))
        self.call(provider, 'cancel', self.root/'jobs/cancel-one', '--attempt', 1)
        self.assertEqual(self.finished(provider, 'cancel-one')['runtime_status'], 'cancelled')
        self.assertEqual(self.finished(provider, 'keep-one')['runtime_status'], 'succeeded')

    def test_saved_configuration_cannot_silently_change(self):
        provider, name = 'codex', 'config-integrity'
        self.call(provider, *self.start_args(provider, name, self.prompt(name)))
        status = self.finished(provider, name)
        config_path = Path(status['job'])/'config.json'
        config = json.loads(config_path.read_text())
        config['timeout'] += 1
        config_path.write_text(json.dumps(config))
        result = self.call(provider, 'resume', status['job'], '--expected-state', status['expected_state'],
                           '--prompt-file', self.prompt('config-next'), ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.dispatches()), 1)

    def test_unknown_outcome_is_never_replayed(self):
        provider, name = 'codex', 'uncertain'
        self.call(provider, *self.start_args(provider, name, self.prompt(name, sleep=20)))
        self.until(lambda: self.status(provider, name).get('session_id'))
        job = self.root/'jobs'/name
        state = json.loads((job/'state.json').read_text())
        pid = self.dispatches()[-1]['pid']
        try:
            os.kill(state['helper_pid'], signal.SIGKILL)
            self.until(lambda: not self.status(provider, name)['active'])
            result = self.status(provider, name)
            self.assertEqual(result['phase'], 'interrupted')
            attempt = self.call(provider, 'resume', job, '--expected-state', result['expected_state'],
                                '--prompt-file', self.prompt('uncertain-next'), ok=False)
            self.assertNotEqual(attempt.returncode, 0)
            self.assertEqual(len(self.dispatches()), 1)
        finally:
            # Test-owned process only; production cancellation never signals a saved PID.
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def test_attempt_limit_duplicate_name_and_private_journal(self):
        provider, name = 'codex', 'limits'
        args = self.start_args(provider, name, self.prompt(name)) + ['--max-attempts', 1]
        self.call(provider, *args)
        state = self.finished(provider, name)
        self.assertFalse(state['resumable'])
        self.assertNotEqual(self.call(provider, *args, ok=False).returncode, 0)
        self.assertEqual(len(self.dispatches()), 1)
        for path in (self.root/'jobs').rglob('*'):
            self.assertEqual(path.stat().st_mode & 0o077, 0, str(path))


if __name__ == '__main__':
    unittest.main()
