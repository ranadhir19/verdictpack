#!/usr/bin/env python3
"""Measure a grader against gold labels and test it against a frozen bound.

Reads a CSV with header: item_id,gold,grader
Labels may be pass/fail, 1/0, true/false (case-insensitive).

Prints: n, agreement with a Wilson 95% interval, Cohen's kappa, the
false-pass and false-fail counts, and a verdict against the acceptance
bound (default: agreement >= 0.90 AND kappa >= 0.75, the bound used in
the evalcrucible pre-registration). The bound is an input, never an
output: set it before you run the grader, and do not move it after.

Usage:
  python3 grader_report.py labels.csv [--min-agreement 0.90] [--min-kappa 0.75]
  python3 grader_report.py --selftest

Standard library only. Exit code 0 = bound met, 1 = bound missed,
2 = input could not be read.
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


def cohens_kappa(pairs):
    n = len(pairs)
    agree = sum(1 for g, r in pairs if g == r)
    po = agree / n
    gold_pos = sum(1 for g, _ in pairs if g) / n
    grad_pos = sum(1 for _, r in pairs if r) / n
    pe = gold_pos * grad_pos + (1 - gold_pos) * (1 - grad_pos)
    if pe >= 1.0:
        return po, 1.0 if po >= 1.0 else 0.0
    return po, (po - pe) / (1 - pe)


def load_pairs(path):
    pairs = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = {"item_id", "gold", "grader"} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {sorted(missing)}")
        for row in reader:
            pairs.append((parse_label(row["gold"]), parse_label(row["grader"])))
    if not pairs:
        raise ValueError("CSV has no data rows")
    return pairs


def report(pairs, min_agreement, min_kappa, out=sys.stdout):
    n = len(pairs)
    po, kappa = cohens_kappa(pairs)
    agree_n = sum(1 for g, r in pairs if g == r)
    lo, hi = wilson(agree_n, n)
    false_pass = sum(1 for g, r in pairs if not g and r)
    false_fail = sum(1 for g, r in pairs if g and not r)
    print(f"items:            {n}", file=out)
    print(f"agreement:        {po:.3f}  (Wilson 95% CI {lo:.3f}-{hi:.3f})", file=out)
    print(f"Cohen's kappa:    {kappa:.3f}", file=out)
    print(f"false passes:     {false_pass}  (grader passed what gold fails)", file=out)
    print(f"false fails:      {false_fail}  (grader failed what gold passes)", file=out)
    ok = po >= min_agreement and kappa >= min_kappa
    bound = f"agreement >= {min_agreement:.2f} and kappa >= {min_kappa:.2f}"
    if ok:
        print(f"VERDICT: ACCEPT — the grader clears the frozen bound ({bound}).", file=out)
    else:
        print(f"VERDICT: FALL BACK — the grader misses the frozen bound ({bound}).", file=out)
        print("Use the strictest grader that clears the bound, and say so.", file=out)
    return 0 if ok else 1


def selftest():
    # 20 items: 12 gold-pass, 8 gold-fail; grader disagrees twice
    # (one false pass, one false fail) -> agreement 0.900, kappa 0.792.
    rows = []
    for i in range(12):
        rows.append((f"p{i}", "pass", "fail" if i == 0 else "pass"))
    for i in range(8):
        rows.append((f"f{i}", "fail", "pass" if i == 0 else "fail"))
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["item_id", "gold", "grader"])
    writer.writerows(rows)
    buf.seek(0)
    pairs = [(parse_label(r["gold"]), parse_label(r["grader"]))
             for r in csv.DictReader(io.StringIO(buf.getvalue()))]
    po, kappa = cohens_kappa(pairs)
    assert abs(po - 0.900) < 1e-9, po
    assert abs(kappa - 0.7917) < 1e-3, kappa
    out = io.StringIO()
    code = report(pairs, 0.90, 0.75, out=out)
    assert code == 0 and "ACCEPT" in out.getvalue(), out.getvalue()
    out = io.StringIO()
    code = report(pairs, 0.95, 0.75, out=out)
    assert code == 1 and "FALL BACK" in out.getvalue(), out.getvalue()
    print("grader_report selftest: PASS (agreement 0.900, kappa 0.792 on the fixture)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", nargs="?", help="CSV with item_id,gold,grader columns")
    ap.add_argument("--min-agreement", type=float, default=0.90)
    ap.add_argument("--min-kappa", type=float, default=0.75)
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
    return report(pairs, args.min_agreement, args.min_kappa)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
