# Run scorecard — <task name>

Trace: `<file>` · Spec: `<file>` · Date: `<date>` · Scorer: `<name>`

| Dimension | Score (0–100 or n/a) | Evidence (step numbers, exact findings) |
|---|---|---|
| outcome | | Did the run deliver what the spec's final checks require? |
| tool_selection | | Expected tools used; undeclared tools touched (list them) |
| argument_validity | | Calls whose arguments violate the spec's schemas (list them) |
| step_economy | | Repeated-after-success calls, loop patterns, calls after the final event |
| error_recovery | | Failures recovered vs stepped over — or UNTESTED if no failure occurred |
| policy | | Forbidden tools/patterns, ordering, call limits — any breach is a hard fail |
| cost_latency | | Steps / tokens / latency vs the spec's budgets |
| groundedness | | Checkable claims in the final answer with no source in the run's evidence |

**Composite:** <mean of scored dimensions; n/a dimensions excluded, never zeroed>

**Policy gate:** PASS / FAIL (a policy breach fails the run regardless of composite)

**Judge use (if any):** judge `<name>`, calibration agreement <x>, kappa <y>,
on <n> labelled items (from the calibrate-llm-judge skill). Judge verdicts are
reported beside the deterministic scores, never blended into them.

**One-line verdict:** <what this run did well or badly, in one sentence>
