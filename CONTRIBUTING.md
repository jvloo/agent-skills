# Contributing

Contributions that make these skills safer, more portable, or more effective are welcome.

## Principles

- Keep each skill self-contained and independent of a particular parent-agent runtime.
- Carry existing user choices and approvals forward; preserve authorization boundaries and
  least-privilege defaults without adding redundant confirmations.
- Confirm CLI behavior against installed help and current first-party documentation.
- Prefer concise decision guidance over copied manuals or machine-specific command recipes.
- Never include credentials, local absolute paths, private repository details, or transcript data.
- Keep the two meta-agent skills aligned: the same entrypoint workflow, reference structure,
  shared rules, worker contract, and result schema. Differences belong in provider-specific
  commands, capabilities, authentication, lifecycle handling, and curated model recommendations.
  Keep each copied skill self-contained.

## Making a change

1. Create a focused branch from `main`.
2. Edit the relevant skill and supporting artifacts. Apply shared behavior changes to both
   meta-agent skills; keep provider-specific changes in the appropriate references.
3. Verify relative links, examples, and the shared-file checks below; run `git diff --check`.
4. Run a compatible Agent Skills validator against every changed skill. For repository-docs-only
   edits, check the changed documentation against the current skills and repository state.
5. Add a concise entry under `Unreleased` in `CHANGELOG.md`; update `README.md` and `ROADMAP.md`
   when installation, capabilities, or project status changes.
6. Open a pull request describing the behavior change and verification performed.

For substantive safety or orchestration changes, include a realistic forward test using a fresh
agent context. Tests must not publish, mutate external systems, or expose secrets without explicit
authorization.

## Validation and synchronization

The two entrypoints should match after accounting for provider names. Both skill directories must
have the same file layout; `assets/worker-contract.md` and `assets/result.schema.json` must be
byte-identical. Keep shared policies consistent while allowing documented provider differences.
Useful checks from the repository root are:

```sh
git diff --check
diff -u meta-agent/use-claude/assets/worker-contract.md meta-agent/use-codex/assets/worker-contract.md
diff -u meta-agent/use-claude/assets/result.schema.json meta-agent/use-codex/assets/result.schema.json
```

A skill validator checks packaging, not runtime behavior. When a result schema changes, validate
it and exercise accepted and rejected handoffs. For behavioral changes, report the scenarios,
installed CLI versions, actual observations, and checks not run. Distinguish a plan-only evaluation
from a live worker run; do not claim cancellation or spending enforcement from help output alone.
Do not make paid model calls solely for a documentation or installation check.

Keep repository copies authoritative. When installed copies are in scope, preserve local
customizations, copy the complete skill, and compare it with the reviewed repository version.
Repository-only documentation changes do not require reinstalling the skills.

## Commits and releases

Use Conventional Commits, such as `feat(use-codex): add bounded session handoff` or
`fix(use-claude): fail closed when runtime approval is unavailable`.

Keep changes under `Unreleased` until a tagged release is published. At release time, add the
version and date, update the comparison links to real tags, and leave a new `Unreleased` section.
Publishing a release is a separate action from editing the changelog.

## Reporting security issues

Do not publish exploit details or credentials in an issue. Contact the repository owner privately
through their GitHub profile and include only the minimum information needed to reproduce the risk.
