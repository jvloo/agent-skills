# Claude worker contract

Copy and fill this template for the Claude invocation. Remove unused guidance and replace every
angle-bracketed field before launch.

## Objective

<One bounded outcome for this worker.>

## Definition of done

- <Observable acceptance criterion.>
- <Required artifact or answer.>

## Execution context

- Working directory: `<absolute-or-runtime-resolved-path>`
- Repository and revision: `<repository>; <branch/ref and commit>`
- Starting state: `<clean, or exact known user changes to preserve>`
- Applicable instructions: `<paths to repository instructions and active constraints>`
- Authoritative sources: `<source paths, URLs, or commands to verify>`

## Scope and ownership

- In scope: <files, modules, questions, or systems>
- Out of scope: <explicit exclusions>
- Worker owns: <investigation or artifact>
- Invoking agent owns: <decisions, integration, external communication, acceptance>

## Authority and capability

- User/task authorization: <approved outcome and explicit action boundaries>
- Parent-runtime approval: <native tool/sandbox approval status and identifier, or not required>
- Claude internal controls: <permission mode, tools, settings sources, and isolation>
- Allowed actions: <read, edit, and narrowly scoped commands>
- Forbidden actions: <commits, pushes, destructive or external mutations unless authorized>
- Allowed directories: <minimum required roots>
- Network and external systems: <none, read-only targets, or explicitly authorized mutations>
- Secrets: <sources that must not be opened, echoed, copied, or committed>

If a required approval is denied, unknown, or unavailable, do not invoke the model. Use the parent
runtime's native approval mechanism when available; plain-text confirmation does not replace a
runtime-enforced approval.

## Evidence and output

- Evidence required: <file:line findings, diffs, command results, or source links>
- Checks to run: <exact authoritative validations>
- Output shape: <schema or concise report structure>
- Uncertainty handling: <state assumptions, missing evidence, and skipped checks>

Unless the task needs another schema, return: status (`complete`, `blocked`, or `failed`), summary,
evidence, changed artifacts, checks with outcomes, uncertainties, and any required input. Empty
sections are explicit; do not omit them in a way that hides skipped work.

## Budget and supervision

- Model and effort: `<model>; <effort>`
- Model availability: <CLI selector/version, provider, compatibility, and Fable entitlement or billing evidence>
- Cost or token ceiling: <limit>
- Wall-clock timeout: <limit>
- Claude subagents: <disabled by default, or approved autonomous purposes, ownership, tools, and isolation>
- Child model and effort: <allowed values per child; `haiku` or `fable` requires an explicit user request>
- Child count and concurrency: <advisory target plus enforcement mechanism; exact limits require a verified control>
- Shared child constraints: <rules and evidence obligations every child must receive>
- Session persistence: <disabled, retained for resume, or background-managed>
- Retry limit: <count and retryable conditions>

## Stop conditions

Stop and report without expanding scope when:

- <required evidence, dependency, authentication, or capability is unavailable>;
- <the task needs an unapproved destructive, external, secret-bearing, or privileged action>;
- <the observed repository state or revision differs from this contract>;
- <continuing would materially expand the approved scope or capability envelope>;
- <budget, timeout, or retry limit is reached>;
- <independent findings materially conflict and primary evidence does not resolve them>.
