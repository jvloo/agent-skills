# Token-effectiveness pilot — 2026-09-09

## Outcome

All 32 final trials passed independent acceptance: 16 baseline and 16 skill-guided. Adding skill
instructions did not improve acceptance on these fixtures and increased reported tokens overall.
This is evidence about the current instructions over a **shared execution broker**, not evidence
that the skills' operational safeguards are unnecessary or that delegation itself is inefficient.

| Skill under evaluation | Accepted baseline → skill | Tokens per accepted result, baseline → skill | Token change | Mean trial time, baseline → skill |
|---|---|---|---|---|
| `use-claude` | 8/8 → 8/8 | 58,965 → 87,242 | +48.0% | 30.7s → 39.5s |
| `use-codex` | 8/8 → 8/8 | 53,290 → 62,286 | +16.9% | 28.2s → 28.5s |

Tokens include controller and worker input/output, cached input, and Claude's reported auxiliary
model work. They are not dollar costs. Two repetitions per cell are exploratory; no significance
claim or general model ranking follows from these averages.

## Method

Source: skills at `820affc`, both version 0.2.0, unchanged throughout this evaluation. macOS 26.6.2
arm64, Python 3.9.6, Claude Code 2.1.263 and Codex CLI 0.153.4. Requested pairings were Codex
Astra/low → Claude Sonnet/medium for `use-claude`, and Claude Sonnet/medium → Codex Astra/low
for `use-codex`. Claude reported Sonnet 5 plus auxiliary Haiku usage; Codex's completion events
expose usage but do not independently echo the effective model.

Four cases × two providers × two arms × two repetitions. Order reversed by repetition; provider
batches ran concurrently in distinct workspaces. Each call had a 90-second deadline; trials allowed
eight controller steps and two worker calls. Claude's $0.50 per-call control is a stopping threshold.
Codex did not report dollar cost. CLI authentication was checked before every call.

Both arms received the same broker interface and preflight evidence. The broker used the same
bounded runner, launch profiles, completion parsing, permissions, and recovery primitives. The
skill arm additionally received its entrypoint and could read its references. Controllers chose
assignments, sequencing, inspections and verification. Native controller tools/discovered skills
were disabled; Claude controllers used `dontAsk`. Every controller step launched a fresh CLI
context with explicit transcript replay. This architecture repeatedly includes prior skill/reference
text and CLI startup; it does not predict native persistent-controller performance.

See the [reproducible procedure](token_effectiveness/README.md) and
[per-trial metrics and source hashes](token_effectiveness/results-2026-09-09.json).

## Acceptance and paired cases

Consultation required correct filtered arithmetic supported by the worker. Editing required seven
independent interval-merging checks, unchanged inputs/user notes, no extra files, and a controller
verification request. Recovery required inspecting a withheld completed response, exact-session
continuation with a fresh prompt omitting the marker, and actual worker recall. Coordination
required distinct A/B consultations and correct reconciliation of their contributions.

An independent read-only audit confirmed distinct assignments/sessions and actual answers in the
16 recovery/coordination trials across both repetitions. Automated checks cover all 32 trials.
The tasks have easy, deterministic answers; a 100% baseline leaves no measured quality headroom.
Recovery does not kill a live worker: it withholds a response after completion. Coordination is
bounded independent consultation, not difficult recursive multi-agent work.

Mean reported tokens per trial; each cell has two accepted trials:

| Worker | Case | Baseline | Skill | Change |
|---|---|---:|---:|---:|
| claude | consult | 34,330 | 56,480 | +64.5% |
| claude | edit | 88,346 | 109,390 | +23.8% |
| claude | recovery | 67,163 | 111,678 | +66.3% |
| claude | coordination | 46,022 | 71,422 | +55.2% |
| codex | consult | 36,108 | 43,598 | +20.7% |
| codex | edit | 81,480 | 98,003 | +20.3% |
| codex | recovery | 56,054 | 63,506 | +13.3% |
| codex | coordination | 39,516 | 44,036 | +11.4% |

