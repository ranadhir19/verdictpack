#!/usr/bin/env python3
"""Pre-flight a (spec, trace) pair before scoring an agent run.

Scoring is only as good as its inputs. This checker answers, for each
of the eight runreckon dimensions, one question: do the spec and the
trace actually contain what this dimension needs? Dimensions without
inputs must be reported n/a and excluded from the composite — never
silently zeroed, never gifted a perfect score. Error recovery gets a
special verdict: if the trace contains no failure, the dimension is
UNTESTED, which is a statement about the trace, not the agent.

It also prints observed facts about the trace (call count, tools used,
undeclared tools, errors). Observed is not scored — scoring is the
method in SKILL.md (or the runreckon tool).

Usage:
  python3 spec_trace_check.py spec.json trace.jsonl
  python3 spec_trace_check.py --selftest

Standard library only. Exit 0 = pair is structurally readable,
2 = unreadable or malformed.
"""
import json
import os
import sys

EVENT_TYPES = {"run", "call", "result", "note", "final"}
DIMENSIONS = ["outcome", "tool_selection", "argument_validity", "step_economy",
              "error_recovery", "policy", "cost_latency", "groundedness"]


def load_spec(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    if not isinstance(spec, dict):
        raise ValueError("spec must be a JSON object")
    return spec


def load_trace(path):
    events = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"trace line {i} is not valid JSON: {exc}")
            if not isinstance(ev, dict) or ev.get("type") not in EVENT_TYPES:
                raise ValueError(f"trace line {i}: type must be one of {sorted(EVENT_TYPES)}")
            events.append(ev)
    if not events:
        raise ValueError("trace has no events")
    return events


def classify(spec, events):
    calls = [e for e in events if e["type"] == "call"]
    results = [e for e in events if e["type"] == "result"]
    finals = [e for e in events if e["type"] == "final"]
    errors = [e for e in results if e.get("status") == "error"]
    allowed = spec.get("allowed_tools") or spec.get("expected_tools") or []
    policy = spec.get("policy") or {}
    policy_live = any(policy.get(k) for k in
                      ("forbidden_tools", "forbidden_arg_patterns",
                       "required_ordering", "max_calls"))
    budgets = spec.get("budgets") or {}
    verdicts = {}
    verdicts["outcome"] = (
        "SCORABLE" if (spec.get("final_checks") or spec.get("required_answer_contains")) and finals
        else "n/a — spec declares no final checks, or the trace has no final event")
    verdicts["tool_selection"] = (
        "SCORABLE" if allowed else "n/a — spec declares no allowed/expected tool set")
    verdicts["argument_validity"] = (
        "SCORABLE" if spec.get("tool_schemas") else "n/a — spec declares no tool schemas")
    verdicts["step_economy"] = (
        "SCORABLE" if calls else "n/a — the trace contains no calls")
    if errors:
        verdicts["error_recovery"] = "SCORABLE"
    elif calls:
        verdicts["error_recovery"] = ("UNTESTED — no failure occurred in this trace; "
                                      "report it as untested, not as a perfect score")
    else:
        verdicts["error_recovery"] = "n/a — the trace contains no calls"
    verdicts["policy"] = (
        "SCORABLE" if policy_live else "n/a — spec declares no policy rules")
    if budgets:
        parts = ["steps"]
        if any("tokens" in r for r in results):
            parts.append("tokens")
        if any("latency_ms" in r for r in results):
            parts.append("latency")
        verdicts["cost_latency"] = "SCORABLE (" + ", ".join(parts) + " measurable)"
    else:
        verdicts["cost_latency"] = "n/a — spec declares no budgets"
    verdicts["groundedness"] = (
        "SCORABLE" if finals and finals[-1].get("answer") and any(r.get("output") for r in results)
        else "n/a — no final answer, or no result output to ground claims against")
    observed = {
        "calls": len(calls),
        "tools_used": sorted({c.get("tool", "?") for c in calls}),
        "undeclared_tools": sorted({c.get("tool", "?") for c in calls} - set(allowed)) if allowed else [],
        "errors": len(errors),
        "final_events": len(finals),
        "total_tokens": sum(r.get("tokens", 0) for r in results),
    }
    return verdicts, observed


def report(spec, events, out=sys.stdout):
    verdicts, observed = classify(spec, events)
    print("Dimension scorability (before any scoring):", file=out)
    for dim in DIMENSIONS:
        print(f"  {dim:<18} {verdicts[dim]}", file=out)
    print("\nObserved facts (not scores):", file=out)
    print(f"  calls: {observed['calls']}   errors: {observed['errors']}   "
          f"final events: {observed['final_events']}   total tokens: {observed['total_tokens']}", file=out)
    print(f"  tools used: {', '.join(observed['tools_used'])}", file=out)
    if observed["undeclared_tools"]:
        print(f"  undeclared tools: {', '.join(observed['undeclared_tools'])}", file=out)
    if observed["final_events"] != 1:
        print(f"  WARNING: expected exactly 1 final event, found {observed['final_events']}", file=out)
    return 0


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    assets = os.path.join(here, "..", "assets")
    spec = load_spec(os.path.join(assets, "task_spec_template.json"))
    events = load_trace(os.path.join(assets, "trace_example.jsonl"))
    verdicts, observed = classify(spec, events)
    assert set(verdicts) == set(DIMENSIONS), verdicts
    assert verdicts["error_recovery"] == "SCORABLE", verdicts
    assert observed["undeclared_tools"] == ["summarize_page"], observed
    assert observed["errors"] == 1 and observed["calls"] == 6, observed
    quiet = [e for e in events if not (e["type"] == "result" and e.get("status") == "error")]
    quiet = [dict(e, status="ok") if e["type"] == "result" else e for e in quiet]
    v2, _ = classify(spec, quiet)
    assert v2["error_recovery"].startswith("UNTESTED"), v2
    print("spec_trace_check selftest: PASS (8 dimensions classified; "
          "error_recovery SCORABLE with a failure present, UNTESTED without)")
    return 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        spec = load_spec(argv[0])
        events = load_trace(argv[1])
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return report(spec, events)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
