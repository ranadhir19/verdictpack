---
name: validate-llm-grader
description: Validate an automated grader, checker, or LLM judge against gold-labelled data before trusting any score it produces. Use when a benchmark, eval harness, or CI gate relies on a grader whose own accuracy has never been measured, or when swapping in a cheaper/faster grader. Freezes an acceptance bound first, then measures agreement and Cohen's kappa and returns an accept / fall-back verdict.
---

# Validate an LLM grader before you trust it

Every score a grader produces is a claim made by an instrument. An
unvalidated grader is not an instrument; it is a hope. This skill is
the procedure for turning a grader — exact-match, normalized,
rubric-based, or a model judge — into a measured instrument with a
known error rate, and for refusing it when it misses a bound you set
*before* seeing its results.

## Inputs you need

- The grader, runnable against individual items.
- A labelled set: items whose correct pass/fail verdict is known
  independently of the grader — by construction, by an independent
  second implementation, or by careful human labelling. If the labels
  came from the grader itself, stop: that is the system's own
  classification used as its own verification signal, and it proves
  nothing.
- An acceptance bound, written down before the run. The reference
  bound from the evalcrucible pre-registration is **agreement ≥ 0.90
  AND Cohen's kappa ≥ 0.75** on the labelled set. Yours may differ;
  what may not differ is that it is frozen first.

## Procedure

1. **Freeze the bound.** Record the thresholds, the labelled-set
   source, and the date, in the artefact that will report the result.
   A bound written after the run is a rationalisation.
2. **Build or audit the labelled set.** Aim for ≥ 100 items spanning
   every task family the grader will score, with both pass and fail
   gold labels well represented. Note the gold prevalence (share of
   the modal class) — you will need it to read kappa honestly (see
   the calibrate-llm-judge skill).
3. **Run the grader** on every labelled item. Save raw outputs, not
   just verdicts; error modes live in the outputs.
4. **Measure.** Run the bundled script:
   `python3 scripts/grader_report.py labels.csv`
   (CSV columns: `item_id,gold,grader`). It prints agreement with a
   Wilson 95% interval, kappa, false-pass and false-fail counts,
   per-class precision and recall, and the verdict against the
   bound.
5. **Read the disagreements.** Classify each one: formatting
   rejections (right answer, wrong shape), content false passes (a
   wrong answer the grader waved through — e.g. a number lifted from
   the prompt), or gold errors (the label was wrong; fix the label
   set, disclose it, and re-run — never quietly).
6. **Decide, by the frozen bound only.** ACCEPT the grader, or FALL
   BACK to the strictest grader that clears the bound, and say so in
   the report. Never relax the bound to fit a measured miss; a missed
   bound is a result, and it is the reason this procedure exists.
7. **Report the measurement wherever the grader's scores are used:**
   "grader X, agreement a, kappa k, on n labelled items" — every
   time, not once in a footnote.

## Worked miniature example

`assets/labelled_example.csv` holds 24 items (14 gold-pass, 10
gold-fail) scored by a plausible string-matching grader. Running the
script gives:

```text
items:            24
agreement:        0.833  (Wilson 95% CI 0.641-0.933)
Cohen's kappa:    0.667
false passes:     1  (grader passed what gold fails)
false fails:      3  (grader failed what gold passes)
pass class:       precision 0.917 / recall 0.786
fail class:       precision 0.750 / recall 0.900
VERDICT: FALL BACK — the grader misses the frozen bound (agreement >= 0.90 and kappa >= 0.75).
```

83% agreement *feels* fine. It is below the bound, its interval
reaches down to 0.64, and its errors are asymmetric: three correct
answers rejected (typically formatting) against one wrong answer
passed. The per-class split names the asymmetry precisely — pass
recall 0.786 (it misses more than a fifth of the correct answers)
against fail recall 0.900 — so the repair is aimed at the false
fails, not spread evenly. The correct action is not to lower the bound to 0.80 — it is
to fix the grader's normalization (which usually recovers the false
fails) or fall back to a stricter grader, then re-measure.

For scale, the same procedure on 150 labelled items in evalcrucible
measured an exact-match grader at 80.0% agreement (kappa 0.545 —
rejected), a normalized grader at 100%, and a cheap rubric grader at
99.3% (kappa 0.986 — accepted, with one documented content false
pass). Cheap graders are fine. *Unmeasured* graders are not.

## Failure modes this catches

- A grader that rejects correct answers for their formatting.
- A grader that passes wrong answers containing prompt material.
- A benchmark whose headline scores move when the grader changes —
  the scores were the grader's, not the agents'.
- Post-hoc bound shopping: thresholds that drift to wherever the
  measurement landed.

## Companion tools

Systematic suite auditing (is the benchmark itself broken?) is the
audit-eval-coverage skill. Full grader-validation and benchmark-audit
tooling: [evalcrucible](https://github.com/ranadhir19/evalcrucible).
