#!/usr/bin/env python3
"""The issue tracker page: the Release 1 issues and pull requests as a
tracker table in the Matins form (id | work | required by | status | notes),
read live from GitHub through `gh api` when `gh` is authenticated, otherwise
from the committed snapshot, with a headline of the numbers the roadmap is
measured by. The progress page counts these rows with every other tracker's.

Every live fetch is written back to data/progress-snapshot.json with a
fetched_at timestamp so a build without `gh` reproduces the last one.

The project moved from Codeberg to GitHub on 2026-11-12 (ADR-008). The
issues keep their numbers; the Codeberg pull requests (#16, #17, #19, #21)
and Actions runs 1 to 11 did not move and are recorded here as history.
GitHub's own pull requests start at #19 again, so GitHub PR #19 (hosting),
#20 (planner) and #21 (target) are not the Codeberg PRs of the same number.

A requirement counts as implemented when a test carries at least one
`Verifies` tag for it and none carries a `Groundwork for` tag (the rule of the
rustinfer repository's docs/testing.md), the same derivation the requirements
page shows per id (common.requirement_states).
"""
import datetime
import re
import subprocess

from common import (EPIC, REPO, RUSTINFER, SEQUENCE, STD_AREAS, WEB, branch_of, commit, header,
                    issue_status, requirement_states, srs_requirements, standards,
                    state_counts, std_badge, std_release_counts, std_slug, test_tags,
                    tracker_state, write)

TODAY = datetime.date.today().isoformat()

# Coverage is taken from the final test run of PR #21's checklist, not measured here.
COVERAGE = ("96.44%", "the final test run of GitHub PR #21's merge-readiness checklist "
            "(`cargo llvm-cov --workspace --all-features`, after the rebase), 2026-11-12")

# Merged on Codeberg before the move; GitHub never saw them.
CODEBERG_PULLS = [
    {"number": 16, "title": "SRS v0.2 and ADR-001 to ADR-006", "head": "docs/1-srs-rustinfer",
     "base": "main", "merged_at": "2026-11-12"},
    {"number": 17, "title": "Project scaffold: workspace, core, CLI, CI, mandatory files (#2)",
     "head": "feat/2-project-scaffold", "base": "main", "merged_at": "2026-11-12"},
    {"number": 19, "title": "Model IR: typed graph, validator, canonical JSON (#3)",
     "head": "feat/3-model-ir", "base": "main", "merged_at": "2026-11-12"},
    {"number": 21, "title": "The .rie engine artifact, verifying reader and atomic writer (#4)",
     "head": "feat/4-artifact-format", "base": "main", "merged_at": "2026-11-12"},
]
source, state = tracker_state()


# ---------------------------------------------------------------- the tree
def remote_branches():
    if state.get("branches"):
        return state["branches"]
    try:
        out = subprocess.check_output(["git", "-C", str(RUSTINFER), "ls-remote", "--heads",
                                       f"git@github.com:{REPO}.git"],
                                      text=True, stderr=subprocess.DEVNULL, timeout=60)
        return [l.split("refs/heads/", 1)[1] for l in out.splitlines() if "refs/heads/" in l]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        return []


branches = remote_branches()
crates = sorted(p.parent.name for p in (RUSTINFER / "crates").glob("*/Cargo.toml"))
rs_files = list((RUSTINFER / "crates").rglob("*.rs"))
lines_rs = sum(len(p.read_text(encoding="utf-8", errors="replace").splitlines()) for p in rs_files)
tests = sum(len(re.findall(r"#\[test\]", p.read_text(encoding="utf-8", errors="replace"))) for p in rs_files)
reqs = srs_requirements()
by_status = {}
for q in reqs:
    by_status[q["status"]] = by_status.get(q["status"], 0) + 1
states = requirement_states(reqs, state, test_tags())
counts = state_counts(states)

# ------------------------------------------------------------- derivations
stds = standards()
std_rel = {r: std_release_counts(stds, r) for r in ("R1", "R2", "R3", "R4")}


def std_row(r):
    c = std_rel[r]
    later = f"; {c['later']} later release (not due yet)" if c["later"] else ""
    return (f"| Mandatory standards ({r}) | `{bar(c['works'], c['total'])}` | "
            f"{c['works']} works / {c['part']} partly / {c['gap']} missing{later}, of the {c['total']} "
            f"standards mandatory from {r} in SRS §1.4; the [standards map](standards.html), each one "
            f"[below](#standards) |")


