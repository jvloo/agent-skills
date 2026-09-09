"""Offline checks for evaluation accounting and independent acceptance."""
import importlib.util
from pathlib import Path
import tempfile
import json
import unittest

spec = importlib.util.spec_from_file_location('token_eval', Path(__file__).resolve().parents[1]/'evals/token_effectiveness/run.py')
evalmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evalmod)

summary_spec = importlib.util.spec_from_file_location('token_summary', Path(__file__).resolve().parents[1]/'evals/token_effectiveness/summarize.py')
summary = importlib.util.module_from_spec(summary_spec)
summary_spec.loader.exec_module(summary)

class TokenEvalTests(unittest.TestCase):
    def test_cache_accounting_provider_semantics(self):
        claude = evalmod.usage('claude', {'usage': {'input_tokens':10,'output_tokens':5,
            'cache_creation_input_tokens':20,'cache_read_input_tokens':30}})
        self.assertEqual(claude['input'],60)
        codex = evalmod.usage('codex', {'usage': {'input_tokens':60,'output_tokens':5,'cached_input_tokens':30}})
        self.assertEqual(codex['input'],60)
        self.assertEqual(codex['uncached'],30)
        self.assertIsNone(codex['cost_usd'])

    def test_missing_usage_is_not_zero(self):
        for record in ({}, {'usage':{'total_cost_usd':.1}}, {'usage':{'input_tokens':8}}):
            self.assertFalse(evalmod.usage('claude',record)['available'])

    def test_acceptance_rejects_original_and_accepts_correct_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace=Path(tmp)
            evalmod.fixture('edit',workspace,0)
            self.assertFalse(evalmod.verify(workspace)['passed'])
            (workspace/'intervals.py').write_text('def merge_intervals(intervals):\n'
                '    out=[]\n    for start,end in sorted(intervals):\n'
                '        if start == end: continue\n'
                '        if out and start < out[-1][1]:\n'
                '            out[-1]=(out[-1][0],max(out[-1][1],end))\n'
                '        else: out.append((start,end))\n    return out\n')
            self.assertTrue(evalmod.verify(workspace)['passed'])

    def test_auxiliary_usage_replaces_primary_without_double_counting(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'stdout.txt'
            path.write_text(json.dumps({'type':'result','modelUsage': {
                'main':{'inputTokens':10,'outputTokens':5,'cacheReadInputTokens':30,'cacheCreationInputTokens':20},
                'aux':{'inputTokens':7,'outputTokens':2,'cacheReadInputTokens':0,'cacheCreationInputTokens':0}}}))
            primary=evalmod.usage('claude',{'usage':{'input_tokens':10,'output_tokens':5,
                'cache_read_input_tokens':30,'cache_creation_input_tokens':20}})
            result=summary.measured_usage({'provider':'claude','usage':primary,'run':{'artifacts':{'stdout':str(path)}}})
            self.assertEqual(result['input'],67)
            self.assertEqual(result['output'],7)
            self.assertEqual(result['auxiliary_tokens'],9)
            self.assertTrue(result['all_reported_models'])

    def test_failed_expenditure_and_partial_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);trial=root/'claude-consult-0-baseline';trial.mkdir()
            record={'role':'controller','provider':'codex','usage':{'available':False},'run':{}}
            (trial/'failure.json').write_text(json.dumps({'records':[record]}))
            result=summary.summarize(root)
            group=result['groups'][0]
            self.assertEqual(group['accepted'],0)
            self.assertFalse(group['token_coverage_complete'])
            self.assertIsNone(group['mean_tokens'])
            self.assertIsNone(group['tokens_per_accepted'])
            record['usage']={'available':True,'input':100,'output':20,'cached':0,
                'cache_created':0,'uncached':100,'cost_usd':None}
            (trial/'failure.json').write_text(json.dumps({'records':[record]}))
            self.assertEqual(summary.summarize(root)['groups'][0]['known_tokens'],120)

    def test_job_indices_cannot_alias_other_jobs(self):
        trial=object.__new__(evalmod.Trial)
        trial.calls=[{'job':0}]
        for index in (-1,True,'0',1):
            with self.assertRaises(ValueError): trial.job(index)
        self.assertEqual(trial.job(0),{'job':0})

if __name__=='__main__': unittest.main()
