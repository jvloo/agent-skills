# Progressive disclosure evaluation — 2026-09-09

## Change

The prepared 0.2.1 skills replace an implied reading sequence with an essential workflow and a
reference map keyed to unresolved decisions. Existing verified host evidence can satisfy setup;
references resolve missing or changed information. Authentication for each dispatch, enforced
limits, changed-workspace checks, exact sessions, uncertain-edit handling, isolation, and independent
acceptance remain required.

Descriptions now require a request for the named local CLI worker. They distinguish worker
consultation/review/implementation/continuation from generic coding, app navigation, and reviewing
the skill itself. Reference introductions state when their detail is needed and avoid sending the
reader through unrelated documents.

## Paired progressive prototype

The previous 0.2.0 entrypoint was compared with an initial progressive prototype using the same
broker, fixed model pairings, authentication checks and limits as the
[earlier pilot](2026-09-09-token-effectiveness.md). There were two repetitions each of consultation
and completed-response recovery, for both providers and both variants: **16 trials, all accepted**.
Order alternated by provider/repetition; provider batches ran concurrently. Each cell below covers
four trials. Counts include controller/worker input, output, cached input and reported auxiliary work.

| Skill | Accepted old → prototype | Total reported tokens | Change | Controller calls | Reference-file reads |
|---|---|---:|---:|---:|---:|
| `use-claude` | 4/4 → 4/4 | 336,360 → 213,014 | -36.7% | 16 → 12 | 16 → 0 |
| `use-codex` | 4/4 → 4/4 | 205,195 → 195,056 | -4.9% | 13 → 12 | 0 → 0 |

The prototype removed unnecessary reads when the host supplied complete verified execution details.
The `use-codex` controller was already mostly doing this; its smaller token difference includes
ordinary output/format variability. These are small synthetic comparisons, not statistically reliable
native-controller speed/cost claims. Recovery withholds a completed response rather than killing
an active worker. Both variants share the same execution safeguards.

## Final description and content check

After that prototype was measured, the final editorial pass shortened and sharpened the discovery
descriptions and core prose, made exact-session/uncertain-edit rules explicit, and clarified reference
entry conditions. Entrypoint word counts: old **532**, prototype **531**,
final **515**, including frontmatter. Word counts alone do not establish token efficiency.

The final wording passed **four additional live smoke trials**: consultation and exact-session
recovery for each provider, all accepted and **zero reference reads** with the verified broker.
The prototype percentages above are not presented as an exact paired estimate for the final wording.
[Per-trial metrics and revision hashes](token_effectiveness/progressive-results-2026-09-09.json)
separate old, prototype and final-smoke observations.

An independent agent with no inherited conversation first read only the final descriptions. It
selected the right skill for named Claude Code review and Codex CLI resume, and neither for a
generic Python fix, Codex app navigation, or a request to review skill wording without invoking Claude.
It then read the entrypoints and handled three decision scenarios:

- Trusted adapter plus 17 × 23: no references, one compact worker assignment, then independent
  verification against 391.
- Unfamiliar custom provider without auth/permission evidence: both invocation-safety references;
  route-specific non-generating inspection before any generation, without inventing access.
- Interrupted edit with stale auth and changed workspace: both job references plus reused safety
  guidance; inspect actual effects and completion/cleanup evidence, refresh auth before dispatch,
  and never automatically replay uncertain edits.

This was a qualitative read-only forward test; no paid worker calls or mutations were made by the
independent evaluator. It found no material correctness or clarity issue in these scenarios.

## Validation and limits

All **35 repository tests** and both skill validators passed. Shared runtime behavior is unchanged;
only the helper's package-version constant advances to 0.2.1. Worker-result v1 and job-journal
format 1 remain unchanged. The evaluator now accepts `--skill-source` and `--arms` for revision
comparisons, while keeping the execution broker fixed.

This follow-up used **95 top-level CLI calls**, **1,153,289 reported tokens**, and a
**$0.646245 Claude estimated component**, including the prototype comparison and final smoke tests.
Codex dollar cost and outer evaluation/review usage are unavailable. The earlier pilot's expenditure
is recorded separately. Raw artifacts remain in private directories named
`progressive-paired-claude-0909`, `progressive-paired-codex-0909`,
`progressive-final-claude-0909`, and `progressive-final-codex-0909`.
No private paths, transcripts, session IDs, or credentials are included in the public metrics.

Native persistent controllers, harder implementation tasks, and live uncertainty/failure scenarios
still need comparative evaluation. The intended improvement is selective retrieval with intact
execution requirements, not avoiding information that the task actually needs.

A subsequent [identical-controller comparison](2026-09-09-identical-controller.md) removes the controller-tier difference when comparing the two skills.
