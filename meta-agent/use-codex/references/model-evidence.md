# Model routing evidence

Snapshot: **2026-09-09**. Read when changing a routing profile or maintaining
[model selection](model-selection.md). Recheck changing model, effort, access, and billing facts
against the installed CLI and current provider documentation. Practitioner experience can suggest
an experiment on an authorized task; it does not establish a universal ranking.

## Official guidance

Sources below were accessed on the snapshot date; they do not all display publication dates.

- [Models](https://learn.chatgpt.com/docs/models): Astra serves the hardest sustained workflows,
  Sol complex work, Terra everyday work, and Luna clear repeatable work. Use the lowest adequate
  effort. Max adds reasoning depth; Ultra also uses subagents. Spark is a text-only research preview
  with account-dependent access.
- [Managing Astra usage](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex):
  model and effort are separate choices. Astra Low can outperform Sol High; try Astra Low or Medium
  when moving from a successful Sol High workflow. Higher effort cannot supply missing information
  or tool access. Actual usage depends on the task and settings.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): choose by role.
  Terra suits broader read-heavy exploration, while Luna suits narrow repeatable assignments.
  Examples include focused documentation checks and mapping a known failing flow. Higher effort
  can help reviewers trace complex logic and edge cases. Each child adds usage and coordination.

## Firsthand practitioner evidence

| Source and publication date | Observation | What to carry forward |
|---|---|---|
| [Simon Willison, Astra comparison](https://simonwillison.net/2026/Sep/4/astra-pelicans/), 2026-09-04 | Compared generated SVGs across models and efforts; preferred Astra Low over all Sol results for his prompt. Lower token use narrowed the price difference. | Consider a stronger model at lower effort and compare actual outputs and usage. This single creative prompt is not a coding benchmark. |
| [Peter Steinberger, Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed), 2025-12-28 | Kept a stable high-effort setting, found little benefit from xhigh, and sometimes finished sooner overall with a slower initial run that needed fewer corrections. | Measure time to accepted work and preserve a useful default. His older model choices and configuration are historical, not current launch instructions. |
| [Addy Osmani, Loop Engineering](https://addyosmani.com/blog/loop-engineering/), 2026-06-07 | Describes his own implementation/review split and spending extra agent usage where another opinion helps. | Route by role and verification value. The report is practitioner experience, not a controlled model comparison or a reason for mandatory reviewer chains. |

## Local compatibility evidence and limits

The review inspected `codex-cli 0.153.4` help and `codex debug models --bundled` without generation.
Its bundled catalog included `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`.
Their default efforts were respectively `low`, `low`, `medium`, and `medium`; the first three
listed levels through `ultra`, while Luna listed levels through `max`. Spark was absent from this
bundled catalog, so documentation alone did not establish local account access.

Bundled metadata shows client compatibility, not current account entitlement. Some documentation
examples use aliases or illustrative defaults; resolve the actual model and effort for each launch.
No paid worker call or task-quality benchmark was performed for this snapshot. The routing table is
a starting profile to refine from accepted results, not a measured winner for a particular repository.
