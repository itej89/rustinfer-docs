#!/usr/bin/env python3
"""Render the rustinfer documentation to static HTML.

No framework. Markdown in, one stylesheet, a nav built from the files
themselves. A documentation site for an inference engine should not need a
toolchain larger than the thing it documents, and a static tree can be
served by anything or read straight off the disk.

Pages live in content/ as Markdown with a small header:

    ---
    title: Design
    section: Design
    order: 10
    summary: One sentence for the index card.
    ---

Fenced ```mermaid blocks are rendered in the browser by mermaid.js; the
diagrams are copied from the rustinfer checkout's docs/uml/ by the reference
generators, so they cannot drift from the tree without a rebuild showing it.

    ./build.py            build into out/
    ./build.py --serve    build, then serve on http://localhost:8080
"""
import functools
import html
import http.server
import os
import pathlib
import re
import shutil
import socketserver
import sys

import markdown
import subprocess

import progress

ROOT = pathlib.Path(__file__).resolve().parent
CONTENT = ROOT / "content"
THEME = ROOT / "theme"
OUT = ROOT / "out"

# The rustinfer checkout the pages describe; the footer names its commit.
RUSTINFER_SRC = pathlib.Path(os.environ.get("RUSTINFER_SRC", ROOT.parent / "rustinfer"))


def source_commit():
    try:
        return subprocess.check_output(
            ["git", "-C", str(RUSTINFER_SRC), "log", "-1", "--format=%h %ad", "--date=short"],
            text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def source_branch():
    try:
        return subprocess.check_output(
            ["git", "-C", str(RUSTINFER_SRC), "branch", "--show-current"], text=True).strip() or "detached"
    except Exception:  # noqa: BLE001
        return "unknown"

SECTIONS = ["Overview", "Design", "Compiler", "Runtime", "Hardware",
            "Development", "Trackers", "Reference", "Standards"]

MD = dict(
    extensions=["extra", "tables", "fenced_code", "codehilite", "toc",
                "sane_lists", "attr_list"],
    extension_configs={"codehilite": {"guess_lang": False,
                                      "noclasses": False,
                                      "pygments_style": "default"}},
)


def parse(path):
    """Split the small header off a page and return (meta, body)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def first_heading(text):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else None


def collect():
    pages = []
    for p in sorted(CONTENT.glob("*.md")):
        meta, text = parse(p)
        pages.append(dict(
            slug=p.stem,
            url=("index.html" if p.stem == "index" else f"{p.stem}.html"),
            title=meta.get("title") or first_heading(text) or p.stem,
            section=meta.get("section", "Overview"),
            order=int(meta.get("order", 100)),
            summary=meta.get("summary", ""),
            group=meta.get("group", ""),
            navtitle=meta.get("navtitle") or "",
            meta=meta,
            text=text,
        ))
    return pages


def nav_html(pages, current):
    """The sidebar: each section, and each group inside it, folds.

    Sections start open. Groups start closed, except the ones on the path to
    the current page, so a reader lands with their place already showing.
    """
    up = "../" * current["url"].count("/")

    def link(p):
        cls = ' class="here"' if p["url"] == current["url"] else ""
        label = p["navtitle"] or p["title"]
        return (f'<li><a href="{up}{p["url"]}"{cls}>'
                f'{html.escape(label)}</a></li>')

    def tree(items):
        node = {"pages": [], "groups": {}}
        for p in items:
            n = node
            for part in [g.strip() for g in p["group"].split("/") if g.strip()]:
                n = n["groups"].setdefault(part, {"pages": [], "groups": {}})
            n["pages"].append(p)
        return node

    def holds_current(n):
        return (any(p["url"] == current["url"] for p in n["pages"])
                or any(holds_current(c) for c in n["groups"].values()))

    def body(n):
        out = []
        n["pages"].sort(key=lambda p: (p["order"], p["title"].lower()))
        out.extend(link(p) for p in n["pages"])
        for name in sorted(n["groups"], key=str.lower):
            child = n["groups"][name]
            opened = " open" if holds_current(child) else ""
            out.append(f'<li><details class="nav-sub"{opened}>'
                       f'<summary>{html.escape(name)}</summary><ul>'
                       + "".join(body(child)) + "</ul></details></li>")
        return out

    out = []
    for section in SECTIONS:
        items = [p for p in pages if p["section"] == section]
        if not items:
            continue
        out.append(f'<details class="nav-group" open>'
                   f'<summary class="nav-head">{html.escape(section)}</summary><ul>'
                   + "".join(body(tree(items))) + "</ul></details>")
    return "\n".join(out)


def lift_mermaid(body):
    """A fenced ```mermaid block becomes <pre class="mermaid"> for mermaid.js,
    kept out of the Markdown converter so it is neither highlighted nor
    escaped twice."""
    return re.sub(r"```mermaid\n(.*?)```",
                  lambda m: '<pre class="mermaid">' + html.escape(m.group(1)) + "</pre>",
                  body, flags=re.S)


def render(pages, page, template):
    md = markdown.Markdown(**MD)
    # [[wiki links]] point at sibling pages by slug.
    body = re.sub(r"\[\[([a-z0-9-]+)\]\]",
                  lambda m: f'<a href="{m.group(1)}.html"><code>{m.group(1)}</code></a>',
                  page["text"])
    body = lift_mermaid(body)
    content = md.convert(body)
    up = "../" * page["url"].count("/")
    heads = re.findall(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', content, re.S)
    toc_items = "".join(
        f'<li><a href="#{i}">{re.sub("<[^>]+>", "", t).strip()}</a></li>'
        for i, t in heads)
    aside = (f'<nav class="toc" aria-label="On this page"><p class="nav-head">On this page</p>'
             f'<ul>{toc_items}</ul></nav>') if len(heads) > 2 else ""
    return (template
            .replace("{{title}}", html.escape(page["title"]))
            .replace("{{tabtitle}}", html.escape(
                page["title"] if page["title"] == "rustinfer"
                else page["title"] + " — rustinfer"))
            .replace("{{summary}}", html.escape(page["summary"]))
            .replace("{{nav}}", nav_html(pages, page))
            .replace("{{content}}", content)
            .replace("{{aside}}", aside)
            .replace("{{commit}}", html.escape(source_commit()))
            .replace("{{branch}}", html.escape(source_branch()))
            .replace("{{up}}", up))


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    template = (THEME / "base.html").read_text(encoding="utf-8")
    pages = collect()
    # the Progress page: counted from the other pages' trackers
    pages.append(dict(
        slug="progress", url="progress.html", title="Progress",
        section="Overview", order=2,
        summary="Every tracked item on this site, counted by its state, in pies.",
        group="", navtitle="", meta={},
        text="# Progress\n\n" + progress.page(pages, SECTIONS),
    ))
    for page in pages:
        dest = OUT / page["url"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(pages, page, template), encoding="utf-8")
    shutil.copy(THEME / "style.css", OUT / "style.css")
    if (CONTENT / "images").is_dir():
        shutil.copytree(CONTENT / "images", OUT / "images")
    print(f"built {len(pages)} pages into {OUT}")
    missing = [p["title"] for p in pages if not p["summary"] and p["section"] != "Overview"]
    if missing:
        print(f"  {len(missing)} without a summary: {', '.join(missing[:4])}"
              + (" ..." if len(missing) > 4 else ""))


def serve(port=8080):
    # Serve by path rather than by changing directory: a rebuild replaces
    # out/, and a server whose working directory had been deleted answered
    # nothing at all with no error worth reading.
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(OUT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        print(f"http://localhost:{port}  (ctrl-c to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve(int(os.environ.get("PORT", 8080)))
