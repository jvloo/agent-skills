# Invocation safety

Use this reference before launching Claude or deciding which trust, configuration, permission, and
tool controls apply. Confirm every option against the installed CLI; top-level help is not an
exhaustive description of every subcommand.

## Preflight

Use the host's executable lookup, then check:

```text
claude --version
claude auth status
claude --help
claude <relevant-subcommand> --help
```

Require a usable authenticated state before a model call. Do not expose credential values while
diagnosing authentication. Record the version because agent-view and isolation behavior evolve
quickly.

For `fable`, confirm the selector in installed help and verify account availability through a
supported model-selection surface such as `/model`. `claude auth status` may show only a broad plan
type; it does not prove seat entitlement, organization enablement, or usage-credit availability.
Record whether access is included or usage-credit-backed and ensure that billing mode fits the
approved budget. Fail closed when selector, provider, entitlement, or billing support is unknown.

## Approval preflight

Resolve approval before a prompt reaches the model or Claude can create a child worker. Record the
planned envelope:

- working directory, repository revision, and in-scope paths;
- read-only or write authority;
- allowed commands, network access, and external systems;
- main and child model selectors, effort compatibility, provider, and any Fable entitlement evidence;
- whether autonomous Claude subagents are allowed, their requested concurrency, any enforcement
  mechanism, and ownership boundaries;
- cost ceiling, wall-clock timeout, retry limit, and session-persistence choice.

User or task authorization, parent-runtime execution approval, and Claude's internal controls are
independent. Use the parent runtime's native tool or sandbox approval mechanism when it exists; do
not treat a plain-text confirmation as a workaround for an approval the runtime itself must grant.
Perform executable discovery, version/help inspection, authentication status, and repository-state
checks without a model call where the runtime permits those read-only operations.

When runtime approval is required, adapt this into its native approval message:

```text
Allow the local Claude Code CLI to run <bounded task> in <working directory> using
<model>/<effort>? It may <read/write/commands/network>. Claude subagents: <disabled, or allowed
autonomously within the same scope; enforced limit/control or advisory target>. Limits: <cost>,
<time>, <persistence>. It will not
<commits/pushes/destructive or external mutations/other exclusions>.
```

Keep the request narrow enough that approval communicates the real capability envelope. Do not ask
for a reusable executable or command-prefix approval broader than the task requires merely to avoid
future prompts.

Do not assume the parent runtime can intercept Claude's internal `Agent` calls. Agent definitions
and prompt instructions can shape child behavior but do not hard-limit spawn count. If approval is
required for each child or an exact count cannot be enforced by a verified control, omit `Agent` and
dispatch each Claude process separately through the parent runtime's native approval path.

Fail closed if any required approval is denied or its state cannot be determined. Narrow the
contract to an already approved envelope or stop and request the missing approval. If new evidence
would materially expand scope, writes, commands, network or external access, model/effort,
subagents, concurrency, cost/time, or persistence, obtain fresh user authorization and applicable
runtime approval before sending a follow-up, resuming, or starting another worker.

## Trust and containment controls

`claude -p` skips the workspace-trust dialog. Inspect repository instructions, settings, hooks,
plugins, skills, commands, agents, and MCP configuration before using print mode in a workspace.
Choose controls for the threat being addressed; their names are not synonyms.

| Control | What it changes | What it does not provide |
|---|---|---|
| `--safe-mode` | Disables customizations for troubleshooting, while policy settings still apply | Built-in tools, permission policy, or host-process containment |
| `--bare` | Skips most auto-discovered project/user customization and context for a minimal scripted call; current releases may require API-key, provider, or configured helper authentication instead of OAuth/keychain | A read-only worker; Bash and file tools remain available, and authentication behavior must be confirmed in installed help |
| `--restricted` | Removes command/code tools and WebFetch by default, ignores user/project/local settings, confines file tools to working directories, and refuses bypass mode | An OS sandbox; `--tools` can explicitly add command/code tools back |
| `--setting-sources` | Selects which user, project, and local setting sources load | Control over managed policy or explicit `--settings`; tool or process isolation |
| `--strict-mcp-config` | Ignores MCP servers outside explicit `--mcp-config` input, subject to managed policy | Disabling built-in tools or containing the process |

Combine controls when their concerns overlap. For example, restricted mode does not by itself omit
all MCP servers, so pair it with strict MCP configuration when MCP exclusion matters. Do not weaken
restricted mode by naming Bash, PowerShell, REPL, or another code-running tool in `--tools` unless
the contract requires it and the parent runtime supplies adequate containment.

These are CLI policy controls, not hard host containment. For adversarial content, untrusted code,
or commands with material host impact, use a parent-runtime or operating-system sandbox with
filesystem, process, credential, and network boundaries.

## Prompt-file safety

Adapt commands to the host shell. Never interpolate code, logs, Markdown, or other untrusted text
into a shell-quoted prompt: quotes, substitutions, and control characters can change execution.
Prefer the parent runtime's safe stdin facility or a securely created, access-restricted temporary
file.

Piped stdin is limited to 10 MB. For larger input, place it in a file Claude is allowed to read and
reference that path in the contract. When an interactive or background session must read a prompt
file, keep it in the intended working directory, verify the path is untracked and ignored, do not
overwrite a tracked file, and remove it after the session no longer needs it.

## Permission and tool controls

Always pass an explicit `--permission-mode` suited to the task. Prefer `plan` for read-only analysis,
`dontAsk` for unattended fixed-tool calls, and a monitored default/manual mode when a person or
permission handler will answer prompts. Never use `bypassPermissions` merely to avoid prompts.

These Claude controls implement only the approved envelope. They cannot replace missing user
authority or parent-runtime execution approval.

For unattended print-mode calls, add `--permission-prompts none` only when installed help exposes
it. It makes any action that would prompt fail automatically; the permission mode still controls
the remaining decisions. `--tools` selects available built-in tools, `--allowedTools` pre-approves
matching calls, and `--disallowedTools` denies tools or patterns. None substitutes for the others.

Official references: [CLI reference](https://code.claude.com/docs/en/cli-usage),
[permission modes](https://code.claude.com/docs/en/permission-modes), and
[programmatic usage](https://code.claude.com/docs/en/headless).
