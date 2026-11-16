#!/usr/bin/env python3
"""verdictpack harness.

Stages:
  1. Structure: every skills/<name>/SKILL.md exists; LICENSE present (MIT).
  2. Frontmatter: each SKILL.md opens with a --- block carrying name and
     description; name matches the folder; name is lowercase-hyphen;
     description is 40-1024 chars (discovery sanity).
  3. Links: every relative Markdown link in README.md and the SKILL.md
     files resolves to a path inside the tree.
  4. Scripts: every bundled scripts/*.py compiles and its --selftest
     exits 0.
  5. Coverage: README.md names every skill folder.

Prints one line per stage and ends with OVERALL PASS or OVERALL FAIL.
Standard library only.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(ROOT, "skills")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

failures = []


def stage(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def skill_dirs():
    return sorted(d for d in os.listdir(SKILLS_DIR)
                  if os.path.isdir(os.path.join(SKILLS_DIR, d)))


def main():
    skills = skill_dirs()

    # Stage 1 — structure
    missing = [s for s in skills
               if not os.path.isfile(os.path.join(SKILLS_DIR, s, "SKILL.md"))]
    lic = os.path.join(ROOT, "LICENSE")
    lic_ok = os.path.isfile(lic) and "MIT License" in open(lic, encoding="utf-8").read()
    stage("structure", not missing and lic_ok and len(skills) >= 1,
          f"{len(skills)} skills, LICENSE MIT={lic_ok}, missing={missing}")

    # Stage 2 — frontmatter
    fm_problems = []
    for s in skills:
        fm = parse_frontmatter(os.path.join(SKILLS_DIR, s, "SKILL.md"))
        if fm is None:
            fm_problems.append(f"{s}: no frontmatter block")
            continue
        if fm.get("name") != s:
            fm_problems.append(f"{s}: frontmatter name={fm.get('name')!r}")
        if not NAME_RE.match(s):
            fm_problems.append(f"{s}: name not lowercase-hyphen")
        desc = fm.get("description", "")
        if not (40 <= len(desc) <= 1024):
            fm_problems.append(f"{s}: description length {len(desc)} outside 40-1024")
    stage("frontmatter", not fm_problems, "; ".join(fm_problems) or "all skills valid")

    # Stage 3 — internal links resolve
    md_files = [os.path.join(ROOT, "README.md")] + \
               [os.path.join(SKILLS_DIR, s, "SKILL.md") for s in skills]
    link_problems = []
    for path in md_files:
        base = os.path.dirname(path)
        for target in LINK_RE.findall(open(path, encoding="utf-8").read()):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#")[0]
            if target and not os.path.exists(os.path.normpath(os.path.join(base, target))):
                link_problems.append(f"{os.path.relpath(path, ROOT)} -> {target}")
    stage("links", not link_problems, "; ".join(link_problems) or "all internal links resolve")

    # Stage 4 — bundled scripts compile + self-test
    script_problems = []
    scripts = []
    for s in skills:
        sdir = os.path.join(SKILLS_DIR, s, "scripts")
        if os.path.isdir(sdir):
            scripts += [os.path.join(sdir, f) for f in sorted(os.listdir(sdir))
                        if f.endswith(".py")]
    for script in scripts:
        rel = os.path.relpath(script, ROOT)
        try:
            compile(open(script, encoding="utf-8").read(), script, "exec")
        except SyntaxError as exc:
            script_problems.append(f"{rel}: syntax {exc}")
            continue
        proc = subprocess.run([sys.executable, script, "--selftest"],
                              capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            script_problems.append(f"{rel}: selftest exit {proc.returncode}: "
                                   f"{(proc.stdout + proc.stderr).strip()[:200]}")
    stage("scripts", not script_problems,
          "; ".join(script_problems) or f"{len(scripts)} scripts self-tested")

    # Stage 5 — README covers every skill
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    unnamed = [s for s in skills if s not in readme]
    stage("readme coverage", not unnamed, "unnamed: " + ", ".join(unnamed) if unnamed else "all skills named")

    print("OVERALL " + ("FAIL" if failures else "PASS"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
