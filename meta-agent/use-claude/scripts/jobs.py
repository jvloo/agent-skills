#!/usr/bin/env python3
"""Recoverable local CLI jobs. Local POSIX filesystems only; see references/jobs.md."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

import launch_profiles as profiles
from run_worker import EXIT_CODES, InputError, SKILL_VERSION, strict_json

FORMAT = 1


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def atomic(path, value):
    """Replace one journal record durably; never expose partially written JSON."""
    fd, temp = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(encode(value) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def load(path):
    with path.open() as stream:
        return strict_json(stream.read())


def private_dir(path):
    if not path.exists():
        path.mkdir(mode=0o700, parents=True)
    if path.is_symlink() or not path.is_dir() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise InputError('job store must be an owner-only real directory')


@contextlib.contextmanager
def lock(path, shared=False):
    fd = os.open(str(path), os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        try:
            fcntl.flock(fd, (fcntl.LOCK_SH if shared else fcntl.LOCK_EX) | fcntl.LOCK_NB)
        except BlockingIOError:
            raise InputError('job or workspace is busy') from None
        yield fd
    finally:
        # Close, rather than LOCK_UN: a surviving child can still own the inherited lease.
        os.close(fd)


def busy(job):
    try:
        with lock(job/'lock'):
            return False
    except InputError:
        return True


def snapshot(config):
    cwd = Path(config['cwd'])
    result = {}
    size = 0
    def visit(path):
        nonlocal size
        relative = str(path.relative_to(cwd))
        if path.is_symlink():
            result[relative] = ['symlink', os.readlink(path)]
        elif path.is_dir():
            result[relative] = ['directory']
            for child in sorted(path.iterdir()):
                if child.name != '.git':
                    visit(child)
        elif path.is_file():
            size += path.stat().st_size
            if size > 128 * 1024 * 1024:
                raise InputError('snapshot exceeds 128 MiB; narrow --watch to task inputs')
            result[relative] = ['file', hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777]
        elif not path.exists():
            result[relative] = ['missing']
        else:
            raise InputError('snapshot contains an unsupported special file')
        if len(result) > 20000:
            raise InputError('snapshot exceeds 20000 entries; narrow --watch to task inputs')
    for value in config['watch']:
        visit(cwd/value)
    # Git metadata is excluded from file hashing, but changes of revision remain observable.
    git = cwd/'.git'
    if git.exists():
        directory = git
        if git.is_file():
            text = git.read_text().strip()
            if text.startswith('gitdir: '):
                directory = (cwd/text[8:]).resolve()
        head = directory/'HEAD'
        if head.is_file():
            value = head.read_text().strip()
            result['@git:HEAD'] = value
            if value.startswith('ref: '):
                common = directory
                if (directory/'commondir').exists():
                    common = (directory/(directory/'commondir').read_text().strip()).resolve()
                ref = common/value[5:]
                result['@git:ref'] = ref.read_text().strip() if ref.exists() else None
                result['@git:packed'] = hashlib.sha256((common/'packed-refs').read_bytes()).hexdigest() if (common/'packed-refs').exists() else None
    return result


def changed(left, right):
    return sorted(key for key in left.keys() | right.keys() if left.get(key) != right.get(key))


def get_session(config, attempt):
    log = attempt/'run/stdout.txt'
    if not log.exists():
        return None
    with log.open(errors='replace') as stream:
        lines = stream.read(1024 * 1024).splitlines()
    for line in lines:
        try:
            event = strict_json(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if config['provider'] == 'codex' and event.get('type') == 'thread.started':
            return event.get('thread_id')
        if config['provider'] == 'claude' and event.get('type') in ('system', 'result'):
            if isinstance(event.get('session_id'), str):
                return event['session_id']
    return None


def inspect(job):
    private_dir(job)
    config = load(job/'config.json')
    state = load(job/'state.json')
    if state.get('config_digest') != digest(config):
        raise InputError('saved launch configuration changed; this job cannot be resumed')
    if state.get('format') != FORMAT:
        raise InputError('unsupported job journal version')
    attempt = job/('attempt-%03d' % state['attempt'])
    active = busy(job)
    result = {'job': str(job), 'attempt': state['attempt'], 'active': active,
              'phase': state['phase'], 'session_id': get_session(config, attempt),
              'expected_state': None, 'runtime_status': None, 'task_status': None}
    if active:
        return result
    manifest = None
    try:
        manifest = load(attempt/'run/run.json')
    except (OSError, ValueError):
        pass
    result['phase'] = 'finished' if manifest else (state['phase'] if state['phase'] in ('launch_failed', 'cancelled') else 'interrupted')
    if not manifest and state['phase'] == 'prepared' and time.time() - state['prepared_at'] < 5:
        result['phase'] = 'queued'
    if manifest:
        result.update(runtime_status=manifest['runtime_status'], task_status=manifest.get('task_status'),
                      session_id=manifest.get('session_id') or result['session_id'],
                      cleanup=manifest.get('process_group_cleanup'), artifacts=manifest.get('artifacts'))
    current = snapshot(config)
    before = load(attempt/'before.json')
    result['changes_from_start'] = changed(before, current)
    assigned = {str(Path(p).relative_to(Path(config['cwd']))) for p in config['write_files']}
    result['changes_outside_assignment'] = [p for p in result['changes_from_start'] if p not in assigned]
    result['changes_since_completion'] = changed(load(attempt/'after.json'), current) if (attempt/'after.json').exists() else None
    result['expected_state'] = digest([state, manifest, current])
    result['session_available'] = bool(result['session_id'] and profiles.session_file(config, result['session_id']))
    result['resumable'] = bool(manifest and result['session_available'] and manifest.get('process_group_cleanup') != 'unconfirmed'
                               and state['attempt'] < config['max_attempts'])
    return result


def prepare(job, config, number, prompt_file, session_id=None, expected_snapshot=None):
    prompt = prompt_file.read_bytes()
    if not prompt.strip() or len(prompt) > 10 * 1024 * 1024:
        raise InputError('supply a nonempty fresh prompt file of at most 10 MiB')
    version = profiles.inspect_cli(config, resume=session_id is not None)
    if session_id and not profiles.session_file(config, session_id):
        raise InputError('exact provider session is not available in the current session store')
    before = snapshot(config)
    if expected_snapshot is not None and before != expected_snapshot:
        raise InputError('workspace changed during preflight; inspect before resuming')
    attempt = job/('attempt-%03d' % number)
    attempt.mkdir(mode=0o700)
    with os.fdopen(os.open(str(attempt/'prompt.txt'), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'wb') as stream:
        stream.write(prompt)
        stream.flush()
        os.fsync(stream.fileno())
    atomic(attempt/'argv.json', profiles.build(config, session_id))
    atomic(attempt/'before.json', before)
    atomic(attempt/'preflight.json', {'cli_version': version, 'time': time.time(), 'resume_session': session_id})
    atomic(job/'state.json', {'format': FORMAT, 'skill_version': SKILL_VERSION, 'attempt': number,
                            'phase': 'prepared', 'config_digest': digest(config), 'prepared_at': time.time()})


def spawn(job):
    fd = os.open(str(job/'supervisor.log'), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '_guard', str(job)],
                         stdin=subprocess.DEVNULL, stdout=fd, stderr=fd, start_new_session=True,
                         close_fds=True)
    finally:
        os.close(fd)


def guard(job):
    with lock(job/'lock') as job_fd:
        config = load(job/'config.json')
        state = load(job/'state.json')
        if state.get('config_digest') != digest(config):
            raise InputError('saved launch configuration changed')
        if state['phase'] != 'prepared':
            raise InputError('attempt has already been claimed; it will not be replayed')
        attempt = job/('attempt-%03d' % state['attempt'])
        workspace_lock = job.parent/'.locks'/digest(config['cwd'])
        try:
            with lock(workspace_lock, shared=config['profile'] == 'consult') as workspace_fd:
                if (attempt/'cancel.json').exists():
                    state.update(phase='cancelled', finished_at=time.time())
                    atomic(job/'state.json', state)
                    return
                if snapshot(config) != load(attempt/'before.json'):
                    raise InputError('workspace changed before launch; no dispatch performed')
                state.update(phase='running', supervisor_pid=os.getpid(), started_at=time.time(),
                             deadline_at=time.time() + config['timeout'])
                atomic(job/'state.json', state)
                command = [sys.executable, str(Path(__file__).with_name('run_worker.py')),
                           '--provider', config['provider'], '--argv-file', str(attempt/'argv.json'),
                           '--cwd', config['cwd'], '--timeout', str(config['timeout']),
                           '--output-dir', str(attempt/'run'), '--prompt-file', str(attempt/'prompt.txt')]
                if config['structured']:
                    command += ['--structured']
                with (attempt/'helper.log').open('xb') as log:
                    os.chmod(log.name, 0o600)
                    worker = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                              pass_fds=(job_fd, workspace_fd))
                    state['helper_pid'] = worker.pid
                    atomic(job/'state.json', state)
                    cancelled = False
                    stop_at = None
                    backup_deadline = time.monotonic() + config['timeout'] + 5
                    while worker.poll() is None:
                        if ((attempt/'cancel.json').exists() or time.monotonic() > backup_deadline) and not cancelled:
                            worker.send_signal(signal.SIGTERM)
                            cancelled = True
                            stop_at = time.monotonic() + 5
                        if stop_at is not None and time.monotonic() > stop_at:
                            worker.kill()
                        session_id = get_session(config, attempt)
                        if session_id and state.get('session_id') != session_id:
                            state['session_id'] = session_id
                            atomic(job/'state.json', state)
                        time.sleep(0.05)
                atomic(attempt/'after.json', snapshot(config))
                state.update(phase='finished', finished_at=time.time(), helper_exit=worker.returncode)
        except Exception as error:
            state.update(phase='launch_failed', error=type(error).__name__)
            atomic(job/'state.json', state)
            raise
        atomic(job/'state.json', state)


def configuration(args):
    cwd = args.cwd.resolve(strict=True)
    if not cwd.is_dir():
        raise InputError('cwd must be a directory')
    cli = args.cli.resolve(strict=True)
    if not args.model.strip() or '\0' in args.model:
        raise InputError('an explicit verified model is required')
    if not math.isfinite(args.timeout) or args.timeout <= 0 or not 1 <= args.max_attempts <= 10:
        raise InputError('timeout must be finite and positive; max-attempts must be 1..10')
    if args.provider == 'claude' and (args.budget_usd is None or not math.isfinite(args.budget_usd) or args.budget_usd <= 0):
        raise InputError('Claude requires a positive finite budget-usd stopping threshold')
    if args.provider == 'codex' and args.budget_usd is not None:
        raise InputError('Codex has no profile dollar cap; do not supply budget-usd')
    files = []
    for item in args.write_file:
        path = (cwd/item).resolve()
        if cwd not in path.parents or any(part in ('.git', '.codex', '.agents', '.claude') for part in path.relative_to(cwd).parts):
            raise InputError('write files must stay inside the workspace and outside protected configuration')
        if any(char in str(path) for char in '*?[],\n\r'):
            raise InputError('file path needs custom permission escaping; use the raw runner')
        files.append(str(path))
    if (args.profile == 'edit') != bool(files):
        raise InputError('edit needs write-file assignments; consult cannot grant write files')
    watch = args.watch or ['.']
    for value in watch:
        path = cwd/value
        if path.is_absolute() and not (path.resolve() == cwd or cwd in path.resolve().parents):
            raise InputError('watch inputs must stay inside cwd')
    return dict(provider=args.provider, cli=str(cli), cwd=str(cwd), profile=args.profile,
                model=args.model, effort=args.effort, budget_usd=args.budget_usd, write_files=files,
                watch=watch, timeout=args.timeout, max_attempts=args.max_attempts,
                structured=args.structured, session_root=profiles.session_root(args.provider))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('start', 'plan'):
        p = sub.add_parser(name)
        p.add_argument('--provider', choices=('claude', 'codex'), required=True)
        p.add_argument('--cli', type=Path, required=True)
        p.add_argument('--cwd', type=Path, required=True)
        p.add_argument('--profile', choices=('consult', 'edit'), default='consult')
        p.add_argument('--model', required=True)
        p.add_argument('--effort')
        p.add_argument('--budget-usd', type=float)
        p.add_argument('--timeout', type=float, required=True)
        p.add_argument('--max-attempts', type=int, default=3)
        p.add_argument('--write-file', action='append', default=[])
        p.add_argument('--watch', action='append', default=[])
        p.add_argument('--structured', action='store_true')
        if name == 'start':
            p.add_argument('--store', type=Path, required=True)
            p.add_argument('--name', required=True)
            p.add_argument('--prompt-file', type=Path, required=True)
            p.add_argument('--wait', action='store_true')
    for name in ('status', 'cancel', 'resume', '_guard'):
        p = sub.add_parser(name)
        p.add_argument('job', type=Path)
        if name == 'cancel':
            p.add_argument('--attempt', type=int, required=True)
        if name == 'resume':
            p.add_argument('--expected-state', required=True)
            p.add_argument('--prompt-file', type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != 'darwin' and not sys.platform.startswith('linux'):
        raise InputError('local jobs require macOS or Linux')
    if args.command in ('start', 'plan'):
        config = configuration(args)
        if args.command == 'plan':
            print(encode({'configuration': config, 'argv': profiles.build(config)}))
            return 0
        store = args.store.absolute()
        private_dir(store)
        store = store.resolve()
        if store == Path(config['cwd']) or Path(config['cwd']) in store.parents:
            raise InputError('keep job state outside the workspace')
        if not args.name or len(args.name) > 80 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.name):
            raise InputError('job name must contain only letters, digits, hyphens or underscores')
        private_dir(store/'.locks')
        job = store/args.name
        job.mkdir(mode=0o700)
        atomic(job/'config.json', config)
        with lock(job/'lock'):
            prepare(job, config, 1, args.prompt_file)
        spawn(job)
        print(encode({'job': str(job), 'phase': 'prepared', 'attempt': 1}), flush=True)
        if args.wait:
            # Losing this client does not kill the separately supervised job.
            while True:
                state = inspect(job)
                if not state['active'] and state['phase'] == 'finished':
                    print(encode(state))
                    return EXIT_CODES.get(state['runtime_status'], 1)
                if not state['active'] and state['phase'] != 'queued':
                    print(encode(state))
                    return 1
                time.sleep(0.1)
        return 0
    job = args.job.resolve(strict=True)
    if args.command == '_guard':
        guard(job)
    elif args.command == 'status':
        print(encode(inspect(job)))
    elif args.command == 'cancel':
        state = load(job/'state.json')
        if state['attempt'] != args.attempt:
            raise InputError('attempt changed; inspect the job before cancelling')
        atomic(job/('attempt-%03d' % args.attempt)/'cancel.json', {'attempt': args.attempt, 'requested_at': time.time()})
        print(encode({'job': str(job), 'attempt': args.attempt, 'cancel_requested': True}))
    elif args.command == 'resume':
        current = inspect(job)
        if current['active'] or not current.get('resumable'):
            raise InputError('job is active, uncertain, unavailable, or out of attempts; inspect before recovery')
        with lock(job/'lock'):
            config = load(job/'config.json')
            state = load(job/'state.json')
            attempt = job/('attempt-%03d' % state['attempt'])
            current_snapshot = snapshot(config)
            token = digest([state, load(attempt/'run/run.json'), current_snapshot])
            if token != args.expected_state:
                raise InputError('state/workspace changed; inspect current status and artifacts before resuming')
            prepare(job, config, state['attempt'] + 1, args.prompt_file, current['session_id'], current_snapshot)
        spawn(job)
        print(encode({'job': str(job), 'phase': 'prepared', 'attempt': state['attempt'] + 1}))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (InputError, OSError, ValueError, KeyError) as error:
        print(encode({'error': str(error) if isinstance(error, InputError) else type(error).__name__}), file=sys.stderr)
        sys.exit(64)
