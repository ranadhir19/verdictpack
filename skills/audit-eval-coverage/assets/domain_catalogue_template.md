# Domain catalogue — <system under test>

Built from the DOMAIN (what the system claims to handle, per its own
docs, task description, and intended users) — never from the eval
suite's existing items. The suite is measured against this list, so
this list must not be copied from the suite.

| # | Domain topic | Source of the claim | Notes |
|---|---|---|---|
| 1 | <topic the system says it handles> | <doc / page / requirement> | |
| 2 | | | |
| 3 | | | |

Rules for building the catalogue:

- One row per distinct thing a user can ask for, at the grain a user
  would name it ("quarterly revenue by region", not "SQL queries").
- Include the unglamorous topics: refusals, empty results, ambiguous
  requests, out-of-scope neighbours of in-scope topics.
- If a topic is claimed in marketing but excluded in the spec, record
  it and mark the exclusion — an eval that never tests the boundary
  cannot find where it leaks.
- Freeze the catalogue before mapping the suite. Topics discovered
  later are additions with dates, not silent edits.
