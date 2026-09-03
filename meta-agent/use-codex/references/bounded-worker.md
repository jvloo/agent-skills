# Bounded worker

Use `codex exec` for a finite assignment whose result the parent runtime will inspect.

## Portable command pattern

Construct the equivalent of this argument vector using the parent runtime's process API and send the
contract on stdin. Adapt quoting to the host shell; do not copy shell syntax blindly.

```text
codex exec
  --sandbox <read-only-or-workspace-write>
  -c approval_policy=\"never\"
  --model <supported-model>
  -c model_reasoning_effort=\"<supported-effort>\"
  -c agents.enabled=false
  --json
  -
```

Use `--ephemeral` when the task does not need a resumable record. Use
`--output-last-message <path>` when only the final message is needed. Use
`--output-schema <schema-path>` when downstream logic requires stable fields; validate the written
result again in the parent runtime before acting on it. The reusable
[result schema](../assets/result.schema.json) is a suitable default handoff shape. Add
`--strict-config` only when rejecting unknown configuration is intentional; stale unrelated fields
can otherwise stop a portable invocation.

The CLI provides no universal task-level cost ceiling. Enforce wall-clock time, retries, process
count, and any available account/runtime budgets in the parent runtime. A prompt budget is a
behavioral instruction, not hard enforcement.

## Contract requirements

The prompt should specify:

- exact objective and done criteria;
- working directory, repository revision, and in-scope paths;
- read-only versus write authority and explicit exclusions;
- primary evidence to inspect and commands allowed;
- whether network or external systems are allowed;
- model, effort, subagent policy, concurrency, and time/cost limits;
- required output shape, evidence, uncertainties, and skipped checks;
- stop conditions and actions that require returning to the orchestrator.

For reviews, ask for findings ordered by severity with file/symbol evidence and reproduction steps.
For implementation, require a concise change summary, exact checks run, failures, and remaining
risks. Do not ask Codex to commit or publish unless separately authorized.

## Result handling

With `--json`, parse the JSONL event stream and retain the thread identifier, completion/failure
event, tool activity, file changes, and usage. Do not treat a final message as proof that commands
ran or edits are correct. Inspect the filesystem and Git diff independently, then run authoritative
checks. Reject results that exceeded scope, depended on unverifiable claims, or concealed skipped
validation.

Official reference: [non-interactive mode](https://developers.openai.com/codex/non-interactive-mode).
