# Changelog

Notable changes are recorded here by skill and version. Skills release independently;
category directories have no version. Repository maintenance is tracked separately.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). No tagged release
has been published yet; future releases will use [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
`Unreleased` records changes since the initial import.

## [Unreleased]

### use-claude 0.2.1 / use-codex 0.2.1 (prepared, not released)

#### Changed

- Clarify discovery descriptions around requests for the named local CLI worker.
- Replace the linked reading sequence with a concise essential workflow and a decision-based
  reference map. Reuse verified host evidence; retrieve detail for missing or changed conditions.
- Make reference entry conditions explicit, and keep authentication, exact-session continuation,
  uncertain-edit handling, isolation, and independent acceptance in the core guidance.
- Evaluate progressive retrieval against the previous wording and forward-test the final descriptions.
  Runtime behavior, worker-result v1 and job-journal format 1 are unchanged.

### use-claude 0.2.0 / use-codex 0.2.0 (prepared, not released)

#### Added

- Optional recoverable jobs with atomic private journals, pre-dispatch snapshots, per-job
  supervisors, attempt-specific cancellation, workspace leases, and exact-session continuation.
- Tested first-party consult/edit launch profiles that preserve permissions and persistence.
- Recovery checks reject stale workspace state, missing sessions, concurrent resumes, exhausted
  attempts, and uncertain outcomes instead of automatically replaying edits.
- Offline client/supervisor interruption, concurrent-job, cancellation, and recovery fixtures.
- [Recovery evaluation](evals/2026-09-09-recoverable-jobs.md): 29 passing fixture tests, independent
  fresh-context checks, and live Claude/Codex client-loss recovery, exact-session resume, and edits.

#### Fixed

- Check the actual resume subcommand and required profile capabilities before dispatch.
- Explicitly disable supported Codex plugin/app and related capabilities in generated profiles;
  ignoring user configuration alone still allowed unrelated plugin startup.

The existing raw bounded runner remains available. Worker-result v1 is unchanged; the new
job journal has its own format version. The earlier 0.1.0 preparation below was never tagged.

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

- Add an opt-in paired token-effectiveness evaluation with controller/worker accounting,
  auxiliary model usage, independent acceptance checks, and a dated comparison report.
  This adds evaluation tooling without changing installed skill contents or versions.

- Move `meta-agent/` to `skills/meta-agent/`, keeping future skill categories separate from
  repository-level `evals/` and `tests/`. Update documentation and test paths; installed skill
  contents and versions are unchanged.

- Adopt independent skill versions and `<skill-name>/v<version>` release tags.
- Remove the root version file; keep one changelog with skill-specific release entries.
- Validate each helper against its own skill version while allowing versions to diverge.
- Align README and roadmap verification status with completed live recovery evidence and remaining gaps.

## [Initial import] - 2026-09-03

### Added

- `use-claude`, a portable skill for bounded Claude Code CLI orchestration.
- `use-codex`, a portable skill for bounded Codex CLI/GPT orchestration.
- Approval preflight, worker-contract, supervision, and structured-result guidance.

[Unreleased]: https://github.com/jvloo/agent-skills/compare/f577e9c5b1d2895cab98ba048aa57d6f5565bc16...main
[Initial import]: https://github.com/jvloo/agent-skills/commit/f577e9c5b1d2895cab98ba048aa57d6f5565bc16
