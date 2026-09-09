---
name: use-claude
description: Meta-agent skill to consult or delegate a bounded task to the local Claude Code CLI for reviews, second opinions, implementation, or supervised sessions. Use when the user or active workflow requests that CLI worker. Reviewing or installing this skill does not request a model call; browser UI work and ordinary host subagents are separate.
metadata:
  version: "0.2.0"
---

# Use Claude

Use the locally installed CLI named above. The invoking agent owns scope, integration, and
acceptance; the worker supplies work to inspect. Do not substitute an API, SDK, hosted connector,
cloud task, or browser UI.

## Authority and defaults

A request to consult this CLI authorizes in-scope model calls. Carry existing choices and approvals
forward. Choose routine model, effort, and limits within that authority; ask only for missing
authority or a material expansion. User and runtime instructions take precedence over this skill.
Worker controls cannot replace parent-runtime permissions or authorize additional external actions.

Prefer finite, non-interactive calls with minimal capabilities, an enforced timeout, finite retries,
and no session persistence unless resume is useful. Use internal subagents when independent work
materially improves the result after coordination and cost; keep simple or sequential work
single-worker. Delegation stays within the original task, capabilities, and budget. Avoid automatic
reviewer chains and recursive handoffs of the same assignment between providers.

## Workflow

1. Complete the [invocation preflight](references/invocation-safety.md) before dispatch. Keep
   authentication, approval, executable/configuration provenance, and deadline-controller evidence
   in the supervisor record, outside the worker prompt. Before a resume or further delegation,
   recheck authentication in the relevant context and any changed boundaries; reuse unchanged
   executable, configuration, and trust evidence.
2. Follow [model selection](references/model-selection.md): explicit choice, verified defaults,
   then justified adjustments. Provider-specific recommendations are advisory. Consult the dated
   [model evidence](references/model-evidence.md) only when changing or maintaining a routing profile.
3. Give a compact contract: objective, done criteria, relevant inputs, permitted actions, output,
   limits, and stop conditions. Scale the [worker template](assets/worker-contract.md) to the task.
   Supply relevant evidence rather than the entire conversation. For second opinions, state the
   question and sources without prescribing a verdict.
4. Follow [bounded workers](references/bounded-worker.md) for finite tasks, including long tasks
   that need no steering. Use the [runner guide](references/runner.md) when choosing the optional
   local helper. For client-disconnect recovery or durable job records, use
   [recoverable jobs](references/jobs.md). Read
   [supervised sessions](references/supervised-sessions.md) when using resumes, live steering,
   parallel workers, or internal subagents.
5. Verify completion, inspect artifacts, and run checks appropriate to the change. Add independent
   review when consequential or disputed work warrants it. Report the worker's contribution,
   verified results, and unresolved limitations.

## Host integration

Use the host's process and terminal tools. A yielded process/session ID means work is still running;
a tool wait interval is not a kill timeout. Capture stdout, stderr, and exit status, using separate
files if the host merges streams. Enforce deadlines and clean up owned worker processes and child
work. Keep the user informed without narrating unchanged polls. Do not create user-visible host
tasks merely to dispatch CLI workers.

Every concurrent writer needs an isolated workspace. Parallel readers may share a stable revision.
A sole authorized writer may use the current checkout while preserving user changes. Worktrees
separate edits, not credentials, processes, network, or external systems. Inspect and integrate
changes before cleanup.
