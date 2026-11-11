#!/usr/bin/env python3
"""Every requirement in docs/SRS-RI-v0.1.md: id, text, priority, status and
release, grouped by component in the SRS's own order."""
import re

from common import RUSTINFER, commit, header, write

SRS = RUSTINFER / "docs/SRS-RI-v0.1.md"
text = SRS.read_text(encoding="utf-8")

# Components appear as "#### 3.2.N Name (`RI-XXX`)" and "#### 3.3.N Name".
sections = re.split(r"^#### ", text, flags=re.M)[1:]
groups = []
for sec in sections:
    title_line, _, body = sec.partition("\n")
    title = re.sub(r"\s*\(`RI-[A-Z]+`\)\s*$", "", title_line.strip())
    reqs = []
    for m in re.finditer(
        r"^(RI-[A-Z]+-\d{3})\s+(.*?)\nPriority:\s*(\w+)\s+Status:\s*(\w+)\s+Release:\s*([^\n]*)"
        r"(?:\nRationale:\s*([^\n]*))?",
        body, re.S | re.M):
        rid, rtext, prio, status, release, rationale = m.groups()
        rtext = " ".join(line.strip() for line in rtext.splitlines())
        reqs.append((rid, rtext, prio, status, release.strip(), (rationale or "").strip()))
    if reqs:
        groups.append((title, reqs))

total = sum(len(r) for _, r in groups)
by_release = {}
for _, reqs in groups:
    for _, _, _, _, release, _ in reqs:
        first = re.match(r"R\d", release)
        key = first.group(0) if first else "unspecified"
        by_release[key] = by_release.get(key, 0) + 1

out = header("Requirements", "Reference", 1,
             "Every requirement of SRS-RI-v0.1 with its priority, status and release, "
             "generated from the SRS in the tree.",
             navtitle="Requirements (SRS)", script="gen_srs.py")
# one tracker card per component on the progress page
out = out.replace("---\n<!--", "cards: headings\n---\n<!--", 1)
out += f"""# Requirements

Generated from `docs/SRS-RI-v0.1.md` at commit {commit()}. {total} requirements
in {len(groups)} groups, every one at status *Draft* until the SRS is approved
(the SRS header says so). The *release* column is the first release named; where
a requirement is split across releases the full text is kept.

By first release: {", ".join(f"{k} {v}" for k, v in sorted(by_release.items()))}.
Each component is one tracker table; the [progress](progress.html) page counts a *Draft*
requirement as open work and an *Implemented* one as done.

"""
for title, reqs in groups:
    out += f"## {title}\n\n| id | text | priority | status | release |\n|---|---|---|---|---|\n"
    for rid, rtext, prio, status, release, rationale in reqs:
        cell = rtext.replace("|", " or ")
        if rationale:
            cell += f" *Rationale: {rationale.replace('|', ' or ')}*"
        out += f"| {rid} | {cell} | {prio} | {status} | {release.replace('|', ' or ')} |\n"
    out += "\n"
write("ref-requirements.md", out)
