# Roadmap

This repository is Xavier Loo's evolving collection of agent skills for his practical agentic
workflow. `meta-agent/` is the first category, not the repository's overall boundary.

The roadmap communicates direction, not delivery commitments. A workflow should become a published
skill only when it is repeatable, useful beyond one private project, and measurably better than
general prompting.

## Current foundation

### Meta-agent

- `use-claude`: bounded Claude Code CLI delegation and supervision.
- `use-codex`: bounded Codex CLI/GPT delegation, supervision, and optional subagents.
- Shared principles for approval preflight, least privilege, isolation, worker contracts, and
  independent verification.

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

- Add realistic forward tests for the existing `use-claude` and `use-codex` skills.
- Track worker-CLI capability drift without hard-coding one machine, version, model, or shell.
- Define a consistent quality and release bar for all skill categories.
- Improve installation and discovery guidance for common agent runtimes while keeping skills
  runtime agnostic.
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

- Portable schemas for worker results, evidence, verification, and unresolved risk.
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
