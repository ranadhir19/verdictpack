---
name: calibrate-llm-judge
description: Calibrate an LLM-as-judge before using its verdicts — measure agreement and Cohen's kappa against gold labels, report prevalence beside kappa, and read every disagreement. Use when a model's judgements feed a score, a gate, a leaderboard, or an annotation pipeline, or when a reported kappa looks suspiciously low (or high) for the agreement level claimed.
---

# Calibrate an LLM judge

A judge model's verdicts are measurements, and an uncalibrated
judge is an unmeasured instrument. Calibration means: run the judge
on items whose correct verdicts are known independently, measure
how often it agrees, and print those numbers next to every verdict
the judge ever produces. This skill is that procedure, including
the statistical trap that makes naive calibration reports lie.

## Procedure

1. **Build the calibration set.** Items with gold verdicts known
   independently of the judge (by construction, by an independent
   implementation, or by careful human labelling). Cover every
   verdict class and every content family the judge will see. Size
   honestly: 12 items is a smoke test, ~50 begins to measure,
   150 gives intervals narrow enough to argue with. The set is a
   cost you pay once; judging without it is a cost you pay forever,
   invisibly.
2. **Run the judge blind.** No gold labels in the prompt, no hints
   about which items are calibration items.
3. **Measure.** `python3 scripts/judge_report.py labels.csv`
   (columns `item_id,gold,judge`) prints raw agreement with a
   Wilson interval, Cohen's kappa, gold prevalence, per-class
   agreement, and the disagreement count.
4. **Read prevalence before kappa — always.** Kappa corrects for
   chance agreement, and when one gold class dominates, chance
   agreement is high and kappa collapses *by construction*. See the
   paradox below. The reporting rule: **raw agreement and
   prevalence are printed with every kappa, every time.** A kappa
   quoted alone is not a measurement; it is a rumour.
5. **Read every disagreement.** Classify the judge's error modes:
   paraphrase misses (correct content, new wording, marked wrong),
   negation false-passes (a "not" the judge skimmed), format
   sensitivity, length bias. The error-mode list, not the headline
   number, is what tells you where the judge may be used.
6. **Decide the judge's jurisdiction.** Where may its verdicts be
   used as-is, where only as a flag for human review, and where not
   at all? Write it down. Then print the calibration —
   "judge X: agreement a, kappa k, prevalence p, on n items" —
   next to its verdicts wherever they appear, and never blend a
   judge's score into a deterministic score.

## The prevalence paradox (measured, not hypothetical)

In an annotation study run by this pack's author, one labelling
dimension had gold labels so skewed that 268 of 270 items fell in a
single class. Two panels agreed on **98.5%** of items — and Cohen's
kappa came out at **−0.007**, apparently "no agreement at all". Both
numbers are arithmetically correct; the kappa is the misleading
one, because with prevalence that extreme, the chance-agreement
correction consumes the entire scale. The bundled script reproduces
the shape in miniature (`--selftest`): 95% raw agreement with a
kappa of exactly 0.000 on a 19-to-1 skewed set. Whenever prevalence
exceeds ~0.90, headline the raw agreement and treat kappa as
uninterpretable.

The mirror-image trap exists too: on a balanced set, a healthy
kappa can hide a judge that fails *systematically on one class* —
which is why the report includes per-class agreement.

## Worked miniature example

`assets/judge_example.csv`: 24 items (18 gold-pass, 6 gold-fail)
judged by a model. The script reports:

```text
raw agreement:    0.875  (Wilson 95% CI 0.690-0.957)
Cohen's kappa:    0.647
gold prevalence:  0.750
agreement on gold-pass items: 0.944
agreement on gold-fail items: 0.667
disagreements:    3
```

Reading it properly: overall agreement looks decent, but the
per-class split shows the judge is much weaker exactly where it
matters — it waves through a third of the items that should fail
(agreement 0.667 on gold-fail). Jurisdiction decision: this judge
may pre-screen passes, but its *pass* verdicts on borderline items
need review, and at n = 24 the interval (0.69–0.96) says the whole
calibration is a smoke test, not a measurement. For comparison, a
deterministic stand-in judge in runreckon measured agreement 0.833,
kappa 0.667 on 12 items, with two instructive failures (a
heavy-paraphrase miss, a negation false-pass) — small numbers,
honestly labelled, printed on every scorecard it touches.

## Failure modes this catches

- Kappa quoted alone on skewed data ("our annotators don't agree"
  when they agree 98.5% of the time — or the reverse complacency).
- A judge trusted on classes where it is weakest, because only the
  pooled number was reported.
- Judge scores blended into deterministic scores, laundering a
  hope into a measurement.
- Calibration sets built from the judge's own outputs (the system's
  classification verifying itself).

## Companion skills and tools

Validating a *grader* against a frozen acceptance bound is the
validate-llm-grader skill. Judge calibration in a scoring pipeline:
[runreckon](https://github.com/ranadhir19/runreckon); grader
validation at scale:
[evalcrucible](https://github.com/ranadhir19/evalcrucible).
