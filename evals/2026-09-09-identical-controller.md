# Identical-controller comparison — 2026-09-09

## Outcome

With **Claude Sonnet/medium controlling both skills**, `use-claude` no longer had the higher token
total seen with different controller pairings. All eight trials passed. This corrects the earlier
comparison: the skill names identify workers, but the prior totals also included different controllers.

Each column below includes four trials: two consultations and two completed-response recovery tasks.

| Metric | `use-claude` | `use-codex` |
|---|---:|---:|
| Controller tokens | 123,215 | 133,814 |
| Worker tokens | 64,777 | 70,990 |
| **Total tokens** | **187,992** | **204,804** |
| Controller calls / worker calls | 12 / 6 | 13 / 6 |
| Controller action errors | 0 | 1 |
| Mean trial time | 17.5s | 20.4s |

`use-claude` used **8.2% fewer reported tokens** in this run. This is not a
claim that it is inherently more efficient. `use-codex` had one formatting retry, and its worker
model/runtime remained different. Every error and its expenditure is retained in the primary totals.
Both skills loaded **zero references** and made the expected six worker calls without worker retries.

In the three paired cases without an action error, controller totals differed by less than 0.3%
per pair. This post-hoc diagnostic helps locate the earlier confound; it does not replace the full
sample totals or establish a statistical equivalence claim.

## Controls and measurement

- Same controller provider, CLI, requested Sonnet model and medium effort in every trial.
  All controller manifests confirm the settings and report Sonnet 5; auxiliary Haiku work is included.
- Same broker, final 0.2.1 skill source, task inputs, acceptance checks, tool restrictions, fresh-context
  transcript replay, 90-second call deadlines, and bounded controller/worker call counts.
- Worker settings deliberately unchanged: Claude Sonnet/medium versus Codex Astra/low.
- Two repetitions, reversing worker order in the second; one sequential batch. Cache state and
  service latency were uncontrolled. There was no no-skill arm in this follow-up.
- Input totals include cached tokens; Claude raw per-model usage includes auxiliary work. Tokens
  from different providers do not represent interchangeable dollar prices. The Claude-only
  estimated component across this batch was **$0.504185**;
  Codex cost and outer evaluator usage are unavailable.

The batch used **37 top-level CLI calls**
and **392,796 reported tokens**. Raw evidence remains in the private directory named
`same-controller-sonnet-0909`. Published [metrics and source hashes](token_effectiveness/same-controller-results-2026-09-09.json)
contain no transcripts, private paths, credentials, or session IDs.

## Interpretation

The remaining observed differences belong to whole controller/worker pipelines, not simply the
length of a skill. Holding the controller fixed removes the controller-tier confound. Holding
worker capability/runtime and native session behavior constant would be necessary for stronger
claims about instruction overhead or provider efficiency. These simple fixtures have a 100%
acceptance rate and limited power to reveal quality differences.

The earlier [progressive-disclosure comparison](2026-09-09-progressive-disclosure.md) remains a
within-pairing comparison of old versus revised instructions; the new test addresses cross-skill
interpretation. Native persistent controllers and harder tasks remain separate work.

## Reproduction and checks

The evaluator now accepts `--controller claude` or `--controller codex`; `cross` preserves the
historical opposite-provider pairing. See the [procedure](token_effectiveness/README.md).
No installed skill content or version changed in this follow-up.

All **36 offline tests passed**, including an override check that preserves worker settings.
For live acceptance, actual worker results support the arithmetic; recovery checks actual marker
recall, exact session continuity, fresh follow-up, status inspection, unchanged notes and completion.
Controller settings and reported model evidence were inspected for every trial. All eight passed.
