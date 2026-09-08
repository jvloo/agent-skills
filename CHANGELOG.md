# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). No tagged release
has been published yet; future releases will use [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
`Unreleased` records changes since the initial import.

## [Unreleased]

### Added

- Matching model-selection references and a shared structured-result schema for both skills.
- Roadmap for expanding the collection into additional reusable agent workflows.

### Changed

- Align both meta-agent skills on one workflow, preflight, worker contract, result schema, and
  workspace policy while retaining provider-specific CLI behavior and curated recommendations.
- Select model and effort by explicit choice, verified defaults, then justified adjustments;
  include Astra guidance for Codex and on-demand Haiku and Fable guidance for Claude.
- Reuse existing authority and unchanged preflight evidence, scale contracts to the task, and use
  internal subagents when independent work justifies coordination and cost.
- Refresh installation, usage, contribution, roadmap, and release-status documentation to match
  the shared skills.

### Fixed

- Correct Codex argument quoting, provider-specific authentication checks, and non-Git consultations.
- Account for Claude background work that can survive cancellation, and preserve required live
  steering when selecting a fallback.
- Require isolated workspaces for every concurrent writer, including Claude agent teams.
- Explain protected Git/configuration writes in Codex workspace-write and Claude restricted mode.
- Preserve required controls across CLI versions, distinguish agent definitions from type
  restrictions, and distinguish spending thresholds from enforced ceilings.
- Replace changelog links to the unpublished `v0.1.0` tag and release with the initial commit.

## [Initial import] - 2026-09-03

### Added

- `use-claude`, a portable skill for bounded Claude Code CLI orchestration.
- `use-codex`, a portable skill for bounded Codex CLI/GPT orchestration.
- Approval preflight, worker-contract, supervision, and structured-result guidance.

[Unreleased]: https://github.com/jvloo/agent-skills/compare/f577e9c5b1d2895cab98ba048aa57d6f5565bc16...main
[Initial import]: https://github.com/jvloo/agent-skills/commit/f577e9c5b1d2895cab98ba048aa57d6f5565bc16
