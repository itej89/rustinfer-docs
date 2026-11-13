#!/usr/bin/env python3
"""The standards tracker: every reference of SRS section 1.4 with the
requirements that cite it and a state derived from their test tags (the
rule of common.requirement_states), the external interfaces of section 3.1.3
with the reference that pins each, and the curated candidates of
data/standards-candidates.json: standards the code or the plan depends on that
section 1.4 does not reference yet."""
import json
import re
import sys

from common import (IMPLEMENTED, PARTIAL, RESERVED_ONLY, PLANNED, RUSTINFER, SITE, SRS,
                    STATES, commit, header, requirement_states, srs_meta,
                    srs_requirements, test_tags, write)

CANDIDATES = SITE / "data" / "standards-candidates.json"
TEXT = SRS.read_text(encoding="utf-8")

# How a requirement cites a reference: its ID, or an unambiguous name of it,
# in the clause, Rationale or Acceptance text (case-sensitive regexes).
ALIASES = {
    "SWG-001": [r"\bSWG-001\b"],
    "IEEE-830": [r"\bIEEE-830\b", r"IEEE Std 830"],
    "IEEE-29148": [r"\bIEEE-29148\b", r"\b29148\b"],
    "INV": [r"\bINV\b", r"trt-llm-feature-inventory"],
    "UC": [r"\bUC\b", r"use-cases\.md"],
    "DEV": [r"\bDEV\b", r"datacenter-device-inventory"],
    "AITER-DOCS": [r"\bAITER-DOCS\b", r"\bAITER\b"],
    "MLIR": [r"\bMLIR\b"],
    "ADR-001 to ADR-006": [r"\bADR-00[1-6]\b"],
    "ADR-010": [r"\bADR-010\b"],
    "OCP-MX": [r"\bOCP-MX\b", r"\bOCP MX\b", r"Microscaling"],
    "QUARK": [r"\bQUARK\b", r"\bQuark\b"],
    "CT": [r"\bCT\b", r"compressed-tensors", r"llm-compressor"],
    "NV-KV": [r"\bNV-KV\b"],
    "MXFP4-RTN": [r"\bMXFP4-RTN\b", r"2509\.23202"],
}

# Our scope of each reference, quoted or condensed from the SRS text (where
# in the SRS in brackets); absent means the SRS does not state one.
SCOPE = {
    "SWG-001": "applies in full with the adaptations in ADR-001 and ADR-004 (§2.5); requirement format per §2.4 (§3)",
    "AITER-DOCS": "reference only: tuned kernels on gfx942 and gfx950 and the benchmark baseline (§1.4); "
                  "GEMM at least 80 percent of the best AITER kernel (RI-NFR-006)",
    "MLIR": "dialects `gpu`, `amdgpu`, `rocdl`, `spirv`, `vector` (§1.4) and `llvm`, linked through `melior` (§3.1.3); "
            "the Kernel IR is an MLIR dialect (RI-KC-002)",
    "OCP-MX": "MXFP4 only: E2M1 elements in blocks of 32 with a UE8M0 scale (§1.3, RI-MIR-003); "
              "conversion per OCP MX v1.1 §6.3 Equation 4 (RI-MIR-012)",
    "QUARK": "the MXFP4 export: `quant_method: \"quark\"`, `dtype: \"fp4\"`, `scale_format: \"e8m0\"`, "
             "`scale_calculation_mode: \"even\"` (§1.4, RI-FE-006 (a))",
    "CT": "the `mxfp4-pack-quantized` format (§1.4, RI-FE-006 (b))",
    "ADR-001 to ADR-006": "decisions of the project; each requirement cites the one it implements",
    "ADR-010": "MXFP4 in Release 1 (RI-FE-006, RI-GC-004, RI-KVC-008)",
}
NOT_STATED = "not stated in the SRS"


def references():
    """The rows of the §1.4 References table: (id, title, version, date)."""
    sec = re.search(r"^### 1\.4 References\s*\n(.*?)(?=^### )", TEXT, re.S | re.M).group(1)
    rows = []
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0] not in ("ID",) and not set(cells[0]) <= set("-: "):
            rows.append(tuple(cells))
    return rows


def interfaces():
    """The rows of the §3.1.3 table: (interface, direction, contract)."""
    sec = TEXT.split("| Interface | Direction | Contract |", 1)[1]
    rows = []
    for line in sec.splitlines()[2:]:
        if not line.startswith("|"):
            break
        rows.append(tuple(c.strip() for c in line.strip().strip("|").split("|")))
    return rows


