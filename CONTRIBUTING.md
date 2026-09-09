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

The two entrypoints should match after accounting for provider names and skill versions. Both skill directories must
have the same file layout; `assets/worker-contract.md`, `assets/result.schema.json`,
`references/runner.md` must be byte-identical. The `scripts/run_worker.py` copies must match
except for their package-specific `SKILL_VERSION` constants. Keep shared policies
consistent while allowing documented provider differences. The duplicated helper keeps each
installed skill self-contained; change both copies together and verify them with the suite.
Useful checks from the repository root are:

```sh
git diff --check
diff -u meta-agent/use-claude/assets/worker-contract.md meta-agent/use-codex/assets/worker-contract.md
diff -u meta-agent/use-claude/assets/result.schema.json meta-agent/use-codex/assets/result.schema.json
python3 -m unittest discover -s tests -v
```

A skill validator checks packaging, not runtime behavior. When a result schema changes, validate
it and exercise accepted and rejected handoffs. For behavioral changes, report the scenarios,
installed CLI versions, actual observations, and checks not run. Distinguish a plan-only evaluation
from a live worker run; do not claim cancellation or spending enforcement from help output alone.
Do not make paid model calls solely for a documentation or installation check.
The standard-library test suite uses synthetic provider events and owned local processes.
See [evals/README.md](evals/README.md) for fresh-context scenarios and comparison criteria.
Do not conflate passing these tests with live provider authentication, sandbox enforcement,
or measured improvement in model decisions. Record that evidence separately.

Keep repository copies authoritative. When installed copies are in scope, preserve local
customizations, copy the complete skill, and compare it with the reviewed repository version.
Repository-only documentation changes do not require reinstalling the skills.

## Commits and releases

Version each independently installable skill in its `SKILL.md` `metadata.version`, the release
source of truth. Keep that skill's helper `SKILL_VERSION` constant in sync; validation checks
the duplicated value. There is no root `VERSION` or category-level version. Both existing skills
start at `0.1.0`, but may advance independently. Provider-specific fixes bump only the affected
skill; shared behavior changes bump every affected skill. New unrelated skills start their own
version history without bumping existing skills. Patch versions correct behavior without changing the
interface; minor versions add compatible capabilities. Document breaking invocation, output,
permission, or compatibility changes explicitly; while below 1.0, use a new minor version for
breaking changes. Do not silently reinterpret an existing release or replace its tag.

The result protocol is versioned separately by the schema's `$id`. Adding output fields can
break consumers because `additionalProperties` is false. Update the protocol identity, fixed
helper validator, fixtures, and migration guidance together when changing that contract.
Package version metadata and protocol metadata belong in supervisor records, not worker-authored
result fields. Neither package versions nor tags freeze provider model aliases.

Before release, run the fixture suite and a compatible skills validator, inspect the final diff,
and record tested CLI/platform/date plus which checks were live. Publish an immutable repository
tag `<skill-name>/v<version>` (for example `use-codex/v0.1.1`) only after the release commit is ready.
Several skill tags may point to the same commit when released together. A prepared version in a working branch
is not a published release. Keep the changelog at repository level.

Use Conventional Commits, such as `feat(use-codex): add bounded session handoff` or
`fix(use-claude): fail closed when runtime approval is unavailable`.

Keep changes under `Unreleased` until a tagged release is published. At release time, add the
skill name, version, and date, and link to real tags. Move only that skill's released changes;
leave pending changes under `Unreleased`. Use skill-specific comparisons between its own tags.
Keep repository tooling changes in a separate repository-maintenance subsection. Split changelogs
per skill only when release volume or standalone distribution warrants it. If skills are later
distributed as a plugin, version that installable bundle explicitly.
Publishing a release is a separate action from editing the changelog.

## Reporting security issues

Do not publish exploit details or credentials in an issue. Contact the repository owner privately
through their GitHub profile and include only the minimum information needed to reproduce the risk.
