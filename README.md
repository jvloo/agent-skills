# Agent Skills

Portable skills for orchestrating local coding-agent CLIs with bounded authority, explicit approval
preflights, and independent verification.

## Skills

| Category | Skill | Purpose |
|---|---|---|
| Meta-agent | [`use-claude`](meta-agent/use-claude/SKILL.md) | Run Claude Code CLI as a bounded cross-model worker. |
| Meta-agent | [`use-codex`](meta-agent/use-codex/SKILL.md) | Run Codex CLI/GPT as a bounded worker, with optional Codex subagents. |

Both skills are parent-runtime, machine, shell, and operating-system agnostic. They define a worker
contract and safety boundary without depending on one orchestrator's terminal or subagent APIs.

## Install

Copy the desired skill directory into a location your agent runtime discovers. For example:

```text
<agent-skills-directory>/use-claude/
<agent-skills-directory>/use-codex/
```

Then restart or reload the runtime. Each skill is self-contained; keep its `assets/` and
`references/` directories with `SKILL.md`.

The corresponding CLI must already be installed and authenticated. The skill deliberately does not
bundle credentials, install executables, or bypass the parent runtime's approval system.

## Safety model

Loading a skill does not authorize a worker invocation. Each skill separates:

1. user or task authorization;
2. approval required by the parent runtime;
3. controls enforced by the worker CLI.

The orchestrating agent approves the complete execution envelope before prompting a worker,
constrains its tools and workspace, independently verifies its output, and retains final ownership.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
