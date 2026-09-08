# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Give both meta-agent skills the same workflow, preflight criteria, worker contract, result schema, and workspace rules; retain provider-specific CLI behavior and curated model guidance.

- Align both skills on explicit choice, verified defaults, then justified model/effort adjustments; retain provider-specific checks.

- Align `use-codex` with verified pre-delegation checks, task-dependent subagents, compact contracts, supervised execution, and account-default-first model/effort guidance including Astra.

- Clarify `use-claude` authority reuse, compact contracts, host supervision, and on-demand model/effort selection, including Haiku and Fable.
- Select Claude subagents by task benefit after authentication and effective-permission checks, retaining single-worker execution for simple tasks.

### Fixed

- Correct Codex argument quoting, provider-specific authentication checks, and non-Git consultations; account for surviving Claude background work at cancellation and require isolated concurrent writers consistently.

- Preserve required controls across CLI versions, distinguish agent definitions from type restrictions, and require enforceable background limits.

### Added

- Roadmap for expanding Xavier's agentic workflow into a broader collection of reusable skills.

## [0.1.0] - 2026-09-03

### Added

- `use-claude`, a portable skill for bounded Claude Code CLI orchestration.
- `use-codex`, a portable skill for bounded Codex CLI/GPT orchestration.
- Approval preflight, worker-contract, supervision, and structured-result guidance.

[Unreleased]: https://github.com/jvloo/agent-skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jvloo/agent-skills/releases/tag/v0.1.0
