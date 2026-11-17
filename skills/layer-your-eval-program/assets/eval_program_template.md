# Eval programme — <product>

One row per layer. A layer that does not exist yet is recorded as
such, with the trigger that will start it — an honest "not started"
is part of the programme, not an omission.

| Layer | Contents | Cadence | Pre-set bar | Evidence produced | Status |
|---|---|---|---|---|---|
| 1 — assertions | <feature × scenario grid + standing invariants> | every change (CI) | <e.g. ≥ 90%, zero tolerated failures in <named shape>> | <score history per version> | |
| 2 — human & model eval | <labelled trace review; judge calibration> | <weekly / per release> | <e.g. judge agreement & kappa vs labels, per calibrate-llm-judge> | <error-mode list; calibration numbers> | |
| 3 — live comparison | <A/B or shadow comparison on real traffic> | significant changes only | <the behaviour metric that decides> | <comparison report> | not started — trigger: <…> |

## Synthetic input log (layer 1 stock)

| Grid cell | Inputs generated | Labelled by | Failures found | Failure mode named |
|---|---|---|---|---|
| <feature × shape> | | construction / independent check / human | | |

## Bar record

- Bar set on: <date>, before the run of <date>.
- Number: <…>. Named exceptions: <shapes or classes with zero
  tolerance, and why>.
- On a miss, the consequence is: <fix list before release / scoped
  sign-off by name> — never a quieter bar.
