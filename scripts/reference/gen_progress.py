#!/usr/bin/env python3
"""The issue tracker page: the Release 1 issues and pull requests as a
tracker table in the Matins form (id | work | required by | status | notes),
read live from Codeberg when a token is present, otherwise from the
committed snapshot, with a headline of the numbers the roadmap is measured
by. The progress page counts these rows with every other tracker's.

The token at ~/.ssh/rustinfer.token goes only into the Authorization header.
Every live fetch is written back to data/progress-snapshot.json with a
fetched_at timestamp so a build without the token reproduces the last one.
"""
import datetime
import json
import pathlib
import re
import subprocess
import urllib.error
import urllib.request

from common import RUSTINFER, SITE, commit, header, write

API = "https://codeberg.org/api/v1/repos/itej89/rustinfer"
TOKEN_FILE = pathlib.Path.home() / ".ssh" / "rustinfer.token"
SNAPSHOT = SITE / "data" / "progress-snapshot.json"
TODAY = datetime.date.today().isoformat()

# Coverage is taken from the merge-readiness checklist of PR #17, not measured here.
COVERAGE = ("89.15%", "the coverage block of PR #17's merge-readiness checklist "
            "(`cargo llvm-cov --workspace --all-features`), 2026-11-11")
EPIC = 1
SEQUENCE = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # the Epic's order


