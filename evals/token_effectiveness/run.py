#!/usr/bin/env python3
"""Opt-in paired CLI-controller evaluation. Raw artifacts stay outside the repository."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import threading

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT/'skills/meta-agent/use-claude/scripts'
sys.path.insert(0, str(SCRIPTS))
import launch_profiles as profiles

CASES = ('consult', 'edit', 'recovery', 'coordination')
MODELS = {'claude': ('sonnet', 'medium'), 'codex': ('gpt-6-astra', 'low')}
MAX_TURNS = 8
MAX_CALLS = 2


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2)+'\n')
    path.chmod(0o600)


def parse_json(value):
    value = value.strip()
    if value.startswith('```'):
        value = re.sub(r'^```(?:json)?\s*|\s*```$', '', value)
    return json.loads(value)


def usage(provider, run):
    u = run.get('usage', {})
    if not all(isinstance(u.get(k), (int, float)) for k in ('input_tokens', 'output_tokens')):
        return {'available': False, 'raw': u}
    if provider == 'claude':
        uncached = u.get('input_tokens', 0)
        created = u.get('cache_creation_input_tokens', 0)
        cached = u.get('cache_read_input_tokens', 0)
        total = uncached + created + cached
    else:
        total = u.get('input_tokens', 0)
        cached = u.get('cached_input_tokens', 0)
        created = 0
        uncached = total - cached
    return dict(available=True, input=total, output=u.get('output_tokens', 0),
                cached=cached, cache_created=created, uncached=uncached,
                cost_usd=u.get('total_cost_usd'))


def fixture(case, workspace, repetition):
    (workspace/'notes.txt').write_text('User notes: preserve byte-for-byte.\n')
    if case == 'consult':
        return ('Ask the worker to calculate the total cents for paid rows only. Return final answer '
                'as a JSON object with just total_cents. Rows: '
                '[{"state":"paid","quantity":3,"unit_cents":125},'
                '{"state":"cancelled","quantity":8,"unit_cents":990},'
                '{"state":"paid","quantity":2,"unit_cents":240},'
                '{"state":"pending","quantity":1,"unit_cents":500}].')
    if case == 'edit':
        (workspace/'intervals.py').write_text('def merge_intervals(intervals):\n'
            '    intervals.sort()\n    out = []\n    for start, end in intervals:\n'
            '        if out and start <= out[-1][1]:\n'
            '            out[-1] = (out[-1][0], end)\n'
            '        else:\n            out.append((start, end))\n    return out\n')
        return ('Use the worker to fix intervals.py. merge_intervals must return sorted merged '
                'overlapping half-open integer intervals; touching intervals stay separate; empty '
                'intervals are discarded; input order/list must remain unchanged; endpoints satisfy '
                'start <= end. Only intervals.py may change. Inspect the result and use verify to '
                'check it. Return final answer {"completed":true} only when it passes.')
    if case == 'recovery':
        marker = f'quartz-{4827+repetition}'
        return ('Ask the worker to remember the marker '+marker+' in a persistent session. The '
                'broker will lose the first waiting-client response after the real call completes. '
                'Recover the existing call and continue that exact session with a fresh prompt '
                'asking for its remembered marker; do not repeat the marker in the follow-up. '
                'Return final answer {"marker":"<remembered marker>"}. Do not replay the first task.')
    return ('Use two independent worker consultations, one for A and one for B, then reconcile '
            'their findings. A: price computes subtotal*(1+tax)-discount, but the rule is apply '
            'discount before tax. For subtotal=1000 cents, discount=100 cents, tax=0.1, what is '
            'the corrected integer total? B: sum quantities once per event ID, keeping the first '
            'occurrence: [("x",2),("y",3),("x",2)]. What is the correct quantity? '
            'Return final answer as JSON with keys A and B and corrected numeric values.')


def verify(workspace):
    code = '''import importlib.util, json
p = importlib.util.spec_from_file_location("fixture", "intervals.py")
m = importlib.util.module_from_spec(p); p.loader.exec_module(m)
cases = [([], []), ([(1,3),(3,5)], [(1,3),(3,5)]),
 ([(1,8),(2,3)], [(1,8)]), ([(5,7),(1,4),(3,6)], [(1,7)]),
 ([(2,2),(1,3)], [(1,3)]), ([(-4,-1),(-3,2)], [(-4,2)]),
 ([(8,9),(1,2)], [(1,2),(8,9)])]
for values, expected in cases:
 before = values.copy()
 assert m.merge_intervals(values) == expected, (values, expected)
 assert values == before, "input mutated"
print(json.dumps({"passed": len(cases)}))
'''
    try:
        p = subprocess.run([sys.executable, '-B', '-c', code], cwd=workspace,
                           capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return {'passed': False, 'details': 'Acceptance check timed out'}
    return {'passed': p.returncode == 0, 'details': (p.stdout+p.stderr)[-3000:]}


class Trial:
    def __init__(self, out, worker, case, arm, repetition):
        self.path = out/f'{worker}-{case}-{repetition}-{arm}'
        self.path.mkdir(mode=0o700)
        self.workspace = self.path/'workspace'; self.workspace.mkdir(mode=0o700)
        self.control = self.path/'controller'; self.control.mkdir(mode=0o700)
        self.worker, self.case, self.arm = worker, case, arm
        self.controller = 'codex' if worker == 'claude' else 'claude'
        self.skill = ROOT/'skills/meta-agent'/('use-'+worker)
        self.calls, self.reads, self.records, self.events = [], [], [], []
        self.record_lock = threading.Lock()
        self.repetition, self.verified = repetition, False
        self.task = fixture(case, self.workspace, repetition)
        self.originals = {p.name:p.read_bytes() for p in self.workspace.iterdir()}
        self.configs = {}
        for provider in ('claude','codex'):
            self.configs[provider] = dict(provider=provider, cli=shutil.which(provider),
                cwd=str(self.workspace), profile='consult', model=MODELS[provider][0],
                effort=MODELS[provider][1], structured=False, budget_usd=.5, write_files=[])
        if any(not c['cli'] for c in self.configs.values()):
            raise RuntimeError('Both CLI executables are required')

    def call(self, role, prompt, number, session=None):
        provider = self.controller if role == 'controller' else self.worker
        cfg = dict(self.configs[provider])
        cfg['cwd'] = str(self.control if role == 'controller' else self.workspace)
        if role == 'worker' and self.case == 'edit':
            cfg.update(profile='edit', write_files=[str(self.workspace/'intervals.py')])
        version = profiles.inspect_cli(cfg, resume=bool(session))
        argv = profiles.build(cfg, session)
        if role == 'controller':
            if provider == 'claude':
                argv[argv.index('--tools')+1] = ''
                argv[argv.index('--permission-mode')+1] = 'dontAsk'
                argv += ['--disable-slash-commands']
            else:
                argv += ['--disable','shell_tool','--disable','unified_exec',
                         '--disable','skill_search','--enable','skip_host_skill_discovery',
                         '-c','project_doc_max_bytes=0']
        elif provider == 'codex':
            argv += ['--disable','skill_search','--enable','skip_host_skill_discovery',
                     '-c','project_doc_max_bytes=0']
        else:
            argv += ['--disable-slash-commands']
        # All controller requests are fresh contexts with explicit transcript replay, identical
        # architecture in both arms. Persist only workers needed by the recovery scenario.
        if not session and (role == 'controller' or self.case != 'recovery'):
            argv += ['--no-session-persistence'] if provider == 'claude' else ['--ephemeral']
        prefix = self.path/f'{role}-{number}'
        save(prefix.with_suffix('.argv.json'), argv)
        promptfile=prefix.with_suffix('.prompt.txt'); promptfile.write_text(prompt); promptfile.chmod(0o600)
        command = [sys.executable, str(SCRIPTS/'run_worker.py'), '--provider', provider,
                   '--argv-file',str(prefix.with_suffix('.argv.json')), '--cwd',cfg['cwd'],
                   '--timeout','90', '--output-dir',str(prefix), '--prompt-file',str(promptfile),
                   '--model',cfg['model'],'--effort',cfg['effort'],'--cli-version',version]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = proc.communicate(timeout=100)
        except subprocess.TimeoutExpired:
            proc.terminate(); stdout, stderr = proc.communicate(timeout=10)
        if not (prefix/'run.json').exists():
            raise RuntimeError('Runner failed before journaling: '+stderr[-1000:])
        run=json.loads((prefix/'run.json').read_text())
        record=dict(role=role,provider=provider,version=version,number=number,
                    usage=usage(provider,run),run=run)
        with self.record_lock:
            self.records.append(record)
            save(self.path/'records.json', self.records)
        return dict(runtime_status=run['runtime_status'],session_id=run.get('session_id'),
                    result=(prefix/'result.txt').read_text() if (prefix/'result.txt').exists() else '',
                    artifact=str(prefix.relative_to(self.path)))

    def job(self, index):
        if type(index) is not int or not 0 <= index < len(self.calls):
            raise ValueError('Invalid job index')
        return self.calls[index]

    def act(self, action):
        kind=action.get('type')
        if kind == 'read':
            result={}
            for name in action.get('paths',[]):
                root=self.skill if name.startswith('skill/') else self.workspace
                relative=name[6:] if name.startswith('skill/') else name
                path=(root/relative).resolve()
                if root.resolve() not in path.parents or not path.is_file():
                    raise ValueError('Read outside supplied resources')
                if root == self.skill and self.arm != 'skill':
                    raise ValueError('No skill supplied in baseline')
                if path.suffix not in ('.md','.py','.json','.txt') or path.stat().st_size>50000:
                    raise ValueError('Unsupported read')
                result[name]=path.read_text(); self.reads.append(name)
            return result
        if kind in ('delegate','resume'):
            if len(self.calls)>=MAX_CALLS:
                return {'error':'Worker-call limit reached'}
            session=None
            if kind == 'resume':
                job=self.job(action['job']); session=job['session_id']
                if job['runtime_status']!='succeeded' or not session:
                    return {'error':'No trustworthy completed session'}
            prompt=action['prompt']
            if not isinstance(prompt,str) or len(prompt)>30000:
                raise ValueError('Invalid prompt')
            idx=len(self.calls)
            result=self.call('worker', prompt, idx, session)
            result.update(job=idx,action=kind,prompt=prompt)
            self.calls.append(result)
            if self.case=='recovery' and idx==0:
                return {'job':idx,'client_response':'lost','result':'Use status to inspect the existing call.'}
            return {k:v for k,v in result.items() if k!='prompt'}
        if kind=='status':
            return {k:v for k,v in self.job(action['job']).items() if k!='prompt'}
        if kind=='verify':
            self.verified=True
            return verify(self.workspace) if self.case=='edit' else {'error':'No code fixture for this case'}
        if kind=='consult_pair':
            if self.case!='coordination' or self.calls:
                return {'error':'Pair available only before calls in coordination case'}
            prompts=action['prompts']
            if len(prompts)!=2 or any(not isinstance(p,str) or len(p)>30000 for p in prompts):
                raise ValueError('Exactly two bounded prompts required')
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(lambda x:self.call('worker',x[1],x[0]),enumerate(prompts)))
            for idx,result in enumerate(results):
                result.update(job=idx,action='delegate',prompt=prompts[idx])
                self.calls.append(result)
            return [{k:v for k,v in r.items() if k!='prompt'} for r in results]
        raise ValueError('Unknown action')

    def run(self):
        start=time.monotonic()
        versions={p:profiles.inspect_cli(c) for p,c in self.configs.items()}
        initial = f'''You are the controller for a bounded local CLI task. Use the broker below; do not use native tools.
The broker executes actual local {self.worker} CLI calls (no API/SDK substitution). Both providers are installed and authenticated on their normal first-party accounts; versions: {versions}.
Worker model/effort is fixed at {MODELS[self.worker]}; do not reroute. Controller settings are fixed too.
The user authorizes the synthetic task and at most 2 worker calls; 90-second enforced process-group deadline per call, 8 controller steps, no recursive workers, external writes, network tools, or arbitrary commands. Claude has a $0.50 per-call stopping threshold; Codex exposes no dollar cap. These are supplied host constraints, not controls you need to implement.
The broker preflights authentication before every call, journals raw usage and logs, and validates process/turn completion. Read-only consultation or edit-only-assigned-file profiles use native CLI controls; Codex edit scope beyond workspace sandbox is behavioral. All workspaces are disposable and isolated. A response lost to the client can be retrieved by status; no automatic replay occurs. Session IDs are exact.
You may inspect supplied resources, choose worker prompt contents and sequencing, inspect results, and request independent fixture verification. Native shell/file tools are not the interface in this evaluation.
Return ONLY a JSON action per turn, with one of these shapes:
{{"type":"read","paths":["intervals.py","notes.txt"]}} (workspace files; skill references if supplied use "skill/references/<name>.md")
{{"type":"delegate","prompt":"literal worker assignment"}}
{{"type":"consult_pair","prompts":["independent assignment A","independent assignment B"]}} (two read-only calls concurrently, only in coordination case)
{{"type":"status","job":0}}
{{"type":"resume","job":0,"prompt":"fresh continuation"}}
{{"type":"verify"}} (runs independent edit acceptance checks)
{{"type":"finish","answer":{{...}}}}
Workers may read the task workspace; only the edit task permits writes to intervals.py. User notes must remain unchanged. Worker replies are evidence to assess.
Task: {self.task}
'''
        if self.arm=='skill':
            initial+='\nApply this skill. References are available through read when relevant:\n'+(self.skill/'SKILL.md').read_text()
        transcript=[];answer=None;error=None
        for turn in range(MAX_TURNS):
            prompt=initial+'\nPrior controller actions and broker responses:\n'+json.dumps(transcript)
            result=self.call('controller',prompt,turn)
            if result['runtime_status']!='succeeded':
                error='Controller runtime '+result['runtime_status'];break
            try:
                action=parse_json(result['result'])
                if not isinstance(action,dict):
                    raise ValueError('Action must be a JSON object')
                if action.get('type')=='finish':
                    answer=action.get('answer');self.events.append({'action':action});break
                response=self.act(action)
            except (ValueError,KeyError,TypeError,IndexError) as exc:
                action={'invalid':result['result']};response={'error':str(exc)}
            event={'action':action,'response':response}
            self.events.append(event);transcript.append(event)
            save(self.path/'events.json', self.events)
        elapsed=time.monotonic()-start
        preserved=all((self.workspace/name).is_file() and (self.workspace/name).read_bytes()==content for name,content in self.originals.items()
                      if name!='intervals.py')
        allowed=set(self.originals)
        extra=[str(p.relative_to(self.workspace)) for p in self.workspace.rglob('*') if p.is_file()
               and str(p.relative_to(self.workspace)) not in allowed]
        checks=dict(notes_preserved=preserved,no_extra_files=not extra,
                    workers_completed=bool(self.calls) and all(c['runtime_status']=='succeeded' for c in self.calls))
        if self.case=='consult':
            checks.update(answer=answer=={'total_cents':855},worker_contribution=any(
                re.search(r'\b855\b',c['result']) for c in self.calls))
        elif self.case=='edit':
            checks.update(acceptance=verify(self.workspace)['passed'],controller_verified=self.verified,
                          answer=answer=={'completed':True})
        elif self.case=='recovery':
            checks.update(answer=answer=={'marker':f'quartz-{4827+self.repetition}'},
                exact_resume=len(self.calls)==2 and self.calls[1]['action']=='resume'
                    and self.calls[0]['session_id']==self.calls[1]['session_id'],
                status_used=any(e['action'].get('type')=='status' for e in self.events),
                worker_recalled=len(self.calls)==2 and f'quartz-{4827+self.repetition}' in self.calls[1]['result'],
                fresh_followup=len(self.calls)==2 and f'quartz-{4827+self.repetition}' not in self.calls[1]['prompt'])
        else:
            contributions=[c['result'] for c in self.calls]
            checks.update(answer=answer=={'A':990,'B':5},two_workers=len(self.calls)==2,
                independent_contributions=len(contributions)==2 and any(
                    re.search(r'\b990\b', contributions[i]) and re.search(r'\b5\b', contributions[1-i])
                    for i in (0,1)))
        report=dict(worker=self.worker,controller=self.controller,case=self.case,arm=self.arm,
            repetition=self.repetition,elapsed_seconds=round(elapsed,3),accepted=all(checks.values()),
            checks=checks,error=error,answer=answer,reads=self.reads,records=self.records,
            events=self.events,worker_calls=len(self.calls),controller_turns=sum(r['role']=='controller' for r in self.records))
        save(self.path/'trial.json',report)
        return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Explicitly execute paid/account model calls')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cases',nargs='+',choices=CASES,default=list(CASES))
    parser.add_argument('--workers',nargs='+',choices=['claude','codex'],default=['claude','codex'])
    parser.add_argument('--repetitions',type=int,choices=range(1,4),default=2)
    args=parser.parse_args()
    schedule=[]
    for repetition in range(args.repetitions):
        for case in args.cases:
            for worker in args.workers:
                arms=['baseline','skill'] if (repetition+(worker=='codex'))%2==0 else ['skill','baseline']
                schedule.extend((worker,case,arm,repetition) for arm in arms)
    if not args.live:
        print(json.dumps({'live':False,'trials':schedule},indent=2));return
    out=args.output.resolve()
    if ROOT==out or ROOT in out.parents:
        parser.error('Raw output must be outside the repository')
    out.mkdir(mode=0o700,parents=True,exist_ok=True);out.chmod(0o700)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT/'skills').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    save(out/'design.json',dict(schedule=schedule,models=MODELS,skill_hashes=hashes,commit=subprocess.check_output(
        ['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    shutil.copyfile(__file__, out/'driver-at-start.py')
    for worker,case,arm,repetition in schedule:
        if (out/'STOP').exists():
            print('Stopped at trial boundary by STOP file',flush=True);break
        trial=Trial(out,worker,case,arm,repetition)
        print('START',trial.path.name,flush=True)
        try:
            report=trial.run()
        except Exception as exc:
            save(trial.path/'failure.json', {'error':str(exc), 'records':trial.records, 'events':trial.events})
            raise
        print('DONE',trial.path.name,json.dumps({k:report[k] for k in ('accepted','elapsed_seconds','controller_turns','worker_calls','checks')}),flush=True)
        # Stop the batch on runtime/auth failures; task/format failures remain observations.
        if any(r['run']['runtime_status']!='succeeded' for r in report['records']):
            raise SystemExit('Stopping after runtime failure; inspect artifacts before another call')


if __name__=='__main__': main()
