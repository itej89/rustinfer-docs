"""The architecture diagram's C4 views, drawn from data, not typed.

build.py replaces the `<!-- c4 -->` marker of content/architecture-diagram.md
with what `render()` returns: the four C4 levels (context, containers,
components, code) and the supplementary diagrams (the layer stack in the
Matins form, standards, dynamic, deployment), as tabs over one page.

Sources, so that nothing on the diagram is a claim typed by hand twice:

- data/c4/*.json: the elements, their relations, and the issues each one is
  delivered by; never a status word;
- data/progress-snapshot.json: the issue tracker as gen_progress.py last
  fetched it; every status chip is derived from it (closed, in an open pull
  request, a branch, nothing yet), or from the release an element is due in;
- the rustinfer checkout's Cargo.toml files and lib.rs: the dependency bands
  of the component view and the public items of the code view, written to
  data/c4/cargo.json so a build without the checkout reproduces the last one;
- data/standards/*.json and data/standards-placement.json: the standards
  chips on every level and the Standards diagram. A mandatory standard that
  is placed nowhere, or a placement naming an element that does not exist,
  stops the build.
"""
import html
import json
import os
import pathlib
import re
import subprocess

from markdown.extensions.toc import slugify

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
C4 = DATA / "c4"
RUSTINFER = pathlib.Path(os.environ.get("RUSTINFER_SRC", ROOT.parent / "rustinfer"))
ISSUES = "https://github.com/itej89/rustinfer/issues/"
PULLS = "https://github.com/itej89/rustinfer/pull/"
CURRENT = "R1"
STD_CLASS = {"works": "std-ok", "part": "std-part", "gap": "std-gap", "later": "std-later"}
STD_LABEL = {"works": "works", "part": "partly works", "gap": "missing", "later": "later release"}
STD_RANK = {"gap": 0, "part": 1, "works": 2, "later": 3}
MAX_BOXES = 9
LAYER_NAME = {"interfaces": "Interfaces", "runtime": "Runtime", "compiler": "Compiler",
              "kernels": "Kernels", "targets": "Targets", "foundation": "Foundation"}

e = html.escape


class C4Error(Exception):
    pass


