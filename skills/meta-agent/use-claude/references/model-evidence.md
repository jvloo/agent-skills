# Model routing evidence

Snapshot: **2026-09-09**. Read when changing a routing profile or maintaining
[model selection](model-selection.md). Recheck changing model, effort, access, and billing facts
against the installed CLI and current provider documentation. Practitioner experience can suggest
an experiment on an authorized task; it does not establish a universal ranking.

## Official guidance

Sources below were accessed on the snapshot date; publication dates are included where available.

- [Model configuration](https://code.claude.com/docs/en/model-config): aliases depend on provider
  and configuration. The direct Anthropic API defaults resolve `sonnet` to Sonnet 5 and `opus` to
  Opus 5; the unmodified `fable` alias resolves to Fable 5.1. Start from a supported effort default.
  Haiku is not listed as supporting effort. Higher levels and orchestration modes need separate
  compatibility checks. Fable can bill usage credits without prompting in print mode.
- [Lydia Hallie, Choosing a Claude model and effort level](https://claude.com/blog/claude-model-and-effort-level-in-claude-code),
  2026-07-07: model capability and effort are different controls. Effort also affects investigation,
  tool use, verification, and persistence. Repair context first; skipped available checks suggest
  more effort, while failure after adequate investigation suggests a more capable model. Preserve
  a useful default as a preference for similar work instead of retuning every prompt.
- [Claude Academy, Choosing the right effort level](https://academy.claude.com/tutorials/choosing-the-right-effort-level-in-claude-code):
  both under-investigation and overthinking can waste resources. Use normal task outcomes to judge
  the balance, and revisit a high effort setting when changing to a more capable model. This skill
  does not turn that advice into automatic retries or paid calibration calls.

## Firsthand practitioner evidence

| Source and publication date | Observation | What to carry forward |
|---|---|---|
| [Armin Ronacher, Better Models: Worse Tools](https://lucumr.pocoo.org/2026/7/4/better-models-worse-tools/), 2026-07-04 | Reported malformed Pi edit-tool calls with Opus 4.8 and Sonnet 5, and investigated the interaction with the tool schema. | Inspect the actual failure and tool contract before increasing model capability or effort. This is a harness-specific report, not a general ranking of those models or evidence of the same failure in Claude Code. |
| [Simon Willison, interview with Cat and Thariq](https://simonwillison.net/2026/Jul/21/cat-and-thariq/), 2026-07-21 | The Claude Code team described model-specific prompt changes and said it lacked measured evidence that a stronger parent could compensate for Haiku through a better child prompt. | Validate a child's assigned work independently and avoid assuming clever delegation replaces capability. This is a firsthand team interview, not an independent comparative benchmark. |

## Local compatibility evidence and limits

The review inspected `Claude Code 2.1.263` version and help without generation. Help exposed
`--model` and `--effort` with `low`, `medium`, `high`, `xhigh`, and `max`. Accepted CLI syntax did
not establish effort support for every model, alias resolution under a particular provider, or
account entitlement. The alias mappings above come from official documentation, not a live model
response. Preserve preflight and check the effective model and effort when the runtime exposes them.

No paid worker call or task-quality benchmark was performed for this snapshot. The routing table is
a starting profile to refine from accepted results, not a measured winner for a particular repository.
