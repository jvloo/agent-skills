# Bounded execution helper

Read only when using `scripts/run_worker.py`. The helper requires Python 3.9+ and macOS or
Linux. It uses the standard library and does not install packages. Other platforms and
interactive/detached sessions use the host's verified process supervisor.

## Launch

Complete [preflight](invocation-safety.md), then build the provider argument list in
[bounded workers](bounded-worker.md). Save that list as a JSON array in a private file.
Use an absolute executable path and explicit flags for the intended provider, tools,
permissions, model, persistence, and output format. Never put credentials in the argument
file. The helper does not construct or approve the worker's launch configuration.

Invoke the helper using the host's process API, with this argument list:

```python
helper_argv = [
    python_executable, str(skill_dir / "scripts/run_worker.py"),
    "--provider", provider,  # "claude" or "codex"
    "--argv-file", str(argv_file),
    "--cwd", str(workspace),
    "--timeout", str(deadline_seconds),
    "--output-dir", str(new_run_directory),
]
```

Deliver the worker contract to the helper's stdin, or add `--prompt-file <path>` for a
private prompt file. The helper passes those bytes directly to the worker's stdin; neither
the prompt nor the argument array becomes shell command text. The output directory must
not exist, and its parent must already exist. Use an absolute path outside tracked files.

Use `--help` for the full interface. Optional `--cli-version`, `--model`, and `--effort`
record supervisor-supplied launch metadata; they do not set CLI flags or establish effective
settings. Confirm the actual provider and model through the worker's supported outputs.

For a resumed turn, put the exact captured session ID and reverified restrictions in the
provider argv. The helper does not choose sessions, persistence, writable roots, or retries.
Do not use `--last` to substitute for the intended session ID.

## Results and supervision

Consume the complete output stream. Claude can emit prompt suggestions, an idle session-state
notification, or a completed task notification after its result; the helper permits those narrow
shapes. Active/failed task notifications are incomplete. A present Claude `terminal_reason`
must be `completed`; interrupted or token-limited results are incomplete even inside a success
envelope. Missing terminal reasons remain compatible with older clients. Codex must end with
`turn.completed`. These checks follow the [Claude loop lifecycle](https://code.claude.com/docs/en/agent-sdk/agent-loop)
and the [Codex event protocol](https://github.com/openai/codex/blob/main/sdk/typescript/src/events.ts).

The helper creates an owner-only directory and files: `stdout.txt`, `stderr.txt`, `run.json`,
and, after successful parsing, `result.txt` or `result.json`. Its stdout contains a compact
JSON summary. `run.json` records execution status separately from the worker's task status;
an executed task can validly report `blocked`. The record includes version/protocol identity,
cwd, elapsed time, process exit, available session/usage evidence, and artifact paths. It does
not copy argv, prompts, or environment variables. Raw worker logs can still contain sensitive
output: keep credentials out of prompts and retain logs only as long as needed.

Add `--structured` only when requesting the bundled `assets/result.schema.json` from the
CLI. Claude needs schema JSON text in `--json-schema`; Codex needs its path in `--output-schema`.
The helper validates the fixed `worker-result-v1` handoff, including required fields, types,
enum values, and rejection of unknown fields. It is not a general JSON Schema validator.
The schema's `$id` identifies this protocol; `$schema` identifies the JSON Schema language.

| Exit | Runtime status | Meaning |
|---|---|---|
| 0 | `succeeded` | Successful process and turn; validate the task result and actual artifacts. |
| 1 | `failed` | Process or provider reported failure. |
| 2 | `incomplete` | Completion evidence or fully finished owned work is missing. |
| 3 | `timed_out` | Deadline elapsed; partial logs retained. |
| 4 | `cancelled` | Supervisor received SIGINT/SIGTERM; partial logs retained. |
| 5 | `invalid_output` | Malformed output or invalid/missing structured handoff. |
| 64 | Launch error | Invalid arguments, unsupported platform, or unusable paths; no accepted result. |

On a deadline or SIGINT/SIGTERM, the helper terminates the new process group, then escalates
to SIGKILL after a short cleanup grace period. A leader that exits while same-group children
remain is incomplete; the helper also cleans those up. The grace period is additional to the
task deadline. Keep the helper attached to host supervision, and allow it to finish cleanup.

This is process-group cleanup, not a sandbox or a universal process-tree controller. Children
that create new sessions, remote work, and detached provider supervisors require separate
verified ownership and cleanup. Do not enable those routes when this helper is the only
deadline controller. SIGKILL of the helper itself cannot run its cleanup handler. A spending
threshold still needs the provider's control; a wall-clock deadline does not establish a bill cap.

Inspect required dependency warnings, edits, and acceptance checks after a successful run.
The helper validates execution evidence; it cannot establish that the worker's conclusions
or changes are correct.
