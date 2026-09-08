# Bounded worker

Use a finite, non-interactive process when the task needs a result and no live steering.
Complete [invocation preflight](invocation-safety.md) and scale the
[worker contract](../assets/worker-contract.md) to the assignment.

## Invocation

Build an argument list with the host's process API and send the contract on stdin. The examples
below define argument contents, not shell commands. If a shell is necessary, quote each argument
for that shell and transport the prompt separately. Use an explicit process cwd.

Minimal read-only, single-worker consultation; `budget_usd` is chosen for this task:

```python
argv = [
    "claude", "-p",
    "--restricted", "--strict-mcp-config",
    "--permission-mode", "plan",
    "--permission-prompts", "none",
    "--tools", "Read,Grep,Glob",
    "--disallowedTools", "mcp__*",
    "--output-format", "json",
    "--max-budget-usd", str(budget_usd),
    "--no-session-persistence",
]
```

Use the resolved executable path in place of `claude`. Apply `--model <verified-model>`
and supported `--effort <level>` overrides when selection requires them. Use the flags
confirmed in installed help; `--permission-prompts none` requires v2.1.259 or later.
If unsupported, verify an unattended equivalent such as a suitably restricted `dontAsk`
configuration, or stop when the contract requires a control that cannot be supplied.

For supplied-text work, `--tools ""` can disable built-in tools. For authorized edits and
tests, explicitly add required edit/command tools, use the appropriate permission mode, and
pre-approve only necessary actions. `--tools` does not pre-approve commands. Do not restore
command tools removed by restricted mode without the required host containment.

For internal delegation, add `Agent` only after the
[child checks](supervised-sessions.md#internal-delegation). Use `--safe-mode` for untrusted
discovered customization when appropriate; it disables custom `--agents` definitions.

`--json-schema` takes schema JSON text, not a filename. Read the schema in the parent and
pass its contents as one argument. For streaming, use `--output-format stream-json --verbose`;
add `--include-partial-messages` only when token-level updates are useful.

## Limits and persistence

Establish a parent-runtime deadline and finite retry bound before dispatch. A tool yield interval
does not terminate the process. Track owned child work as well as the main process; preserve partial
output when stopping. A prompt budget is behavioral guidance, not spending enforcement.

Set `--max-budget-usd` from the task's value and existing spending authority. This print-mode
control is a stopping threshold, not a guaranteed provider billing cap; spend can occur before the
next check. If a strict no-overshoot ceiling is required, verify an adequate provider/runtime limit
or report the unsupported requirement before dispatch.

Keep `--no-session-persistence` for one-shot work. Omit it deliberately when follow-up requires
durable resume state; capture the exact session ID. See [supervised sessions](supervised-sessions.md).

## Result handling

Capture stdout, stderr, and process exit status separately. A nonzero exit, failed/incomplete turn,
interrupted stream, deadline termination, or exhausted budget is incomplete even when useful text
appears. Validate the CLI completion signal before accepting the worker's answer.

Parse the complete JSON envelope, or the final `result` event for `stream-json`.
Check subtype, `is_error`, and error details. When using `--json-schema`, extract and validate
`structured_output`, not prose from `result`. Missing structured output is incomplete.

Treat `mcp_server_errors` as a dependency failure when the task requires those servers.
Retain `session_id`, usage, `total_cost_usd`, and per-model costs when available; cost fields
are client estimates. Distinguish intermediate child messages from the main final result.

For a plain consultation, concise prose with a successful completion check is enough. When a
structured handoff is needed, use [result.schema.json](../assets/result.schema.json); validate the
extracted object again in the parent before acting. Its task status is separate from CLI success:
a successful model call may correctly report a blocked task.

Compare the result with the contract. Inspect edits, including untracked files, and run appropriate
acceptance checks independently. Do not infer that commands ran or artifacts are correct from a
plausible final message. Report skipped checks and stderr warnings without exposing secrets.

Official source: [programmatic usage](https://code.claude.com/docs/en/headless).
