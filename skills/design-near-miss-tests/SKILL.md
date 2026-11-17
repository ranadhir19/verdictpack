---
name: design-near-miss-tests
description: Design near-miss negative tests for an AI system or eval — in-domain-but-uncovered requests, qualifier-modified requests, set operations, and boundary cases that must be answered modified, refused, or clarified rather than silently substituted. Use when a test set only contains happy-path requests the system already handles, or when reviewing whether a system handles variations of its supported requests honestly.
---

# Design near-miss tests

Happy-path tests certify the requests a system already handles. The
failures that embarrass systems in front of reviewers live one step
away from the happy path: a request that *resembles* a supported one
but is modified, narrowed, combined, or just outside the envelope.
The characteristic defect is **silent substitution** — answering a
different, easier request confidently. A substituted answer is a
failure even when it is correct, because the user asked for something
else and was never told.

## The mutation operators

Start from the system's genuinely supported requests (its base set)
and apply one operator at a time. One mutation per test: a test that
changes two things cannot attribute its failure.

| Operator | Mutation | Required behaviour |
|---|---|---|
| qualifier: subgroup | "…for the enterprise segment" | answer-modified |
| qualifier: time | "…last quarter" → "…the quarter before" | answer-modified |
| qualifier: place | "…in Ohio" → "…in Ontario" | answer-modified or refuse |
| near neighbour | an adjacent topic the system does not cover | refuse or clarify |
| set operation | "add X", "remove Y", "only the ones that…" | answer-modified (context applied) |
| carry-over | a follow-up that refers to earlier state ("and for the second one?") | answer-modified |
| boundary: just inside | the largest/smallest/oldest case the envelope admits | answer-modified |
| boundary: just outside | one step past a stated limit | refuse or clarify |
| empty case | a valid request whose true answer set is empty | answer-modified (report empty — never invent a filler answer) |
| format shift | same request, different surface form (table vs prose, units changed) | answer-modified |

Required behaviour is always one of three: **answer-modified**
(compute the modified thing), **refuse**, or **clarify** (ask the
question whose answer makes it answerable). Anything else —
answering the base request, answering a neighbour, answering with
the qualifier dropped — is silent substitution.

## Two companion test classes

Near-misses mutate supported requests. Two further classes complete
the set, and neither is a mutation:

**Result-cardinality scenarios.** For every feature that returns a
set — search, listing, lookup, extraction over several records —
test the three shapes of result separately, each with its own
expectation written in advance:

- **exactly one match** — that result, whole, with nothing added;
- **several matches** — the complete set: none dropped, none
  duplicated, none merged;
- **no matches** — an honest empty result, reported as empty (the
  empty-case operator above, applied to the set itself).

Systems routinely pass the several-match shape while inventing a
filler in the no-match shape or truncating the one-match shape; a
single blended "search works" test cannot see any of that.

**Standing invariants.** Checks that must hold on *every* response,
whatever feature produced it and whatever mutation was applied.
Write them once, run them across the whole set:

- internal identifiers — record keys, UUIDs, internal codes — never
  appear in user-facing output;
- nothing is presented as retrieved, computed, or verified that the
  run did not actually retrieve, compute, or verify;
- the declared output contract holds throughout: language, format,
  units, and any fields the contract promises or forbids.

An answer can satisfy its required behaviour and still fail an
invariant — the right result with an internal ID leaked into it is
a failure. Invariants are also the cheapest tests in the set: most
are pattern checks that run in milliseconds, on every change.

## Procedure

1. **List the base set.** The requests the system demonstrably
   supports (from its spec and its passing tests, not its claims).
2. **Apply each operator to each base request** where it makes
   sense. Aim for at least two near-misses per base request: one
   qualifier mutation and one of {near neighbour, boundary, set
   operation}.
3. **Write the required behaviour before running anything.** The
   expectation is part of the test; deciding it after seeing the
   output is how substitutions get rationalised.
4. **Include the conversation dimension.** Single-turn tests miss
   the set-operation failures: run sequences — establish a result
   set, then add, remove, and narrow it; switch topics and return;
   restart mid-session and check what state honestly survives.
5. **Score by behaviour class**, not by answer similarity: correct
   class (modified/refused/clarified as required) or substitution.
   Report per operator, so the weak operator is visible.
6. **Keep the set.** Near-misses that failed and were fixed become
   regression tests. Template: `assets/near_miss_template.md`.

## Worked miniature example

Base set of a small weather-data assistant: "What was the high
temperature in <city> on <date>?" and "List the days it rained in
<city> in <month>." Its data covers US cities, 2020–2025.

| # | Near-miss | Required | What substitution looks like |
|---|---|---|---|
| 1 | "High temperature in Austin on 2024-07-04, **in Celsius**" | answer-modified (unit applied) | the Fahrenheit number, unlabelled |
| 2 | "High temperature in **Toronto** on 2024-07-04" | refuse or clarify (outside coverage) | Austin's number, or a plausible invented one |
| 3 | "List the days it rained in Austin in **June 2026**" | refuse or clarify (outside the data window) | June 2025's list |
| 4 | "…and **only the weekends**" (follow-up to #3's base) | answer-modified (set narrowed) | the full month's list again |
| 5 | "List the days it rained in Austin in **February 2023**" (it did not rain) | answer-modified: report none | an invented rainy day, or the nearest month's |
| 6 | "High temperature in Austin on **1850-01-01**" | refuse | a confident number |

Six tests, none of them exotic, each aimed at a named defect class:
dropped qualifier, out-of-envelope substitution, stale-window
substitution, ignored set operation, empty-set invention, and
limit-stretching. A system can pass a hundred base requests and fail
all six of these — which is precisely why the base set alone is not
evidence.

## Notes

- Over-refusal is also a defect: the just-inside boundary case
  exists to catch systems that refuse everything unusual.
- A clarify response only counts if the question asked would
  actually make the request answerable.
- These tests pair with the audit-eval-coverage skill: the audit
  finds the uncovered domain cells; this skill writes the tests
  that probe them.
