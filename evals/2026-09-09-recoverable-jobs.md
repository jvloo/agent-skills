# Recoverable jobs evaluation — 2026-09-09

Candidate: independently prepared `use-claude` and `use-codex` 0.2.0, based on merged
revision `4a1cdaf`. Worker-result v1 is unchanged; the new private job journal is format 1.
Environment: macOS 26.6.2 arm64, Python 3.9.6, Claude Code 2.1.263, Codex CLI 0.153.4.

## Outcome

The candidate persists jobs before dispatch, survives loss of the waiting client, and can recover
a known terminal result and continue the exact locally available session with a fresh prompt.
It refuses uncertain outcomes instead of replaying edits. It is not full host-crash recovery or
an exactly-once external-action system.

## Deterministic checks

All **29 test methods passed**. The 12 added job tests use explicit local CLI doubles, no account
credentials, network calls, or models. They cover:

- Private journals, preserved earlier attempts, duplicate-name rejection and attempt limits.
- Generated edit profiles and exact-session resume for both providers.
- Waiting-client SIGKILL followed by fresh-process status and successful completion.
- Per-job supervisor SIGKILL while the bounded runner retains its leases and enforced timeout.
- Bounded-runner SIGKILL producing an uncertain outcome that cannot be resumed or replayed.
- Changed workspace, missing session, and changed saved configuration preventing dispatch.
- Competing resumes admitting exactly one new attempt.
- Attempt-specific cancellation, partial-log retention, safe continuation after confirmed cleanup,
  rejection of stale cancellation, and an unrelated concurrent reader completing normally.
- Same-workspace writer exclusion, actual resume-subcommand compatibility checks, and capability
  switches in the generated Codex arguments.

The existing 17 methods continue to cover strict result parsing, provider lifecycle completion,
structured handoffs, literal stdin, deadlines, cancellation, child cleanup and package portability.
Both skill-creator validators and the shared-resource/local-link checks passed. Entry points remain
62 lines; execution detail is conditional in the job reference and scripts.

## Fresh-context forward test

An independent controller received the two skills, the realistic client-loss/recovery task, and
only the raw offline CLI fixture setup. It did not read the job test suite or earlier reports.
For both providers it started a job, killed the waiting client, recovered active then completed
status from fresh processes, resumed with a new prompt, recovered the original session marker,
and preserved user notes byte-for-byte. Racing two resumes with one state token admitted exactly
one dispatch per provider. It corrected its own unsupported `resume --wait` invocation by following
resume with status; no production workflow correction was supplied for this task.

Its source review identified that the first implementation checked Codex exec help during resume
instead of the resume subcommand's help, omitted some emitted flags from checks, and required an
unused flag. These were corrected and regression-tested. A focused independent follow-up verified
the actual-subcommand and capability checks and repeated offline Codex client-loss/exact-resume
success. No remaining actionable issue was reported in that focused review.

Offline doubles do not establish authentication, sandbox enforcement, or real provider persistence.

## Live provider checks

Existing first-party Claude team login and Codex ChatGPT login were checked before dispatch.
Native supervisor execution access supplied normal account/session-store access. Calls used
90-second deadlines, explicit models, no recursive delegation, and disposable synthetic inputs.
Claude used Sonnet/medium with a $1 stopping threshold per call; Codex used Astra/low. Those are
requested settings; Codex JSONL did not independently echo the effective model.

| Scenario | Claude | Codex |
|---|---|---|
| Kill waiting client, recover completed structured handoff | Pass | Pass |
| Fresh prompt resumes exact persisted session and original marker | Pass | Pass |
| Generated edit profile changes only assigned source | Pass | Pass after contract/profile correction |
| Four independent edit acceptance tests; notes/tests unchanged | Pass | Pass after correction |

The first Codex edit contract incorrectly prohibited every command, including local file reads;
the worker correctly reported a blocked task without editing. Its startup logs also exposed
unrelated plugin MCP authentication attempts despite `--ignore-user-config`. The profile now
explicitly disables supported plugin/app/hook/browser and related capabilities, and checks those
switches before dispatch. A corrected bounded edit, plus another client-loss and exact-resume
pair using the final profile, all passed with empty stderr. The failed first edit remains evidence,
not a successful implementation. Managed policy and externally supplied tools still require the
supervisor's normal preflight; absence of stderr is not a universal network-containment proof.

Nine live top-level calls were made: three Claude, six Codex, including the blocked Codex task and
the final-profile retests. Claude reported an estimated $0.0792188 total. Codex did not expose a
dollar cost. Host-controller usage is not included. No model-quality or skill-versus-no-skill
comparison was performed.

## Evidence and limits

Private raw artifacts are retained in temporary directories named `recoverable-live-f47op77w`,
`recoverable-final-2tu5r0cj`, and `recoverable-forward-jvloo-0909`. They contain the actual drivers,
commands, private job journals, prompts, session IDs, CLI logs, snapshots, acceptance outputs and
independent forward-test reports. No raw transcripts or credential material are committed here.

The suite tests process interruption, not power failure, filesystem corruption or a physical reboot.
Unknown terminal evidence intentionally blocks resume. Cancelling after the per-job supervisor
itself dies still relies on the surviving bounded runner's deadline; no unsafe saved-PID signalling
is used. Provider interruption mid-generation followed by resume is covered offline, not live.
Linux, remote/detached provider jobs, provider-internal agents, custom/API-key routes, hostile
same-user processes and cross-store/nested-workspace locking remain outside the verified boundary.
