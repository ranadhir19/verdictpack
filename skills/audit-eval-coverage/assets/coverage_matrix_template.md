# Coverage matrix — <suite name> vs domain catalogue

Coverage is reported as **topics covered of topics in the catalogue**,
never as the suite's pass rate. A suite can pass 100% of its items and
cover 40% of the domain.

| # | Domain topic | Suite items (ids) | Items | Audit flags |
|---|---|---|---|---|
| 1 | <topic> | <id, id> | 2 | |
| 2 | <topic> | — | 0 | UNCOVERED |
| 3 | <topic> | <id> | 1 | probe B suspect |

**Coverage: <covered topics> of <catalogue topics> topics (<pct>%).**

Audit flags come from the four probes in the skill:

- **A — reference failure:** a known-correct solver fails the item →
  the item (or its gold) is the suspect, not the solver.
- **B — free pass:** a null, echo, or constant solver passes the item →
  the item measures nothing.
- **C — loose gate:** deliberately wrong answers pass → the item's
  checker is too loose.
- **D — leakage:** the item duplicates a development/training item.

Plus the standing warning: if an item's gold and the reference solver
were produced from the same source, no output-based probe can catch a
shared error — only independently re-deriving the gold can.
