# Bounded print-mode worker

Use `claude -p` for a finite assignment with a defined result and no need for live steering. Build
the prompt from [../assets/worker-contract.md](../assets/worker-contract.md), and apply the trust and
prompt rules in [invocation-safety.md](invocation-safety.md).

Before launch, resolve and record the full approval envelope from the contract. Do not send the
prompt if user/task authorization or any required parent-runtime tool or sandbox approval is denied,
unknown, or unavailable. Claude permission and tool flags constrain an approved call; they do not
authorize it.

## Invocation shape

This is a semantic pattern, not a copy-paste wrapper. Translate it for the host shell and omit or
replace options absent from installed help:

```text
claude -p
  --model <model>
  --effort <effort>
  --permission-mode <mode>
  --permission-prompts none
  --tools <required-built-in-tools>
  [--allowedTools <pre-approved-rules>]
  --output-format json
  --json-schema <result-schema>
  --max-budget-usd <ceiling>
  [--no-session-persistence]
  < <prompt-file>
```

Use `--permission-prompts none` only when supported and only for an unattended call. Choose
`--max-budget-usd` from the task's value and risk rather than applying a universal ceiling. Enforce
a separate parent-runtime wall-clock timeout: a spend ceiling is not a time limit.

Decide persistence before launch. Add `--no-session-persistence` when the contract is one-shot or
contains sensitive context and no resume is needed. Otherwise retain `session_id` deliberately and
use `--resume` only for an in-scope follow-up. Do not assume the new call preserves launch-time
restrictions; verify the effective contract and installed resume behavior.

A resume is another model call. Recheck approval before sending it, and obtain fresh authorization
and parent-runtime approval first if its prompt or effective capability materially expands the
approved envelope.

## Least-privilege shapes

For repository investigation, expose only read/search tools when the installed tool names support
that boundary. For implementation, add edit tools and only the exact command capability needed for
authoritative checks. Treat tool availability and permission pre-approval as separate decisions.
Pair restricted mode with a minimal explicit tool set only when adding a removed tool is justified.
When `dontAsk` work needs a command or another non-read-only action, pre-approve only the exact
rule required; listing a tool in `--tools` does not itself approve its use.

Omit `Agent` by default. If the approved envelope permits autonomous Claude-managed subagents,
include the installed `Agent` tool explicitly; an allowlist that contains only read/search tools
silently prevents delegation. A read-only shape is:

```text
claude -p
  --restricted
  --strict-mcp-config
  --permission-mode plan
  --permission-prompts none
  --tools "Read,Grep,Glob,Agent"
  --disallowedTools "mcp__*"
  < <prompt-file>
```

Use only options confirmed for the installed version. For an untrusted workspace, `--safe-mode`
can disable discovered instructions and customizations while retaining built-in subagents; pass
required trusted instructions explicitly. It also disables custom agents, including definitions
provided with `--agents`, so do not combine those modes.

When named specialists materially improve the task, omit `--safe-mode`, address untrusted workspace
content with compatible installed controls and parent-runtime containment, and define a bounded
read-only set with `--agents <trusted-json>`. Include each child's purpose, tools, model, turn limit,
and output obligation. Where supported,
`--append-subagent-system-prompt <shared-child-constraints>` can reinforce constraints common to
every child. Defining agents does not enable delegation by itself: the parent still needs `Agent`.
Require the parent to reconcile child findings rather than forwarding their verdicts.

`--agents` bounds which named definitions are available; it does not enforce spawn count. Prompted
child-count and concurrency limits are advisory unless a verified hook, permission handler, or
runtime control enforces them. If exact per-spawn approval is required, omit `Agent` and have the
invoking agent launch separately approved Claude processes instead.

## Result handling

The parent runtime must capture stdout, stderr, and the process exit status separately. Apply these
checks in order:

1. Fail or diagnose a non-zero process status; do not accept a plausible-looking partial stdout.
2. Parse the complete JSON envelope, or the final `result` event for `stream-json`.
3. When `--json-schema` is used, consume `structured_output`, not prose from `result`.
4. Treat a non-empty `mcp_server_errors` array as a failed dependency when the contract relies on
   MCP. Invalid MCP entries can otherwise be skipped while the run exits successfully.
5. Record `session_id`, usage, `total_cost_usd`, and per-model cost data when present. Cost fields
   are client-side estimates, not billing truth.
6. Compare the artifact and evidence with the worker contract, inspect all diffs, and run independent
   acceptance checks.

For streamed work, parse newline-delimited events and distinguish intermediate subagent messages
from the final result. A timeout or interrupted stream is incomplete even if useful text appeared.
Report stderr warnings without exposing secrets.

Official references: [Run Claude Code programmatically](https://code.claude.com/docs/en/headless)
and [create custom subagents](https://code.claude.com/docs/en/sub-agents).
