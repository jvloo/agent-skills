#!/usr/bin/env python3
"""Summarize trial records, including failed expenditure and auxiliary model usage."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import statistics


def measured_usage(record):
    primary=record['usage']
    result=dict(primary,auxiliary_tokens=0,all_reported_models=record['provider']=='codex')
    if record['provider']!='claude': return result
    # Claude's top-level usage excludes auxiliary model work present in modelUsage.
    path=Path(record['run']['artifacts']['stdout'])
    try:
        finals=[json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        models=next(e['modelUsage'] for e in reversed(finals) if e.get('type')=='result' and e.get('modelUsage'))
        required=('inputTokens','outputTokens','cacheReadInputTokens','cacheCreationInputTokens')
        if not all(all(isinstance(m.get(k),(int,float)) for k in required) for m in models.values()):
            return result
        result.update(input=sum(m['inputTokens']+m['cacheReadInputTokens']+m['cacheCreationInputTokens'] for m in models.values()),
            output=sum(m['outputTokens'] for m in models.values()),
            cached=sum(m['cacheReadInputTokens'] for m in models.values()),
            cache_created=sum(m['cacheCreationInputTokens'] for m in models.values()),
            uncached=sum(m['inputTokens'] for m in models.values()),all_reported_models=True,available=True)
        result['auxiliary_tokens']=(result['input']+result['output']-primary['input']-primary['output']) if primary.get('available') else None
    except (OSError,ValueError,KeyError,StopIteration):
        pass
    return result


def trial_metrics(report):
    records=report['records']
    measured=[(r,measured_usage(r)) for r in records]
    available=[(r,u) for r,u in measured if u.get('available')]
    totals={k:sum(u[k] for _,u in available) for k in ('input','output','cached','cache_created','uncached')}
    return dict(accepted=report['accepted'],elapsed_seconds=report.get('elapsed_seconds'),
        worker_calls=report.get('worker_calls',sum(r['role']=='worker' for r in records)),
        controller_turns=report.get('controller_turns',sum(r['role']=='controller' for r in records)),
        token_coverage_complete=len(available)==len(records) and all(u['all_reported_models'] for _,u in available),**totals,
        controller_tokens=sum(u['input']+u['output'] for r,u in available if r['role']=='controller'),
        worker_tokens=sum(u['input']+u['output'] for r,u in available if r['role']=='worker'),
        auxiliary_tokens=sum(u['auxiliary_tokens'] or 0 for _,u in available),
        claude_cost_usd=sum(r['usage']['cost_usd'] for r in records if r['usage'].get('cost_usd') is not None),
        total_cost_available=all(r['usage'].get('cost_usd') is not None for r in records))


def summarize(root):
    grouped=defaultdict(list);pairs=defaultdict(dict);rows=[];incomplete=[]
    for directory in sorted(p for p in root.iterdir() if p.is_dir()):
        trial=directory/'trial.json';failure=directory/'failure.json'
        if trial.exists():
            report=json.loads(trial.read_text())
            # Enforce worker contribution for consult, including trials from the initial driver.
            if report['case']=='consult':
                outputs=[Path(r['run']['artifacts']['result']).read_text() for r in report['records']
                         if r['role']=='worker' and r['run']['artifacts'].get('result')]
                report['accepted'] &= any(re.search(r'\b855\b',out) for out in outputs)
        elif failure.exists():
            report=json.loads(failure.read_text());worker,case,repetition,arm=directory.name.split('-')
            report.update(worker=worker,controller='codex' if worker=='claude' else 'claude',case=case,
                          repetition=int(repetition),arm=arm,accepted=False)
        else:
            records=[]
            for path in sorted(directory.glob('*-*/run.json')):
                run=json.loads(path.read_text());u=run.get('usage',{});provider=run['provider']
                if provider=='claude':
                    inp=sum(u.get(k,0) for k in ('input_tokens','cache_creation_input_tokens','cache_read_input_tokens'))
                    cached=u.get('cache_read_input_tokens',0);created=u.get('cache_creation_input_tokens',0)
                else:
                    inp=u.get('input_tokens',0);cached=u.get('cached_input_tokens',0);created=0
                records.append(dict(role=path.parent.name.split('-')[0],provider=provider,run=run,
                    usage=dict(available='input_tokens' in u and 'output_tokens' in u,input=inp,output=u.get('output_tokens',0),
                        cached=cached,cache_created=created,uncached=inp-cached-created,cost_usd=u.get('total_cost_usd'))))
            if records:
                incomplete.append(dict(trial=directory.name,**trial_metrics({'records':records,'accepted':False})))
            continue
        m=trial_metrics(report)
        row={k:report[k] for k in ('worker','controller','case','arm','repetition')};row.update(m)
        row.update(reference_reads=report.get('reads',[]),
            action_errors=sum('invalid' in e['action'] for e in report.get('events',[])),
            worker_retries=max(0,m['worker_calls']-(2 if report['case'] in ('recovery','coordination') else 1)),
            acceptance_checks=report.get('checks',{}))
        rows.append(row);grouped[(report['worker'],report['case'],report['arm'])].append(m)
        pairs[(report['worker'],report['case'],report['repetition'])][report['arm']]=m
    groups=[]
    for (worker,case,arm),values in sorted(grouped.items()):
        successes=sum(v['accepted'] for v in values)
        tokens=sum(v['input']+v['output'] for v in values)
        complete=all(v['token_coverage_complete'] for v in values)
        groups.append(dict(worker=worker,case=case,arm=arm,trials=len(values),accepted=successes,
            token_coverage_complete=complete,known_tokens=tokens,
            mean_tokens=tokens/len(values) if complete else None,
            tokens_per_accepted=tokens/successes if successes and complete else None,
            mean_seconds=statistics.mean(v['elapsed_seconds'] for v in values) if all(v['elapsed_seconds'] is not None for v in values) else None,
            controller_tokens=sum(v['controller_tokens'] for v in values),
            worker_tokens=sum(v['worker_tokens'] for v in values),
            claude_cost_usd=sum(v['claude_cost_usd'] for v in values)))
    paired=[]
    for (worker,case,repetition),arms in sorted(pairs.items()):
        if set(arms)!={'baseline','skill'}: continue
        a,b=arms['baseline'],arms['skill'];complete=a['token_coverage_complete'] and b['token_coverage_complete']
        paired.append(dict(worker=worker,case=case,repetition=repetition,
            baseline_accepted=a['accepted'],skill_accepted=b['accepted'],token_coverage_complete=complete,
            token_ratio=(b['input']+b['output'])/(a['input']+a['output']) if complete and a['input']+a['output'] else None,
            elapsed_ratio=b['elapsed_seconds']/a['elapsed_seconds'] if a['elapsed_seconds'] and b['elapsed_seconds'] is not None else None))
    return dict(trials=rows,groups=groups,pairs=paired,incomplete_trials_known_expenditure=incomplete,
                infrastructure_failures=[str(p.relative_to(root)) for p in root.glob('*/failure.json')])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('roots',type=Path,nargs='+')
    summaries=[summarize(root) for root in p.parse_args().roots]
    combined={key:[item for s in summaries for item in s[key]] for key in summaries[0]}
    print(json.dumps(combined,indent=2))
