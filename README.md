# Agent Skills

Xavier Loo's collection of portable skills for practical agentic workflows. Skills are organized by
capability so the repository can grow across engineering, research, collaboration, and meta-agent
work without coupling them to one agent runtime.

## Skills

| Category | Skill | Purpose |
|---|---|---|
| Meta-agent | [`use-claude`](skills/meta-agent/use-claude/SKILL.md) | Consult or delegate to the local Claude Code CLI. |
| Meta-agent | [`use-codex`](skills/meta-agent/use-codex/SKILL.md) | Consult or delegate to the local Codex CLI. |

The current skills form the `meta-agent` category: portable skills for delegating to and
supervising local CLI agents. Their guidance is independent of the invoking runtime, shell, and
operating system. An optional Python 3.9+ helper implements bounded process-group supervision on
macOS/Linux; other platforms use their host's verified process tools. The host supplies permissions
and containment, and the worker CLI supplies the agent's tool loop.

Both skills share the same workflow, reference structure, worker contract, and result schema.
Provider differences are limited to CLI commands, authentication, capabilities, lifecycle handling,
and curated model guidance. Both support bounded consultations, implementation, supervised sessions,
and internal subagents when the task benefits from them.

## Repository layout

```text
skills/
  meta-agent/
    use-claude/
    use-codex/
evals/          # Evaluation scenarios and reports
tests/          # Automated tests and fixtures
```

Add future categories under `skills/<category>/<skill-name>/`. Install the individual skill
folder, including its supporting files. Repository paths have moved from `meta-agent/` to
`skills/meta-agent/`; existing installed copies keep their runtime discovery paths.

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

Each skill is self-contained: keep its `assets/`, `references/`, and `scripts/` alongside `SKILL.md`. Repository
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
[Claude guidance](skills/meta-agent/use-claude/references/model-selection.md) or
[Codex guidance](skills/meta-agent/use-codex/references/model-selection.md) for compatibility and billing.
Choose model capability separately from effort. Dated evidence references distinguish official
guidance, firsthand practitioner observations, and local compatibility checks. Measure the cost
and time of an accepted result, including retries and corrections, when adjusting working defaults.

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
| `references/model-evidence.md` | Dated source evidence; read when changing routing or maintaining guidance. |
| `references/bounded-worker.md` | Finite calls, limits, persistence, and result handling. |
| `references/runner.md` | Optional helper usage, output contract, platform support, and cleanup limits. |
| `references/jobs.md` | Recoverable job profiles, status, cancellation, exact resume, and uncertainty handling. |
| `references/supervised-sessions.md` | Resume, steering, cleanup, parallel work, and subagents. |
| `assets/worker-contract.md` | Shared template for complex assignments. |
| `assets/result.schema.json` | Shared structured handoff schema; optional for plain consultations. |
| `scripts/run_worker.py` | Literal prompt transport, private artifacts, deadlines, and completion validation. |
| `scripts/jobs.py` | Atomic job journal, per-job supervision, leases, status, cancellation, and checked resume. |
| `scripts/launch_profiles.py` | First-party consultation/edit profiles, authentication checks, and session evidence. |

## Versioning and checks

Each skill is versioned independently in its `SKILL.md` `metadata.version`; both current skills
are prepared at **0.2.0**. The root [changelog](CHANGELOG.md) records changes by skill and version.
Release tags use `<skill-name>/v<version>`, for example `use-claude/v0.1.0`. Category directories
are organizational and have no version. See [release guidance](CONTRIBUTING.md#commits-and-releases).
The worker-result protocol has a separate identity, `urn:jvloo:agent-skills:worker-result:1`;
the JSON Schema `$schema` field identifies the schema language, not the handoff version.

Run the local fixture suite without provider credentials or model calls:

```sh
python3 -m unittest discover -s tests -v
```

See [evaluation guidance](evals/README.md) for fresh-context scenarios, comparison metrics, and
the distinction between fake-CLI lifecycle checks and live provider verification.

For work that must outlive its waiting client, the optional [job helper](skills/meta-agent/use-codex/references/jobs.md)
persists attempts and keeps a separate bounded supervisor. It can recover a completed result and
resume an available exact session after workspace inspection. Missing completion evidence blocks
automatic recovery; this does not promise exactly-once edits or full host-crash recovery.

## Project status

No tagged release has been published yet. The [changelog](CHANGELOG.md) records changes since
the initial import. The [recoverable-job evaluation](evals/2026-09-09-recoverable-jobs.md) records
29 passing fixture tests, fresh-context recovery checks, and live Claude/Codex client-loss recovery,
exact-session resume, and bounded edits. Live interruption during generation followed by resume,
additional platforms, and measured model-quality comparisons remain verification work.
A [token-effectiveness pilot](evals/2026-09-09-token-effectiveness.md) separately compares
baseline and skill-guided controllers over the same execution harness.
See [CONTRIBUTING.md](CONTRIBUTING.md) and the [roadmap](ROADMAP.md).

## Contributing

See the [roadmap](ROADMAP.md) for planned directions and [CONTRIBUTING.md](CONTRIBUTING.md) for the
contribution process. Changes are recorded in [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
