# Token-effectiveness pilot

This opt-in evaluation compares a controller with no skill against a controller given the current
skill entrypoint and access to its references. Both arms receive the same task, worker model,
permissions, deadline, result parser, and mediated tool interface. The controller chooses its
worker prompts, reference reads, sequencing, verification, and final answer.

This isolates **added instruction effectiveness atop a common execution harness**. It does not
compare the harness against unsupervised execution, or delegation against solving a task directly.

## Run

Preview the schedule without model calls:

```sh
python3 evals/token_effectiveness/run.py --output /tmp/token-effectiveness
```

After authorizing account/model usage, add `--live`. Choose a new private output directory outside
the repository. Both local CLIs must be installed and authenticated through their normal first-party
account routes. No credentials are copied. The run preflights each call and stops on runtime failures. Create `STOP` in its output directory
to stop before the next trial; the current bounded trial finishes first.

```sh
python3 evals/token_effectiveness/run.py --live --output /tmp/token-effectiveness-run
python3 evals/token_effectiveness/summarize.py /tmp/token-effectiveness-run
```

`--cases`, `--workers`, and `--repetitions` allow smaller runs. For revision comparisons,
`--skill-source <directory-containing-use-claude-and-use-codex>` selects instruction files, and
`--arms skill` omits the no-skill arm. The execution broker remains the current repository version.
Pin both the instruction source and broker revision when comparing runs. Separate worker-provider batches
may run concurrently in distinct output directories; the summary accepts multiple directories.
Record that concurrency when interpreting latency. Default: four cases × two worker
providers × two arms × two repetitions = 32 trials. Order alternates baseline/skill by repetition
and worker provider. Repetitions reuse the fixture; recovery markers differ by repetition.

## Design and boundaries

- Default `--controller cross`: `use-claude` uses a Codex Astra/low controller and Claude
  Sonnet/medium worker; `use-codex` uses a Claude Sonnet/medium controller and Codex Astra/low
  worker. This historical pairing cannot isolate skill overhead across providers.
- `--controller claude` fixes both controllers to Sonnet/medium; `--controller codex` fixes both
  to Astra/low. Worker settings remain unchanged. Fixed-controller runs reverse worker order
  on alternate repetitions. Different worker models/runtimes still limit cross-skill conclusions.
- Each trial permits eight controller steps and two worker calls, with a 90-second enforced
  deadline per call. Claude has a $0.50 per-call stopping threshold; Codex exposes no dollar cap.
  These are call limits, not a guaranteed overall billing ceiling.
- Controllers return JSON actions. The evaluator performs actual local CLI calls and supplies
  observations on the next controller step. Native controller tools and discovered skills are
  disabled for isolation; Claude controllers use `dontAsk` rather than plan mode to avoid native
  planning instructions competing with the JSON broker interface. Workers use the existing consultation/edit profiles.
- Every controller step starts a fresh CLI context and receives the explicit prior transcript.
  Repeated skill/reference input and process startup are measured costs of this architecture;
  they do not predict a native persistent controller's costs.
- Only the treatment receives `SKILL.md`; it may request references on demand. Both arms inherit
  the same host preflight evidence and execution controls. This deliberately removes the need
  to rediscover launch flags and implement process supervision.
- Raw prompts, outputs, argv, manifests, reference reads, per-call usage, source hashes, checks,
  and failures remain in the private output directory. No model-produced code is published.

## Cases and acceptance

| Case | Required result |
|---|---|
| Consultation | Correct filtered arithmetic, with an actual successful worker contribution. |
| Editing | Fix overlapping half-open interval merging; seven independent cases, input preservation, controller-requested verification, unchanged notes, no extra files. |
| Recovery | Recover a withheld completed response, inspect status, resume the exact persisted worker session with a fresh prompt, and obtain its remembered marker. |
| Coordination | Two worker consultations contribute the respective corrected values, followed by correct controller reconciliation. |

Recovery simulates losing a response **after** the real worker completes. It is not a live process
crash or an interrupted generation. Coordination can be sequential or concurrent; prompts and
results also need human inspection to establish useful independent contributions. Worker results
and artifacts determine acceptance; a controller's claim of success is insufficient.

## Measurement

Report acceptance before efficiency. Include failed trials in token/time expenditure; divide total
expenditure by the number of accepted trials for cost per accepted result. Retain paired observations,
not only pooled averages. Record controller/worker calls, reference reads, and corrections separately.

For Claude, primary-turn input is `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`.
For Codex, `input_tokens` already includes cached input; do not add `cached_input_tokens` again.
The summary uses Claude's raw `modelUsage` totals to include auxiliary models (such as Haiku), replacing rather than
adding to primary usage. It reports the additional tokens separately. Keep output, cached input,
cache creation, and uncached input separately. Missing counters are
unavailable, never zero. These are CLI-reported counters, not tokenizer estimates. Retain raw manifests and per-model
usage. If per-model evidence is missing, totals are marked incomplete; unreported provider work
remains outside the measurement.

Claude's cost is a client estimate. Codex has no dollar cost in these outputs, so a complete combined
cost per accepted result is unavailable. The outer evaluator's development, analysis, and review
usage is outside trial counters. Cache state and service latency are uncontrolled. Two repetitions
per cell support a pilot observation, not a model ranking or statistically reliable general claim.

## Identical-controller comparison

After authorizing live usage, compare both skills with one controller model/runtime:

```sh
python3 evals/token_effectiveness/run.py --live --output /tmp/same-controller \
  --controller claude --arms skill --cases consult recovery --repetitions 2
```

Compare controller and worker counters separately. Holding the controller constant removes the
earlier controller-tier confound; it does not make the worker models, tokenizers, cache state, or
CLI startup content identical. This mode still uses fresh controller contexts and transcript replay.
