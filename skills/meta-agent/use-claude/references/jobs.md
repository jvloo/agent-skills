# Recoverable bounded jobs

Use `scripts/jobs.py` when the calling client may disconnect or the task needs a later continuation.
For a single attached call or custom launch configuration, keep using [run_worker.py](runner.md).
The jobs helper requires Python 3.9+, macOS/Linux, and a local filesystem with working POSIX locks.

## Choose and inspect a profile

`consult` provides read-only work. `edit` takes explicit `--write-file` assignments: Claude gets
exact-file Edit permissions with no shell; Codex gets a workspace-write sandbox, so its file
assignments are behavioral scope and must also be in the worker contract. Codex may need shell
commands for local file inspection; permit those in its contract when needed. Run acceptance tests
in the supervisor when the worker has no command tool. Internal agents and network tools are
disabled through explicit CLI controls; managed policy and externally supplied tools still require
the normal preflight. Codex retains normal temporary-directory support. These profiles preserve provider
session state for exact resume and disable discovered customization where supported.

Profiles currently support normal Claude first-party account login and Codex ChatGPT login.
They require an explicit verified model; effort is optional. They check CLI help, version and
route-specific login before every dispatch, without a generating probe. Model entitlement and
effective effort still need the [normal preflight](invocation-safety.md). Custom providers, API-key
routes, hooks, or different tools use the raw runner with supervisor-verified arguments.

Use `plan` with the provider/profile arguments to inspect the generated argument array without
authentication or generation. It does not prove the installed CLI supports those arguments.

## Start and inspect

Use the host's argument-array API; these are argument contents, not shell interpolation:

```text
python /absolute/skill/scripts/jobs.py start
  --store /private/job-store --name calculation-review
  --provider claude --cli /absolute/claude --cwd /verified/workspace
  --profile consult --model sonnet --effort medium --budget-usd 1
  --timeout 120 --max-attempts 3 --structured --prompt-file /private/contract.txt
```

For Codex, use `--provider codex`, its executable and verified model; omit `--budget-usd`.
For edits add `--profile edit --write-file relative/source.py` (repeat for each assignment).
The store must be an owner-only directory outside the workspace. Keep it outside worker-writable
roots, including temporary roots, when protecting controller state from worker mutations matters.
These are trusted same-user job records, not an independent security boundary.

The helper persists configuration, fresh prompt bytes, argument array, preflight outcome and a
workspace fingerprint before dispatch. It returns the job path. Optional `--wait` waits in the
client and returns the runner's runtime exit code; losing that client does not cancel the job.
A separate per-job supervisor keeps the bounded CLI attached and owns cancellation. There is no
global background service or automatic retry loop. Keep both helper processes in the host's
authorized execution context; a platform that kills the whole process tree can still interrupt it.

```text
python /absolute/skill/scripts/jobs.py status /private/job-store/calculation-review
python /absolute/skill/scripts/jobs.py cancel /private/job-store/calculation-review --attempt 1
```

Status exposes runtime/task outcomes separately, session availability, artifacts, file changes,
and an `expected_state` token when idle. Inspect the actual diff and result, especially changes
outside the assignment; passing CLI status is not task acceptance. A cancellation is an
attempt-specific request, not confirmation that work stopped. Read status until completion and
inspect cleanup. Cancellation never signals a saved PID; PID reuse cannot target an unrelated job.

Snapshots cover the workspace except `.git`, with Git revision evidence recorded separately.
For large workspaces use repeated `--watch` paths for relevant inputs, instructions and outputs.
Unwatched paths are outside change detection. Limits are 20,000 entries and 128 MiB of file content.
Jobs in the same store serialize writers for the same canonical cwd; consult readers may coexist.
Different stores or nested/overlapping workspaces do not share that protection. Continue to isolate
parallel writers using worktrees as described in [supervised sessions](supervised-sessions.md).

## Resume deliberately

Inspect status, previous results, current workspace changes and remaining scope. Then supply the
returned token and a **fresh follow-up prompt**, never an automatically replayed original edit:

```text
python /absolute/skill/scripts/jobs.py resume /private/job-store/calculation-review
  --expected-state TOKEN_FROM_STATUS --prompt-file /private/follow-up.txt
```

The token is an optimistic concurrency check, not a new user-approval requirement. Resume refuses
changed state/workspace, busy jobs, changed saved configuration, unavailable session records,
unconfirmed cleanup, and exhausted attempt limits. It rechecks authentication, requires persisted
evidence for the exact captured session in the same session store, reapplies the same profile,
and appends a new attempt with a new deadline. Local persistence is necessary evidence, not a
guarantee that the remote service will accept a resume; provider errors remain recorded failures.

## Interrupted and uncertain outcomes

The supervisor and bounded runner share job/workspace leases. If the client dies, the supervisor
continues. If only the supervisor dies, the bounded runner retains the leases and deadline; after
it finishes, a fresh status command can recover the result from its manifest. State records are
atomically replaced and synced to disk. Status never launches work.

If the bounded runner is forcibly killed, the machine loses power, or no trustworthy terminal
manifest exists, status reports `interrupted` and resume refuses. Worker effects may already exist.
Inspect artifacts and live provider/process state through an authorized supervisor before creating
a new job or using a verified raw resume. Never infer cancellation from a missing lock, and never
replay an uncertain write just because a result file is absent. This milestone recovers known
bounded outcomes; it does not promise exactly-once external effects or full host-crash recovery.

Keep job records and provider session files for as long as continuation is useful. Prompts and raw
logs may contain sensitive task data; no credentials belong in them. Cleanup is an explicit
supervisor action after accounting for results, edits and all owned work.
