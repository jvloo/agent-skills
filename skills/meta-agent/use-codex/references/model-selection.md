# Model and effort selection

Read when choosing or changing a model/effort setting, resolving compatibility, or diagnosing
an escalation. An explicit compatible choice or suitable verified default needs no fresh routing
exercise. Consult the relevant section below; evidence sources are for evaluating recommendations.

## Shared selection policy

Selection order: explicit user choice, verified account/configuration defaults, then a justified
task adjustment. Keep a suitable default. Choose for uncertainty, verification cost, latency, and
budget; do not impose one model/effort on every task. Use session-local overrides instead of
changing global defaults.

Choose model capability and reasoning effort separately. Start with the supported default or a
lower effort justified by task evidence; raise effort for deeper planning, analysis, or checking.
A stronger model at lower effort can outperform a weaker model at higher effort. Judge the cost of
an accepted result, including worker usage, elapsed time, correction, review, and integration.

Resolve the provider, model, and supported effort from installed configuration, a non-generating
catalog, or version-compatible official metadata. A host agent's model list does not prove the
external CLI has the same access. If a default cannot be established, select a documented candidate
for that provider and state the assumption. Follow [authentication preflight](invocation-safety.md);
do not make a separate paid probe merely to discover models.

The recommendations below are curated task-routing opinions, not benchmark rankings or universal
provider defaults. They apply only when adjusting the selected profile is justified.
Read the dated [model evidence](model-evidence.md) only when changing a routing profile or
maintaining this guidance. Use outcomes from representative, authorized tasks to refine a profile;
do not add paid calibration probes or automatic model-selection loops.

## Provider recommendations

| Assignment | Advisory model | Effort guidance |
|---|---|---|
| Ordinary coding, repository scans, or focused review | `gpt-5.6-terra` | Supported default; `medium` is a balanced candidate, `high` for subtle logic or edge cases |
| Complex, ambiguous implementation or synthesis | `gpt-5.6-sol` | Supported default; consider `medium` or `high` for additional planning or checking |
| Hard sustained investigation or adversarial reasoning | `gpt-6-astra` | Supported default; consider `low` or `medium` when moving from Sol, then higher effort when justified |
| Narrow extraction or repeatable transformations | `gpt-5.6-luna` | `low` or `medium`, with cheap acceptance checks |
| Very short interactive iteration | `gpt-5.3-codex-spark` | On demand when available and its limitations fit the task |

Use these OpenAI model IDs only with a provider that supports them. An explicitly selected local
or custom provider needs its own catalog; do not switch providers to match the table.
Luna and Spark are on-demand choices, not automatic fallbacks for broad repository discovery.
Luna can handle a tightly scoped source lookup or a known flow with explicit evidence requirements;
use Terra for broader exploration. Choose child models by their assigned work, not automatically
by the parent's difficulty. A difficult review can warrant more effort than routine implementation.

## Compatibility and billing

Availability and effort support vary by account, sign-in route, model, and client. Confirm against
the CLI's own catalog or compatible official metadata. Apply `--model` and, when supported,
the `model_reasoning_effort` config override. Omit effort when the model does not support it.
Reject an unsupported required setting instead of silently dropping it.

Reserve `max` for measured gains on exceptionally hard work, if supported. `ultra` also enables
delegation: use it when useful independent work and verified child controls justify it. Confirm its
installed meaning and delegation permissions. Spark is text-only; verify account access. Do not assume a
one-to-one model or effort mapping to another provider. For custom/local providers, verify their
capabilities separately. Apply the budget rules in [bounded workers](bounded-worker.md).

## Escalation

Identify the failed check or unresolved question before another attempt. Repair missing inputs,
unclear acceptance criteria, unavailable tools, or access failures before increasing model capability
or effort. When reasoning is the gap, pass the evidence and bound the next attempt; change the model
or effort for a stated reason. Avoid automatic escalation loops and cheap-model retry ladders when
the initial task already requires deeper reasoning. Prefer deterministic tools for pure lookup.

Do not silently replace an explicitly requested unavailable model. Use an already authorized
alternative only when the task permits it, and report the actual fallback. A model or effort
change within existing authority does not itself require a new permission question.

Official sources: [model guidance](https://learn.chatgpt.com/docs/models) and
[configuration reference](https://developers.openai.com/codex/config-reference).