def requirement_texts(ids):
    """{id: clause + Rationale + Acceptance} for every requirement of the SRS:
    the code blocks split at blank lines, the Priority and Changed fields left out."""
    out = {}
    for code in re.findall(r"^```[^\n]*\n(.*?)^```", TEXT, re.S | re.M):
        for chunk in re.split(r"\n\s*\n", code):
            m = re.match(r"\s*(RI-[A-Z]+-\d{3})\b", chunk)
            if not m or m.group(1) not in ids:
                continue
            keep, cur = [], True
            for line in chunk.splitlines():
                field = re.match(r"(\w+):", line)
                if field:
                    cur = field.group(1) in ("Rationale", "Acceptance")
                    if field.group(1) == "Priority":
                        cur = False
                if cur:
                    keep.append(line)
            out[m.group(1)] = "\n".join(keep)
    return out


def citing(patterns, texts):
    return [rid for rid, t in texts.items() if any(re.search(p, t) for p in patterns)]


def standard_state(cites, states):
    """(badge class or None, label): state-ok when at least one citing
    requirement is R1 and every citing R1 requirement is implemented;
    state-part when some citing requirement is implemented or partial;
    state-no otherwise; no badge when nothing cites the reference."""
    if not cites:
        return None, "not cited"
    r1 = [states[r] for r in cites if states[r]["tag"] == "R1"]
    if r1 and all(s["state"] == IMPLEMENTED for s in r1):
        return "state-ok", "implemented (R1 scope)"
    if any(states[r]["state"] in (IMPLEMENTED, PARTIAL) for r in cites):
        return "state-part", "in part"
    return "state-no", "not implemented"


def counts(cites, states):
    c = {st: sum(1 for r in cites if states[r]["state"] == st) for st in STATES}
    return ", ".join(f"{c[st]} {st}" for st in STATES)


def check_evidence(cands):
    """Every evidence entry `path:line` must name a line of the checkout."""
    bad = []
    for c in cands:
        for ev in c["evidence"]:
            m = re.match(r"([^\s:]+):(\d+)", ev)
            path = RUSTINFER / m.group(1) if m else None
            if not m or not path.is_file() or int(m.group(2)) > len(path.read_text(errors="replace").splitlines()):
                bad.append(f"{c['id']}: {ev}")
    return bad


def ids_cell(ids, states):
    return ", ".join(f"{r} ({states[r]['tag']})" for r in ids) or "—"


def esc(s):
    return s.replace("|", "\\|")


reqs = srs_requirements()
by_id = {r["id"]: r for r in reqs}
tags = test_tags()
states = requirement_states(reqs, {"issues": []}, tags)
texts = requirement_texts(set(by_id))
version, status = srs_meta()
data = json.loads(CANDIDATES.read_text(encoding="utf-8"))
cands = data["candidates"]
bad = check_evidence(cands)
if bad:
    sys.exit("evidence not found in the checkout:\n  " + "\n  ".join(bad))
unknown = [f"{c['id']}: {r}" for c in cands for r in c["cite"] if r not in by_id]
if unknown:
    sys.exit("candidate cites an id the SRS does not have:\n  " + "\n  ".join(unknown))

refs = references()
rows, summary = [], {"state-ok": 0, "state-part": 0, "state-no": 0, None: 0}
for rid, title, ver, date in refs:
    cites = citing(ALIASES.get(rid, [re.escape(rid)]), texts)
    cls, label = standard_state(cites, states)
    summary[cls] += 1
    rows.append((rid, title, ver, date, SCOPE.get(rid, NOT_STATED), cites, cls, label))

out = header("Standards tracker", "Standards", 2,
             "Every reference of SRS §1.4 with the requirements that cite it and a state derived from "
             "their test tags, the interfaces of §3.1.3, and the standards the tree depends on that the SRS "
             "does not reference yet.",
             navtitle="Standards tracker", script="gen_standards.py")
