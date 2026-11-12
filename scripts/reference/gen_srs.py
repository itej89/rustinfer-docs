#!/usr/bin/env python3
"""Every requirement in docs/SRS-RI-v0.1.md: id, text, priority, release and
the implementation state the site derives for it, next to the SRS's own
status field, grouped by component in the SRS's own order.

The SRS's status field is *Draft* for every requirement until a release
revises the document, so it says nothing about what the tree holds. The
state column is derived instead (common.requirement_states): *implemented*
when a test in the tree cites the id or the Epic's checklist assigns it to a
closed issue, *in progress* when its issue has a branch or an open pull
request, *planned* otherwise. The issues page computes its headline from
the same function."""
from common import (WEB, badge, commit, header, requirement_states, srs_meta,
                    srs_requirements, state_counts, test_citations, tracker_state, write)

reqs = srs_requirements()
doc_version, doc_status = srs_meta()
source, state = tracker_state()
citations = test_citations()
states = requirement_states(reqs, state, citations)
counts = state_counts(states)
groups = []
for r in reqs:
    if not groups or groups[-1][0] != r["group"]:
        groups.append((r["group"], []))
    groups[-1][1].append(r)

TAGS = ["R1", "R2", "R3", "R4"]
if any(r["tag"] == "unspecified" for r in reqs):
    TAGS.append("unspecified")


def per_release(tag):
    ids = [r["id"] for r in reqs if r["tag"] == tag]
    return (len(ids), sum(1 for i in ids if states[i]["state"] == "implemented"),
            sum(1 for i in ids if states[i]["state"] == "partial"),
            sum(1 for i in ids if states[i]["state"] == "in progress"),
            sum(1 for i in ids if states[i]["state"] == "planned"))


by_status = {}
for r in reqs:
    by_status[r["status"]] = by_status.get(r["status"], 0) + 1
closed_issues = sorted({n for v in states.values() for n in v["closed_issues"]})
reserved_only = sum(1 for v in states.values() if v["reserved"] and not v["tests"])


def issue_link(n):
    return f"[#{n}]({WEB}/issues/{n})"


def evidence(info):
    parts = []
    if info["tests"]:
        parts.append("tests: " + ", ".join(
            f"[`{f}`]({WEB}/blob/main/crates/{f})" for f in info["tests"]))
    if info["reserved"]:
        parts.append("cited by a reserved-feature test: " + ", ".join(
            f"[`{f}`]({WEB}/blob/main/crates/{f})" for f in info["reserved"]))
    if info["closed_issues"]:
        parts.append("Epic: closed " + ", ".join(issue_link(n) for n in info["closed_issues"]))
    if info["open_issues"]:
        parts.append("Epic: open " + ", ".join(
            f"{issue_link(n)} ({st.lower()})" for n, st in info["open_issues"]))
    return "; ".join(parts) or "—"


def state_cell(info):
    cell = badge(info)
    if info["state"] == "implemented":
        cell += " — by " + " and ".join(info["sources"])
        if info["disagree"]:
            cell += f" only; {info['disagree']}"
    elif info["state"] == "partial":
        cell += (" — plain citations in " + ", ".join(f"`{f}`" for f in info["tests"])
                 + "; reserved-feature citations in " + ", ".join(f"`{f}`" for f in info["reserved"])
                 + (f"; Epic: closed " + ", ".join(f"#{n}" for n in info["closed_issues"]) if info["closed_issues"] else ""))
    elif info["state"] == "in progress":
        cell += " — " + ", ".join(f"#{n} {st.lower()}" for n, st in info["open_issues"])
    elif info["reserved"]:
        cell += " — cited by a reserved-feature test: " + ", ".join(f"`{f}`" for f in info["reserved"])
    return cell


out = header("Requirements", "Reference", 1,
             "Every requirement of SRS-RI-v0.1 with its priority, release, the implementation "
             "state derived from the tests and the tracker, and the SRS's own status field.",
             navtitle="Requirements (SRS)", script="gen_srs.py")