issues = {i["number"]: i for i in state["issues"]}
pulls = state["pulls"]
pr_for_branch = {p["head"]: p for p in pulls}
codeberg_pr_for_branch = {p["head"]: p for p in CODEBERG_PULLS}
closed = [n for n in SEQUENCE if issues.get(n, {}).get("state") == "closed"]
implemented = counts["implemented"]


def status_of(n):
    return issue_status(state, n)


def open_blockers(n):
    return [b for b in issues.get(n, {}).get("blocked_by", []) if issues.get(b, {}).get("state") != "closed"]


# the item everything else waits on: the first open issue in sequence with no open blocker
blocking = next((n for n in SEQUENCE if issues.get(n, {}).get("state") != "closed" and not open_blockers(n)), None)


def bar(done, total, width=10):
    filled = round(width * done / total) if total else 0
    return "█" * filled + "░" * (width - filled) + f" {done}/{total}"


runs = state["runs"]
latest = runs[0] if runs else None
ci_text = (f"[run {latest['id']}]({latest['url']}) ({latest['ref']}, `{latest['sha']}`): **{latest['conclusion'] or latest['status']}**, "
           f"{latest['created'].replace('T', ' ')}") if latest else "no run recorded"
merged = sum(1 for p in pulls if p["merged"])
open_prs = sum(1 for p in pulls if p["state"] == "open")
milestone = next((m for m in state["milestones"] if m["title"].startswith("R1")), None)
where = "GitHub" if state.get("source") == "github" else "Codeberg"

# ------------------------------------------------------------------ page
out = header("Issue tracker", "Trackers", 1,
             "The Epic and the fourteen Release 1 issues and the pull requests on GitHub as a tracker: "
             "work, blockers, derived status and notes, with the numbers the roadmap is measured by.",
             script="gen_progress.py")
