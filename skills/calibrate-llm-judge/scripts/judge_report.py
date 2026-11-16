#!/usr/bin/env python3
"""Calibrate an LLM judge against gold labels — honestly, prevalence included.

Reads a CSV with header: item_id,gold,judge
Labels may be pass/fail, 1/0, true/false (case-insensitive).

Prints: n, raw agreement with a Wilson 95% interval, Cohen's kappa,
the prevalence of the modal gold class, per-class agreement, and the
disagreement count. Two warnings are built in because they are the two
ways judge calibration is most often misreported:

- PREVALENCE: when one gold class dominates (share >= 0.90), kappa is
  depressed by construction and can sit near zero even at 95%+ raw
  agreement. In that regime raw agreement is the headline number and
  kappa must not be quoted alone.
- SMALL N: below 30 items the interval around agreement is wide;
  differences smaller than the interval are not evidence.

Usage:
  python3 judge_report.py labels.csv
  python3 judge_report.py --selftest

Standard library only. Exit code 0 on a successful report, 2 on bad input.
"""
import argparse
import csv
import io
import math
import sys

TRUE_WORDS = {"pass", "1", "true", "yes", "y", "correct"}
FALSE_WORDS = {"fail", "0", "false", "no", "n", "incorrect"}


def parse_label(text):
    t = str(text).strip().lower()
    if t in TRUE_WORDS:
        return True
    if t in FALSE_WORDS:
        return False
    raise ValueError(f"unrecognised label: {text!r}")


def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def load_pairs(path):
    pairs = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = {"item_id", "gold", "judge"} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {sorted(missing)}")
        for row in reader:
            pairs.append((parse_label(row["gold"]), parse_label(row["judge"])))
    if not pairs:
        raise ValueError("CSV has no data rows")
    return pairs


def stats(pairs):
    n = len(pairs)
    agree_n = sum(1 for g, j in pairs if g == j)
    po = agree_n / n
    gold_pos = sum(1 for g, _ in pairs if g) / n
    judge_pos = sum(1 for _, j in pairs if j) / n
    pe = gold_pos * judge_pos + (1 - gold_pos) * (1 - judge_pos)
    kappa = 1.0 if pe >= 1.0 and po >= 1.0 else (0.0 if pe >= 1.0 else (po - pe) / (1 - pe))
    prevalence = max(gold_pos, 1 - gold_pos)
    pos_items = [(g, j) for g, j in pairs if g]
    neg_items = [(g, j) for g, j in pairs if not g]
    pos_agree = (sum(1 for g, j in pos_items if g == j) / len(pos_items)) if pos_items else None
    neg_agree = (sum(1 for g, j in neg_items if g == j) / len(neg_items)) if neg_items else None
    return {
        "n": n, "agreement": po, "kappa": kappa, "prevalence": prevalence,
        "agree_n": agree_n, "pos_agree": pos_agree, "neg_agree": neg_agree,
        "disagree": n - agree_n,
    }


def report(pairs, out=sys.stdout):
    s = stats(pairs)
    lo, hi = wilson(s["agree_n"], s["n"])
    print(f"items:            {s['n']}", file=out)
    print(f"raw agreement:    {s['agreement']:.3f}  (Wilson 95% CI {lo:.3f}-{hi:.3f})", file=out)
    print(f"Cohen's kappa:    {s['kappa']:.3f}", file=out)
    print(f"gold prevalence:  {s['prevalence']:.3f}  (share of the modal gold class)", file=out)
    if s["pos_agree"] is not None:
        print(f"agreement on gold-pass items: {s['pos_agree']:.3f}", file=out)
    if s["neg_agree"] is not None:
        print(f"agreement on gold-fail items: {s['neg_agree']:.3f}", file=out)
    print(f"disagreements:    {s['disagree']}  (read every one before trusting the judge)", file=out)
    if s["prevalence"] >= 0.90:
        print("WARNING — PREVALENCE: one gold class dominates, so kappa is "
              "depressed by construction. Headline the raw agreement; do not "
              "quote kappa alone.", file=out)
    if s["n"] < 30:
        print("WARNING — SMALL N: under 30 items the interval is wide. Treat "
              "this as a smoke calibration, not a measurement.", file=out)
    print("Print these numbers next to any verdict this judge produces. "
          "A judge's say-so without them is a hope, not a measurement.", file=out)
    return 0


def selftest():
    # Prevalence paradox fixture: 20 items, 19 gold-pass / 1 gold-fail;
    # the judge passes everything -> agreement 0.950, kappa exactly 0.
    rows = [(f"p{i}", "pass", "pass") for i in range(19)]
    rows.append(("f0", "fail", "pass"))
    pairs = [(parse_label(g), parse_label(j)) for _, g, j in rows]
    s = stats(pairs)
    assert abs(s["agreement"] - 0.95) < 1e-9, s
    assert abs(s["kappa"] - 0.0) < 1e-9, s
    assert abs(s["prevalence"] - 0.95) < 1e-9, s
    out = io.StringIO()
    report(pairs, out=out)
    assert "PREVALENCE" in out.getvalue(), out.getvalue()
    print("judge_report selftest: PASS (agreement 0.950 with kappa 0.000 "
          "on the skewed fixture — the paradox, reproduced)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", nargs="?", help="CSV with item_id,gold,judge columns")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.csv:
        ap.error("a CSV path is required (or use --selftest)")
    try:
        pairs = load_pairs(args.csv)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return report(pairs)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
