"""Conservative first-party CLI profiles; arbitrary providers use run_worker.py."""
import json
import os
from pathlib import Path
import subprocess
import uuid

from run_worker import InputError

CODEX_DISABLED = ('apps', 'plugins', 'hooks', 'memories', 'multi_agent', 'browser_use',
                  'computer_use', 'image_generation', 'remote_plugin', 'shell_snapshot',
                  'skill_mcp_dependency_install', 'in_app_browser')

def inspect_cli(config, resume=False):
    """Non-generating checks in the same cwd/auth context used for dispatch."""
    cli = config['cli']
    provider = config['provider']
    if not Path(cli).is_file() or not os.access(cli, os.X_OK):
        raise InputError('CLI executable is unavailable')
    forbidden = ('ANTHROPIC_API_KEY', 'ANTHROPIC_BASE_URL', 'CLAUDE_CODE_USE_BEDROCK',
                 'CLAUDE_CODE_USE_VERTEX', 'CLAUDE_CODE_USE_FOUNDRY') if provider == 'claude' else (
                     'OPENAI_BASE_URL', 'OPENAI_API_KEY', 'CODEX_API_KEY')
    if any(os.environ.get(key) for key in forbidden):
        raise InputError('profile requires the normal account route; use the raw runner for custom routes')

    def call(args):
        try:
            result = subprocess.run([cli] + args, cwd=config['cwd'], capture_output=True,
                                    text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            raise InputError('CLI preflight could not complete') from None
        if result.returncode:
            raise InputError('CLI preflight failed; inspect authentication/runtime access separately')
        return result.stdout + result.stderr

    version = call(['--version']).strip()
    help_args = ['--help'] if provider == 'claude' else ['exec'] + (['resume'] if resume else []) + ['--help']
    help_text = call(help_args)
    required = (['--restricted', '--safe-mode', '--strict-mcp-config', '--permission-prompts',
                 '--permission-mode', '--tools', '--disallowedTools', '--no-chrome', '--output-format',
                 '--verbose', '--max-budget-usd', '--model', '--resume' if resume else '--session-id']
                if provider == 'claude' else ['--ignore-user-config', '--strict-config', '--config', '--disable',
                                             '--skip-git-repo-check', '--model', '--json'])
    if provider == 'codex' and not resume:
        required.append('--sandbox')
    if config['structured']:
        required.append('--json-schema' if provider == 'claude' else '--output-schema')
    if provider == 'claude' and config['profile'] == 'edit':
        required.append('--allowedTools')
    if provider == 'claude' and config.get('effort'):
        required.append('--effort')
    if any(flag not in help_text for flag in required):
        raise InputError('installed CLI does not support this profile; use verified raw arguments')
    if provider == 'codex':
        features = {line.split()[0] for line in call(['features', 'list']).splitlines() if line.split()}
        if not set(CODEX_DISABLED).issubset(features):
            raise InputError('installed CLI lacks required capability switches; use verified raw arguments')
    auth = call(['auth', 'status'] if provider == 'claude' else ['login', 'status'])
    if provider == 'claude':
        try:
            status = json.loads(auth)
        except ValueError:
            raise InputError('Claude account status was not valid JSON') from None
        if (status.get('loggedIn') is not True or status.get('authMethod') != 'claude.ai'
                or status.get('apiProvider') != 'firstParty'):
            raise InputError('profile requires a usable first-party Claude account')
    elif 'Logged in using ChatGPT' not in auth:
        raise InputError('profile requires a usable ChatGPT login')
    return version


def session_root(provider):
    if provider == 'claude':
        return str(Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home()/'.claude'))).resolve()/'projects')
    return str(Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex'))).resolve()/'sessions')


def session_file(config, session_id):
    """Require local persisted evidence, not just an ID returned by a transient turn."""
    try:
        uuid.UUID(session_id)
    except (ValueError, TypeError, AttributeError):
        return None
    root = Path(config['session_root'])
    if root != Path(session_root(config['provider'])):
        raise InputError('session-store context changed')
    pattern = session_id + '.jsonl' if config['provider'] == 'claude' else '*' + session_id + '.jsonl'
    for path in root.rglob(pattern):
        if path.is_symlink() or root not in path.resolve().parents:
            continue
        try:
            with path.open() as stream:
                lines = stream.read(262144).splitlines()
            for line in lines:
                try:
                    item = json.loads(line)
                except ValueError:
                    continue
                if isinstance(item, dict) and (item.get('sessionId') == session_id or
                        item.get('type') == 'session_meta' and isinstance(item.get('payload'), dict)
                        and item['payload'].get('id') == session_id):
                    return str(path)
        except (OSError, UnicodeError):
            continue
    return None


def build(config, session_id=None):
    provider = config['provider']
    editing = config['profile'] == 'edit'
    schema = Path(__file__).resolve().parent.parent/'assets/result.schema.json'
    if provider == 'claude':
        argv = [config['cli'], '-p', '--restricted', '--safe-mode', '--strict-mcp-config',
                '--permission-mode', 'dontAsk' if editing else 'plan', '--permission-prompts', 'none',
                '--tools', 'Read,Grep,Glob,Edit' if editing else 'Read,Grep,Glob',
                '--disallowedTools', 'Agent,Bash,WebFetch,WebSearch,mcp__*', '--no-chrome',
                '--output-format', 'stream-json', '--verbose', '--max-budget-usd', str(config['budget_usd']),
                '--model', config['model']]
        if editing:
            argv += ['--allowedTools', ','.join('Edit(/' + p + ')' for p in config['write_files'])]
        if config.get('effort'):
            argv += ['--effort', config['effort']]
        if config['structured']:
            argv += ['--json-schema', schema.read_text()]
        argv += ['--resume', session_id] if session_id else ['--session-id', str(uuid.uuid4())]
    else:
        argv = [config['cli'], 'exec'] + (['resume'] if session_id else [])
        argv += ['--ignore-user-config', '--strict-config', '-c', 'approval_policy="never"',
                 '-c', 'agents.enabled=false', '-c', 'model_provider="openai"',
                 '-c', 'sandbox_workspace_write.network_access=false', '-c', 'web_search="disabled"',
                 '--model', config['model'], '--json', '--skip-git-repo-check']
        for feature in CODEX_DISABLED:
            argv += ['--disable', feature]
        sandbox = 'workspace-write' if editing else 'read-only'
        argv += ['-c', 'sandbox_mode="' + sandbox + '"'] if session_id else ['--sandbox', sandbox]
        if config.get('effort'):
            argv += ['-c', 'model_reasoning_effort=' + json.dumps(config['effort'])]
        if config['structured']:
            argv += ['--output-schema', str(schema)]
        argv += [session_id, '-'] if session_id else ['-']
    return argv
