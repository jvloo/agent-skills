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

Use `claude --version` and relevant `--help` commands to establish the installed interface.
Resolve the provider and auth route from the launch environment, settings, and flags.

- For normal account/provider execution, run `claude auth status` through the same authorized
  execution path. Require a usable status for the selected route, not an unrelated account login.
- For `--bare`, confirm installed behavior: current releases do not read OAuth/keychain auth.
  Anthropic uses `ANTHROPIC_API_KEY` or a helper supplied through `--settings`; third-party
  providers use their own credentials. Verify that source without printing credentials.
- If a custom provider/helper cannot be represented by auth status, use its documented
  non-generating credential/status check. Do not diagnose missing Claude account login as a
  failure of an independently authenticated provider.

An environment API key can select a paid billing route instead of subscription usage. Check that
the resolved route fits existing spending authority. Credential presence/status does not prove
remote validity or model entitlement. If no non-generating validity check exists, record the
limitation; the first authorized, bounded task call may establish remote access. Do not add a
separate paid probe. Stop on an authentication error instead of retrying indefinitely.

## Workspace and controls

Print mode skips the workspace-trust dialog and can silently ignore invalid settings. Inspect
applicable repository instructions and configuration that can change required controls: settings,
hooks, plugins, skills, commands, agents, and MCP servers. Use the following controls for their
documented purpose; combine them only as needed.

| Control | Effect and limit |
|---|---|
| `--tools` | Selects built-in tool availability; does not pre-approve calls or independently exclude MCP. |
| `--allowedTools` / `--disallowedTools` | Pre-approves / denies matching calls. Keep command rules narrow. |
| `--permission-mode plan` | Analysis/planning behavior; shell commands can still run. Use a read/search tool set for read-only inspection. |
| `--permission-mode dontAsk` | Unattended work with denied prompts; pre-approve necessary non-read-only actions separately. |
| `--permission-prompts none` | In supported print-mode versions, denies actions that would prompt. Does not replace the permission mode. |
| `--restricted` | Removes command/code tools and WebFetch unless explicitly restored via `--tools`; ignores user/project/local settings, confines file tools to working directories, and rejects bypass mode. Writes to settings, Git, and tool configuration require a person or configured permission handler. Managed settings and `--settings` still apply. |
| `--strict-mcp-config` | Excludes MCP outside explicit configuration, subject to managed policy. |
| `--safe-mode` | Disables discovered customizations, including custom agents and `--agents` definitions; preserves built-in tools, auth, and policy. |
| `--bare` | Minimal discovered context/customization; retains command/file tools and changes authentication behavior. |
| `--setting-sources` | Chooses user/project/local settings sources; does not remove managed policy or explicit settings. |

Always choose a permission mode. Use monitored manual/default mode only when a person or handler
can answer prompts. Never use bypass permissions merely to avoid prompts. An exceptional bypass
requires specific user/runtime authority and independent external containment.
For an authorized commit, `--restricted` plus `dontAsk` and a Git allowlist is insufficient:
the protected-write gate still needs a person or permission handler. Before dispatch, choose a
compatible authorized execution setup that preserves required containment, or let the invoking
agent commit verified changes. This is a capability adjustment, not missing user authorization.
For untrusted workspace content, `--safe-mode` can remove discovered instructions; pass required
trusted instructions explicitly. For actual untrusted command execution, use host/OS containment.

No Git repository is required for supplied-text consultations. Use a verified directory. Stdin is
limited to 10 MB; provide larger inputs as files the worker is authorized to read. A background
session's prompt file must remain accessible in its intended working directory until consumed;
use an untracked, ignored path, preserve existing files, and remove it when no longer needed.

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

Official sources: [CLI reference](https://code.claude.com/docs/en/cli-usage),
[permission modes](https://code.claude.com/docs/en/permission-modes), and
[programmatic usage](https://code.claude.com/docs/en/headless).