# one tracker card per component on the progress page
out = out.replace("---\n<!--", "cards: headings\n---\n<!--", 1)
out += f"""# Requirements

Generated from `docs/SRS-RI-v0.1.md` at commit {commit()}: document version
{doc_version}, status *{doc_status}* (the SRS header says so). {len(reqs)} requirements
in {len(groups)} groups. The *state* column is derived from the tree and the tracker
(below); the *SRS status* column is the document's own field. The *release* column is
the first release named; where a requirement is split across releases the full text is kept.

## Headline

**{counts["implemented"]} implemented, {counts["partial"]} implemented in part, {counts["in_progress"]} in progress,
{counts["planned"]} planned** of {len(reqs)}. Implemented by a test that cites the id: {counts["by_tests"]}
({counts["partial"]} ids with both plain and reserved-feature citations are *implemented in part* and not
counted here; {reserved_only} ids cited only by reserved-feature tests stay planned); by the Epic's checklist
assigning it to a closed issue ({", ".join(issue_link(n) for n in closed_issues) or "none"}):
{counts["by_epic"]}; by both: {counts["both"]}. The two sources disagree on
{len(counts["disagree"])} ids (a test cites them but the Epic assigns them to an open issue or to
none; each row says so): {", ".join(counts["disagree"]) or "none"}.

| release | requirements | implemented | implemented in part | in progress | planned |
|---|---|---|---|---|---|
"""
for tag in TAGS:
    n, done, part, prog, plan = per_release(tag)
    out += f"| {tag} | {n} | {done} | {part} | {prog} | {plan} |\n"
out += f"| all | {len(reqs)} | {counts['implemented']} | {counts['partial']} | {counts['in_progress']} | {counts['planned']} |\n"

out += f"""
**How the state is derived.** A requirement is <span class="state-ok">implemented</span> when a test
on `main` cites its id in a comment (the integration tests under `crates/*/tests` and the
`#[cfg(test)]` modules under `crates/*/src`, matched as a whole token; the files are linked in the
*evidence* column; a comment that says the feature is reserved, not implemented, refused as R2 or
R3, or of a later release cites the id without implementing it, and such a file is noted, not counted).
An id cited plainly in some test files and as a reserved feature in others is
<span class="state-part">implemented in part</span>, with both lists, counted on its own and not as implemented. It or when the Epic [#1]({WEB}/issues/1) checklist assigns it to an issue that is
closed; the row says which of the two applies, and when only one does, what the other says.
A requirement is <span class="state-part">in progress</span> when its issue is open and has a branch on GitHub or an
open pull request, and <span class="state-no">planned</span> otherwise, with its release tag. The
SRS's own status field, in the *SRS status* column, changes only when a release revises the
document, so it is *Draft* for every requirement today (by SRS status: {", ".join(f"{k} {v}" for k, v in sorted(by_status.items()))})
and is not what the [progress](progress.html) page counts: that page reads the *state* column of each
component table below, implemented as done, implemented in part and in progress as progress, planned as later. The tracker
state is {"read live from GitHub" if source == "live" else "the committed snapshot"}
(`data/progress-snapshot.json`, fetched {state["fetched_at"][:16].replace("T", " ")} UTC); the
[issues](issues.html) page computes its *SRS requirements implemented* headline from the same code.

"""
for title, rs in groups:
    out += (f"## {title}\n\n| id | text | priority | release | state | SRS status | evidence |\n"
            f"|---|---|---|---|---|---|---|\n")
    for r in rs:
        cell = r["text"].replace("|", " or ")
        if r["rationale"]:
            cell += f" *Rationale: {r['rationale'].replace('|', ' or ')}*"
        info = states[r["id"]]
        out += (f"| {r['id']} | {cell} | {r['priority']} | {r['release'].replace('|', ' or ')} | "
                f"{state_cell(info)} | {r['status']} | {evidence(info)} |\n")
    out += "\n"
write("ref-requirements.md", out)
