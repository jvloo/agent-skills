# Changelog

Notable changes are recorded here by skill and version. Skills release independently;
category directories have no version. Repository maintenance is tracked separately.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). No tagged release
has been published yet; future releases will use [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
`Unreleased` records changes since the initial import.

## [Unreleased]

### use-claude 0.1.0 / use-codex 0.1.0 (prepared, not released)

#### Added

- Prepared independent `0.1.0` skill metadata and a separately identified worker-result v1 protocol.
- Optional standard-library bounded runner for macOS/Linux, with private logs, literal prompt
  transport, deadline/cancellation cleanup, provider completion parsing, and handoff validation.
- Repeatable fake-CLI lifecycle tests, packaging checks, and fresh-context evaluation scenarios.
- Dated model-selection evidence separating official guidance, practitioner reports, and local checks.
- Matching model-selection references and a shared structured-result schema for both skills.
- Roadmap for expanding the collection into additional reusable agent workflows.

#### Changed

- Separate model capability from reasoning effort and optimize the cost/time of accepted results.
- Keep worker contracts focused on the task; retain launch provenance and controller evidence
  in supervisor records outside the worker prompt.
- Align both meta-agent skills on one workflow, preflight, worker contract, result schema, and
  workspace policy while retaining provider-specific CLI behavior and curated recommendations.
- Select model and effort by explicit choice, verified defaults, then justified adjustments;
  include Astra guidance for Codex and on-demand Haiku and Fable guidance for Claude.
- Reuse existing authority and unchanged preflight evidence, scale contracts to the task, and use
  internal subagents when independent work justifies coordination and cost.
- Refresh installation, usage, contribution, roadmap, and release-status documentation to match
  the shared skills.

#### Fixed

- Use a Draft 7 handoff schema accepted by Claude Code's structured-output validator.
- Clarify absolute Claude file-permission patterns, durable resume evidence, non-Git Codex resume,
  and temporary-directory requirements found during live bottom-up evaluation.
- Correct Claude's failed-fetch fallback to retain cached `origin/HEAD` when available.
- Correct Codex argument quoting, provider-specific authentication checks, and non-Git consultations.
- Account for Claude background work that can survive cancellation, and preserve required live
  steering when selecting a fallback.
- Require isolated workspaces for every concurrent writer, including Claude agent teams.
- Explain protected Git/configuration writes in Codex workspace-write and Claude restricted mode.
- Preserve required controls across CLI versions, distinguish agent definitions from type
  restrictions, and distinguish spending thresholds from enforced ceilings.
- Replace changelog links to the unpublished `v0.1.0` tag and release with the initial commit.

### Repository maintenance

- Adopt independent skill versions and `<skill-name>/v<version>` release tags.
- Remove the root version file; keep one changelog with skill-specific release entries.
- Validate each helper against its own skill version while allowing versions to diverge.

## [Initial import] - 2026-09-03

### Added

- `use-claude`, a portable skill for bounded Claude Code CLI orchestration.
- `use-codex`, a portable skill for bounded Codex CLI/GPT orchestration.
- Approval preflight, worker-contract, supervision, and structured-result guidance.

[Unreleased]: https://github.com/jvloo/agent-skills/compare/f577e9c5b1d2895cab98ba048aa57d6f5565bc16...main
[Initial import]: https://github.com/jvloo/agent-skills/commit/f577e9c5b1d2895cab98ba048aa57d6f5565bc16
