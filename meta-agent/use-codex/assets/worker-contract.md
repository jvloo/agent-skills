# Worker contract

Use this template for complex work; keep simple consultations to a short paragraph. Remove unused
fields and replace placeholders. Keep authentication evidence, approval records, runtime provenance,
and deadline-controller details in the supervisor record, outside the worker prompt.

## Objective and acceptance

- Objective: <one bounded outcome>
- Done when: <observable acceptance criteria>
- Deliverable: <answer or artifact and its destination>

## Relevant context

- Working directory: <absolute or runtime-resolved path>
- Inputs and instructions: <relevant paths, URLs, supplied evidence, and revision when needed>
- Scope: <paths, questions, systems, and existing changes to preserve>
- Worker owns: <bounded investigation or artifact; invoking agent handles integration and acceptance>

## Permitted actions

- Allowed: <reads, edits, commands, directories, and any authorized external actions>
- Excluded: <task-specific exclusions, or omit>
- Internal subagents: <disabled, or bounded assignments with permitted tools and writer isolation>

Commit, publish, destructive actions, and access to additional systems require authorization in this
contract and runtime permission. Report a needed action that falls outside these boundaries.

## Output and verification

- Output format: <concise prose, or result.schema.json for a structured handoff>
- Evidence: <source locations, relevant diff, command results, or source links>
- Acceptance checks: <checks appropriate to this task>
- Report uncertainty, skipped checks, blockers, and remaining work.

## Limits and stopping

- Time and usage: <task deadline and applicable budget; distinguish guidance from enforced limits>
- Retries: <bounded count and useful retry conditions>
- Child limits, if enabled: <concurrency, depth, and per-child scope or budget>

Stop and report when a required action or input is unavailable, unexpected changes invalidate the
agreed inputs, an attempt repeats without new evidence, or a task limit is reached. Expected edits
by this worker do not invalidate the starting state. Return unresolved material conflicts to the
invoking agent.
