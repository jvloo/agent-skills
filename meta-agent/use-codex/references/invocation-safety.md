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
revision, dirty state, effective user/project/managed configuration, hooks, web search, apps and
connectors, plugins, skills, MCP servers, rules, and trust settings before giving Codex access.

## Approval preflight

Before any model prompt or internal child spawn, record and resolve:

- working directory, revision, and in-scope paths;
- read-only or write authority and workspace isolation;
- allowed commands, shell network, hosted tools, external systems, and credential exposure;
- effective main and child model/effort, including requested overrides and compatibility;
- whether Codex subagents are allowed, their enforced concurrency, and ownership boundaries;
- wall-clock/cost limits, retry count, and session persistence.

User/task authorization, parent-runtime approval, and Codex controls are independent. Use the
parent runtime's native approval prompt when one exists; a chat confirmation does not replace a
required tool or sandbox approval. Fail closed when required approval is unavailable or unclear.

Adapt this into the runtime's native approval message:

```text
Allow the local Codex CLI to run <bounded task> in <directory> at <revision> using
<effective model>/<effort>? It may <read/write/commands/local network> and use <hosted tools or
none>. Codex subagents: <disabled, or enabled with enforced concurrency and the same scope>.
Limits: <time/cost/retries/persistence>. It will not <commits/pushes/destructive actions/external
mutations/other exclusions>.
```

Any expansion in scope, writes, commands, network, hosted/external access, model/effort, subagents,
concurrency, cost/time, or persistence requires fresh user/task authorization and applicable
parent-runtime approval before a follow-up or resume.

## Model and effort preflight

Choose every unspecified model or effort using the entrypoint's task-based routing; explicit user
choices take precedence. Resolve and verify the exact resulting pair against the installed CLI and
account model catalog before launch. Stop if unavailable; never silently downgrade, upgrade, or
change effort. Use `ultra`, or a model outside the default Sol/Terra/Luna routing set, only on
explicit request.

Use a supported runtime model picker or catalog without launching a model. When installed help
exposes the experimental `codex debug models`, it can report the account catalog and supported
efforts; ignore entries marked hidden or internal. Otherwise use installed help and current official
documentation, and stop if the exact pair cannot be verified.

## Native controls

Pass explicit security and execution controls on every call:

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

Do not use `--ignore-user-config` casually: it can remove required safe defaults. Loaded
configuration can also add tools, MCP servers, plugins, hooks, or instructions. Inspect effective
layers and use `--strict-config` where drift must fail rather than degrade silently.

## Hosted-tool containment

The shell sandbox applies to spawned commands. Its filesystem and network policy does not itself
disable hosted web search, apps/connectors, plugins, or MCP tools. Inventory these routes and apply
their effective feature, enablement, allowlist, and approval controls separately. A disabled local
network is not a closed-network claim while any hosted route can retrieve or mutate external data.
If the installed version cannot verifiably contain a route, disable it or report the limitation.

## Prompt transport and secrets

Never interpolate untrusted code, logs, or Markdown into shell-quoted command text. Send the worker
contract through the parent runtime's safe stdin facility or a securely created temporary file.
Keep prompt and result files outside tracked paths, restrict access where supported, and remove them
after use. Do not place real secrets in prompts. Give Codex only credentials required by the task,
and avoid running untrusted repository code in a process environment containing credentials.

Official references: [command reference](https://developers.openai.com/codex/cli/reference),
[configuration reference](https://developers.openai.com/codex/config-reference), and
[agent approvals and security](https://developers.openai.com/codex/agent-approvals-security).
