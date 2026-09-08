# Agent Skills

Xavier Loo's collection of portable skills for practical agentic workflows. Skills are organized by
capability so the repository can grow across engineering, research, collaboration, and meta-agent
work without coupling them to one agent runtime.

## Skills

| Category | Skill | Purpose |
|---|---|---|
| Meta-agent | [`use-claude`](meta-agent/use-claude/SKILL.md) | Consult or delegate to the local Claude Code CLI. |
| Meta-agent | [`use-codex`](meta-agent/use-codex/SKILL.md) | Consult or delegate to the local Codex CLI. |

The current skills form the `meta-agent` category. They are parent-runtime, machine, shell, and
operating-system agnostic, defining worker contracts and safety boundaries without depending on one
orchestrator's terminal or subagent APIs.

Both skills share the same workflow, reference structure, worker contract, and result schema.
Provider differences are limited to CLI commands, authentication, capabilities, lifecycle handling,
and curated model guidance. Both support bounded consultations, implementation, supervised sessions,
and internal subagents when the task benefits from them.

## Install

Copy the complete skill directory into a location the **invoking runtime** discovers. A common
setup gives Codex `use-claude` and Claude Code `use-codex`:

| Invoking runtime | Personal installation | Project installation |
|---|---|---|
| Codex | `~/.agents/skills/use-claude/` | `.agents/skills/use-claude/` |
| Claude Code | `~/.claude/skills/use-codex/` | `.claude/skills/use-codex/` |

These paths follow the current [Codex skill guide](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
and [Claude Code skill guide](https://code.claude.com/docs/en/skills#where-skills-live).
For an existing installation, update the directory already managed by your runtime or installer;
avoid duplicate copies with the same skill name. Back up local customizations before replacing it.

Each skill is self-contained: keep its `assets/` and `references/` alongside `SKILL.md`. Repository
documentation does not need to be copied into the installed skill. Restart or reload the invoking
runtime if it does not discover the change.

The worker CLI must be installed and executable from the invoking runtime. Authentication must fit
the selected provider: an authorized unauthenticated local Codex provider does not require an
OpenAI login. The skills check the applicable route and required controls before dispatch; they do
not install executables or bundle credentials.

## Use

Ask the invoking agent for a bounded task, for example:

> Use Claude to review this diff for correctness. Report findings with evidence.

> Use Codex to give a second opinion on this design, using only the supplied documents.

Reading, reviewing, or installing a skill does not request a model call. A request to consult the
CLI authorizes calls within that task. Existing choices and approvals carry forward; additional
authority is needed only for actions outside that scope or permissions required by the runtime.
Worker controls constrain execution and do not grant user or runtime authority.

Model and effort selection follows explicit choice, verified account/configuration defaults, then
a justified task adjustment. Provider recommendations are advisory; consult the
[Claude guidance](meta-agent/use-claude/references/model-selection.md) or
[Codex guidance](meta-agent/use-codex/references/model-selection.md) for compatibility and billing.

The invoking agent owns acceptance: it checks completion, inspects artifacts, and verifies results.
Every concurrent writer needs an isolated workspace. Supervisors enforce deadlines and account for
owned child work; a process wait interval or a prompt budget does not enforce a timeout or spending
ceiling.

## Skill contents

Both skill directories have the same layout:

| File | Purpose |
|---|---|
| `SKILL.md` | Discovery, shared workflow, authority, and host integration. |
| `references/invocation-safety.md` | Authentication, workspace, permissions, and prompt transport. |
| `references/model-selection.md` | Shared selection policy and provider recommendations. |
| `references/bounded-worker.md` | Finite calls, limits, persistence, and result handling. |
| `references/supervised-sessions.md` | Resume, steering, cleanup, parallel work, and subagents. |
| `assets/worker-contract.md` | Shared template for complex assignments. |
| `assets/result.schema.json` | Shared structured handoff schema; optional for plain consultations. |

## Project status

The skills are maintained on `main`; no tagged release has been published yet. The
[changelog](CHANGELOG.md) records changes since the initial import. Structural and behavioral
validation are described in [CONTRIBUTING.md](CONTRIBUTING.md); repeatable evaluation fixtures and
release automation remain on the [roadmap](ROADMAP.md).

## Contributing

See the [roadmap](ROADMAP.md) for planned directions and [CONTRIBUTING.md](CONTRIBUTING.md) for the
contribution process. Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
