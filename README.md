![verdictpack — measure the measurer](assets/banner.svg)

# verdictpack

**Measure the measurer.** Five agent skills that turn AI evaluation
from a vibe into an instrument: validate your graders before you
trust their scores, score how an agent *executed* a run (not just
whether it finished), audit what your eval suite actually covers,
design the near-miss tests that catch silent substitution, and
calibrate an LLM judge before its verdicts feed anything.

Every score is a claim made by a measuring instrument. These skills
are the procedures for measuring the instruments — each one
self-contained, executable by an agent with no other context, with
a worked miniature example and, where counting is involved, a
stdlib-only script whose numbers you can check.

## The skills

| Skill | What it does | Reach for it when |
|---|---|---|
| [validate-llm-grader](skills/validate-llm-grader/SKILL.md) | Measures a grader/checker/judge against gold-labelled data under an acceptance bound frozen *before* the run; returns accept / fall-back. | A benchmark, harness, or CI gate relies on a grader whose own accuracy has never been measured. |
| [score-agent-run](skills/score-agent-run/SKILL.md) | Scores a recorded agent run against its task spec across eight dimensions — outcome, tool selection, argument validity, step economy, error recovery, policy (hard gate), cost/latency, groundedness. | Reviewing a trace, gating a change on run quality, or investigating a run that "succeeded" badly. |
| [audit-eval-coverage](skills/audit-eval-coverage/SKILL.md) | Builds the domain catalogue from the domain (not the suite), maps suite items to it, reports coverage as topics covered of topics claimed, and probes for broken tests. | Pass rates are quoted as capability evidence, or a suite was written by the same process it tests. |
| [design-near-miss-tests](skills/design-near-miss-tests/SKILL.md) | Generates near-miss tests from supported requests — qualifier mutations, near neighbours, set operations, boundaries, empty cases — each with a required behaviour: answer-modified, refuse, or clarify. | A test set holds only happy-path requests, or a system keeps answering an easier question than the one asked. |
| [calibrate-llm-judge](skills/calibrate-llm-judge/SKILL.md) | Calibrates an LLM-as-judge: agreement, Cohen's kappa, prevalence reported beside kappa (with the paradox explained and reproduced), per-class agreement, disagreement analysis. | A model's judgements feed a score, gate, leaderboard, or annotation pipeline. |

## Install

The pack uses the standard agent-skill format: each skill is a
folder containing a `SKILL.md` (name + description frontmatter,
then the procedure) plus any scripts and templates it needs.

**Claude Code** — copy the skill folders into your skills
directory:

```bash
git clone https://github.com/ranadhir19/verdictpack.git
cp -r verdictpack/skills/* ~/.claude/skills/        # personal
# or, per project:
cp -r verdictpack/skills/* <your-project>/.claude/skills/
```

**Other agent hosts** — any host that loads skill folders in this
format (a `SKILL.md` with `name`/`description` frontmatter) can use
the pack the same way: place the folders from `skills/` wherever
your host discovers skills. The procedures themselves are plain
Markdown and the scripts are Python standard library only, so the
pack also works read directly by a human or an agent with no skill
loader at all.

**Verify the pack** after cloning:

```bash
python3 validate.py   # must end with OVERALL PASS
```

The harness parses every skill's frontmatter, checks that internal
links resolve, and runs each bundled script's self-test.

## Where the methods come from

The pack is the method layer of two open tools by the same author:

- [evalcrucible](https://github.com/ranadhir19/evalcrucible) — the
  grader tool: validates graders against labelled data and audits
  static (prompt → gold) task suites. The validate-llm-grader
  acceptance bound and the audit probes come from its
  pre-registered experiment.
- [runreckon](https://github.com/ranadhir19/runreckon) — the eval
  tool: scores a recorded run against its task spec across the
  eight dimensions used by score-agent-run, with a fault-injection
  self-test and measured judge calibration.

The skills teach and operationalise the procedures; the tools run
them at scale. The validation protocol behind audit-eval-coverage
and design-near-miss-tests — domain-first acceptance questions,
near-miss negatives, qualifier preservation, never trusting the
system's own classification as the verification signal — was
distilled from a real benchmark review failure and its
investigation.

## Honest scope

- These are *procedures*, not oracles. Each one ends in a
  measurement with stated provenance and limits, or in a refusal to
  claim more than the inputs support (an n/a dimension, an UNTESTED
  error-recovery score, a kappa flagged uninterpretable).
- The bundled scripts count labels and check structures. They do
  not call models, need no API keys, and make no network calls.
- Worked examples are miniature and synthetic, built so every
  number in them can be re-derived by running the bundled script.
  Small-n results are labelled as smoke tests, not measurements —
  the pack holds itself to the standards it teaches.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Ranadhir Ghosh.
Originality and IP record: [COMPLIANCE.md](COMPLIANCE.md).
