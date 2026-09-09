# Supervised sessions

Read the relevant section when session controls, steering, concurrency, or child-work ownership
are unresolved. Reuse controls already verified by the host. For finite invocation details, see
[bounded workers](bounded-worker.md); persistence alone is not a reason to load every section.

## Resume and steering

Capture and use an exact session identifier. Recheck authentication and changed scope, workspace,
capabilities, model/effort, limits, and persistence using [preflight](invocation-safety.md). Expected
worker edits are part of the follow-up context, not an automatic scope violation. Reapply required
controls where resume does not preserve them. Ask for new approval only when existing authority or
runtime policy requires it.

Retain `session_id` from print-mode output. Resume with `claude -p --resume <session_id>`
plus the verified model, tools, permission, budget, and output controls, sending the new contract on
stdin. Do not assume a bare resume preserves the launch restrictions. A one-shot run with
`--no-session-persistence` cannot be resumed.
When resume matters, verify the normal session store is writable and the session was persisted.
A returned `session_id` alone is insufficient: a sandboxed call can succeed without saving a
resumable conversation. Resolve the runtime access issue before promising continuity.

For background sessions, use the captured short ID for logs, attach, and stop commands. Attaching
can restart a stopped session; revalidate before attaching as well as before sending a follow-up.

## Supervision and cleanup

A supervisor must track completion, deadline, retry limits, and owned child work. Inspect logs at
useful milestones, steer only to resolve an in-scope question or drift, and distinguish completed,
blocked, failed, stopped, and timed-out states. A timeout on a launcher that has already exited
does not stop detached work.

Use `claude --bg` only when deliberate persistence or steering warrants its supervisor.
Confirm `--bg`, `agents`, `logs`, `attach`, and `stop` in installed help.
Background and print mode cannot be combined; `--max-budget-usd` applies only to print mode.
Use print mode when a required spending threshold cannot be enforced for background execution.
Periodic billing estimates cannot guarantee a hard cap.

Before detaching, establish a deadline controller that survives the launcher, captures the returned
worker ID, stops owned work at the deadline, and confirms all owned work ended. On supported
versions, make [CLAUDE_CODE_DISABLE_BG_EXIT_HANDOFF](https://code.claude.com/docs/en/env-vars#variables)
equal to `1` in the actual background worker
so its background shell commands, dynamic workflows, and background subagents stop with the session
process. Check the supervisor/settings environment, not just the launcher's environment.
This control requires v2.1.196+, with subagent coverage from v2.1.198.

By default that work can survive `claude stop <id>`; a stopped session row is not proof that its
children stopped. If handoff cannot be disabled, use a verified controller that stops all owned
work, or fall back to a foreground bounded worker. Do not delete the session/worktree merely to
achieve cancellation.
Preserve any required live steering in a fallback: use a foreground interactive session with a
verified input channel when print mode cannot provide it, or report that specific capability gap.

Launch from the verified directory with explicit model/effort, permission mode, tool boundary,
and contract. Use monitored manual/default mode only with a prompt handler; unattended background
work uses `dontAsk` with narrowly pre-approved actions. Capture the short ID from `--bg`
output. Use `claude logs <id>`, `claude attach <id>`, and `claude stop <id>`.
If the ID is lost, recover with `claude agents --json --all --cwd <directory>` when supported,
matching directory, name, and start time before acting.

Before deleting any session or workspace, account for edits, commits, untracked files, and evidence.
Termination does not authorize deleting useful artifacts. Do not stop unrelated user sessions.

## Parallel workers and workspaces

Launch separate top-level workers for independent failure handling or exact per-worker control.
Bound concurrency in the parent runtime and name one reconciliation owner. Parallel readers may
share stable inputs; every concurrent writer needs an isolated workspace, normally a Git worktree.
Disjoint file assignments alone do not satisfy this isolation rule.

Before launching writers, verify the actual base revision, known user changes, applicable
instructions, and any ignored files copied into the workspace. Copy only what the task needs;
worktrees do not isolate credentials, network, or external systems. Review and integrate each diff
before cleanup.

Claude-created worktrees normally start from `origin/HEAD`, retaining its cached ref when a fetch
fails. Local `HEAD` is the fallback when no remote is configured, or `origin/HEAD` is unavailable
and cannot be fetched. Configuration can change the base; verify the actual ref instead of assuming
it matches the dispatch checkout.

Agent teams do not automatically provide separate worktrees. Under this skill, teammates sharing
a checkout must be read-only or have at most one active writer. For concurrent editing, use
independent sessions or subagents with verified isolated worktrees.

## Internal delegation

Choose internal subagents when useful independent work justifies coordination and cost. Give each
child a purpose, scope, output obligation, and suitable model/effort. Verify shared authentication
and supported child capabilities once; recheck differing contexts. Keep children read-only unless
isolated writes are supported and authorized. Require the parent worker to reconcile evidence.

A prompted child-count limit is advisory. Distinguish concurrency, nesting depth, total lifetime
spawns, and model/capability restrictions. If a required boundary cannot be enforced internally,
disable that delegation route and use separately checked top-level workers. Do not replace an
explicitly requested model or expand external access through children.

The parent needs the `Agent` tool; defining `--agents <trusted-json>` does not enable it.
Agent definitions should specify purpose, tools, model/effort, turn limit, output, and isolation.
`--append-subagent-system-prompt`, where supported, can add shared behavioral constraints.
`--safe-mode` disables custom definitions, so choose compatible trust controls if using them.

`--agents` adds types; it does not exclude built-ins or discovered agents. A main agent
launched with `--agent` can restrict allowed types through tools such as
`Agent(worker,researcher)`; this does not itself restrict nested types.
To disable nesting, use `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` when supported, or withhold
`Agent` from child tool sets.

`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` bounds ordinary Agent spawns in supported versions,
but is not a universal hard concurrency cap: ultracode is exempt, resumes can exceed it, and
workflows/teams have separate limits. Do not use it alone for an exact overall worker ceiling.
If exact per-spawn approval or hard overall bounds are required, omit `Agent` and launch
separately checked processes. Agent teams are experimental; enable them only within existing
authority and the workspace rule above.

## Stop conditions

Stop or decline to resume when the worker needs unapproved actions, cannot preserve required
isolation, repeats without new evidence, exhausts the deadline/retry budget, or encounters a
required approval the supervisor cannot surface. Preserve enough output for diagnosis and report
the specific blocker.

Official sources: [agent view and lifecycle](https://code.claude.com/docs/en/agent-view),
[environment controls](https://code.claude.com/docs/en/env-vars),
[subagents](https://code.claude.com/docs/en/sub-agents), and
[worktrees](https://code.claude.com/docs/en/worktrees).
