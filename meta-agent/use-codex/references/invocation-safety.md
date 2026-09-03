# Invocation safety

Read this before launching Codex. Confirm every option against the installed CLI and relevant
subcommand help.

## Preflight

Use the host's executable lookup, then check:

```text
codex --version
codex login status
codex --help
codex exec --help
codex exec resume --help       # when resuming
```

Do not expose credentials while diagnosing authentication. Inspect repository instructions,
revision, dirty state, applicable user/project configuration, hooks, plugins, skills, MCP servers,
rules, and trust settings before giving Codex access.

## Approval preflight

Before any model prompt or internal child spawn, record and resolve:

- working directory, revision, and in-scope paths;
- read-only or write authority and workspace isolation;
- allowed commands, network access, external systems, and credential exposure;
- model and reasoning effort;
- whether Codex subagents are allowed, their enforced concurrency, and ownership boundaries;
- wall-clock/cost limits, retry count, and session persistence.

User/task authorization, parent-runtime approval, and Codex controls are independent. Use the
parent runtime's native approval prompt when one exists; a chat confirmation does not replace a
required tool or sandbox approval. Fail closed when required approval is unavailable or unclear.

Adapt this into the runtime's native approval message:

```text
Allow the local Codex CLI to run <bounded task> in <directory> at <revision> using
<model>/<effort>? It may <read/write/commands/network>. Codex subagents: <disabled, or enabled with
enforced concurrency and the same scope>. Limits: <time/cost/retries/persistence>. It will not
<commits/pushes/destructive actions/external mutations/other exclusions>.
```

Any expansion in scope, writes, commands, network, external access, model/effort, subagents,
concurrency, cost/time, or persistence requires a new checkpoint before a follow-up or resume.

## Native controls

Prefer explicit values on every call:

| Intent | Codex controls |
|---|---|
| Read-only unattended inspection | `--sandbox read-only -c approval_policy=\"never\"` |
| Read-only monitored work | `--sandbox read-only -c approval_policy=\"on-request\"` |
| Authorized unattended workspace edits | `--sandbox workspace-write -c approval_policy=\"never\"` |
| Authorized monitored workspace edits | `--sandbox workspace-write -c approval_policy=\"on-request\"` |
| Model selection | `--model <supported-model>` |
| Reasoning effort | `-c model_reasoning_effort=\"<supported-effort>\"` |
| Disable internal subagents | `-c agents.enabled=false` |
| Bound internal concurrency | `-c agents.max_concurrent_threads_per_session=<n>` |

`approval_policy=never` means Codex never pauses; it does not grant blocked capabilities. Use it for
unattended runs only with a sandbox that already expresses the complete approved envelope.
`approvals_reviewer=auto_review` delegates eligible approval decisions to another model and is not
equivalent to user approval or expanded authorization.

Some releases expose `--ask-for-approval` only before the subcommand while others document it with
`exec`. The repeatable `-c approval_policy=\"...\"` override is less sensitive to flag position;
still confirm it in installed help before use.

Never use `--dangerously-bypass-approvals-and-sandbox`/`--yolo`, `danger-full-access`,
`--dangerously-bypass-hook-trust`, or `--ignore-rules` merely to avoid a prompt. If an exceptional
workflow explicitly requires one, obtain specific user and runtime approval and require independent
external containment. Prefer narrow writable roots, network settings, or exec-policy rules.

Non-interactive approval prompts may not be serviceable in the parent runtime. After the complete
envelope is approved up front, prefer `approval_policy=never` so out-of-envelope actions fail and
return control to the orchestrator. Use `on-request` only when the process is actively supervised
through a channel that can present and answer native Codex prompts.

Do not use `--ignore-user-config` casually: it can improve reproducibility, but may also remove
required safe defaults. Conversely, loaded configuration can add tools, MCP servers, hooks, or
instructions. Inspect the effective layers and use `--strict-config` where configuration drift must
fail rather than degrade silently.

## Prompt transport and secrets

Never interpolate untrusted code, logs, or Markdown into shell-quoted command text. Send the worker
contract through the parent runtime's safe stdin facility or a securely created temporary file.
Keep prompt and result files outside tracked paths, restrict access where supported, and remove them
after use. Do not place real secrets in prompts. Give Codex only credentials required by the task,
and avoid running untrusted repository code in a process environment containing credentials.

Official references: [command reference](https://developers.openai.com/codex/cli/reference),
[configuration reference](https://developers.openai.com/codex/config-reference), and
[agent approvals and security](https://developers.openai.com/codex/agent-approvals-security).
