---
name: use-codex
description: Use when a user or workflow requests Codex as a local CLI worker for a second opinion, code review, implementation, or session continuation. Delegates bounded work and verifies the returned result.
metadata:
  version: "0.2.1"
---

# Use Codex

Use the local CLI as a worker. The invoking agent owns scope, integration, and acceptance.
Reviewing or installing this skill does not authorize a worker call.

## Essential workflow

1. Carry existing authority and choices forward. Require a successful actual-route authentication
   check for each dispatch/resume; the host may perform it for this dispatch. Confirm workspace,
   executable/configuration provenance, permissions, and enforced limits. Reuse unchanged verified
   evidence; inspect missing or changed conditions. Keep preflight records outside worker prompts.
   Worker controls do not grant authority or replace host containment.
2. Choose model and effort by explicit choice, verified defaults, then justified adjustment.
   Retain a suitable established selection; consult guidance when selection or compatibility is unresolved.
3. Supply a compact objective, done criteria, relevant evidence, permitted actions, output, limits,
   and stop conditions. Avoid the full conversation and prescribed second-opinion verdicts.
   Plain consultations need no elaborate template or schema unless the consumer requires one.
4. Use a verified finite invocation with minimal capabilities, enforced timeout, and bounded
   retries. A process ID or wait interval is not a deadline. Capture output/errors/exit status and
   account for owned children and cleanup. Persist sessions when continuation is useful. Keep
   simple work single-worker; delegate internally only when independent work justifies its cost
   within the original scope. Avoid automatic reviewer chains and recursive handoffs.
   Continue only a verified exact session; inspect changed work and uncertain completion first.
   Never automatically replay an uncertain edit.
5. Verify process/turn completion, artifacts, and proportionate acceptance checks. Worker success
   is not acceptance. Report contributions, verification, and limitations through the host interface.

Isolate every concurrent writer; readers may share a stable revision. Preserve user changes and
inspect work before integration. Worktrees do not isolate credentials, processes, or external
systems. Do not create user-visible host tasks merely to dispatch CLI work.

## Retrieve detail when needed

When a verified host adapter or prior setup supplies the necessary controls and evidence, proceed
from the core workflow. References are decision aids, not a checklist: read the section that resolves
a missing decision, not every document matching the task's topics. Reuse it until conditions change.
Per-dispatch authentication, changed-boundary checks, and acceptance verification still apply.

| Unresolved decision | Reference |
|---|---|
| Authentication route, permissions, workspace trust, or execution provenance | [Invocation safety](references/invocation-safety.md) |
| Model/effort choice, compatibility, escalation, or billing route | [Model selection](references/model-selection.md) |
| Constructing CLI arguments, persistence flags, or interpreting completion | [Bounded workers](references/bounded-worker.md) |
| Invoking or diagnosing the optional bounded runner | [Runner](references/runner.md) |
| Setting up job journals, status/cancel/resume, or diagnosing uncertain recovery | [Recoverable jobs](references/jobs.md) |
| Session steering, concurrency, or child-work ownership/cleanup not supplied by the host | [Supervised sessions](references/supervised-sessions.md) |
| A complex assignment needs a fuller contract or a consumer requires a structured handoff | [Worker contract](assets/worker-contract.md), [result schema](assets/result.schema.json) |
| Evaluating or changing a routing recommendation | [Dated model evidence](references/model-evidence.md) |
