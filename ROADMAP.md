# Roadmap

This repository is Xavier Loo's evolving collection of agent skills for his practical agentic
workflow. `skills/meta-agent/` is the first category, not the repository's overall boundary.

The roadmap communicates direction, not delivery commitments. A workflow should become a published
skill only when it is repeatable, useful beyond one private project, and measurably better than
general prompting.

## Current foundation

### Meta-agent

- `use-claude` and `use-codex`: local CLI consultations, bounded delegation, supervised sessions,
  and internal subagents when the task benefits from them.
- Matching entrypoints and reference structure, byte-identical worker contracts and result
  schemas, and shared authentication-preflight, authority, isolation, and verification policies.
- Provider-specific commands, authentication routes, lifecycle controls, and curated model
  recommendations under one selection policy: explicit choice, verified defaults, then justified
  adjustments.
- Documented installation paths, independent skill versions currently prepared at 0.2.1, a versioned result protocol,
  and contribution requirements. A self-contained optional bounded runner and repeatable fake-CLI
  lifecycle tests cover prompt transport, completion, output validation, deadlines, and cancellation.
- Optional recoverable job journals and first-party launch profiles support client loss,
  known-result recovery, checked exact-session continuation, and concurrent-writer leases.
  Unknown outcomes stop for inspection; full host-crash and exactly-once side effects are not promised.
- Dated model evidence distinguishes official guidance, practitioner observations, and locally
  checked CLI interfaces. Fresh-context scenario definitions and baseline comparison guidance are
  checked in. [Recoverable-job evaluation](evals/2026-09-09-recoverable-jobs.md) records 29 passing
  fixture tests, independent fresh-context checks, and live Claude/Codex client-loss recovery,
  exact-session resume, and bounded edits. An [instruction-efficiency pilot](evals/2026-09-09-token-effectiveness.md)
  compares baseline and skill-guided controllers over a shared harness; it does not establish
  model-routing quality or native-controller efficiency.

The repository currently publishes source on `main`, with no tagged release. See
[CHANGELOG.md](CHANGELOG.md) for the initial import and subsequent changes.

## Expansion areas

Future categories may include:

- **Engineering:** implementation, debugging, testing, review, architecture, migration, performance,
  security, Git, and release workflows.
- **Product and domain:** problem discovery, requirements, domain modeling, specifications, and
  decision records.
- **Research and knowledge:** source-driven investigation, synthesis, evidence management, and
  durable documentation.
- **Collaboration:** planning, handoffs, stakeholder communication, reviews, and recurring team
  workflows.
- **Meta-agent:** delegation, model routing, context design, evaluation, supervision, reconciliation,
  and recovery across agent runtimes.

Category names remain provisional until each has enough skills to justify a stable boundary. Empty
category directories will not be added in advance.

## Near-term

- Execute and expand the fresh-context scenarios for authorized writes, custom/local providers,
  non-Git work, exact-session continuation, and concurrent writers. Compare measured outcomes
  before making stronger claims about routing quality or instruction improvements.
- Extend live lifecycle coverage to interruption during generation followed by resume, steering,
  and child-work cancellation in controlled environments with authorized runtime access and usage.
  Completed-session resume and recovery after client loss already have live evidence.
- Extend progressive-disclosure evaluation to native controllers and harder tasks; retain
  authentication, changed-boundary and uncertain-recovery checks while reducing unnecessary reads.
- Track worker-CLI capability drift without hard-coding one machine, version, model, or shell.
- Run the documented quality suite on additional supported Python/platform combinations and
  collect live compatibility evidence before widening the helper's support claims.
- Keep installation and discovery guidance current as host runtimes evolve.
- Identify the next reusable skills from Xavier's working agentic workflows.

## Candidate meta-agent skills

- `delegate-task`: create bounded, evidence-oriented assignments for arbitrary worker agents.
- `cross-model-review`: obtain independent reviews without leaking the implementer's reasoning.
- `reconcile-agent-results`: resolve conflicting findings against primary evidence.
- `route-agent-work`: select workers, models, effort, tools, and concurrency by task characteristics.
- `evaluate-agent`: forward-test agent behavior with repeatable scenarios and outcome-based checks.
- `handoff-context`: transfer the minimum sufficient context between agents and sessions.
- `recover-agent-work`: diagnose stalled, failed, or scope-drifting workers and resume safely.

These candidates illustrate one category rather than defining the whole repository. A candidate
becomes a skill only when its trigger boundary is distinct and its reusable guidance justifies
separate context.

## Repository-wide infrastructure

- Build on the shared worker-result schema when new categories need additional evidence or
  handoff formats; avoid adding schemas without a concrete consumer.
- Reusable evaluation fixtures that do not depend on private repositories or credentials.
- Compatibility notes derived from installed tool behavior and first-party documentation.
- Lightweight release automation after the structure and validation contract stabilize.

## Non-goals

- Limiting the repository to meta-agent or CLI-orchestration skills.
- Publishing company-confidential rules, credentials, private transcripts, or machine-specific
  configuration.
- Adding generic prompt collections without a clear operational contract.
- Replacing a host runtime's native approvals, sandbox, or policy enforcement.
- Treating agent output as accepted without proportionate independent verification.

Suggestions and focused contributions are welcome through the process in
[CONTRIBUTING.md](CONTRIBUTING.md).