# ----------------------------------------------------------------- Codeberg
def fetch(path, token):
    req = urllib.request.Request(API + path, headers={"Authorization": "token " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def live_state():
    if not TOKEN_FILE.exists():
        return None
    token = TOKEN_FILE.read_text().strip()
    try:
        issues = fetch("/issues?state=all&type=issues&limit=50", token)
        pulls = fetch("/pulls?state=all", token)
        milestones = fetch("/milestones?state=all", token)
        runs = fetch("/actions/runs?limit=5", token).get("workflow_runs", [])
        deps = {i["number"]: [d["number"] for d in fetch(f"/issues/{i['number']}/dependencies", token)]
                for i in issues}
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None
    return {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "issues": [{"number": i["number"], "title": i["title"], "state": i["state"],
                    "closed_at": (i.get("closed_at") or "")[:10],
                    "labels": [l["name"] for l in i["labels"]],
                    "milestone": (i.get("milestone") or {}).get("title"),
                    "blocked_by": sorted(deps.get(i["number"], []))}
                   for i in sorted(issues, key=lambda x: x["number"])],
        "pulls": [{"number": p["number"], "title": p["title"], "state": p["state"],
                   "head": p["head"]["ref"], "base": p["base"]["ref"],
                   "merged": p["merged"], "merged_at": (p.get("merged_at") or "")[:10],
                   "mergeable": p["mergeable"], "created_at": p["created_at"][:10]}
                  for p in sorted(pulls, key=lambda x: x["number"])],
        "milestones": [{"title": m["title"], "state": m["state"],
                        "open": m["open_issues"], "closed": m["closed_issues"]} for m in milestones],
        "runs": [{"id": r["id"], "title": r.get("title"), "status": r.get("status"),
                  "conclusion": r.get("conclusion"), "event": r.get("event"),
                  "ref": r.get("prettyref"), "sha": (r.get("commit_sha") or "")[:7],
                  "created": (r.get("created") or "")[:16], "url": r.get("html_url")}
                 for r in runs],
    }


state = live_state()
source = "live"
if state:
    SNAPSHOT.parent.mkdir(exist_ok=True)
    SNAPSHOT.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
else:
    state = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    source = "snapshot"


# ---------------------------------------------------------------- the tree
def remote_branches():
    try:
        out = subprocess.check_output(["git", "-C", str(RUSTINFER), "ls-remote", "--heads", "origin"],
                                      text=True, stderr=subprocess.DEVNULL)
        return [l.split("refs/heads/", 1)[1] for l in out.splitlines() if "refs/heads/" in l]
    except (subprocess.CalledProcessError, OSError):
        return []


branches = remote_branches()
crates = sorted(p.parent.name for p in (RUSTINFER / "crates").glob("*/Cargo.toml"))
rs_files = list((RUSTINFER / "crates").rglob("*.rs"))
lines_rs = sum(len(p.read_text(encoding="utf-8", errors="replace").splitlines()) for p in rs_files)
tests = sum(len(re.findall(r"#\[test\]", p.read_text(encoding="utf-8", errors="replace"))) for p in rs_files)
srs = (RUSTINFER / "docs/SRS-RI-v0.1.md").read_text(encoding="utf-8")
reqs = re.findall(r"^(RI-[A-Z]+-\d{3})\s.*?\nPriority:\s*\w+\s+Status:\s*(\w+)\s+Release:\s*(R\d)",
                  srs, re.S | re.M)
by_release = {r: sum(1 for q in reqs if q[2] == r) for r in ("R1", "R2", "R3", "R4")}
by_status = {}
for _, st, _ in reqs:
    by_status[st] = by_status.get(st, 0) + 1

# ------------------------------------------------------------- derivations
issues = {i["number"]: i for i in state["issues"]}
pulls = state["pulls"]
pr_for_branch = {p["head"]: p for p in pulls}
closed = [n for n in SEQUENCE if issues.get(n, {}).get("state") == "closed"]
implemented = 0  # a requirement is implemented when its issue is closed; none is


def branch_of(n):
    return next((b for b in branches if re.match(rf"(feat|fix|docs|refactor|ci|chore)/{n}-", b)), None)


def status_of(n):
    i = issues.get(n)
    if not i:
        return "Not started"
    if i["state"] == "closed":
        return f"Done {i['closed_at']}".strip()
    b = branch_of(n)
    if b and b in pr_for_branch and pr_for_branch[b]["state"] == "open":
        return f"In review {pr_for_branch[b]['created_at']}"
    if b:
        return "In progress"
    return "Not started"


def open_blockers(n):
    return [b for b in issues.get(n, {}).get("blocked_by", []) if issues.get(b, {}).get("state") != "closed"]


# the item everything else waits on: the first open issue in sequence with no open blocker
blocking = next((n for n in SEQUENCE if issues.get(n, {}).get("state") != "closed" and not open_blockers(n)), None)


def bar(done, total, width=10):
    filled = round(width * done / total) if total else 0
    return "█" * filled + "░" * (width - filled) + f" {done}/{total}"


runs = state["runs"]
latest = runs[0] if runs else None
ci_text = (f"run {latest['id']} ({latest['ref']}, `{latest['sha']}`): **{latest['conclusion'] or latest['status']}**, "
           f"{latest['created'].replace('T', ' ')}") if latest else "no run recorded"
merged = sum(1 for p in pulls if p["merged"])
open_prs = sum(1 for p in pulls if p["state"] == "open")
milestone = next((m for m in state["milestones"] if m["title"].startswith("R1")), None)

# ------------------------------------------------------------------ page
out = header("Issue tracker", "Trackers", 1,
             "The Epic and the fourteen Release 1 issues and the pull requests on Codeberg as a tracker: "
             "work, blockers, derived status and notes, with the numbers the roadmap is measured by.",
             script="gen_progress.py")
out += f"""# Issue tracker

**As of {TODAY}.** The tracker state is {"read live from Codeberg" if source == "live" else "the committed snapshot"}
(fetched {state["fetched_at"][:16].replace("T", " ")} UTC, kept in `data/progress-snapshot.json`); the
counts of requirements, tests and lines are read from the rustinfer tree at commit {commit()}.
Coverage is not measured here: it is {COVERAGE[1]}. The [progress](progress.html) page counts the rows
below with every other tracker on the site; the [roadmap](roadmap.html) is the same sequence as prose.

## Headline

| measure | state | note |
|---|---|---|
| Release 1 issues closed | `{bar(len(closed), len(SEQUENCE))}` | #2 to #15; the Epic #1 is not counted. Milestone `{milestone["title"] if milestone else "—"}`: {milestone["closed"] if milestone else 0} closed, {milestone["open"] if milestone else 0} open |
| Pull requests | {merged} merged, {open_prs} open | {", ".join(f"#{p['number']} `{p['head']}` → `{p['base']}` ({'merged' if p['merged'] else p['state']})" for p in pulls) or "none"} |
| Latest CI run | {ci_text} | Forgejo Actions on Codeberg; the recent runs are listed below |
| SRS requirements implemented | `{bar(implemented, len(reqs))}` | a requirement is implemented when the issue that carries it is closed; by SRS status today: {", ".join(f"{k} {v}" for k, v in sorted(by_status.items()))}; by release: {", ".join(f"{k} {v}" for k, v in by_release.items())} |
| Tests | {tests} | `#[test]` functions across {len(crates)} crates |
| Line coverage | {COVERAGE[0]} | from {COVERAGE[1]}; the CI gate is 80 percent |
| Rust | {lines_rs:,} lines in {len(rs_files)} files | `crates/**/*.rs`, tests and build scripts included |

## Release 1 issues

The ids are `R1-n` for Codeberg issue #n. The status is derived, not typed: **Done** with its
date when the issue is closed; **In review** with the date its pull request opened; **In
progress** when its branch exists on `origin`; otherwise **Not started**, with `waits on #n` for
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
    b = branch_of(n)
    notes = []
    if b:
        notes.append(f"branch `{b}`")
    if b and b in pr_for_branch:
        p = pr_for_branch[b]
        notes.append(f"PR #{p['number']} → `{p['base']}`, opened {p['created_at']}, "
                     f"{'merged ' + p['merged_at'] if p['merged'] else p['state']}"
                     + ("" if p["mergeable"] else ", not mergeable as it stands"))
    if n == 7:
        notes.append("writes ADR-007 (OI-009); needs a self-hosted runner for LLVM")
    if n in (9, 12):
        notes.append("needs an MI300X or MI355X on the bench (OI-008)")
    if n == 14:
        notes.append("closes the Epic's acceptance criteria")
    out += f"| R1-{n} | {i['title']} | {blockers} | {cell} | {'; '.join(notes) or '—'} |\n"

e = issues.get(EPIC, {})
out += f"""
The Epic #{EPIC} is `{e.get("state", "?")}` with labels {", ".join(f"`{l}`" for l in e.get("labels", []))}; it closes with R1-14.

## Pull requests

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
             + ("; only the owner can approve the SRS" if p["base"] == "main" else ""))
    out += f"| PR-{p['number']} | {p['title']} | {req} | {st} | {notes} |\n"

out += """
## CI runs

The most recent runs of `ci.yml`, newest first. `waiting` means queued for a runner; the two
cancelled runs of 2026-11-11 were the jobs that asked for `ubuntu-latest`, a label Codeberg's
hosted runners never answer, before CI was retargeted to `codeberg-medium` (ADR-004).

| run | for | commit | event | state | when |
|---|---|---|---|---|---|
"""
for r in runs:
    out += (f"| [{r['id']}]({r['url']}) | {r['ref'] or '—'} | `{r['sha'] or '—'}` | {r['event']} | "
            f"**{r['conclusion'] or r['status']}** | {r['created'].replace('T', ' ')} |\n")

out += """
## Branches on Codeberg

| branch | holds |
|---|---|
"""
HOLDS = {"main": "the skeleton commit",
         "docs/1-srs-rustinfer": "the SRS, ADR-001 to ADR-006, planning documents, issue drafts",
         "feat/2-project-scaffold": "the workspace, core, command, CI, mandatory files, `LICENSE`; rebased on the docs branch"}
for b in branches:
    out += f"| `{b}` | {HOLDS.get(b, 'see its issue')} |\n"
write("issues.md", out)
