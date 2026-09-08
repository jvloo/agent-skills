# Model and effort selection

## Shared selection policy

Selection order: explicit user choice, verified account/configuration defaults, then a justified
task adjustment. Keep a suitable default. Choose for uncertainty, verification cost, latency, and
budget; do not impose one model/effort on every task. Use session-local overrides instead of
changing global defaults.

Resolve the provider, model, and supported effort from installed configuration, a non-generating
catalog, or version-compatible official metadata. A host agent's model list does not prove the
external CLI has the same access. If a default cannot be established, select a documented candidate
for that provider and state the assumption. Follow [authentication preflight](invocation-safety.md);
do not make a separate paid probe merely to discover models.

The recommendations below are curated task-routing opinions, not benchmark rankings or universal
provider defaults. They apply only when adjusting the selected profile is justified.

## Provider recommendations

| Assignment | Advisory model | Effort guidance |
|---|---|---|
| Ordinary implementation, tests, or focused review | `sonnet` | Supported default; consider `high` for subtle correctness or interacting changes |
| Bounded analysis with inexpensive validation | `sonnet` | Consider `medium` when lower cost justifies the tradeoff |
| Architecture, ambiguous failures, or adversarial review | `opus` | Supported default; consider `high` or `xhigh` for difficult reasoning |
| Narrow extraction or supplied-text transformations | `haiku` | Omit effort unless the resolved model supports it; require cheap acceptance checks |
| Hard sustained investigation or a large cohesive assignment | `fable` | Supported default; consider `high` or `xhigh` when difficulty and budget warrant it |

Haiku and Fable are on-demand choices, not automatic fallbacks. Avoid Haiku for broad repository
discovery or subtle correctness judgments. Length alone does not justify Fable. A reviewed Opus
plan may be handed to Sonnet for bounded implementation when that division actually helps.

## Compatibility and billing

Aliases resolve differently by provider/configuration; CLI acceptance of a name does not prove
account entitlement. Record the resolved model and effective effort when exposed. Current Haiku
is not listed as supporting effort, so omit `--effort`. Fable and newer Opus/Sonnet support
`xhigh`; older variants may not, and unsupported levels can be downgraded. Reject a downgrade
when the requested level is required.

Reserve `max` for measured gains on exceptionally hard work. `ultracode` also enables workflow
orchestration; verify its meaning and delegation permissions. Do not assume a one-to-one model or
effort mapping to another provider.

Fable access and billing vary; print mode can charge usage credits without prompting. Confirm the
billing route fits existing authority, including when Fable is the configured default. Where no
non-generating access check exists and billing is already authorized, the first bounded task call
may establish access. Do not add a paid test prompt or retry access/billing errors indefinitely.
Avoid `best` when a predictable model or billing boundary matters. Apply the budget rules in
[bounded workers](bounded-worker.md).

## Escalation

Identify the failed check or unresolved question, pass relevant evidence, and bound the next
attempt. Fix missing context or broken tools before paying for a larger model. Avoid a cheap-model
retry ladder when the initial task already requires deeper reasoning. Prefer deterministic tools
for pure lookup; account for correction and synthesis costs when judging a smaller model.

Do not silently replace an explicitly requested unavailable model. Use an already authorized
alternative only when the task permits it, and report the actual fallback. A model or effort
change within existing authority does not itself require a new permission question.

Official source: [model configuration](https://code.claude.com/docs/en/model-config).
