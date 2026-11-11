"""The Progress page: every tracked item on the site, counted by state.

Ported from Matins (its progress.py), with rustinfer's status words added.

Read at build time from the pages' own tables, so it cannot drift from
them: a table whose first column is an item's id (R1-3, OI-009, RI-KC-002,
ADR-005) and which has a "Status" or "State" column is a tracker. Each
item's state is read from the start of that cell, the way the trackers
write it ("**In review** 2026-11-11 ...", "Open", "Draft", "Decided ...").

Drawn as pies in plain SVG: one for the whole site, one per page, or one
per heading on a page whose header says `cards: headings` (the requirements
page, one card per SRS component).
"""
import html
import math
import re

from markdown.extensions.toc import slugify

ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+[a-z]?$")
RULE = re.compile(r"^\|[\s:|-]+\|$")

# (key, label, the words that put an item there); checked in this order,
# the first that matches wins. Awaiting is read from anywhere in the cell
# ("Fixed ..., on the board with the next image"); the rest from its start.
# rustinfer's words: draft, approved, specified and not started are open
# work (a requirement not yet implemented); in review and pr open are
# progress; implemented, merged and closed as done are done; withdrawn is
# dropped, as it was.
STATES = [
    ("dropped", "Not pursued", r"won.?t fix|by design|not needed|out of scope|withdrawn|n/a\b|^closed(?! as done)|not our bug|not reproducible|"
                    r"premise wrong|deliberately|^not offered|^informative|^never sent|^dropped$"),
    ("awaiting", "Awaiting the board",
     r"with the next (image|release)|in the next release|in the release after|to verify on the board|shipping\b|"
     r"^in the build|^awaiting$"),
    ("progress", "In progress", r"^(partly|improving|in progress|in review|pr open|prototype|done as a prototype|built|designed|"
                                r"written|running|in the driver|started|underway)"),
    ("done", "Done", r"^(done|fixed|verified|met|working|shipped|conforms|passes|seen|on the board|measured|"
                     r"audited|confirmed|listed|decided|supported|in place|complete|parity|installed|tested|"
                     r"implemented|merged|closed as done)"),
    ("open", "Open", r"^(open|not started|not tried|fails|failing|missing|to do|todo|broken|not met|unmet|"
                     r"draft|approved|specified)"),
    ("later", "Later", r"^(later|planned|next|to build|needs|waits? on|deferred|parked|held)"),
]
OTHER = ("progress", "In progress")
ORDER = ["done", "awaiting", "progress", "later", "open", "dropped"]
LABEL = {k: l for k, l, _ in STATES}
PENDING = ("awaiting", "progress", "later", "open")


def classify(cell):
    s = re.sub(r"[*`_]", "", cell).strip().lower()
    # what a status was before ("...; was: Shipping in the next release")
    # is history, never its state now
    s = re.split(r"[;.,]\s*(?:was|before|earlier):", s)[0]
    for key, _, words in STATES:
        # awaiting the board is read from the status's first sentence: a
        # done row's account of how it got there ("..., in the release
        # after r731, verified ...") is not a wait
        hay = s.split(". ")[0] if key == "awaiting" else s
        if re.search(words, hay):
            return key
    return OTHER[0]