out += f"""# Issue tracker

**As of {TODAY}.** The tracker state is {f"read live from {where}" if source == "live" else f"the committed snapshot, taken from {where}"}
(fetched {state["fetched_at"][:16].replace("T", " ")} UTC, kept in `data/progress-snapshot.json`); the
counts of requirements, tests and lines are read from the rustinfer tree at commit {commit()}.
Coverage is not measured here: it is {COVERAGE[1]}. The [progress](progress.html) page counts the rows
below with every other tracker on the site; the [roadmap](roadmap.html) is the same sequence as prose.
The project moved from Codeberg to [github.com/itej89/rustinfer]({WEB}) on 2026-11-12 (ADR-008,
[decisions](decisions.html)); the issues kept their numbers, the Codeberg pull requests and Actions
runs did not move and are listed below as history.

## Headline

| measure | state | note |
|---|---|---|
| Release 1 issues closed | `{bar(len(closed), len(SEQUENCE))}` | #2 to #15; the Epic #1 is not counted. Milestone `{milestone["title"] if milestone else "—"}`: {milestone["closed"] if milestone else 0} closed, {milestone["open"] if milestone else 0} open |
| Pull requests on GitHub | {merged} merged, {open_prs} open | {", ".join(f"[#{p['number']}]({p.get('url', WEB + '/pull/' + str(p['number']))}) `{p['head']}` → `{p['base']}` ({'merged' if p['merged'] else p['state']})" for p in pulls) or "none yet"}; four more were merged on Codeberg before the move, see below |
| Latest CI run | {ci_text} | GitHub Actions on `ubuntu-latest`; the recent runs are listed below |
| SRS requirements implemented | `{bar(implemented, len(reqs))}` | by the tag rule of `docs/testing.md`: a requirement is implemented when a test carries a `Verifies` tag for it and no test a `Groundwork for` tag; {counts["implemented"]} implemented, {counts["partial"]} partial (a `Groundwork for` tag), {counts["reserved only"]} reserved only (only `Reserved` tags), {counts["planned"]} planned; by release: {"; ".join(f"{r} {c['implemented']}/{c['partial']}/{c['reserved only']}/{c['planned']} of {c['total']}" for r, c in ((r, state_counts(states, r)) for r in ("R1", "R2", "R3", "R4")))} (implemented/partial/reserved only/planned); the tags and files per id are on the [requirements](ref-requirements.html) page. The SRS's own status field changes only at a release, so by SRS status today: {", ".join(f"{k} {v}" for k, v in sorted(by_status.items()))} |
{chr(10).join(std_row(r) for r in ("R1", "R2", "R3", "R4") if std_rel[r]["total"])}
| Tests | {tests} | `#[test]` functions across {len(crates)} crates |
| Line coverage | {COVERAGE[0]} | from {COVERAGE[1]}; the CI gate is 80 percent |
| Rust | {lines_rs:,} lines in {len(rs_files)} files | `crates/**/*.rs`, tests and build scripts included |

## Standards

Every standard SRS §1.4 marks mandatory, from its record in `data/standards/` and its
tracker: the state its audit found, the gaps open (status *Open* or *In PR #N*) and all
its gaps, which include those recorded for a later release, never counted as open. A standard mandatory
from a later release shows no state badge until that release is current. The map, with
what the states mean, is [Standards](standards.html).

| standard | area | conformance | state | open gaps | all gaps | tracker |
|---|---|---|---|---|---|---|
{chr(10).join(f"| [{d['name']}]({std_slug(d['id'])}.html) {d['version']} | {d['area']} | {d['conformance']} | {std_badge(d)} | {d['gaps_open']} | {d['gaps_total']} | [tracker]({std_slug(d['id'])}-tracker.html) |" for d in sorted(stds, key=lambda d: (d['release'], STD_AREAS.index(d['area']), d['name'].lower())))}

## Release 1 issues

The ids are `R1-n` for [GitHub issue]({WEB}/issues) #n. The status is derived, not typed: **Done** with its
date when the issue is closed; **In review** with the date its pull request opened; **In
progress** when its branch exists on GitHub; otherwise **Not started**, with `waits on #n` for
each blocker still open. The bold **Open** marks the item everything else waits on: the first
open issue in dependency order whose blockers are all closed. Bodies are drafted in
`docs/planning/issues/` in the tree.

| id | work | required by | status | notes |
|---|---|---|---|---|
"""
for n in SEQUENCE:
    i = issues.get(n, {"title": "?", "state": "?", "blocked_by": []})
    blockers = ", ".join(f"#{b}" for b in i["blocked_by"]) or "—"
    st = status_of(n)
    waits = open_blockers(n)
    cell = f"**{st}**" if n == blocking and not st.startswith("Done") else st
    if waits and not st.startswith("Done"):
        cell += "; waits on " + ", ".join(f"#{b}" for b in waits)
    b = branch_of(state, n)
    notes = []
    if b:
        notes.append(f"branch `{b}`")
    if b and b in pr_for_branch:
        p = pr_for_branch[b]
        notes.append(f"[PR #{p['number']}]({p.get('url', WEB + '/pull/' + str(p['number']))}) → `{p['base']}`, opened {p['created_at']}, "
                     f"{'merged ' + p['merged_at'] if p['merged'] else p['state']}"
                     + ("" if p["mergeable"] else ", not mergeable as it stands"))
    cb = next((p for p in CODEBERG_PULLS if p["title"].endswith(f"(#{n})")), None)
    if cb:
        notes.append(f"Codeberg PR #{cb['number']} `{cb['head']}` merged {cb['merged_at']}, before the move (not GitHub PR #{cb['number']})")
    if n == 7:
        notes.append("writes ADR-007 (OI-009); needs a self-hosted runner for LLVM")
    if n in (9, 12):
        notes.append("needs an MI300X or MI355X on the bench (OI-008)")
    if n == 14:
        notes.append("closes the Epic's acceptance criteria")
    title = f"[{i['title']}]({WEB}/issues/{n})" if n in issues else i["title"]
    out += f"| R1-{n} | {title} | {blockers} | {cell} | {'; '.join(notes) or '—'} |\n"

