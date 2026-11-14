#!/usr/bin/env python3
"""The Standards map, kept consistent with its sources.

Reads SRS section 1.4 on `origin/main` (five columns since SRS v0.4.3, PR
#50: ID, Title, Version, Date, Conformance). The `Conformance` column is the
source of which standards are mandatory and from which release
(`mandatory R<n>`); the other rows are `process`, `informative` or
`internal`. It reads with that the record of each standard in data/standards/<id>.json and the four pages
of each, content/std-<id>{,-requirements,-audit,-tracker}.md, and:

1. checks them: one record and four pages per mandatory standard, the same
   section, group ("<Area> / <Name> <version>") and order block on the four
   pages, the navtitles, the area and conformance of the record against the
   group, and every gap id unique on the whole site; a record whose
   `conformance` differs from the SRS is rewritten from the SRS;
2. recomputes `gaps_open` and `gaps_total` of every record from its tracker
   table and writes the record back when they differ. The rule: a gap whose
   status starts with "Open" or "In PR #N" is open; "Later release R<n>" is
   counted in `gaps_total` only; "Out of scope" (an owner decision that
   narrowed the SRS scope) is counted in neither; "Fixed", "Closed" and the
   like are closed (also in the total);
3. writes the two generated blocks of content/standards.md: the map (one
   card per area) and the other referenced documents of section 1.4 (process,
   informative, internal), each with the one-line purpose kept below.

Exits non-zero on any inconsistency, so a build never publishes a map that
disagrees with the pages.
"""
import html
import json
import re
import subprocess
import sys

from common import (CONTENT, RUSTINFER, STD_AREAS, STD_LABEL, STD_MAP_CLASS,
                    std_slug, standards)

SRS_PATH = "docs/SRS-RI-v0.1.md"
SRS_REF = "origin/main"
SRS_COLUMNS = ["ID", "Title", "Version", "Date", "Conformance"]
PAGE = CONTENT / "standards.md"
KINDS = [("", "Overview", "overview"), ("-requirements", "Requirements", "requirements"),
         ("-audit", "Audit", "audit"), ("-tracker", "Tracker", "tracker")]
ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+[a-z]?$")
RULE = re.compile(r"^\|[\s:|-]+\|$")

# One line on what each non-mandatory reference of SRS §1.4 is for. A new
# §1.4 row that is not mandatory needs a line here, or the script stops.
PURPOSE = {
    "SWG-001": "The engineering standard the project is developed under: requirement format, "
               "reviews, logging, tests; adapted by ADR-001, ADR-004 and ADR-008.",
    "IEEE-830": "The structure of the SRS and the qualities a requirement must have.",
    "IEEE-29148": "The requirements-engineering standard that succeeds IEEE 830; the SRS follows both.",
    "INV": "The TensorRT-LLM feature inventory the scope of each release was drawn from.",
    "UC": "The use cases the requirements trace back to.",
    "DEV": "The datacenter GPUs and accelerators the targets are chosen from.",
    "AITER-DOCS": "The kernels rustinfer's generated kernels are compared with, never linked: "
                  "the GEMM baseline of RI-NFR-006.",
    "ADR-001 to ADR-006": "The founding decisions: Rust under SWG-001, the artifact format, the target "
                          "abstraction, Codeberg rules, the three representations, the artifact as a cache.",
    "ADR-007": "The pinned LLVM 23 and the in-process MLIR link.",
    "ADR-008": "The move of the project to GitHub.",
    "ADR-009": "Placement names devices and tiers.",
    "ADR-010": "MXFP4 in Release 1.",
    "NV-KV": "Background for a low-precision KV cache (NVFP4 KV cache, long context and large batches).",
    "MXFP4-RTN": "Evidence that weight-only MXFP4 round-to-nearest keeps about 95.6 percent of "
                 "Llama-3.1-8B's accuracy, behind MXFP4 in Release 1.",
}
KIND_ORDER = {"process": 0, "informative": 1, "internal": 2}
MANDATORY = re.compile(r"^mandatory R\d$")

errors = []


def fail(msg):
    errors.append(msg)