def load(name):
    return json.loads((C4 / name).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ cargo
def _api(src):
    """The public items a Rust file names: `pub use a::{B, C}` and `pub struct D`."""
    names = []
    for m in re.finditer(r"^pub use [\w:]+::\{(.*?)\};", src, re.S | re.M):
        names += [n.strip().split(" as ")[-1] for n in m.group(1).split(",") if n.strip()]
    for m in re.finditer(r"^pub use [\w:]+::(\w+);", src, re.M):
        names.append(m.group(1))
    for m in re.finditer(r"^pub (?:struct|enum|trait|fn|type|const|mod) (\w+)", src, re.M):
        names.append(m.group(1))
    drop = {"Error", "Result", "COMPONENT"}
    out = []
    for n in names:
        if n not in drop and n not in out and n != "self":
            out.append(n)
    return out


def cargo():
    """{crate: {deps, api}} from the checkout, written to data/c4/cargo.json;
    the file when the checkout is missing."""
    snap = C4 / "cargo.json"
    crates = RUSTINFER / "crates"
    if not crates.is_dir():
        return json.loads(snap.read_text(encoding="utf-8"))
    out = {"commit": "", "crates": {}, "modules": {}}
    try:
        out["commit"] = subprocess.check_output(
            ["git", "-C", str(RUSTINFER), "log", "-1", "--format=%h"], text=True).strip()
    except Exception:  # noqa: BLE001
        pass
    for d in sorted(crates.iterdir()):
        toml = d / "Cargo.toml"
        if not toml.is_file():
            continue
        deps, section = [], None
        for line in toml.read_text(encoding="utf-8").splitlines():
            if line.startswith("["):
                section = line.strip()
            elif section == "[dependencies]" and line.startswith("rustinfer"):
                deps.append(line.split("=")[0].strip())
        lib = d / "src" / "lib.rs"
        api = _api(lib.read_text(encoding="utf-8")) if lib.is_file() else []
        out["crates"][d.name] = {"deps": deps, "api": api}
        if not lib.is_file():
            for f in sorted((d / "src").glob("*.rs")):
                out["modules"][f"{d.name}/src/{f.name}"] = _api(f.read_text(encoding="utf-8"))
    text = json.dumps(out, indent=1) + "\n"
    if not snap.exists() or snap.read_text(encoding="utf-8") != text:
        snap.write_text(text, encoding="utf-8")
    return out


def ranks(crates):
    """A crate's band: one above the highest crate it depends on."""
    memo = {}

    def r(c, seen=()):
        if c in memo:
            return memo[c]
        if c in seen:
            raise C4Error(f"dependency cycle through {c}")
        deps = [d for d in crates[c]["deps"] if d in crates]
        memo[c] = 0 if not deps else 1 + max(r(d, seen + (c,)) for d in deps)
        return memo[c]
    return {c: r(c) for c in crates}


# ----------------------------------------------------------------- status
class Tracker:
    def __init__(self):
        self.state = json.loads((DATA / "progress-snapshot.json").read_text(encoding="utf-8"))
        self.issues = {i["number"]: i for i in self.state["issues"]}
        self.date = self.state.get("fetched_at", "")[:10]

    def _branch(self, n):
        return next((b for b in self.state.get("branches", [])
                     if re.match(rf"(feat|fix|docs|refactor|ci|chore|infra)/{n}-", b)), None)

    def gpu_test_for(self, pr):
        """The open gpu-test issue that a pull request waits on, if any."""
        for i in self.state["issues"]:
            if (i["state"] == "open" and "gpu-test" in i.get("labels", [])
                    and re.search(rf"\(PR #{pr}\)", i["title"])):
                return i["number"]
        return None

    def issue(self, n):
        """(kind, text) of one issue: done, review, progress or todo."""
        i = self.issues.get(n)
        if i is None:
            return "todo", f"#{n} not filed"
        if i["state"] == "closed":
            return "done", f"#{n} done"
        b = self._branch(n)
        pulls = [p for p in self.state["pulls"] if b and p["head"] == b]
        live = next((p for p in pulls if p["state"] == "open"), None)
        if live:
            gpu = self.gpu_test_for(live["number"])
            if gpu:
                return "review", f"#{n} in PR #{live['number']}, awaiting the hardware test #{gpu}"
            return "review", f"#{n} in PR #{live['number']}"
        merged = next((p for p in pulls if p.get("merged_at")), None)
        if merged:
            return "progress", f"#{n} open, PR #{merged['number']} merged"
        if b:
            return "progress", f"#{n} in progress"
        return "todo", f"#{n} not started"

    def status(self, el):
        """The chip of an element: (css class, text), and its issue line."""
        if el.get("hwtest"):
            # hardware is not built here: its state is whether the GPU test has passed
            n = el["hwtest"]
            i = self.issues.get(n)
            if i and i["state"] == "closed":
                return ("chip-ok", f"run on hardware (#{n})"), self._link(n, f"#{n} done")
            return ("chip-todo", f"not yet run on hardware (#{n})"), self._link(n, f"#{n} open")
        if el.get("external"):
            return ("chip-ext", "external"), ""
        rel = el.get("release")
        if rel and rel != CURRENT:
            return ("chip-later", ("stub; " if el.get("stub") else "") + f"later · {rel}"), ""
        issues = el.get("issues", [])
        if not issues:
            return ("chip-ext", "context"), ""
        states = [self.issue(n) for n in issues]
        kinds = {k for k, _ in states}
        line = " · ".join(self._link(n, t) for n, (_, t) in zip(issues, states))
        if kinds == {"done"}:
            chip = ("chip-ok", "built")
        elif "done" in kinds:
            rest = [t for k, t in states if k == "review"]
            chip = ("chip-part", "built; " + rest[0] if len(rest) == 1 and len(kinds) == 2
                    else "partly built")
        elif kinds == {"todo"}:
            chip = ("chip-todo", "not started")
        elif "review" in kinds:
            t = next(t for k, t in states if k == "review")
            pr = re.search(r"PR #\d+", t).group(0)
            chip = ("chip-part", f"in {pr}, awaiting hardware test" if "hardware" in t else f"in {pr}")
        else:
            chip = ("chip-part", "in progress")
        return chip, line

    @staticmethod
    def _link(n, text):
        t = e(text)
        t = re.sub(r"PR #(\d+)", lambda m: f'<a href="{PULLS}{m.group(1)}">PR #{m.group(1)}</a>', t)
        return re.sub(r"^#(\d+)", lambda m: f'<a href="{ISSUES}{m.group(1)}">#{m.group(1)}</a>', t)


def chip_html(chip):
    cls, text = chip
    return f'<span class="chip {cls}">{e(text)}</span>'


# -------------------------------------------------------------- standards
class Standards:
    def __init__(self, elements):
        self.records = {}
        for p in sorted((DATA / "standards").glob("*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            self.records[d["id"]] = d
        doc = json.loads((DATA / "standards-placement.json").read_text(encoding="utf-8"))
        self.rows = doc["placements"]
        errs = []
        for r in self.rows:
            if r["standard"] not in self.records:
                errs.append(f"placement names unknown standard {r['standard']}")
            if r["element"] not in elements.get(r["level"], set()):
                errs.append(f"placement of {r['standard']} names unknown {r['level']} element {r['element']}")
        placed = {r["standard"] for r in self.rows}
        for sid, d in self.records.items():
            if d["conformance"].startswith("mandatory") and sid not in placed:
                errs.append(f"mandatory standard {sid} is placed on no element")
        if errs:
            raise C4Error("data/standards-placement.json: " + "; ".join(errs))

    def at(self, level, element):
        ids = [r["standard"] for r in self.rows if r["level"] == level and r["element"] == element]
        return [self.records[i] for i in ids]

    def chips(self, level, element, always=False):
        items = self.at(level, element)
        if not items:
            return ""
        cls = "c4-stds c4-stds-on" if always else "c4-stds"
        return (f'<span class="{cls}">' + "".join(self.chip(d) for d in items) + "</span>")

    @staticmethod
    def chip(d):
        slug = "std-" + d["id"].lower()
        tip = f'{d["name"]} {d["version"]}: {STD_LABEL[d["state"]]}, {d["conformance"]}'
        if d.get("assessed"):
            tip += f', assessed {d.get("audit_date", "")}'
        mark = '<span class="stdchip-a" aria-label="assessed">✓</span>' if d.get("assessed") else ""
        return (f'<a class="stdchip {STD_CLASS[d["state"]]}" href="{slug}.html" title="{e(tip)}">'
                f'{e(d["id"])}{mark}</a>')


# ---------------------------------------------------------------- helpers
def class_anchors():
    """{crate: anchor} of the class diagram sections on design-diagrams.html."""
    p = ROOT / "content" / "design-diagrams.md"
    out = {}
    if not p.exists():
        return out
    seen = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{1,6} (.+)$", line)
        if not m:
            continue
        text = re.sub(r"[`*]", "", m.group(1)).strip()
        slug = slugify(text, "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        if n:
            slug = f"{slug}_{n}"
        c = re.search(r"\((rustinfer-[a-z-]+)", text)
        if c and c.group(1) not in out:
            out[c.group(1)] = slug
    return out


def key(items):
    return ('<div class="c4-key" aria-label="Key"><span class="c4-key-head">Key</span>'
            + "".join(f'<span class="c4-key-item">{i}</span>' for i in items) + "</div>")


KEY_CHIPS = [
    '<span class="chip chip-ok">built</span> every issue closed on main',
    '<span class="chip chip-part">in PR · partly</span> open pull request, or some issues closed',
    '<span class="chip chip-todo">not started</span> no branch yet',
    '<span class="chip chip-later">later · Rn</span> due in a later release',
]
KEY_STD = ('<span class="stdchip std-ok">ID</span><span class="stdchip std-part">ID</span>'
           '<span class="stdchip std-gap">ID</span><span class="stdchip std-later">ID</span> '
           'standards, when shown: works, partly, missing, later; ✓ assessed')


def view(vid, level, tab, title, intro, subs, toggle=False):
    """One tab: a C4 level or a supplementary diagram, made of one or more views."""
    return (f'<section class="c4-view" id="{vid}" data-tab="{e(tab)}"'
            f'{" data-std" if toggle else ""}>\n'
            f'<h2 class="c4-title"><span class="c4-level">{e(level)}</span> {e(title)}</h2>\n'
            f'<p class="c4-intro">{intro}</p>\n' + "\n".join(subs) + "\n</section>\n")


def sub(sid, title, lede, body, keyitems):
    """One view: at most about nine boxes, a title, one sentence and its key."""
    return (f'<div class="c4-sub" id="{sid}"><h3 class="c4-subtitle">{e(title)}</h3>'
            f'<p class="c4-intro">{lede}</p>{body}{key(keyitems)}</div>')


def groups_of(items, size, cut=None):
    """Split items into runs of at most `size`, breaking only where cut(prev, next) allows."""
    out, cur = [], []
    for x in items:
        if cur and len(cur) >= size and (cut is None or cut(cur[-1], x)):
            out.append(cur)
            cur = []
        cur.append(x)
    if cur:
        out.append(cur)
    return out


def rels(items, names, stds, level):
    lis = []
    for r in items:
        later = r.get("release") and r["release"] != CURRENT
        lis.append(
            f'<li class="c4-rel{" c4-rel-later" if later else ""}" id="{r["id"]}">'
            f'<span class="c4-rel-ends">{e(names[r["from"]])} <span class="c4-arrow" aria-hidden="true">→</span> '
            f'{e(names[r["to"]])}</span>'
            f'<span class="c4-rel-label">{e(r["label"])}</span>'
            f'<span class="c4-rel-tech">[{e(r["tech"])}]</span>'
            + (f'<span class="chip chip-later">later · {r["release"]}</span>' if later else "")
            + stds.chips(level, r["id"]) + "</li>")
    return '<ul class="c4-rels">' + "".join(lis) + "</ul>"


def box(el, kind, chip=None, line="", stds="", link=None, extra="", prefix=""):
    name = e(el["name"])
    if link:
        name = f'<a href="{link}">{name}</a>'
    tech = f': {e(el["tech"])}' if el.get("tech") else ""
    return (f'<div class="c4-box c4-{kind}" id="{prefix}{el["id"]}">'
            f'<div class="c4-box-head"><span class="c4-name">{name}</span>'
            + (chip_html(chip) if chip else "") + "</div>"
            f'<span class="c4-type">[{e(el.get("type", kind.title()))}{tech}]</span>'
            f'<p class="c4-desc">{e(el["desc"])}</p>'
            + (f'<p class="c4-issues">{line}</p>' if line else "") + extra + stds + "</div>")


# ------------------------------------------------------------------ views
def render():
    ctx, cont, comp = load("context.json"), load("containers.json"), load("components.json")
    layers, dyn, dep = load("layers.json"), load("dynamic.json"), load("deployment.json")
    cg = cargo()
    tr = Tracker()
    rank = ranks(cg["crates"])
    comps = {c["id"]: c for c in comp["components"]}
    for c in comp["components"]:
        if c["id"].startswith("rustinfer-") and c["id"] not in cg["crates"]:
            raise C4Error(f"data/c4/components.json names {c['id']}, which is not a crate on main")
    for crate in cg["crates"]:
        if crate != "rustinfer-cli" and crate not in comps:
            raise C4Error(f"crate {crate} has no card in data/c4/components.json")
    elements = {
        "context": {p["id"] for p in ctx["people"]} | {x["id"] for x in ctx["externals"]}
        | {r["id"] for r in ctx["relations"]} | {ctx["system"]["id"]},
        "container": {c["id"] for c in cont["containers"]} | {s["id"] for s in cont["stores"]}
        | {r["id"] for r in cont["relations"]},
        "component": set(comps),
    }
    stds = Standards(elements)
    anchors = class_anchors()
    names = {p["id"]: p["name"] for p in ctx["people"]}
    names |= {x["id"]: x["name"] for x in ctx["externals"]}
    names[ctx["system"]["id"]] = ctx["system"]["name"]
    names |= {c["id"]: c["name"] for c in cont["containers"] + cont["stores"]}
    date = tr.date
    out = []

    # tabs
    tabs = [("c4-context", "1", "Context"), ("c4-containers", "2", "Containers"),
            ("c4-components", "3", "Components"), ("c4-code", "4", "Code"),
            ("c4-layers", "+", "Layers"), ("c4-standards", "+", "Standards"),
            ("c4-dynamic", "+", "Dynamic"), ("c4-deployment", "+", "Deployment")]
    out.append('<div class="c4" id="c4">\n<div class="c4-bar">'
               '<nav class="c4-tabs" aria-label="Diagram levels">'
               + "".join(f'<a class="c4-tab" href="#{v}" data-view="{v}">'
                         f'<span class="c4-tab-no">{n}</span>{t}</a>' for v, n, t in tabs)
               + '</nav><button type="button" class="c4-stdtoggle" aria-pressed="false">'
               'Show standards</button></div>\n')

    # 1 context
    def person(p, prefix=""):
        return (f'<div class="c4-box c4-person" id="{prefix}{p["id"]}"><div class="c4-box-head">'
                f'<span class="c4-name">{e(p["name"])}</span></div>'
                f'<span class="c4-type">[{"Automated actor" if p.get("automated") else "Person"}]</span>'
                f'<p class="c4-desc">{e(p["desc"])}</p></div>')
    sysd = ctx["system"]
    inc = [r for r in ctx["relations"] if r["to"] == sysd["id"]]
    outr = [r for r in ctx["relations"] if r["to"] != sysd["id"]]
    chip, _ = tr.status(sysd)

    def system(prefix=""):
        return ('<div class="c4-row c4-row-one">'
                + box(sysd, "system", chip, "", stds.chips("context", sysd["id"]), link=sysd["link"],
                      extra='<a class="c4-open" href="#c4-containers">open its containers →</a>', prefix=prefix)
                + "</div>")
    ext_chip = lambda x: tr.status(x)[0] if x.get("release") else ("chip-ext", "external")
    k_ctx = ['<span class="kshape kshape-person"></span> person',
             '<span class="kshape kshape-system"></span> rustinfer',
             '<span class="kshape kshape-external"></span> external system or data',
             '<span class="c4-arrow">→</span> relationship: purpose [technology]'] + KEY_CHIPS + [KEY_STD]
    subs = [
        sub("c4-context-people", "Who uses rustinfer",
            "The four kinds of user of SRS §2.3 that touch the product, and what each does with it.",
            '<div class="c4-row">' + "".join(person(p) for p in ctx["people"]) + "</div>"
            + rels(inc, names, stds, "context") + system(), k_ctx),
        sub("c4-context-systems", "What rustinfer uses",
            "The data it reads, the systems it drives and the toolchain it links, with how it talks to each.",
            system("out-") + rels(outr, names, stds, "context") + '<div class="c4-row">'
            + "".join(box(x, "external", ext_chip(x), "", stds.chips("context", x["id"])) for x in ctx["externals"])
            + "</div>", k_ctx)]
    out.append(view("c4-context", "Level 1", "Context", ctx["title"], e(ctx["intro"]), subs, toggle=True))

    # 2 containers
    people = {p["id"]: p for p in ctx["people"]}
    byid = {c["id"]: c for c in cont["containers"] + cont["stores"]}

    def cbox(c, prefix=""):
        kind = "store" if c in cont["stores"] else "container"
        ch, ln = tr.status(c)
        extra = (f'<a class="c4-open" href="{c["link"]}">open its components →</a>'
                 if c.get("link") else "")
        return box(c, kind, ch, ln, stds.chips("container", c["id"]), link=c.get("link"),
                   extra=extra, prefix=prefix)
    users = [r for r in cont["relations"] if r["from"] in people]
    inner = [r for r in cont["relations"] if r["from"] not in people]
    fronts = [byid[i] for i in ("c-cli", "c-lib", "c-http")]
    backs = [byid[i] for i in ("c-lib", "c-device", "s-artifact", "s-catalog")]
    k_cont = ['<span class="kshape kshape-person"></span> person',
              '<span class="kshape kshape-container"></span> container',
              '<span class="kshape kshape-store"></span> data store',
              '<span class="kshape kshape-boundary"></span> rustinfer\'s boundary',
              '<span class="c4-arrow">→</span> relationship: purpose [technology]'] + KEY_CHIPS + [KEY_STD]
    boundary = ('<div class="c4-boundary"><span class="c4-boundary-label">rustinfer '
                '<span class="c4-type">[Software system]</span></span><div class="c4-row">')
    subs = [
        sub("c4-containers-entry", "How people reach rustinfer",
            "The three ways in: the command, the library and, from Release 3, the HTTP server; the command and the server are thin layers over the library.",
            '<div class="c4-row">' + "".join(person(people[p], "in-") for p in cont["people"]) + "</div>"
            + rels(users, names, stds, "container") + boundary + "".join(cbox(c) for c in fronts) + "</div></div>"
            + rels([r for r in inner if r["to"] == "c-lib"], names, stds, "container"), k_cont),
        sub("c4-containers-data", "What the library reads, writes and drives",
            "The library's stores and its one device boundary: the checkpoint it reads in place, the artifact it caches, the tuning catalog, and the GPU behind HIP.",
            boundary + "".join(cbox(c, "d-" if c["id"] == "c-lib" else "") for c in backs) + "</div></div>"
            + rels([r for r in inner if r["to"] != "c-lib"], names, stds, "container")
            + '<div class="c4-row">' + "".join(cbox(c) for c in cont["stores"] if c.get("external")) + "</div>",
            k_cont)]
    out.append(view("c4-containers", "Level 2", "Containers", cont["title"], e(cont["intro"]), subs, toggle=True))

    # 3 components
    def card(c):
        ch, ln = tr.status(c)
        crate = c["id"] if c["id"].startswith("rustinfer-") else None
        nm = c.get("name") or c["id"]
        kind = "Rust crate" if crate else f"module {c['module']}"
        deps = cg["crates"][crate]["deps"] if crate else c.get("uses", [])
        uses = " ".join(f'<a href="#comp-{d}">{e(d.replace("rustinfer-", ""))}</a>' for d in deps)
        page = (f' · <a href="{c["page"]}">page</a>' if c.get("page") else "")
        return (f'<div class="c4-box c4-comp" id="comp-{c["id"]}" data-layer="{c["layer"]}">'
                f'<div class="c4-box-head"><span class="c4-name"><a href="#code-{c["id"]}">{e(nm)}</a></span>'
                f'{chip_html(ch)}</div>'
                f'<span class="c4-type">[{e(kind)}] · {LAYER_NAME[c["layer"]]}{page}</span>'
                f'<p class="c4-desc">{e(c["desc"])}</p>'
                f'<ul class="parts c4-types">' + "".join(f"<li>{e(t)}</li>" for t in c["types"]) + "</ul>"
                + (f'<p class="c4-issues">{ln}</p>' if ln else "")
                + (f'<p class="c4-uses"><span>depends on</span> {uses}</p>' if uses else
                   '<p class="c4-uses"><span>depends on</span> nothing in the workspace</p>')
                + stds.chips("component", c["id"]) + "</div>")
    lib = sorted([c for c in comp["components"] if c["view"] == "library"],
                 key=lambda c: (-rank[c["id"]], c["id"]))
    cli = [c for c in comp["components"] if c["view"] == "cli"]
    libviews = groups_of(lib, 8, cut=lambda a, b: rank[a["id"]] != rank[b["id"]])
    k_comp = ['<span class="kshape kshape-container"></span> component: a crate, or a module of the CLI',
              '<span class="bound-rule"></span> dependencies point down, from Cargo.toml',
              'a name opens its code view'] + KEY_CHIPS + [KEY_STD]
    vw = {v["id"]: v for v in comp["views"]}
    subs = []
    for i, grp in enumerate(libviews):
        bands = sorted({rank[c["id"]] for c in grp}, reverse=True)
        body = ('<div class="c4-boundary"><span class="c4-boundary-label">rustinfer library '
                '<span class="c4-type">[Container: Rust crates]</span></span>')
        for j, b in enumerate(bands):
            cs = [c for c in grp if rank[c["id"]] == b]
            body += f'<span class="c4-band-no">band {b}</span><div class="c4-row">' + "".join(card(c) for c in cs) + "</div>"
            if j < len(bands) - 1:
                body += ('<div class="bound"><span class="bound-rule"></span><span class="bound-label">'
                         'each crate above depends only on crates below it</span></div>')
        body += "</div>"
        lo, hi = min(bands), max(bands)
        span = f"band {hi}" if lo == hi else f"bands {hi} to {lo}"
        subs.append(sub("c4-components-library" if i == 0 else f"c4-components-library-{i + 1}",
                        f"{vw['library']['title']}, {span}",
                        e(vw["library"]["intro"]) if i == 0 else
                        "The crates the upper band builds on, down to the foundation every crate shares.",
                        body, k_comp))
    subs.append(sub("c4-components-cli", vw["cli"]["title"], e(vw["cli"]["intro"]),
                    '<div class="c4-boundary"><span class="c4-boundary-label">rustinfer CLI <span class="c4-type">'
                    '[Container: Rust binary, crate rustinfer-cli]</span></span><div class="c4-row">'
                    + "".join(card(c) for c in cli) + "</div></div>", k_comp))
    out.append(view("c4-components", "Level 3", "Components", "Component diagrams for rustinfer",
                    e("One view per container that has components: the library, in two views by "
                      "dependency band, and the CLI binary. The HTTP server has none yet (Release 3); the "
                      "stores and the device boundary hold data, not code."), subs, toggle=True))

    # 4 code
    def codecard(c):
        crate = c["id"] if c["id"].startswith("rustinfer-") else None
        api = cg["crates"][crate]["api"] if crate else cg["modules"].get(f"rustinfer-cli/src/{c['module']}", [])
        diag = anchors.get(crate or "rustinfer-cli")
        link = (f'<a class="c4-open" href="design-diagrams.html#{diag}">its class diagram →</a>' if diag
                else '<span class="c4-none">no class diagram in docs/uml yet</span>')
        return (f'<div class="c4-box c4-code" id="code-{c["id"]}"><div class="c4-box-head">'
                f'<span class="c4-name"><a href="#comp-{c["id"]}">{e(c.get("name") or c["id"])}</a></span></div>'
                f'<span class="c4-type">[{len(api)} public items{", from lib.rs" if crate else ""}]</span>'
                f'<ul class="parts c4-api">' + "".join(f"<li>{e(a)}</li>" for a in api) + "</ul>" + link + "</div>")
    k_code = ['<span class="kshape kshape-container"></span> component, with its public items',
              'a name returns to the component view']
    subs = [sub(f"c4-code-library-{i + 1}", f"Code view: the library, part {i + 1} of {len(libviews)}",
                "The public items of each crate, as its lib.rs exports them.",
                '<div class="c4-row">' + "".join(codecard(c) for c in grp) + "</div>", k_code)
            for i, grp in enumerate(libviews)]
    subs.append(sub("c4-code-cli", "Code view: the CLI binary",
                    "The public items of each module of rustinfer-cli.",
                    '<div class="c4-row">' + "".join(codecard(c) for c in cli) + "</div>", k_code))
    out.append(view("c4-code", "Level 4", "Code", "Code views for rustinfer",
                    "C4 makes this level optional and says it should be generated. Each card lists the public "
                    f"items its crate exports, read from its <code>lib.rs</code> at commit <code>{e(cg.get('commit', ''))}</code>, "
                    "and links to the crate's class diagram on <a href=\"design-diagrams.html#class-diagram\">design "
                    "diagrams</a>, drawn from the tree's <code>docs/uml</code>; this page draws no new ones.", subs))

    # + layers (the Matins stack)
    first = {}
    for c in lib + cli:
        first.setdefault(c["layer"], c["id"])
    parts = []
    for L in layers["layers"]:
        if "bound" in L:
            parts.append(f'<div class="bound"><span class="bound-rule"></span><span class="bound-label">{e(L["bound"])}</span></div>')
            continue
        ch, ln = tr.status(L)
        target = "#c4-deployment" if L["id"] == "hardware" else f'#comp-{first.get(L["id"], "")}'
        lis = []
        for p in L["parts"]:
            pc, _ = tr.status(p)
            lis.append(f'<li class="part-{pc[0]}" title="{e(pc[1])}">{e(p["name"])}</li>')
        parts.append(
            f'<div class="layer {L["cls"]}" id="layer-{L["id"]}"><div class="layer-head">'
            f'<span class="layer-no">{e(L["no"])}</span>'
            f'<a class="layer-name" href="{target}" data-layer="{L["id"]}">{e(L["name"])}</a>'
            f'{chip_html(ch)}</div>'
            f'<p class="layer-note">{e(L["note"])}</p>'
            f'<ul class="parts">' + "".join(lis) + "</ul>"
            + (f'<p class="c4-issues">{ln}</p>' if ln else "") + "</div>")
    body = ('<div class="stack" role="img" aria-label="From the hardware upward: targets, kernels, '
            'the compiler and the artifact, the runtime with Sluice and the planner, and the interfaces.">'
            + "".join(parts) + "</div>")
    out.append(view("c4-layers", "Supplementary", "Layers", layers["title"],
                    "The same system as a stack, in the form the Matins site uses.",
                    [sub("c4-layers-stack", "The layers of rustinfer",
                         "Read it from the bottom: each band is a layer, the strip between two bands the contract "
                         f"that enforces the boundary, and a layer's name opens its components. The chips are the truth as of {e(date)}.",
                         body, ['<span class="kshape kshape-hw"></span> hardware',
                                '<span class="bound-rule"></span> the contract between two layers',
                                'a part outlined green is built, amber in progress, dashed due later']
                         + KEY_CHIPS)]))

    # + standards
    def stdcard(level, el_id, title, link):
        items = stds.at(level, el_id)
        if not items:
            return ""
        worst = min(items, key=lambda d: STD_RANK[d["state"]])["state"]
        lis = "".join(
            f'<li class="{STD_CLASS[d["state"]]}"><span class="std-name"><a href="std-{d["id"].lower()}.html">'
            f'{e(d["name"])}</a></span><span class="std-scope">{e(d["id"])} · {STD_LABEL[d["state"]]} · {e(d["conformance"])}</span>'
            + (f'<a class="std-tag" href="std-{d["id"].lower()}-audit.html" title="audited {e(d.get("audit_date", ""))}">assessed</a>'
               if d.get("assessed") else "") + "</li>" for d in items)
        return (f'<section class="std-card c4-stdcard {STD_CLASS[worst]}" id="std-at-{el_id}">'
                f'<h4 class="std-sys"><a href="{link}">{e(title)}</a></h4><ul>{lis}</ul></section>')
    rel_names = {r["id"]: f'{names[r["from"]]} → {names[r["to"]]}'
                 for r in ctx["relations"] + cont["relations"]}
    groups = [("Context: relationships and external systems", "context",
               [(r["id"], rel_names[r["id"]], f'#{r["id"]}') for r in ctx["relations"]]
               + [(x["id"], x["name"], f'#{x["id"]}') for x in ctx["externals"]]),
              ("Containers and stores", "container",
               [(c["id"], c["name"], f'#{c["id"]}') for c in cont["containers"] + cont["stores"]]
               + [(r["id"], rel_names[r["id"]], f'#{r["id"]}') for r in cont["relations"]]),
              ("Components", "component",
               [(c["id"], c.get("name") or c["id"], f'#comp-{c["id"]}') for c in lib])]
    k_std = ['<span class="std-key std-ok">works</span>', '<span class="std-key std-part">partly works</span>',
             '<span class="std-key std-gap">missing</span>', '<span class="std-key std-later">later release</span>',
             '<span class="std-tag">assessed</span> an audit page checks it item by item',
             "a card's edge: its weakest standard"]
    subs = []
    for gt, level, els in groups:
        cards = [x for x in (stdcard(level, i, t, l) for i, t, l in els) if x]
        parts_ = groups_of(cards, MAX_BOXES)
        for j, grp in enumerate(parts_, 1):
            suffix = f", part {j} of {len(parts_)}" if len(parts_) > 1 else ""
            subs.append(sub(f"c4-standards-{level}-{j}", gt + suffix,
                            f"The mandatory standards that apply at the {level} level, on the element each applies to.",
                            '<div class="std-map c4-stdmap">' + "".join(grp) + "</div>", k_std))
    mand = [d for d in stds.records.values() if d["conformance"].startswith("mandatory")]
    out.append(view("c4-standards", "Supplementary", "Standards", "Standards diagram for rustinfer",
                    f"The {len(mand)} mandatory standards of SRS §1.4, placed on the most specific element at each "
                    "level by <code>data/standards-placement.json</code>, the same placements the "
                    "<em>show standards</em> chips use. The <a href=\"standards.html\">standards map</a> groups the "
                    "same standards by area.", subs))

    # + dynamic
    phases = []
    for s_ in dyn["steps"]:
        if not phases or phases[-1][0] != s_["phase"]:
            phases.append((s_["phase"], []))
        phases[-1][1].append(s_)
    subs, n = [], 0
    for ph, steps_ in phases:
        rows = []
        for s_ in steps_:
            n += 1
            el = {"issues": [s_["issue"]]} if s_.get("issue") else dict(comps.get(s_["ref"]) or {})
            ch, _ = tr.status(el)
            rows.append(f'<li class="c4-step"><span class="c4-step-no">{n}</span><div>'
                        f'<span class="c4-rel-ends">{e(s_["from"])} <span class="c4-arrow">→</span> {e(s_["to"])}</span>'
                        f'{chip_html(ch)}<span class="c4-rel-label">{e(s_["what"])}</span>'
                        f'<span class="c4-rel-tech">[{e(s_["tech"])}]</span></div></li>')
        subs.append(sub(f"c4-dynamic-{len(subs) + 1}", dyn["phases"][ph]["title"], e(dyn["phases"][ph]["lede"]),
                        '<ol class="c4-steps">' + "".join(rows) + "</ol>",
                        ["number: the order of the interaction", "from → to: who asks whom, then [technology]"]
                        + KEY_CHIPS))
    out.append(view("c4-dynamic", "Supplementary", "Dynamic", dyn["title"], e(dyn["intro"]), subs))

    # + deployment
    allel = {x["id"]: x for x in ctx["externals"]} | {c["id"]: c for c in cont["containers"] + cont["stores"]}
    subs = []
    for nd in dep["nodes"]:
        kids = []
        for k in nd["children"]:
            ref = allel.get(k.get("ref"), {})
            if ref.get("type", "").startswith("External"):
                ch = ("chip-ext", "external")
            else:
                ch, _ = tr.status(ref if ref else k)
            kind = "store" if k.get("store") else ("hw" if k.get("hw") else "container")
            kids.append(f'<div class="c4-box c4-{kind}"><div class="c4-box-head"><span class="c4-name">'
                        f'{e(k["name"])}</span>{chip_html(ch)}</div><span class="c4-type">[{e(k["tech"])}]</span></div>')
        body = (f'<div class="c4-node"><span class="c4-node-label">{e(nd["name"])} '
                f'<span class="c4-type">[Deployment node: {e(nd["tech"])}]</span></span>'
                f'<div class="c4-row">' + "".join(kids) + "</div></div>")
        subs.append(sub(f"c4-deployment-{len(subs) + 1}", nd["name"], e(nd["lede"]), body,
                        ['<span class="kshape kshape-node"></span> deployment node',
                         '<span class="kshape kshape-container"></span> container',
                         '<span class="kshape kshape-store"></span> data store',
                         '<span class="kshape kshape-hw"></span> hardware'] + KEY_CHIPS))
    out.append(view("c4-deployment", "Supplementary", "Deployment", dep["title"], e(dep["intro"]), subs))
    out.append("</div>")
    return "\n".join(out), date