out += f"""# Standards tracker

Generated from `docs/SRS-RI-v0.1.md` (version {version}, status *{status}*) and the
test tags of the rustinfer checkout at commit {commit()}, and from the curated
`data/standards-candidates.json` of this site. What the states mean and how a
standard enters this table: [Standards](standards.html).

## Headline

**{len(refs)} references in SRS §1.4: {summary['state-ok']} implemented in their R1 scope,
{summary['state-part']} in part, {summary['state-no']} not implemented, {summary[None]} not cited by
any requirement.** {len(cands)} standards the tree depends on are not referenced yet
([below](#required-not-yet-in-the-srs)).

## How the table is derived

- **Cites.** A requirement cites a reference when its clause, `Rationale` or
  `Acceptance` text (not `Priority` or `Changed`) contains the reference ID or an
  unambiguous name of it. The names matched, as regular expressions:
"""
for rid, *_ in refs:
    pats = ALIASES.get(rid, [re.escape(rid)])
    out += f"    - {rid}: " + ", ".join(f"`{p}`" for p in pats) + "\n"
out += f"""- **Requirement state** is the site's rule (`scripts/reference/common.py`, the tag
  rule of the rustinfer repository's `docs/testing.md`): *implemented* with a `Verifies`
  tag and no `Groundwork for` tag, *partial* with any `Groundwork for` tag, *reserved only*
  with `Reserved` tags alone, *planned* otherwise. Each citing id is shown with the first
  release its SRS `Release` field names.
- **Standard state.** <span class="state-ok">implemented (R1 scope)</span> when at least one
  citing requirement is R1 and every citing R1 requirement is implemented;
  <span class="state-part">in part</span> when some citing requirement is implemented or
  partial; <span class="state-no">not implemented</span> otherwise; *not cited* when no
  requirement cites the reference.
- **Our scope** is what the SRS says we implement of the reference, with the place it says
  so; "{NOT_STATED}" where it says nothing.

## SRS §1.4 references

| reference | title | pinned version | date | our scope | cited by | standard state | requirement states |
|---|---|---|---|---|---|---|---|
"""
for rid, title, ver, date, scope, cites, cls, label in rows:
    badge = f'<span class="{cls}">{label}</span>' if cls else label
    out += (f"| {rid} | {esc(title)} | {esc(ver) or '—'} | {date or '—'} | {esc(scope)} | "
            f"{ids_cell(cites, states)} | {badge} | {counts(cites, states) if cites else '—'} |\n")

cand_alias = {c["id"]: c.get("aliases", []) for c in cands}
out += """
## External interfaces of §3.1.3

The contract column of SRS §3.1.3 and the references that pin it: a §1.4 reference whose
ID or name appears in the row, else the candidate below that would.

| interface | direction | contract | pinned by §1.4 | candidate |
|---|---|---|---|---|
"""
for name, direction, contract in interfaces():
    row = f"{name} {contract}"
    pinned = [rid for rid, *_ in refs if any(re.search(p, row) for p in ALIASES.get(rid, [re.escape(rid)]))]
    cand = [cid for cid, pats in cand_alias.items() if any(re.search(p, row) for p in pats)]
    out += (f"| {esc(name)} | {direction} | {esc(contract)} | {', '.join(pinned) or 'none'} | "
            f"{', '.join(f'[{c}](#cand-{c.lower()})' for c in cand) or '—'} |\n")

out += f"""
## Required, not yet in the SRS

Standards the code or the plan already depends on that SRS §1.4 does not reference, from
`data/standards-candidates.json` (curated by reading the tree; every evidence line is
checked against the checkout when this page is generated). None is tracked above until
an SRS amendment adds its §1.4 row and a requirement cites it. *Should be cited by*
lists the SRS ids with their first release and current state; *named in the SRS by* lists
the requirements whose text already names the standard without a §1.4 row.

| candidate | title | version to pin | date | release | should be cited by | named in the SRS by | why | evidence |
|---|---|---|---|---|---|---|---|---|
"""
for c in cands:
    named = citing(c.get("aliases", []), texts)
    cited = ", ".join(f"{r} ({states[r]['tag']}, {states[r]['state']})" for r in c["cite"])
    ev = "<br>".join(f"`{e.split(' ', 1)[0]}`" + (f" {e.split(' ', 1)[1]}" if " " in e else "")
                     for e in c["evidence"])
    title = f"[{esc(c['title'])}]({c['url']})"
    out += (f"| <a id=\"cand-{c['id'].lower()}\"></a>{c['id']} | {title} | {esc(c['version'])} | "
            f"{c['date'] or '—'} | {c['release']} | {cited} | {', '.join(named) or '—'} | "
            f"{esc(c['why'])} | {ev} |\n")

out += """
### Considered and rejected

| candidate | title | why not |
|---|---|---|
"""
for r in data["rejected"]:
    out += f"| {r['id']} | {esc(r['title'])} | {esc(r['reason'])} |\n"
write("ref-standards.md", out)
