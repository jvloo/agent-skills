# Worker contract

Use this template for complex work. For a simple consultation, keep objective, relevant inputs,
allowed actions, output, and limits. Record existing authorization; these fields are not a user
questionnaire. Remove unused sections and replace placeholders before dispatch.

## Objective and acceptance

- Objective: <one bounded outcome>
- Done when: <observable acceptance criteria>
- Required artifact or answer: <deliverable>

## Context and ownership

- Working directory: <absolute or runtime-resolved path>
- Repository revision and starting state: <ref, commit, user changes; or not applicable>
- Relevant sources and applicable instructions: <paths, URLs, or supplied evidence>
- In-scope paths, questions, and systems: <scope>
- Worker owns: <bounded investigation or artifact>
- Invoking agent owns: <integration, acceptance, and external communication>

## Authority and execution

- Existing user/task authorization: <approved actions and explicit exclusions>
- Authentication evidence: <provider route, status or credential-source check; no secrets>
- Required capability evidence: <preflight results and relevant configuration/containment>
- Parent-runtime approval: <native approval reference, or not required>
- Worker controls: <permission/sandbox mode, tools, relevant configuration sources>
- Allowed actions and directories: <reads, edits, commands, and minimum roots>
- Network and external systems: <allowed targets and authorized mutations, or none>
- Secrets: <required credential mechanism and data that must not enter prompts or output>

Do not infer permission to commit, publish, perform destructive actions, or access additional
systems. Perform such actions only when this contract includes existing authorization and the
runtime permits them. If required approval is denied or unavailable, report the blocker through
the invoking agent.

## Evidence and output

- Evidence: <file/symbol findings, diffs, command results, or source links>
- Checks: <authoritative validations appropriate to the task>
- Output: <concise prose or the sibling result.schema.json when structured handoff is needed>
- Include uncertainties, skipped checks, and blockers; do not claim unverified completion.

## Limits and supervision

- Model and effort: <verified selection>
- Cost/usage limit: <behavioral target, stopping threshold, or enforced ceiling; identify which>
- Wall-clock deadline and controller: <limit, ownership, child-work cleanup>
- Retry limit: <count and retryable conditions>
- Internal subagents: <disabled, or purposes, ownership, models, tools, and isolation>
- Child concurrency/depth: <targets and enforcement for any required exact limits>
- Persistence: <none, resume, or supervised background>

## Stop conditions

Stop and report when required evidence or capability is unavailable, a required control cannot be
enforced, an action would exceed authorization, unexpected workspace changes invalidate the agreed
inputs, or the time/cost/retry limit is reached. Expected edits by this worker do not invalidate the
starting-state record. Return unresolved material conflicts to the invoking agent.
