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
| Ordinary coding or focused review | `gpt-5.6-terra` | `medium`; consider `high` for subtle correctness or interacting changes |
| Complex, ambiguous implementation or synthesis | `gpt-5.6-sol` | `medium` or `high` according to uncertainty |
| Hard sustained investigation or adversarial reasoning | `gpt-6-astra` | `high`; consider `xhigh` when justified |
| Narrow extraction or repeatable transformations | `gpt-5.6-luna` | `low` or `medium`, with cheap acceptance checks |
| Very short interactive iteration | `gpt-5.3-codex-spark` | On demand when available and its limitations fit the task |

Use these OpenAI model IDs only with a provider that supports them. An explicitly selected local
or custom provider needs its own catalog; do not switch providers to match the table.
Luna and Spark are on-demand choices, not automatic fallbacks for broad repository discovery.

## Compatibility and billing

Availability and effort support vary by account, sign-in route, model, and client. Confirm against
the CLI's own catalog or compatible official metadata. Apply `--model` and, when supported,
the `model_reasoning_effort` config override. Omit effort when the model does not support it.
Reject an unsupported required setting instead of silently dropping it.

Reserve `max` for measured gains on exceptionally hard work, if supported. An `ultra` mode can
involve orchestration; verify its installed meaning and delegation permissions. Do not assume a
one-to-one model or effort mapping to another provider. For custom/local providers, verify their
capabilities separately. Apply the budget rules in [bounded workers](bounded-worker.md).

## Escalation

Identify the failed check or unresolved question, pass relevant evidence, and bound the next
attempt. Fix missing context or broken tools before paying for a larger model. Avoid a cheap-model
retry ladder when the initial task already requires deeper reasoning. Prefer deterministic tools
for pure lookup; account for correction and synthesis costs when judging a smaller model.

Do not silently replace an explicitly requested unavailable model. Use an already authorized
alternative only when the task permits it, and report the actual fallback. A model or effort
change within existing authority does not itself require a new permission question.

Official sources: [model guidance](https://learn.chatgpt.com/docs/models) and
[configuration reference](https://developers.openai.com/codex/config-reference).
