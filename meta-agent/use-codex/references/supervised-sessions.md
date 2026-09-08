# Supervised sessions

Read when using a resume, live steering, parallel workers, or internal delegation. Prefer a finite
[bounded worker](bounded-worker.md) when persistence or steering adds no value.

## Resume and steering

Capture and use an exact session identifier. Recheck authentication and changed scope, workspace,
capabilities, model/effort, limits, and persistence using [preflight](invocation-safety.md). Expected
worker edits are part of the follow-up context, not an automatic scope violation. Reapply required
controls where resume does not preserve them. Ask for new approval only when existing authority or
runtime policy requires it.

Capture `thread_id` from `codex exec --json`. A read-only resume uses this argument list,
with the follow-up sent on stdin and an explicitly chosen process cwd:

```python
argv = [
    "codex", "exec", "resume",
    "-c", 'sandbox_mode="read-only"',
    "-c", 'approval_policy="never"',
    "-c", "agents.enabled=false",
    "--json", session_id, "-",
]
```

Confirm `codex exec resume --help`; resume options differ from a new exec call. Adjust controls
only within the verified contract. Avoid `--last`/`--all` for dispatch: other activity can select
the wrong session. Ephemeral runs do not supply durable resume state.

## Supervision and cleanup

A supervisor must track completion, deadline, retry limits, and owned child work. Inspect logs at
useful milestones, steer only to resolve an in-scope question or drift, and distinguish completed,
blocked, failed, stopped, and timed-out states. A timeout on a launcher that has already exited
does not stop detached work.

Keep `codex exec` attached to the parent runtime's process supervisor. Enforce a deadline on
the worker and its owned process tree; confirm they stopped. If reliable detached supervision is
unavailable, keep execution foreground. The `codex agents` daemon browser is not needed to
supervise a portable CLI worker.

There is no universal task-dollar-budget flag. If a required strict ceiling lacks a verified
provider/runtime enforcement mechanism, report that before launch.

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

Create worktrees through the invoking runtime when needed and inspect their actual revision before
dispatch. Do not assume child workers automatically get isolated checkouts.

## Internal delegation

Choose internal subagents when useful independent work justifies coordination and cost. Give each
child a purpose, scope, output obligation, and suitable model/effort. Verify shared authentication
and supported child capabilities once; recheck differing contexts. Keep children read-only unless
isolated writes are supported and authorized. Require the parent worker to reconcile evidence.

A prompted child-count limit is advisory. Distinguish concurrency, nesting depth, total lifetime
spawns, and model/capability restrictions. If a required boundary cannot be enforced internally,
disable that delegation route and use separately checked top-level workers. Do not replace an
explicitly requested model or expand external access through children.

Confirm installed support before enabling:

```text
-c agents.enabled=true
-c agents.max_concurrent_threads_per_session=<child-limit>
```

The concurrency value excludes the primary worker and does not cap lifetime spawns. Trusted agent
configuration can supply default child models, effort, sandbox, and role instructions, but explicit
spawn parameters can override defaults. Use managed enforcement or separate top-level workers when
exact model/effort restrictions are required. Do not create or change global agent configuration for
one worker. Disable internal delegation with `-c agents.enabled=false` when needed.

## Stop conditions

Stop or decline to resume when the worker needs unapproved actions, cannot preserve required
isolation, repeats without new evidence, exhausts the deadline/retry budget, or encounters a
required approval the supervisor cannot surface. Preserve enough output for diagnosis and report
the specific blocker.

Official sources: [subagents](https://developers.openai.com/codex/agent-configuration/subagents)
and [CLI reference](https://developers.openai.com/codex/cli/reference).
