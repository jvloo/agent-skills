# Invocation safety

Read for initial execution setup; revisit when the executable, configuration, trust, capabilities,
or provider changes. Confirm required controls against installed help and version-compatible official
documentation. Help can omit supported options. Keep a required control, use a verified equivalent,
or stop; optional conveniences may be omitted.

## Preflight

Record a concise outcome for each applicable check below. Use read-only inspection, not model
prompts or destructive permission probes.

| Check | Sufficient evidence before dispatch |
|---|---|
| Authority | The user's request and existing approvals cover the intended actions; native runtime approval is granted or not required. |
| Execution context | Resolved executable/version, process cwd, OS user, provider/auth route, relevant environment and credential-store access. Record variable names or status, never secrets. |
| Workspace | In Git: revision, dirty state, applicable instructions, and writer ownership. Outside Git: verified directory and supplied inputs; revision/branch fields are not applicable. |
| Capabilities | Explicit launch controls plus the applicable configuration/policy layers that can alter the required tools, roots, network, hooks, or external access. Check only capabilities relevant to this launch. |
| Limits | Deadline controller, retry bound, persistence choice, and an enforcement mechanism for each limit the contract requires to be hard. |
| Children | When enabled: supported child controls, shared/differing auth context, allowed tools, ownership, and isolated workspaces for writers. |

Before each model dispatch or resume, perform the authentication check for the selected route below.
Reuse unchanged version, trust, and configuration evidence; recheck a differing child context.
If the sandbox cannot access the normal credential store, diagnose through an authorized execution
path. A sandbox-only failure does not prove the user's login is invalid.

Distinguish behavioral scope from enforced boundaries. A contract can define the question or files
to work on; a required filesystem/network/tool restriction needs evidence from the runtime or
documented CLI control. Intended flags alone do not override managed policy. If a required boundary
cannot be established, narrow to an already authorized capability set or report the specific gap.
This is not a requirement to audit unrelated configuration or prove every possible worker action safe.

## Authentication

Use `codex --version` and relevant `--help` commands to establish the installed interface.
Resolve the selected provider from launch flags/profile/configuration before choosing an auth check.

- For stored OpenAI account or API-key login, run `codex login status` through the same
  execution path and credential context as the worker; require successful status.
- For a provider using its own environment credential, federation, or credential helper, verify
  the documented credential source and its availability without printing its value. Use a
  provider-native non-generating status check when available. OpenAI login status is not evidence
  for this route.
- For a deliberately unauthenticated local provider, such as an authorized `--oss` setup,
  verify the selected endpoint and local model/service availability without generation. Record
  authentication as not required; do not demand an OpenAI login.

A credential's presence or local login record does not prove remote validity or model entitlement.
If the route has no non-generating validity check, record that limitation; the first authorized,
bounded task call may establish remote access. Do not add a separate paid probe. Stop on an
authentication error instead of retrying indefinitely.

## Workspace and controls

Inspect applicable repository instructions and the configuration layers that affect required
controls: user/project/profile settings, managed policy, extra roots, exec rules, hooks, plugins,
and MCP/tools. Record the relevant overrides. A shell sandbox does not by itself restrict every
MCP action or external service.

| Intent | Control |
|---|---|
| Unattended read-only work | `--sandbox read-only` and config argument `approval_policy="never"` |
| Unattended workspace edits | `--sandbox workspace-write` and config argument `approval_policy="never"` |
| Monitored permission requests | Config argument `approval_policy="on-request"`, only with a channel that can answer native prompts |
| Disable internal subagents | `-c agents.enabled=false` |
| Additional writable root | `--add-dir <path>`, only within authorized scope |

The string-valued config examples above show argument contents: the double quotes belong to TOML;
backslashes do not. See the executable argument-list example in [bounded workers](bounded-worker.md).
`approval_policy=never` denies blocked capabilities; it does not grant them. Automatic approval
review is not new user authority. If non-interactive approval cannot be serviced, use already
authorized controls with `never` or return the blocker.

Workspace-write still protects `.git` (including resolved worktree Git directories), `.agents`,
and `.codex` within writable roots. For authorized commits or configuration edits, verify a native
permission route that covers those writes, or let the invoking agent perform them after checking
the worker's changes. Do not assume workspace-write with `never` grants protected-path access.

Use `--strict-config` when unknown configuration must fail; otherwise inspect compatibility
without requiring unrelated stale settings to block the task. `--ignore-user-config` can remove
required defaults as well as unwanted customization, so inspect its consequences first.
Do not use bypass flags, `danger-full-access`, or `--ignore-rules` merely to avoid a prompt.
An exceptional bypass requires specific user/runtime authority and independent external containment.

Outside Git, use a verified safe directory and add `--skip-git-repo-check`. Keep sandbox and
approval restrictions intact. Do not initialize a repository or modify trust settings just to ask
a supplied-text question.
Keep the sandbox's normal temporary-directory support unless the task requires a stricter boundary.
If disabling it, verify required tools still work: macOS Git's launcher can need temporary cache
writes even for inspection. An unrelated cache warning is not evidence that the requested edit is denied.

## Approval and prompt transport

Existing authorization does not need another confirmation. Use the parent runtime's native approval
mechanism only when required; a chat confirmation does not replace sandbox/tool approval. A material
expansion beyond existing authority needs authorization before the next action. A routine in-scope
model choice, follow-up, or previously authorized write is not automatically an expansion.

When native approval is needed, describe the concrete task, directory, permitted actions, provider,
model, relevant child permissions, limits, and exclusions. Do not request a reusable executable or
command-prefix approval broader than the task requires.

Never interpolate code, logs, or Markdown into shell command text. Send the contract through a safe
stdin facility or a securely created, access-restricted prompt file. Keep temporary files outside
tracked paths, remove them when no longer needed, and do not place real secrets in prompts. Avoid
running untrusted repository code in an environment containing credentials. Worktrees and CLI tool
policies are not substitutes for host containment when untrusted code requires it.

Official sources: [CLI reference](https://developers.openai.com/codex/cli/reference),
[configuration](https://developers.openai.com/codex/config-reference),
[authentication](https://developers.openai.com/codex/auth), and
[non-interactive mode](https://developers.openai.com/codex/non-interactive-mode).
See also [protected paths](https://developers.openai.com/codex/agent-approvals-security#protected-paths-in-writable-roots).