# ------------------------------------------------------------------ sources
def srs():
    """§1.4 of the SRS on origin/main, which must have the five columns."""
    try:
        text = subprocess.check_output(["git", "-C", str(RUSTINFER), "show", f"{SRS_REF}:{SRS_PATH}"],
                                       text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        sys.exit(f"gen_standards: cannot read {SRS_PATH} at {SRS_REF} in {RUSTINFER}")
    sec = re.search(r"^### 1\.4 References\s*\n(.*?)(?=^### )", text, re.S | re.M)
    if not sec:
        sys.exit(f"gen_standards: no §1.4 References in {SRS_PATH} at {SRS_REF}")
    return SRS_REF, sec.group(1)


def cells_of(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def references(section):
    """{id: (title, conformance)} of the §1.4 table, by its Conformance column."""
    out, head = {}, None
    for line in section.splitlines():
        if not line.startswith("|") or RULE.match(line.strip()):
            continue
        cells = cells_of(line)
        if head is None:
            head = cells
            if head != SRS_COLUMNS:
                sys.exit(f"gen_standards: §1.4 columns are {head}, expected {SRS_COLUMNS}")
            continue
        if len(cells) != len(head):
            sys.exit(f"gen_standards: §1.4 row {cells[0]!r} has {len(cells)} cells, expected {len(head)}")
        row = dict(zip(head, cells))
        conf = row["Conformance"]
        if not (MANDATORY.match(conf) or conf in KIND_ORDER):
            sys.exit(f"gen_standards: §1.4 row {row['ID']!r} has conformance {conf!r}")
        out[row["ID"]] = (row["Title"], conf)
    if head is None:
        sys.exit("gen_standards: §1.4 has no table")
    return out


def front(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta, text


def table_rows(text):
    """(id, {header: cell}) of every table row whose first cell is an id."""
    head = None
    for line in text.split("\n"):
        if not line.startswith("|"):
            head = None
            continue
        if RULE.match(line.strip()):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not ID.match(cells[0]):
            head = [c.lower() for c in cells]
            continue
        if head:
            yield cells[0], dict(zip(head, cells))


def gap_kind(status):
    s = re.sub(r"[*`]", "", status).strip()
    if re.match(r"later release R\d", s, re.I):
        return "later"
    if re.match(r"out of scope\b", s, re.I):
        return "excluded"
    if re.match(r"(open|in pr #\d+)\b", s, re.I):
        return "open"
    if re.match(r"(closed|met|fixed|done|conforms|merged)\b", s, re.I):
        return "closed"
    return None


# ------------------------------------------------------------------- checks
ref, section = srs()
refs = references(section)
mandatory = {i: c for i, (_, c) in refs.items() if MANDATORY.match(c)}
items = standards()
by_id = {d["id"]: d for d in items}

for i in sorted(set(mandatory) - set(by_id)):
    fail(f"{i}: mandatory in SRS §1.4 ({ref}) but no data/standards record")
for i in sorted(set(by_id) - set(mandatory)):
    fail(f"{i}: has a record but is not mandatory in SRS §1.4 ({ref})")

pages = {}
for d in items:
    sid, slug = d["id"], std_slug(d["id"])
    if sid in mandatory and d["conformance"] != mandatory[sid]:
        print(f"corrected {sid}: conformance {d['conformance']!r} -> {mandatory[sid]!r} (SRS §1.4)")
        d["conformance"], d["release"] = mandatory[sid], mandatory[sid].split()[-1]
        d["_dirty"] = True
    if d["area"] not in STD_AREAS:
        fail(f"{sid}: unknown area {d['area']!r}")
    if d["state"] not in STD_LABEL:
        fail(f"{sid}: unknown state {d['state']!r}")
    metas = {}
    for suffix, nav, _ in KINDS:
        p = CONTENT / f"{slug}{suffix}.md"
        if not p.exists():
            fail(f"{sid}: missing {p.name}")
            continue
        metas[suffix] = front(p)
        meta = metas[suffix][0]
        for key in ("title", "navtitle", "section", "group", "order", "summary"):
            if not meta.get(key):
                fail(f"{p.name}: no {key}")
        if meta.get("section") != "Standards":
            fail(f"{p.name}: section {meta.get('section')!r}")
        if meta.get("navtitle") != nav:
            fail(f"{p.name}: navtitle {meta.get('navtitle')!r}, expected {nav!r}")
    if len(metas) != 4:
        continue
    base = metas[""][0]
    group = base.get("group", "")
    area, _, label = group.partition(" / ")
    if area != d["area"]:
        fail(f"{sid}: group area {area!r}, record area {d['area']!r}")
    if base.get("title") != label:
        fail(f"{sid}: overview title {base.get('title')!r} is not the group's name {label!r}")
    for n, (suffix, nav, _) in enumerate(KINDS):
        meta = metas[suffix][0]
        if meta.get("group") != group:
            fail(f"{slug}{suffix}: group {meta.get('group')!r}, overview has {group!r}")
        if int(meta.get("order", -1)) != int(base.get("order", 0)) + n:
            fail(f"{slug}{suffix}: order {meta.get('order')}, expected {int(base.get('order', 0)) + n}")
        if suffix and meta.get("title") != f"{label} {nav.lower()}":
            fail(f"{slug}{suffix}: title {meta.get('title')!r}, expected {label + ' ' + nav.lower()!r}")
    d["_label"], d["_order"] = label, int(base.get("order", 0))
    pages[sid] = metas

# gap ids: unique across the whole site, and each tracker's rows classified
owner = {}
for p in sorted(CONTENT.glob("*.md")):
    for gid, _ in table_rows(p.read_text(encoding="utf-8")):
        owner.setdefault(gid, set()).add(p.stem)
changed = []
for d in items:
    sid = d["id"]
    if sid not in pages:
        continue
    text = pages[sid]["-tracker"][1]
    counts = {"open": 0, "later": 0, "closed": 0, "excluded": 0}
    for gid, row in table_rows(text):
        holders = owner.get(gid, set())
        if len(holders) > 1:
            fail(f"gap id {gid} of {std_slug(sid)}-tracker also used on {sorted(holders - {std_slug(sid) + '-tracker'})}")
        status = row.get("status")
        kind = gap_kind(status or "")
        if kind is None:
            fail(f"{gid}: status {status!r} is not Open, In PR #N, Later release R<n>, Out of scope or closed")
            continue
        counts[kind] += 1
    new_open, new_total = counts["open"], counts["open"] + counts["later"] + counts["closed"]
    if (d["gaps_open"], d["gaps_total"]) != (new_open, new_total):
        changed.append(f"{sid}: gaps {d['gaps_open']}/{d['gaps_total']} -> {new_open}/{new_total}")
        d["gaps_open"], d["gaps_total"] = new_open, new_total
        d["_dirty"] = True
    if d.pop("_dirty", False):
        record = {k: v for k, v in d.items() if not k.startswith("_") and k != "release"}
        d["_path"].write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    d["_later"] = counts["later"]

others = {i: v for i, v in refs.items() if i not in mandatory}
for i in sorted(set(others) - set(PURPOSE)):
    fail(f"{i}: in SRS §1.4 ({ref}) as {others[i][1]!r} with no purpose line in gen_standards.py")

for c in changed:
    print("corrected", c)
if errors:
    for e in errors:
        print("error:", e, file=sys.stderr)
    sys.exit(1)


# ------------------------------------------------------------------- output
def esc(s):
    return html.escape(s, quote=False)


def entry(d):
    slug = std_slug(d["id"])
    links = " · ".join(f'<a href="{slug}{suffix}.html">{word}</a>' for suffix, _, word in KINDS)
    gaps = f'{d["gaps_open"]} open gap{"" if d["gaps_open"] == 1 else "s"}'
    if d["_later"]:
        gaps += f', {d["_later"]} later'
    secondary = d.get("spec_source") == "secondary"
    tag = "assessed · secondary" if secondary else "assessed"
    tip = (f"audited {d['audit_date']}"
           + (" against secondary sources: the specification is not freely available" if secondary
              else " against the downloaded specification"))
    tag_html = (f'<a class="std-tag" href="{slug}-audit.html" title="{tip}">{tag}</a>'
                if d.get("assessed") else "")
    return (f'    <li class="{STD_MAP_CLASS[d["state"]]}">'
            f'<span class="std-name"><a href="{slug}.html">{esc(d["name"])}</a></span>'
            f'<span class="std-scope">{esc(d["version"])}</span>'
            f'<span class="std-scope">{d["conformance"]} · {gaps}</span>'
            f'<span class="std-pages">{links}</span>{tag_html}</li>')


cards = ['<div class="std-map" role="list" aria-label="Areas and the mandatory standards in each">', ""]
for area in STD_AREAS:
    group = sorted((d for d in items if d["area"] == area), key=lambda d: d["_order"])
    if not group:
        continue
    cards += ['<section class="std-card" role="listitem">',
              f'  <h3 class="std-sys">{esc(area)}</h3>', "  <ul>"]
    cards += [entry(d) for d in group]
    cards += ["  </ul>", "</section>", ""]
cards.append("</div>")

rows = ["| ID | Document | Conformance | Purpose |", "|---|---|---|---|"]
for i, (title, conf) in sorted(others.items(), key=lambda kv: (KIND_ORDER.get(kv[1][1], 9), kv[0])):
    title = re.sub(r"\s*\(?https?://\S+", "", title).rstrip(",; ")
    rows.append(f"| {i} | {title} | {conf} | {PURPOSE[i]} |")

text = PAGE.read_text(encoding="utf-8")


def put(text, name, body):
    pat = re.compile(rf"(<!-- begin generated {name}[^>]*-->\n).*?(<!-- end generated {name} -->)", re.S)
    if not pat.search(text):
        sys.exit(f"gen_standards: content/standards.md has no generated {name} block")
    return pat.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)


text = put(text, "map", "\n".join(cards))
text = put(text, "references", f"\nRead from the Conformance column of SRS §1.4 at `{ref}`.\n\n" + "\n".join(rows) + "\n")
PAGE.write_text(text, encoding="utf-8")
print(f"wrote standards.md: {len(items)} standards in {len(STD_AREAS)} areas, "
      f"{len(others)} other references (SRS from {ref})")
