---
name: score-agent-run
description: Score how an AI agent executed a recorded run — not just whether the task succeeded — across eight dimensions (outcome, tool selection, argument validity, step economy, error recovery, policy, cost/latency, groundedness). Use when reviewing an agent trace/log after a run, gating a change on run quality, or investigating a run that "succeeded" but behaved badly (loops, undeclared tools, blown budgets, ungrounded claims).
---

# Score an agent run against its task spec

A run can succeed and still be bad: the same search issued four
times, tools the spec never granted, a malformed call, a blown token
budget, a policy quietly crossed — under a final answer that passes
every outcome check. Outcome-only evaluation calls that run a
success. This skill scores the *execution*, dimension by dimension,
against the task spec the run was supposed to follow.

## Inputs you need

- A **trace**: the recorded run — one event per line (JSONL) with
  types `run`, `call`, `result`, `note`, `final`. Calls carry the
  tool and its arguments; results carry status, and ideally tokens
  and latency; the final event carries the answer.
- A **spec**: what the run was supposed to do — allowed/expected
  tools, per-tool argument schemas, policy rules, budgets, and
  final-state checks. `assets/task_spec_template.json` is a filled
  template.

## Step 0 — pre-flight before scoring

Run `python3 scripts/spec_trace_check.py spec.json trace.jsonl`. It
classifies each dimension SCORABLE / n/a / UNTESTED from what the
spec and trace actually contain. Scoring is only as good as the
spec: a dimension without inputs is reported **n/a and excluded from
the composite — never silently zeroed, never gifted**. Error
recovery is special: if no failure occurred in the trace, it is
**UNTESTED**, a fact about the trace, not a virtue of the agent.

## The eight dimensions

Score each 0–100 with step-level evidence, or mark it n/a/UNTESTED.

1. **outcome** — Did the run deliver what the spec's final checks
   require (final state, required answer content)?
2. **tool_selection** — Were the expected tools used, and were any
   *undeclared* tools touched? An undeclared tool is a finding even
   if it helped.
3. **argument_validity** — Does every call's arguments satisfy the
   spec's JSON Schema for that tool (required properties, types)?
4. **step_economy** — Repeated calls with identical arguments *after
   already succeeding* are waste; loop patterns; calls after the
   final event. Two distinctions are mandatory: a repeat after an
   **error** is a retry, not waste; a repeat with **different
   arguments** is new work, not a loop.
5. **error_recovery** — Of the failures that occurred, how many were
   recovered (a later step fixed the problem) vs silently stepped
   over (the run continued as if nothing happened)?
6. **policy** — Forbidden tools, forbidden argument patterns,
   required ordering (e.g. approval before action), call limits,
   forbidden end-states. Policy is a **hard gate**: any breach fails
   the run regardless of the composite.
7. **cost_latency** — Steps, tokens, and recorded latency against
   the spec's budgets. (Latency here is the sum of per-event recorded
   latencies, not wall-clock.)
8. **groundedness** — Every *checkable* claim in the final answer —
   numbers, URLs, emails, quoted strings — must appear in evidence
   the agent actually had (tool outputs, or the task prompt itself;
   a number the user supplied is grounded, not invented). A fluent
   falsehood with no checkable token is invisible to this layer;
   that is what a measured judge layer is for.

**Composite** = mean of the scored dimensions. Report with
`assets/scorecard_template.md`.

## Judges: optional, and only as far as measured

A judge may assist groundedness or outcome assessment, but its
verdicts are reported *beside* the deterministic scores, never
blended in — and only with its calibration printed next to them
(agreement and kappa on a labelled set; see the calibrate-llm-judge
skill). An unmeasured judge's score is a hope.

## Test your scorer before trusting it

If you automate this scoring, validate the scorer itself by fault
injection: take clean traces that score perfectly, plant one known
defect per copy (a wrong tool, an invalid argument, an ungrounded
claim, a silent policy breach, loop waste, a masked failure), and
check the responsible dimension catches it. Add negative controls —
legitimate traces that *resemble* defects (a retry after an error, a
repeat with new arguments) and must not be flagged. The runreckon
self-test, on three small author-built bases, catches 18/18 planted
defects with 3/3 controls passing; treat such rates as a regression
floor, not a field measurement.

## Worked miniature example

`assets/trace_example.jsonl` is a six-call run against
`assets/task_spec_template.json`. Pre-flight: all eight dimensions
SCORABLE; observed 6 calls, 1 error, 4,100 tokens, one undeclared
tool (`summarize_page`). Hand-scoring the dimensions:

- **outcome** — pass: the brief was written and the answer covers
  the required content.
- **tool_selection** — finding: step 5 used `summarize_page`, which
  the spec never granted.
- **argument_validity** — finding: step 3 called `fetch_page` with
  no `url`, violating the schema's required property.
- **step_economy** — finding: step 2 repeats step 1's search with
  identical arguments after it already succeeded — one wasted step.
  (Had step 1 *errored*, the repeat would be a retry, not waste.)
- **error_recovery** — recovered: step 3's error is fixed by step
  4's correct call.
- **policy** — pass: the forbidden tool (`send_email`) was never
  touched; no ordering or limit rules were crossed.
- **cost_latency** — pass: 6 calls ≤ 8 max steps; 4,100 tokens ≤
  6,000 budget.
- **groundedness** — finding: "17.1 hours" and "41.2" both appear in
  tool outputs; "99.9 hours" appears nowhere in the run's evidence —
  an ungrounded claim in a run that otherwise succeeded.

The task succeeded; the run had three real defects. That gap is the
thing being measured.

## Companion tool

This skill is the method, executable by hand on one run. For the
deterministic scorer that does it at scale, with CI exit codes and
a GitHub Action: [runreckon](https://github.com/ranadhir19/runreckon).
