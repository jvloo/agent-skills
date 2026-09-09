#!/usr/bin/env python3
"""Explicit non-network test double for persisted provider sessions and job recovery."""
import json
import os
from pathlib import Path
import sys
import time
import uuid

args = sys.argv[1:]
provider = 'claude' if 'claude' in Path(sys.argv[0]).name else 'codex'
if '--version' in args:
    print('fixture-cli 1.0 (test double)')
    sys.exit(0)
if '--help' in args:
    help_text = ('--restricted --safe-mode --strict-mcp-config --permission-prompts --session-id '
                 '--max-budget-usd --json-schema --ignore-user-config --sandbox --output-schema --json '
                 '--permission-mode --tools --disallowedTools --no-chrome --output-format --verbose '
                 '--model --resume --strict-config --config --skip-git-repo-check --allowedTools --effort --disable')
    if 'resume' in args and os.environ.get('JOB_TEST_RESUME_UNSUPPORTED'):
        help_text = help_text.replace('--skip-git-repo-check', '')
    print(help_text)
    sys.exit(0)
if args[:2] == ['features', 'list']:
    for feature in ('apps', 'plugins', 'hooks', 'memories', 'multi_agent', 'browser_use',
                    'computer_use', 'image_generation', 'remote_plugin', 'shell_snapshot',
                    'skill_mcp_dependency_install', 'in_app_browser'):
        print(feature, 'stable', 'true')
    sys.exit(0)
if args[:2] == ['auth', 'status']:
    print(json.dumps({'loggedIn': True, 'authMethod': 'claude.ai', 'apiProvider': 'firstParty'}))
    sys.exit(0)
if args[:2] == ['login', 'status']:
    print('Logged in using ChatGPT')
    sys.exit(0)

prompt = json.loads(sys.stdin.read())
resumed = '--resume' in args or 'resume' in args
if '--resume' in args:
    session = args[args.index('--resume') + 1]
elif 'resume' in args:
    session = args[-2]
elif '--session-id' in args:
    session = args[args.index('--session-id') + 1]
else:
    session = str(uuid.uuid4())
root = Path(os.environ['CLAUDE_CONFIG_DIR'])/'projects' if provider == 'claude' else Path(os.environ['CODEX_HOME'])/'sessions'
root.mkdir(parents=True, exist_ok=True)
path = root/(session+'.jsonl')
previous = json.loads(path.read_text()) if resumed and path.exists() else None
if resumed and not previous:
    sys.exit(3)
marker = previous.get('marker') if previous else prompt.get('marker', 'literal-fixture')
record = {'sessionId': session, 'marker': marker} if provider == 'claude' else {'type': 'session_meta', 'payload': {'id': session}, 'marker': marker}
path.write_text(json.dumps(record)+'\n')
with open(os.environ['JOB_TEST_DISPATCHES'], 'a') as stream:
    stream.write(json.dumps({'pid': os.getpid(), 'session': session, 'resumed': resumed, 'cwd': os.getcwd(), 'argv': args})+'\n')
if provider == 'claude':
    print(json.dumps({'type': 'system', 'subtype': 'init', 'session_id': session}), flush=True)
else:
    print(json.dumps({'type': 'thread.started', 'thread_id': session}), flush=True)
    print(json.dumps({'type': 'turn.started'}), flush=True)
time.sleep(prompt.get('sleep', 0))
output = marker if resumed else prompt.get('answer', marker)
handoff = {'status': 'completed', 'summary': output, 'findings': [], 'changes': [],
           'verification': [], 'blockers': [], 'recommended_next_steps': []}
if provider == 'claude':
    event = {'type': 'result', 'subtype': 'success', 'is_error': False, 'session_id': session,
             'terminal_reason': 'completed', 'result': output}
    if '--json-schema' in args:
        event['structured_output'] = handoff
    print(json.dumps(event), flush=True)
else:
    if '--output-schema' in args:
        output = json.dumps(handoff)
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': output}}), flush=True)
    print(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 1, 'output_tokens': 1}}), flush=True)