def strip_md(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return re.sub(r"[*`]", "", s).strip()


def items(text, with_heading=False):
    """(id, what, state, status text) for each tracked row of a page; with
    `with_heading`, a fifth element names the nearest ## heading above."""
    out, head, heading = [], None, ""
    for line in text.split("\n"):
        if line.startswith("## "):
            heading = line[3:].strip()
        if not line.startswith("|"):
            head = None
            continue
        if RULE.match(line.strip()):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not ID.match(cells[0]):
            head = [c.lower() for c in cells]
            continue
        if head is None:
            continue
        col = next((i for i, h in enumerate(head) if h in ("status", "state")), None)
        if col is None or col >= len(cells):
            continue
        what = strip_md(cells[1]) if len(cells) > 1 and col != 1 else ""
        row = (cells[0], what, classify(cells[col]), strip_md(cells[col]))
        out.append(row + (heading,) if with_heading else row)
    return out


def pie(counts, size, hole=0.0):
    """A pie (or a ring, with a hole) of the states, in SVG."""
    total = sum(counts.values())
    r = size / 2
    parts = []
    if total:
        a = -math.pi / 2
        for key in ORDER:
            n = counts.get(key, 0)
            if not n:
                continue
            if n == total:
                parts.append(f'<circle cx="{r}" cy="{r}" r="{r}" class="st-{key}"/>')
                break
            b = a + 2 * math.pi * n / total
            large = 1 if b - a > math.pi else 0
            x0, y0 = r + r * math.cos(a), r + r * math.sin(a)
            x1, y1 = r + r * math.cos(b), r + r * math.sin(b)
            parts.append(f'<path class="st-{key}" d="M{r},{r} L{x0:.2f},{y0:.2f} '
                         f'A{r},{r} 0 {large} 1 {x1:.2f},{y1:.2f} Z"/>')
            a = b
    if hole:
        parts.append(f'<circle cx="{r}" cy="{r}" r="{r * hole:.2f}" class="pie-hole"/>')
    label = ", ".join(f"{counts[k]} {LABEL[k].lower()}" for k in ORDER if counts.get(k))
    return (f'<svg class="pie" width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
            f'role="img" aria-label="{html.escape(label)}">{"".join(parts)}</svg>')


def tally(rows):
    c = {}
    for row in rows:
        c[row[2]] = c.get(row[2], 0) + 1
    return c


def legend(counts):
    return "".join(
        f'<li><span class="sw st-{k}"></span>{LABEL[k]} <b>{counts.get(k, 0)}</b></li>'
        for k in ORDER)


WAITS = re.compile(r"waits? on the person|the person.s look|needs a person|only the owner", re.I)


def week(pages, days=7):
    """The last `days` days from git: the rows that closed, the rows
    opened, the rows that moved state; nothing when git is not there."""
    import datetime
    import pathlib
    import subprocess
    root = pathlib.Path(__file__).resolve().parent
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    try:
        rev = subprocess.run(["git", "log", "-1", "--format=%H", "--before", since + " 00:00"],
                             capture_output=True, text=True, cwd=root).stdout.strip()
    except OSError:
        return ""
    if not rev:
        return ""
    counted = [p for p in pages if p["slug"] != "progress"]
    old = {}
    for p in counted:
        r = subprocess.run(["git", "show", f"{rev}:content/{p['slug']}.md"], capture_output=True, text=True, cwd=root)
        if r.returncode == 0:
            for i, _, k, _ in items(r.stdout):
                old[i] = k
    now, what, url = {}, {}, {}
    for p in counted:
        for i, w, k, _ in items(p["text"]):
            now[i], what[i], url[i] = k, w, p["url"]
    done = ("done", "dropped")
    closed = sorted(i for i, k in now.items() if k in done and old.get(i) not in done)
    opened = sorted(i for i, k in now.items() if i not in old and k not in done)
    moved = sorted(i for i, k in now.items() if i in old and old[i] != k and k not in done)

    def lst(ids):
        if not ids:
            return "<p>none</p>"
        return '<ul class="dash-items">' + "".join(
            f'<li><span class="sw st-{now[i]}"></span><a href="{url[i]}"><code>{html.escape(i)}</code></a> '
            f'{html.escape(what[i][:90])}</li>' for i in ids) + "</ul>"
    return ('<section class="waits"><h2 id="this-week">This week</h2>'
            f'<p class="dash-sub">Since {since}, as the trackers moved: {len(closed)} closed, {len(opened)} opened, '
            f'{len(moved)} changed state ({len(old)} items then, {len(now)} now).</p>'
            f'<details open><summary>{len(closed)} closed</summary>{lst(closed)}</details>'
            f'<details><summary>{len(opened)} opened</summary>{lst(opened)}</details>'
            f'<details><summary>{len(moved)} changed state</summary>{lst(moved)}</details></section>')


def waiting(tracked):
    """What waits on the person: every row whose status says so, with what
    to do, from its own tracker (the rows say it; nothing is kept here)."""
    rows = [(p, r) for p, rows in tracked for r in rows
            if r[2] not in ("done", "dropped") and WAITS.search(r[3])]
    if not rows:
        return '<section class="waits"><h2 id="waits-on-you">Waits on you</h2><p class="dash-sub">Nothing.</p></section>'
    items = []
    for p, (i, what, _, status) in rows:
        todo = re.sub(r"^[\s:;,.]*", "", WAITS.split(status, 1)[-1])
        items.append(f'<li><a href="{p["url"]}">{html.escape(i)}</a> {html.escape(what)}'
                     + (f': <em>{html.escape(todo[:220])}</em>' if todo else '') + '</li>')
    return ('<section class="waits"><h2 id="waits-on-you">Waits on you</h2>'
            f'<p class="dash-sub">{len(rows)} things only you can do or see, from the trackers; '
            'each leaves this list when its row is closed.</p><ol>' + ''.join(items) + '</ol></section>')


def cards_of(p):
    """The cards a page contributes: one, or one per ## heading when its
    header says `cards: headings`."""
    if p.get("meta", {}).get("cards") == "headings":
        groups, order = {}, []
        for i, w, k, s, h in items(p["text"], with_heading=True):
            if h not in groups:
                groups[h] = []
                order.append(h)
            groups[h].append((i, w, k, s))
        # the same slug the Markdown toc extension gives the heading
        return [(h, p["url"] + "#" + slugify(h, "-"), groups[h]) for h in order]
    rows = items(p["text"])
    title = p["navtitle"] if p["navtitle"] and p["navtitle"] != "Tracker" else p["title"]
    return [(title, p["url"], rows)] if rows else []


def page(pages, sections):
    """The Progress page's HTML, from the other pages."""
    tracked = []
    for p in pages:
        if p["slug"] == "progress":
            continue
        rows = items(p["text"])
        if rows:
            tracked.append((p, rows))
    every = [r for _, rows in tracked for r in rows]
    total = tally(every)
    pending = sum(total.get(k, 0) for k in PENDING)
    closed = total.get("done", 0) + total.get("dropped", 0)
    pct = round(100 * closed / len(every)) if every else 0

    out = [
        '<p class="dash-sub">Under the <a href="roadmap.html">roadmap</a>: '
        '<a href="#trackers">trackers</a>, <a href="#requirements">the requirements</a>, '
        'then the rest.</p>',
        waiting(tracked),
        week(pages),
        '<div class="dash">',
        '<p class="dash-lede">Every item the trackers on this site hold, counted by its state as the '
        'tracker writes it. Built with the site, so it is as current as the pages.</p>',
        '<section class="dash-total">',
        pie(total, 168, 0.58),
        f'<div class="dash-figure"><span class="dash-big">{pct}%</span>'
        f'<span class="dash-small">closed: {closed} of {len(every)} items, '
        f'{pending} pending, in {len(tracked)} trackers</span>'
        f'<ul class="dash-legend">{legend(total)}</ul></div>',
        '</section>',
    ]
    # under the roadmap: the trackers first, then the requirements they
    # implement, then the rest
    head = ["Trackers", "Reference"]
    shown = {"Reference": "Requirements"}
    for section in head + [x for x in sections if x not in head]:
        group = [(p, rows) for p, rows in tracked if p["section"] == section]
        if not group:
            continue
        cards = [c for p, _ in group for c in cards_of(p)]
        cards.sort(key=lambda c: (-sum(1 for r in c[2] if r[2] in PENDING), c[0].lower()))
        st = tally([r for _, rows in group for r in rows])
        name = shown.get(section, section)
        out.append(f'<h2 id="{re.sub(r"[^a-z0-9]+", "-", name.lower())}">{html.escape(name)}</h2>')
        out.append(f'<p class="dash-sub">{pie(st, 18)} '
                   + " · ".join(f"{st[k]} {LABEL[k].lower()}" for k in ORDER if st.get(k))
                   + "</p>")
        out.append('<div class="dash-grid">')
        for title, url, rows in cards:
            c = tally(rows)
            todo = [r for r in rows if r[2] in PENDING]
            done = len(rows) - len(todo)
            card = [
                '<article class="dash-card">',
                f'<header>{pie(c, 64)}<div><a href="{url}">{html.escape(title)}</a>'
                f'<span class="dash-count">{done} of {len(rows)} closed</span></div></header>',
                '<p class="dash-bar">' + " ".join(
                    f'<span class="tag st-{k}">{c[k]} {LABEL[k].lower()}</span>'
                    for k in ORDER if c.get(k)) + "</p>",
            ]
            if todo:
                todo.sort(key=lambda r: PENDING.index(r[2]))
                card.append(f'<details><summary>{len(todo)} pending</summary><ul class="dash-items">')
                for i, what, k, status in todo:
                    tip = html.escape(status[:300])
                    card.append(f'<li title="{tip}"><span class="sw st-{k}"></span>'
                                f'<code>{html.escape(i)}</code> {html.escape(what[:110])}</li>')
                card.append("</ul></details>")
            card.append("</article>")
            out.append("".join(card))
        out.append("</div>")
    out.append("</div>")
    return "\n".join(out)
