# Bounded worker

Use a finite, non-interactive process when the task needs a result and no live steering.
Complete [invocation preflight](invocation-safety.md) and scale the
[worker contract](../assets/worker-contract.md) to the assignment.

## Invocation

On macOS/Linux with Python 3.9+, the optional [bounded runner](runner.md) handles literal
stdin, private logs, deadlines, completion parsing, and the bundled structured handoff. Read
that reference only when using the helper. It executes the argument list you verify below;
authentication, permissions, model selection, and required containment remain with the host.

Build an argument list with the host's process API and send the contract on stdin. The examples
below define argument contents, not shell commands. If a shell is necessary, quote each argument
for that shell and transport the prompt separately. Use an explicit process cwd.

Minimal read-only, single-worker consultation:

```python
argv = [
    "codex", "exec",
    "--sandbox", "read-only",
    "-c", 'approval_policy="never"',
    "-c", "agents.enabled=false",
    "--ephemeral", "--json", "-",
]
```

Use the resolved executable path in place of `codex`. String config values contain TOML
quotes, without literal backslashes. For example, an effort override is the two arguments
`-c` and `model_reasoning_effort="medium"`. Omit effort if unsupported. Apply
`--model <verified-model>` when an explicit selection or task adjustment requires it.

For authorized edits, select `workspace-write` and the required roots. Outside Git, after
checking directory safety, add `--skip-git-repo-check`; retain sandbox/approval controls.
For internal delegation, replace the disabled-agent setting only after the
[child checks](supervised-sessions.md#internal-delegation).

`--output-last-message <path>` saves the final answer. Add `--output-schema <path>` if
downstream logic requires stable fields; it takes a schema file path. With JSONL enabled, continue
checking the event stream for completion even when the final answer is also written to a file.

## Limits and persistence

Establish a parent-runtime deadline and finite retry bound before dispatch. A tool yield interval
does not terminate the process. Track owned child work as well as the main process; preserve partial
output when stopping. A prompt budget is behavioral guidance, not spending enforcement.

Codex CLI has no universal per-task dollar cap. If a strict spending ceiling is required, verify
an adequate provider/runtime limit or report the unsupported requirement before dispatch.
Deadlines, concurrency bounds, and token estimates do not establish a dollar cap.

Keep `--ephemeral` for one-shot work. Omit it deliberately when follow-up requires durable
resume state; capture the exact thread ID. See [supervised sessions](supervised-sessions.md).

## Result handling

Capture stdout, stderr, and process exit status separately. A nonzero exit, failed/incomplete turn,
interrupted stream, deadline termination, or exhausted budget is incomplete even when useful text
appears. Validate the CLI completion signal before accepting the worker's answer.

Parse `--json` output as JSONL. Retain the thread ID, completion/failure events, tool
activity, file changes, and usage when available. Require successful turn completion and process
exit. Validate a schema-constrained final answer from its message or output file, not the event
envelope itself.

For a plain consultation, concise prose with a successful completion check is enough. When a
structured handoff is needed, use [result.schema.json](../assets/result.schema.json); validate the
extracted object again in the parent before acting. Its task status is separate from CLI success:
a successful model call may correctly report a blocked task.

Compare the result with the contract. Inspect edits, including untracked files, and run appropriate
acceptance checks independently. Do not infer that commands ran or artifacts are correct from a
plausible final message. Report skipped checks and stderr warnings without exposing secrets.

Official source: [non-interactive mode](https://developers.openai.com/codex/non-interactive-mode).
