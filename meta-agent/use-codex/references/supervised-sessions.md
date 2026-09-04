# Supervised sessions

Use this when work needs follow-ups, long-running process supervision, parallel workers, worktrees,
or Codex-managed subagents.

## Resuming safely

Capture the `thread_id` from `codex exec --json`. Resume an exact session with:

```text
codex exec resume <SESSION_ID> <FOLLOW_UP_PROMPT>
```

Prefer an explicit ID. `--last` is convenient but can select the wrong session when other work ran
in the same directory; `--all` broadens discovery across directories. A resume is a new approval
checkpoint: revalidate revision, dirty state, scope, permissions, model/effort, time/cost, and
persistence before sending the follow-up. Ephemeral runs cannot provide durable resume state.

The `codex agents` command browses sessions on a shared app-server daemon; it is not the same as
launching a bounded non-interactive worker. Do not depend on daemon or GUI session facilities when a
portable parent-runtime process supervisor is sufficient.

## Parallel top-level workers

Use separate `codex exec` processes for exact per-worker approval, independent failure handling, or
stronger orchestration control. Give each a complete contract. Parallel read-only workers may share
a revision. Every writer needs an isolated workspace—normally a separate Git worktree—and a clear
ownership boundary. The parent agent integrates only after reviewing each diff and resolving overlap.

Bound concurrency in the parent runtime. Avoid fan-out whose synthesis cost exceeds its benefit.

## Codex-managed subagents

Current Codex releases may expose internal multi-agent tools. Confirm installed support and enable
them only after approval:

```text
-c agents.enabled=true
-c agents.max_concurrent_threads_per_session=<approved-n>
```

Inspect and record `agents.default_subagent_model` and
`agents.default_subagent_reasoning_effort`. Without overrides, children inherit the parent pair.
Resolution order is explicit spawn, corresponding `[agents]` default, then parent; selecting a
model through an explicit spawn or `[agents]` default without an associated effort uses that
model's default effort. A custom agent file may then override declared settings; one that sets only
`model` preserves the previously resolved effort.

This runtime order does not define policy precedence. Explicit user choices come first; derive every
unspecified field from the entrypoint's task routing. Treat `[agents]` defaults and custom-agent
files as effective-config inputs, not authorization to use `ultra` or a model outside the default
routing set. Verify the final effective pair after all layers resolve. If it differs from the policy
pair, enforce the exact pair through supported controls or disable internal delegation and launch a
separate top-level worker; stop when neither is possible. Never substitute silently.

Tell the parent Codex worker which children to use, their ownership, output contract, and whether
they may write. Require it to synthesize conflicts and cite evidence. Keep children read-only unless
isolated writes are both supported and explicitly authorized.

Reasoning effort, including `ultra`, never authorizes delegation. Keep `agents.enabled=false`
unless the authorization envelope or applicable project/skill instructions explicitly allow it.

If exact approval is required for every child, or the runtime cannot verify/enforce the child
envelope, set `agents.enabled=false` and launch separate top-level workers instead.

## Stop conditions

Terminate or decline to resume when the worker requests unapproved scope, cannot honor isolation,
repeats without new evidence, exhausts the agreed time/retry budget, or encounters an approval it
cannot safely surface. Preserve enough output for diagnosis without retaining secrets.

Official references: [subagents](https://developers.openai.com/codex/agent-configuration/subagents)
and [command reference](https://developers.openai.com/codex/cli/reference).
