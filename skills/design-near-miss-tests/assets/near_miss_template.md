# Near-miss test set — <system under test>

One row per near-miss. Every row names the base (supported) request it
was mutated from, the mutation operator, and the required behaviour.
"Required behaviour" is one of:

- **answer-modified** — compute the modified thing, not the base thing.
- **refuse** — decline, because the request is outside the envelope.
- **clarify** — ask a question whose answer would make it answerable.

The defect class being hunted is *silent substitution*: answering a
different, easier request confidently instead of doing one of the
three things above. A silent substitution is a failure even when the
substituted answer is correct.

| # | Base request | Mutation operator | Near-miss request | Required behaviour | Catches |
|---|---|---|---|---|---|
| 1 | | qualifier: subgroup | | answer-modified | qualifier dropped |
| 2 | | qualifier: time window | | answer-modified | stale/base window answered |
| 3 | | qualifier: place | | answer-modified | wrong place answered |
| 4 | | out-of-envelope: near neighbour topic | | refuse or clarify | silent substitution |
| 5 | | set operation: add / remove / narrow | | answer-modified | context ignored |
| 6 | | boundary: just outside a limit | | refuse or clarify | limit silently stretched |
| 7 | | boundary: just inside a limit | | answer-modified | over-refusal |
| 8 | | carry-over: follow-up referring to earlier state | | answer-modified | context lost |
