---
name: layer-your-eval-program
description: "Layer an AI product's evaluation programme by cost — fast deterministic tests on every change, human and model evaluation on a set cadence, live A/B comparison only once real users exist. Use when a team has scattered tests but no programme: no cadence, no pre-set pass bar, or model judges running before the cheap assertion layer exists. Includes generating synthetic test inputs against a feature-by-scenario grid and setting the acceptable pass rate as an explicit product decision."
---

# Layer your eval program

Individual tests are not a programme. A programme decides *which*
checks run *when*, and the deciding variable is cost: a check that
runs in milliseconds can run on every change; a check that consumes
human attention or model calls must earn a cadence; a check that
exposes real users to a variant must wait until there are real
users whose behaviour is worth measuring. Teams that skip the
layering end up with the expensive layers running rarely and
randomly, and the cheap layer missing entirely — so every change is
judged by vibe.

## The three layers

| Layer | Contents | Cadence | Cost driver |
|---|---|---|---|
| 1 — assertions | Deterministic checks on outputs: exact values, set shapes, format contracts, standing invariants | every change (CI) | ~nothing per run |
| 2 — human & model eval | Labelled trace review (start binary: good/bad), judge calibration, error-mode analysis | fixed cadence — weekly, or per release | labels and judge calls |
| 3 — live comparison | A/B test or shadow comparison against real traffic | significant changes only, mature products only | real users' experience |

Rules that make the layers work:

- **Cadence follows cost, never enthusiasm.** If a layer-2 review
  happens "when someone remembers", it does not happen. Put it on
  the calendar like a release.
- **Build layer 1 first.** Model eval layered over missing
  assertions measures noise: the judge ends up grading failures a
  regex would have caught, at judge prices. A useful test: if a
  failure mode has ever been seen twice, it belongs in layer 1.
- **Layer 3 before real users is theatre.** With no traffic there
  is nothing to compare; the honest entry in the programme table is
  "not started — no users yet", with the trigger that will start it.
- **Assertions come from observed failures.** Read traces, note how
  the system actually breaks, and write the check that would have
  caught it. A brainstormed list (a model can help draft candidates)
  is a starting point; the trace-derived list is the programme.

## Stocking layer 1: synthetic inputs

You do not need production traffic to build the assertion layer.

1. **Draw the grid.** Features down one side, scenario shapes
   across the top — for set-returning features: exactly one match /
   several matches / no matches; for everything: the standing
   invariants (internal identifiers never surface, the output
   contract holds). The domain catalogue from the
   audit-eval-coverage skill is the grid's source.
2. **Generate inputs against the grid with a model.** Ask for many
   phrasings per cell — users do not phrase requests the way
   developers do. Hundreds of inputs cost less than one debugging
   session. Keep the generator's prompt and the grid with the tests,
   so the set can be regenerated and extended honestly.
3. **Label by construction wherever possible.** Generate the input
   together with the fact that makes its expected output known (the
   record created is the record the lookup must return), so the
   expectation is not itself a guess.
4. **Treasure the failures.** The inputs the system gets wrong are
   the layer's real output: each one names a failure mode to fix,
   or a cell of the grid the product does not actually cover. A
   synthetic set the system passes entirely is either too easy or
   measuring the wrong grid.
5. **Refresh from reality.** Once real traces exist, mine them for
   the phrasings and edge cases the generator missed, and fold them
   in. Synthetic stock is a bootstrap, not a substitute.

## The pass bar is a product decision

Unlike ordinary unit tests, an eval layer is not expected to sit at
100% — some inputs probe behaviour the product has consciously not
built yet. So the bar is set *in advance*, in writing, as a product
decision:

- the number ("layer 1 ≥ 90%"), and
- the named exceptions ("no tolerated failures in the no-match
  shape: an invented result is worse than any other failure"), and
- what a miss triggers (a fix list before release, not a quieter
  bar).

A bar set after seeing the score is not a bar. A bar at 100% is
usually a sign the grid is too easy. Report the measured rate
against the recorded bar, per layer, over time — a programme whose
results are not trended is a snapshot, and snapshots cannot show
whether the system is improving.

## Worked miniature example

A service-records assistant answers questions about equipment
maintenance history. Its programme:

**Layer 1.** Grid: *find records* (one / several / no matches),
*summarise one record*, *refuse a non-records request*, plus the
invariant "internal asset IDs never appear in an answer". 140
synthetic inputs generated against the grid, expectations labelled
by construction. Bar set in advance: ≥ 90% overall, zero tolerated
failures in the no-match shape. Measured: **131/140 (93.6%)** — the
9 failures are 6 several-match truncations and 3 one-match answers
with an invented extra field; the no-match shape is clean. Verdict:
bar met, and the failure list (truncation first) is the next
sprint's work, in order.

**Layer 2.** Monthly: 40 recent traces labelled good/bad by the
support lead; the model judge used for pre-screening is calibrated
against those labels before its verdicts count (see the
calibrate-llm-judge skill). Error modes from the disagreements feed
new layer-1 assertions.

**Layer 3.** Recorded as *not started*: the assistant has internal
users only, in dozens. Trigger to start: general availability, when
a change can be compared on real task-completion behaviour.

Three layers, three honest statuses: one measured, one calendared,
one deliberately waiting — that is a programme. Template:
`assets/eval_program_template.md`.

## Failure modes this catches

- Judge-first programmes: expensive model eval grading failures a
  pattern check would have caught for free.
- Cadence by memory: layer-2 reviews that silently stop happening.
- Perfection theatre: a 100% bar on a grid too easy to fail, quoted
  as quality.
- Retro-fitted bars: thresholds written after the run, wherever the
  score happened to land.
- Premature layer 3: "A/B tests" run on synthetic traffic and
  reported as user evidence.

## Companion skills and tools

The layers are stocked and audited by the other skills in this
pack: audit-eval-coverage (build the grid from the domain),
design-near-miss-tests (the mutation and invariant classes inside
layer 1), validate-llm-grader and calibrate-llm-judge (layer 2's
instruments). At scale, the deterministic machinery lives in
[evalcrucible](https://github.com/ranadhir19/evalcrucible) (grader
validation, suite audit) and
[runreckon](https://github.com/ranadhir19/runreckon) (run scoring
with CI exit codes — a layer-1 citizen for agent runs).
