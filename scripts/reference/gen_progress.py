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
"""
import datetime
import json
import pathlib
import re
import subprocess

from common import RUSTINFER, SITE, commit, header, write

REPO = "itej89/rustinfer"
WEB = f"https://github.com/{REPO}"
SNAPSHOT = SITE / "data" / "progress-snapshot.json"
TODAY = datetime.date.today().isoformat()

# Coverage is taken from the merge-readiness checklist of PR #19, not measured here.
COVERAGE = ("95.50%", "the coverage block of PR #19's merge-readiness checklist "
            "(`cargo llvm-cov --workspace --all-features`), 2026-11-12")
EPIC = 1
SEQUENCE = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # the Epic's order

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
# The issue body's `## Blocked By` section, the drafts' form, when the dependency API has nothing.
BLOCKED_BY = re.compile(r"^##\s*Blocked By\s*\n(.*?)(?=^##\s|\Z)", re.I | re.M | re.S)


# ------------------------------------------------------------------- GitHub
def gh(path, paginate=True):
    """One `gh api` call; the token never leaves `gh`'s keyring."""
    cmd = ["gh", "api"] + (["--paginate"] if paginate else []) + [f"repos/{REPO}/{path}"]
    out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=120)
    if paginate and out.count("][") > 0:  # --paginate concatenates pages of a list
        out = "[" + out.replace("][", ",") + "]" if not out.startswith("[[") else out
        parts = json.loads(out)
        return [x for page in parts for x in page] if parts and isinstance(parts[0], list) else parts
    return json.loads(out)


def blocked_by(issue):
    """The issues this one waits on: GitHub's dependency API and the body's `## Blocked By` section."""
    found = set()
    try:
        deps = gh(f"issues/{issue['number']}/dependencies/blocked_by", paginate=False)
        if isinstance(deps, list):
            found.update(d["number"] for d in deps)
    except (subprocess.CalledProcessError, OSError, ValueError, KeyError, TypeError):
        pass
    for m in BLOCKED_BY.finditer(issue.get("body") or ""):
        found.update(int(n) for n in re.findall(r"#(\d+)", m.group(1)))
    found.discard(issue["number"])
    return sorted(found)


def live_state():
    try:
        subprocess.check_output(["gh", "auth", "status"], stderr=subprocess.DEVNULL, timeout=30)
        items = gh("issues?state=all&per_page=100")
        issues = [i for i in items if "pull_request" not in i]  # GitHub lists PRs as issues
        pulls = gh("pulls?state=all&per_page=100")
        milestones = gh("milestones?state=all")
        runs = gh("actions/runs?per_page=12", paginate=False).get("workflow_runs", [])
        branches = gh("branches?per_page=100")
        deps = {i["number"]: blocked_by(i) for i in issues}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, ValueError, KeyError):
        return None
    if not issues and not pulls:
        return None  # the tracker is not on GitHub yet; keep the snapshot
    return {
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": "github",
        "issues": [{"number": i["number"], "title": i["title"], "state": i["state"],
                    "closed_at": (i.get("closed_at") or "")[:10],
                    "labels": [l["name"] for l in i["labels"]],
                    "milestone": (i.get("milestone") or {}).get("title"),
                    "blocked_by": deps.get(i["number"], [])}
                   for i in sorted(issues, key=lambda x: x["number"])],
        "pulls": [{"number": p["number"], "title": p["title"], "state": p["state"],
                   "head": p["head"]["ref"], "base": p["base"]["ref"],
                   "merged": bool(p.get("merged_at")), "merged_at": (p.get("merged_at") or "")[:10],
                   "mergeable": p.get("mergeable", True) is not False,
                   "created_at": p["created_at"][:10], "url": p["html_url"]}
                  for p in sorted(pulls, key=lambda x: x["number"])],
        "milestones": [{"title": m["title"], "state": m["state"],
                        "open": m["open_issues"], "closed": m["closed_issues"]} for m in milestones],
        "runs": [{"id": r["run_number"], "title": r.get("display_title"), "status": r.get("status"),
                  "conclusion": r.get("conclusion"), "event": r.get("event"),
                  "ref": r.get("head_branch"), "sha": (r.get("head_sha") or "")[:7],
                  "created": (r.get("created_at") or "")[:16], "url": r.get("html_url")}
                 for r in runs],
        "branches": sorted(b["name"] for b in branches),
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
codeberg_pr_for_branch = {p["head"]: p for p in CODEBERG_PULLS}
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
| SRS requirements implemented | `{bar(implemented, len(reqs))}` | a requirement is implemented when the issue that carries it is closed; by SRS status today: {", ".join(f"{k} {v}" for k, v in sorted(by_status.items()))}; by release: {", ".join(f"{k} {v}" for k, v in by_release.items())} |
| Tests | {tests} | `#[test]` functions across {len(crates)} crates |
| Line coverage | {COVERAGE[0]} | from {COVERAGE[1]}; the CI gate is 80 percent |
| Rust | {lines_rs:,} lines in {len(rs_files)} files | `crates/**/*.rs`, tests and build scripts included |

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
    b = branch_of(n)
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
        notes.append(f"Codeberg PR #{cb['number']} `{cb['head']}` merged {cb['merged_at']}, before the move")
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
are history: they are not GitHub pull requests and GitHub's own numbering continues after the
issues it holds.

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
    out += f"| PR-{p['number']} | [{p['title']}]({p.get('url', WEB + '/pull/' + str(p['number']))}) | {req} | {st} | {notes} |\n"
for p in CODEBERG_PULLS:
    out += (f"| PR-{p['number']} | {p['title']} | a reviewer's sign-off | Merged {p['merged_at']} | "
            f"`{p['head']}` → `{p['base']}`; merged on Codeberg before the move, the branch is on GitHub |\n")

out += f"""
## CI runs

The most recent runs of `ci.yml` on GitHub Actions, newest first. `queued` means waiting for a
hosted runner. GitHub's run numbers restart at 1: the Codeberg history, runs 1 and 2 of
2026-11-11 cancelled unanswered (`ubuntu-latest`, a label Codeberg never served), runs 3 to 6
each failing on one Codeberg-specific rule recorded in ADR-004, run 7 the first green run, runs 8
to 11 green on PRs #17 and #19 and `main`, did not move and is gone with the Codeberg repository
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
HOLDS = {"main": "the approved SRS v0.2, ADR-001 to ADR-006, the fourteen-crate workspace, the Model IR and the artifact crate (Codeberg PRs #16, #17, #19 and #21)",
         "feat/3-model-ir": "the Model IR crate `rustinfer-mir`, merged as Codeberg PR #19",
         "feat/4-artifact-format": "the `.rie` artifact crate `rustinfer-artifact`, merged as Codeberg PR #21",
         "feat/5-target-and-cpu-reference": "the `Target` trait and the CPU reference target (#5), in progress",
         "feat/15-planner-interfaces": "the planner's R1 interfaces (#15), in progress",
         "docs/1-srs-rustinfer": "the SRS, ADR-001 to ADR-006, planning documents, issue drafts",
         "feat/2-project-scaffold": "the workspace, core, command, CI, mandatory files; rebased on the docs branch"}
for b in branches:
    out += f"| [`{b}`]({WEB}/tree/{b}) | {HOLDS.get(b, 'see its issue')} |\n"
write("issues.md", out)
