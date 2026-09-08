# Contributing

Contributions that make these skills safer, more portable, or more effective are welcome.

## Principles

- Keep each skill self-contained and independent of a particular parent-agent runtime.
- Preserve explicit authorization boundaries and least-privilege defaults.
- Confirm CLI behavior against installed help and current first-party documentation.
- Prefer concise decision guidance over copied manuals or machine-specific command recipes.
- Never include credentials, local absolute paths, private repository details, or transcript data.
- Keep the two meta-agent skills aligned: the same entrypoint workflow, reference structure,
  shared rules, worker contract, and result schema. Differences belong in provider-specific
  commands, capabilities, authentication, lifecycle handling, and curated model recommendations.
  Keep each copied skill self-contained.

## Making a change

1. Create a focused branch from `main`.
2. Edit the smallest relevant skill and its supporting artifacts.
3. Verify all relative links and examples.
4. Run a compatible Agent Skills validator against every changed skill.
5. Add a concise entry under `Unreleased` in `CHANGELOG.md`.
6. Open a pull request describing the behavior change and verification performed.

For substantive safety or orchestration changes, include a realistic forward test using a fresh
agent context. Tests must not publish, mutate external systems, or expose secrets without explicit
authorization.

Use Conventional Commits, such as `feat(use-codex): add bounded session handoff` or
`fix(use-claude): fail closed when runtime approval is unavailable`.

## Reporting security issues

Do not publish exploit details or credentials in an issue. Contact the repository owner privately
through their GitHub profile and include only the minimum information needed to reproduce the risk.
