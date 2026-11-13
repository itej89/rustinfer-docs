#!/usr/bin/env python3
"""Every requirement in docs/SRS-RI-v0.1.md: id, text, priority, release and
the implementation state the site derives for it, next to the SRS's own
status field, grouped by component in the SRS's own order.

The SRS's status field is *Draft* for every requirement until a release
revises the document, so it says nothing about what the tree holds. The
state column is derived instead (common.requirement_states) from the tags
the tests carry, by the rule of the rustinfer repository's docs/testing.md:
*implemented* with at least one `Verifies` tag and no `Groundwork for` tag,
*partial* with any `Groundwork for` tag, *reserved only* with only `Reserved`
tags, *planned* otherwise. The issues page computes its headline from the
same function."""
from common import (WEB, badge, commit, header, requirement_states, srs_meta,
                    srs_requirements, state_counts, test_tags, tracker_state, write)

reqs = srs_requirements()
doc_version, doc_status = srs_meta()
source, state = tracker_state()
states = requirement_states(reqs, state, test_tags())
counts = state_counts(states)
groups = []
for r in reqs:
    if not groups or groups[-1][0] != r["group"]:
        groups.append((r["group"], []))
    groups[-1][1].append(r)

TAGS = ["R1", "R2", "R3", "R4"]
if any(r["tag"] == "unspecified" for r in reqs):
    TAGS.append("unspecified")

by_status = {}
for r in reqs:
    by_status[r["status"]] = by_status.get(r["status"], 0) + 1
tag_total = {k: sum(v["counts"][k] for v in states.values()) for k in ("verifies", "groundwork", "reserved")}
covered_by_closed = [k for k, v in states.items() if v["closed_issues"]]
closed_not_impl = [k for k in covered_by_closed if states[k]["state"] != "implemented"]


def issue_link(n):
    return f"[#{n}]({WEB}/issues/{n})"


def file_list(files):
    return ", ".join(f"[`{f}`]({WEB}/blob/main/crates/{f})" + (f" ×{n}" if n > 1 else "")
                     for f, n in sorted(files.items()))


def tags_cell(info):
    c = info["counts"]
    return f"{c['verifies']} / {c['groundwork']} / {c['reserved']}"


def evidence(info):
    parts = []
    for kind, word in (("verifies", "Verifies"), ("groundwork", "Groundwork for"), ("reserved", "Reserved")):
        if info[kind]:
            parts.append(f"{word}: " + file_list(info[kind]))
    if info["closed_issues"]:
        parts.append("Epic: closed " + ", ".join(issue_link(n) for n in info["closed_issues"]))
    if info["open_issues"]:
        parts.append("Epic: open " + ", ".join(
            f"{issue_link(n)} ({st.lower()})" for n, st in info["open_issues"]))
    return "; ".join(parts) or "—"


out = header("Requirements", "Reference", 1,
             "Every requirement of SRS-RI-v0.1 with its priority, release, the implementation "
             "state derived from the test tags, and the SRS's own status field.",
             navtitle="Requirements (SRS)", script="gen_srs.py")
# one tracker card per component on the progress page
out = out.replace("---\n<!--", "cards: headings\n---\n<!--", 1)
out += f"""# Requirements

Generated from `docs/SRS-RI-v0.1.md` at commit {commit()}: document version
{doc_version}, status *{doc_status}* (the SRS header says so). {len(reqs)} requirements
in {len(groups)} groups. The *state* column is derived from the tags the tests carry
(below); the *SRS status* column is the document's own field. The *release* column is
the first release named; where a requirement is split across releases the full text is kept.

## Headline

**{counts["implemented"]} implemented, {counts["partial"]} partial, {counts["reserved only"]} reserved only,
{counts["planned"]} planned** of {len(reqs)}. The tests on `main` carry {tag_total["verifies"]} `Verifies`,
{tag_total["groundwork"]} `Groundwork for` and {tag_total["reserved"]} `Reserved` tags.

| release | requirements | implemented | partial | reserved only | planned |
|---|---|---|---|---|---|
"""
for tag in TAGS:
    c = state_counts(states, tag)
    out += (f"| {tag} | {c['total']} | {c['implemented']} | {c['partial']} | "
            f"{c['reserved only']} | {c['planned']} |\n")
out += (f"| all | {len(reqs)} | {counts['implemented']} | {counts['partial']} | "
        f"{counts['reserved only']} | {counts['planned']} |\n")

out += f"""
**How the state is derived.** By the tag rule of the rustinfer repository's
[`docs/testing.md`]({WEB}/blob/main/docs/testing.md) (set in [#27]({WEB}/issues/27)), a test
cites a requirement in its doc comment with exactly one of three tags: `Verifies RI-X-NNN: <part>`
only when the clause is fully implemented in the code, `Groundwork for RI-X-NNN: <part>` while it
is not, and `Reserved RI-X-NNN (R<n>)` for a test asserting a later-release refusal. A requirement is
<span class="state-ok">implemented</span> when it has at least one `Verifies` tag and no
`Groundwork for` tag; <span class="state-part">partial</span> when it has any `Groundwork for` tag;
<span class="state-no">reserved only</span> when it has only `Reserved` tags; and
<span class="state-no">planned</span> otherwise, with its release. The tags are read from the comments
of the integration tests under `crates/*/tests` and the `#[cfg(test)]` modules under `crates/*/src`;
an id mentioned without a tag word (prose, a `//!` module header) never counts. The *tags* column gives
the counts as Verifies / Groundwork for / Reserved and the *evidence* column the files, with the count
per file where it is more than one.

The Epic [#1]({WEB}/issues/1) checklist's assignment of an id to an issue is shown in the evidence
column as information and does not change the state: {len(covered_by_closed)} ids are assigned to a
closed issue, and {len(closed_not_impl)} of them are not implemented by the tag rule
({", ".join(closed_not_impl) or "none"}). The SRS's own status field, in the *SRS status* column,
changes only when a release revises the document, so it is *Draft* for every requirement today
(by SRS status: {", ".join(f"{k} {v}" for k, v in sorted(by_status.items()))}) and is not what the
[progress](progress.html) page counts: that page reads the *state* column of each component table
below, implemented as done, partial as progress, reserved only and planned as later. The tracker
state is {"read live from GitHub" if source == "live" else "the committed snapshot"}
(`data/progress-snapshot.json`, fetched {state["fetched_at"][:16].replace("T", " ")} UTC); the
[issues](issues.html) page computes its *SRS requirements implemented* headline from the same code.

"""
for title, rs in groups:
    out += (f"## {title}\n\n| id | text | priority | release | state | tags | SRS status | evidence |\n"
            f"|---|---|---|---|---|---|---|---|\n")
    for r in rs:
        cell = r["text"].replace("|", " or ")
        if r["rationale"]:
            cell += f" *Rationale: {r['rationale'].replace('|', ' or ')}*"
        info = states[r["id"]]
        out += (f"| {r['id']} | {cell} | {r['priority']} | {r['release'].replace('|', ' or ')} | "
                f"{badge(info)} | {tags_cell(info)} | {r['status']} | {evidence(info)} |\n")
    out += "\n"
write("ref-requirements.md", out)