## Where the tokens went

| Worker / arm | Controller / worker calls | Controller / worker tokens | Broker action errors | Cached share of input | Claude estimated component |
|---|---:|---:|---:|---:|---:|
| claude / baseline | 26 / 12 | 302,017 / 169,705 | 0 | 52.1% | $0.155362 |
| claude / skill | 32 / 12 | 527,428 / 170,512 | 0 | 35.5% | $0.156159 |
| codex / baseline | 27 / 12 | 221,288 / 205,030 | 2 | 52.0% | $0.275503 |
| codex / skill | 27 / 12 | 282,472 / 215,813 | 2 | 44.3% | $0.459101 |

Final comparison: **160 top-level CLI calls**, **2,094,265 reported tokens**, including
**149,892 auxiliary tokens**; Claude's estimated component was **$1.046124**. No worker retry
was needed. Controller action/formatting errors are retained as observed overhead. The corrected
mode avoids the known plan-mode conflict but does not eliminate every formatting error.

The `use-claude` controller repeatedly requested safety/model/bounded-worker references, and in
recovery the job/session references, despite the broker supplying launch controls and verified preflight
facts. Those reads added controller steps and replayed context. The `use-codex` controller generally
used the entrypoint without reference reads; its differences were smaller and more variable.
These patterns identify a candidate optimization; they do not establish that those references can
be removed from general native execution.

Claude primary input combines uncached input, cache creation, and cache reads. The summary replaces
primary counts with raw `modelUsage` totals to include auxiliary Haiku work without double-counting.
Codex input already includes cached input. Missing measurements remain unavailable. Complete
combined dollar cost per accepted result cannot be calculated from these CLIs. Cache state and
service latency were uncontrolled, and provider/model token units are not interchangeable prices.

## Development overhead and corrections

Before the final comparison, one controller-only pilot failed because the evaluator read `status`
instead of `runtime_status`. Four corrected consultation pilot trials then passed. An earlier main
batch completed ten trials before a Claude controller plan-mode/broker conflict was identified.
That batch was paused, its current bounded child allowed to finish, and the parent stopped. Its
partial next trial is retained. Claude controller mode was corrected before starting all 32 final
trials afresh. None of those development observations is pooled into the comparison above.

The retained development runs used **67 top-level calls**, **944,367 reported tokens** and a
**$0.720128 Claude estimated component**. These costs are additional to the final comparison.
The outer evaluator's implementation, analysis, and independent-review usage is not exposed by
these trial manifests and is excluded. Native CLI auxiliary calls are counted in tokens/cost when
reported, but are not additional top-level CLI calls.

The independent accounting review caught omitted auxiliary usage, weak contribution/file checks,
and failure-record handling; fixes have offline regression coverage. All **35 repository tests**
passed, including six evaluator tests. Source skill contents and installed packages were unchanged.
Private evidence directories are named `token-effectiveness-pilot-0909`,
`token-effectiveness-pilot2-0909`, `token-effectiveness-main-0909`,
`token-effectiveness-final-claude-0909`, and `token-effectiveness-final-codex-0909`.
Raw prompts, transcripts, session IDs and local paths are not published.

## Next experiment

1. Test a smaller common path that explicitly reuses supplied preflight/profile evidence and loads
   model/invocation references only when a decision remains unresolved. Keep the operational
   invariants in the full skill; do not trim them based solely on these easy fixtures.
2. Compare that candidate against the unchanged skill with native controller tools and persisted
   context, plus harder repository tasks with room for acceptance differences.
3. Add a direct-solve arm where delegation is optional to measure whether delegation pays for its
   extra calls. Separately compare recovery mechanisms if evaluating harness value.

No production instruction change or token-saving claim is promoted from this pilot alone.

The [progressive-disclosure follow-up](2026-09-09-progressive-disclosure.md) tests the subsequent candidate and final wording.
