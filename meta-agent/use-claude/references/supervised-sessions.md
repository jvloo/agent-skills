# Supervised sessions

Use Claude-managed background sessions for work that is long-running or benefits from steering.
Use a foreground interactive session only when background management is unavailable and the parent
runtime can monitor and communicate with the process.

## Launch and recovery

Confirm `--bg`, `agents`, `logs`, `attach`, and `stop` in installed help. Background mode and print
mode are distinct and cannot be combined. Launch from the intended working directory with an
explicit model, effort, permission mode, capability boundary, and prompt contract.

Resolve user/task authorization and all known parent-runtime tool or sandbox approvals before the
launch prompt reaches the model. This includes approval for the intended working directory,
read/write access, commands, network or external systems, model/effort, background persistence,
cost/time, and any Claude subagents or concurrency. Fail closed if required approval is unknown or
unavailable. Use the runtime's native approval mechanism when present, not a plain-text workaround.

Use the installed syntax equivalent of this semantic pattern:

```text
claude --bg
  --name <session-name>
  --model <model>
  --effort <effort>
  --permission-mode <manual-or-dontAsk>
  --tools <required-built-in-tools>
  [--allowedTools <pre-approved-rules>]
  "Read <prompt-file> and execute that contract."
```

Use monitored manual/default mode when the supervisor can answer prompts. For unattended
background work, use `dontAsk` with only the required tools and narrowly pre-approved rules so an
unexpected action fails instead of waiting invisibly.

`claude --bg` prints the session's short ID. Capture that launch output directly and retain the ID
for `claude logs <id>`, `claude attach <id>`, and `claude stop <id>`. Do not rediscover an ID by name
when direct capture succeeded. If launch output was lost or state must be reconciled, recover with:

```text
claude agents --json --all --cwd <working-directory>
```

Use only flags shown by `claude agents --help`. Verify the recovered session's directory, name,
state, and timing before acting on it. Stop a session only when cancellation is authorized or it is
unsafe, irrecoverably off-scope, or no longer useful. Preserve useful evidence and changes before
deleting any session or worktree.

## Supervision loop

- Inspect logs and state at useful milestones; avoid busy polling.
- Attach or send input only to resolve an in-scope question or correct drift.
- Treat every steering prompt, resume, and parent-initiated worker launch as an approval checkpoint;
  material expansion requires new authorization and applicable parent-runtime approval first.
- Do not assume the parent runtime can intercept Claude-internal child spawns. Enable `Agent` only
  when the upfront envelope permits autonomous delegation within existing capability, cost, and
  time bounds.
- Enforce the contract's cost, elapsed-time, retry, and stop limits outside the worker.
- On completion, inspect repository status and diff, capture test evidence, and verify independently.
- Treat `Needs input`, failed, stopped, and timed-out states as distinct outcomes.

## Worktrees

Every concurrent writer gets a separate worktree. Before launch, establish:

- the trusted repository root and whether workspace trust has been accepted where required;
- the exact base ref—Claude worktrees normally use `origin/HEAD`, with local `HEAD` as fallback when
  no remote is available or fetching fails, unless configured otherwise;
- the source revision and expected clean/dirty state;
- which ignored files may be copied and whether they contain credentials;
- who owns integration and when cleanup is safe.

Worktrees isolate file edits, not credentials, processes, network access, external systems, or the
semantic correctness of changes. Inspect the actual worktree revision and diff rather than assuming
it matches the dispatch checkout. Never delete a session or worktree before accounting for commits,
uncommitted changes, untracked files, and evidence.

## Claude concurrency choices

Use subagents for bounded side investigations that report into one Claude conversation. Use
background sessions when the invoking agent owns coordination across independent conversations.
Agent teams are experimental and disabled by default; teammates communicate and share a task list,
but they do not automatically receive separate worktrees. Do not assume per-teammate worktree
isolation: partition ownership so only one teammate writes each file, or choose independent sessions
or subagents that support isolated worktrees. Parallelism multiplies token usage and synthesis cost,
so bound the worker count and name one reconciliation owner. Do not enable subagents or teams unless
their model, effort, concurrency, capability, and budget fit the pre-approved envelope. Treat a
prompted child-count limit as advisory unless a verified control enforces it; use separately approved
parent-launched sessions when exact per-child approval is required.

Official references: [agent view](https://code.claude.com/docs/en/agent-view),
[parallel agents](https://code.claude.com/docs/en/agents), and
[worktrees](https://code.claude.com/docs/en/worktrees).