e = issues.get(EPIC, {})
out += f"""
The Epic [#{EPIC}]({WEB}/issues/{EPIC}) is `{e.get("state", "?")}` with labels {", ".join(f"`{l}`" for l in e.get("labels", [])) or "none"}; it closes with R1-14.

## Pull requests

GitHub's pull requests, then the four merged on Codeberg before the move. The Codeberg numbers
are history: they are not GitHub pull requests, and GitHub's own numbering restarted after the
eighteen issues it holds, so GitHub PR #19 (hosting), #20 (planner) and #21 (target) share
their numbers with Codeberg PR #19 (Model IR) and #21 (artifact) and are different pull requests.

| id | work | required by | status | notes |
|---|---|---|---|---|
"""
for p in pulls:
    if p["merged"]:
        st = f"Merged {p['merged_at']}"
    elif p["state"] == "open":
        st = f"In review {p['created_at']}"
    else:
        st = f"Closed {p['state']}"
    base_pr = next((q for q in pulls if q["head"] == p["base"]), None)
    req = f"PR-{base_pr['number']} merged first (stacked)" if base_pr else "a reviewer's sign-off"
    notes = (f"`{p['head']}` → `{p['base']}`; {'mergeable' if p['mergeable'] else 'not mergeable as it stands'}"
             + ("; only the owner can approve the SRS" if p["head"].startswith("docs/1-") else ""))
    out += f"| PR-{p['number']} | [{p['title']}]({p.get('url', WEB + '/pull/' + str(p['number']))}) | {req} | {st} | {notes} |\n"
for p in CODEBERG_PULLS:
    out += (f"| PR-{p['number']} | {p['title']} | a reviewer's sign-off | Merged {p['merged_at']} | "
            f"`{p['head']}` → `{p['base']}`; merged on Codeberg before the move; the branch did not move |\n")

out += f"""
## CI runs

The most recent runs of `ci.yml` on GitHub Actions, newest first. `queued` means waiting for a
hosted runner. GitHub's run numbers restart at 1: the Codeberg history, runs 1 and 2 of
2026-11-11 cancelled unanswered (`ubuntu-latest`, a label Codeberg never served), runs 3 to 6
each failing on one Codeberg-specific rule recorded in ADR-004, run 7 the first green run, runs 8
to 11 green on Codeberg PRs #17 and #19 and `main`, did not move and is gone with the Codeberg repository
([build steps](build-steps.html)).

| run | for | commit | event | state | when |
|---|---|---|---|---|---|
"""
for r in runs:
    out += (f"| [{r['id']}]({r['url']}) | {r['ref'] or '—'} | `{r['sha'] or '—'}` | {r['event']} | "
            f"**{r['conclusion'] or r['status']}** | {r['created'].replace('T', ' ')} |\n")

out += f"""
## Branches on GitHub

| branch | holds |
|---|---|
"""
HOLDS = {"main": "the approved SRS v0.2, ADR-001 to ADR-006 and ADR-008, the fourteen-crate workspace, the Model IR, the artifact crate, the planner interfaces and the target abstraction with the CPU reference (Codeberg PRs #16, #17, #19, #21; GitHub PRs #19, #20, #21)",
         "feat/3-model-ir": "the Model IR crate `rustinfer-mir`, merged as Codeberg PR #19",
         "feat/4-artifact-format": "the `.rie` artifact crate `rustinfer-artifact`, merged as Codeberg PR #21",
         "infra/github-hosting": "ADR-008 and the CI retarget to GitHub, merged as GitHub PR #19 (9d448ce)",
         "feat/15-planner-interfaces": "the planner's topology model, placement and `Planner` trait (#15), merged as GitHub PR #20 (d886a3c)",
         "feat/5-target-and-cpu-reference": "the `Target` trait family, the registry and the CPU reference target (#5), merged as GitHub PR #21 (f039b4d)",
         "feat/18-sluice": "Sluice, the weight streamer (#18), in progress",
         "feat/6-llama-frontend": "the LLaMA frontend (#6), in progress",
         "feat/7-kernel-ir-mlir-link": "the Kernel IR dialect and the MLIR link (#7), in progress",
         "docs/readme-docs-link": "the README's link to this site, GitHub PR #22",
         "docs/1-srs-rustinfer": "the SRS, ADR-001 to ADR-006, planning documents, issue drafts",
         "feat/2-project-scaffold": "the workspace, core, command, CI, mandatory files; rebased on the docs branch"}
for b in branches:
    out += f"| [`{b}`]({WEB}/tree/{b}) | {HOLDS.get(b, 'see its issue')} |\n"
write("issues.md", out)
