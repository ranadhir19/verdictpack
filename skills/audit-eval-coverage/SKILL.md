---
name: audit-eval-coverage
description: Audit an eval suite or benchmark for domain coverage and broken tests — acceptance questions authored from the domain, not from the suite. Use when a benchmark's pass rates are quoted as capability evidence, when a suite was written by the same people/process as the system it tests, or before adopting a third-party benchmark. Produces a coverage figure (topics covered of topics in the domain) and probe flags for flawed tests.
---

# Audit an eval suite's coverage — from the domain inwards

An eval suite proves only what it samples. The standard failure:
acceptance questions authored from the *implementation's* coverage
list, so the suite certifies exactly the space its authors already
handled and never samples the rest. The suite passes; the claim
("the system handles X") is false in the uncovered space. This audit
reverses the direction: catalogue the domain first, then measure the
suite against it.

## Procedure

1. **Build the domain catalogue from the domain.** List the topics
   the system claims to handle — from its documentation, task
   description, product claims, and intended users — at the grain a
   user would name them. Include the unglamorous cells: refusals,
   empty results, ambiguity, and the out-of-scope neighbours of
   in-scope topics. **Never build the catalogue from the suite's
   items**; that is the failure being audited. Freeze it before
   mapping. Template: `assets/domain_catalogue_template.md`.
2. **Map every suite item to a catalogue cell.** Items that map to
   no cell are recorded as off-domain (they may be fine tests of
   something — just not of the claim). Cells with no items are
   **uncovered**.
3. **Report coverage as topics, not pass rates.** "11 of 19 domain
   topics covered" is the headline. A suite's internal pass rate is
   reported separately and never as coverage. Template:
   `assets/coverage_matrix_template.md`.
4. **Run the four flaw probes** on the items themselves:
   - **A — reference failure.** Run a known-correct solver. Where it
     fails, the item or its gold is the suspect, not the solver.
   - **B — free pass.** Run null (returns nothing), echo (returns
     the prompt), and constant solvers. Any item they pass measures
     nothing.
   - **C — loose gate.** Feed deliberately wrong answers. Any item
     they pass has a checker that is too loose.
   - **D — leakage.** Check items against the development set; a
     test that duplicates a dev item measures memory, not ability.
5. **Hunt the shared-source flaw.** If an item's gold answer and the
   reference solver were produced from the same source (same table,
   same generator, same author assumptions), probes A–D all pass
   while the item is wrong. The only cure is independently
   re-deriving the gold. Record which items carry this risk.
6. **Write the verdict with provenance:** who authored the tests,
   what space they cover, which cells are uncovered, which items are
   flagged. "Verified" without provenance is not a verdict.

## Worked miniature example

A team ships a "meeting-notes assistant" and an eval of 6 items, all
passing. The domain catalogue, built from the product's own claims,
has 8 topics:

| # | Domain topic | Items | Flag |
|---|---|---|---|
| 1 | Summarise a single meeting | 2 | |
| 2 | Extract action items with owners | 2 | |
| 3 | Extract decisions | 1 | probe B: echo solver passes it (the "decision" is quoted verbatim in the notes, so returning the prompt scores full marks) |
| 4 | Compare two meetings / track changes | 0 | UNCOVERED |
| 5 | Handle a meeting with no decisions | 0 | UNCOVERED |
| 6 | Refuse a non-meeting document | 0 | UNCOVERED |
| 7 | Multi-speaker attribution | 1 | |
| 8 | Follow-up questions about earlier meetings | 0 | UNCOVERED |

**Coverage: 4 of 8 domain topics.** The suite's 100% pass rate was
true and nearly meaningless: half the claimed domain — including
every refusal and empty-case behaviour — was never sampled, and one
covered item measured nothing. In evalcrucible's larger measured
version of this audit, 11 of 12 planted test flaws were detected by
probes A–D with zero false flags on the clean suite; the twelfth
was a shared-source flaw, catchable only by re-deriving the gold.

## Reporting rules

- Coverage is "X of Y domain topics", always with the catalogue
  shown. Never substitute the suite's pass rate.
- Reviewer conditions matter: audit the suite as a cold reviewer
  meets it — first items, fresh state — not only in the authors'
  warmed-up arrangement.
- An uncovered cell is not an accusation; it is the boundary of
  what the suite's scores are evidence *about*. Say the boundary.

## Companion tool

The full audit implementation, with a clean suite, a flawed twin,
and the measured detection rates:
[evalcrucible](https://github.com/ranadhir19/evalcrucible). For
designing the tests that fill uncovered cells — especially the
near-boundary ones — see the design-near-miss-tests skill.
