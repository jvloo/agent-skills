# Model and effort selection

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
| Ordinary implementation, tests, or focused review | `sonnet` | Supported default; higher supported effort for demonstrated gaps in diligence |
| Bounded analysis with inexpensive validation | `sonnet` | Consider `medium` when lower cost justifies the tradeoff |
| Architecture, ambiguous failures, or adversarial review | `opus` | Supported default; consider `xhigh` when more investigation or checking is justified |
| Narrow extraction or supplied-text transformations | `haiku` | Omit effort unless the resolved model supports it; require cheap acceptance checks |
| Hard sustained investigation or a large cohesive assignment | `fable` | Supported default; higher supported effort when difficulty and budget warrant it |

Haiku and Fable are on-demand choices, not automatic fallbacks. Avoid Haiku for broad repository
discovery or subtle correctness judgments. Length alone does not justify Fable. A reviewed Opus
plan may be handed to Sonnet for bounded implementation when that division actually helps.

Claude effort affects investigation, tool use, verification, and persistence as well as thinking.
Keep a useful effort default across similar tasks. After repairing inputs and tools, skipped
available files or checks and premature stopping can suggest more effort. A substantive failure
despite adequate context and investigation can suggest a more capable model. These are diagnostic
signals, not automatic retries. Give smaller children explicit inputs and acceptance checks; a
strong parent's prompt does not guarantee that a smaller child can perform a difficult task.

## Compatibility and billing

Aliases resolve differently by provider/configuration; CLI acceptance of a name does not prove
account entitlement. Record the resolved model and effective effort when exposed. Current Haiku
is not listed as supporting effort, so omit `--effort`. Fable and newer Opus/Sonnet support
`xhigh`; older variants may not, and unsupported levels can be downgraded. Reject a downgrade
when the requested level is required.

Reserve `max` for measured gains on exceptionally hard work. `ultracode` also enables workflow
orchestration; verify its meaning and delegation permissions. Do not assume a one-to-one model or
effort mapping to another provider, or equal underlying effort from the same label across models.

Fable access and billing vary; print mode can charge usage credits without prompting. Confirm the
billing route fits existing authority, including when Fable is the configured default. Where no
non-generating access check exists and billing is already authorized, the first bounded task call
may establish access. Do not add a paid test prompt or retry access/billing errors indefinitely.
Avoid `best` when a predictable model or billing boundary matters. Apply the budget rules in
[bounded workers](bounded-worker.md).

## Escalation

Identify the failed check or unresolved question before another attempt. Repair missing inputs,
unclear acceptance criteria, unavailable tools, or access failures before increasing model capability
or effort. When reasoning is the gap, pass the evidence and bound the next attempt; change the model
or effort for a stated reason. Avoid automatic escalation loops and cheap-model retry ladders when
the initial task already requires deeper reasoning. Prefer deterministic tools for pure lookup.

Do not silently replace an explicitly requested unavailable model. Use an already authorized
alternative only when the task permits it, and report the actual fallback. A model or effort
change within existing authority does not itself require a new permission question.

Official source: [model configuration](https://code.claude.com/docs/en/model-config).
