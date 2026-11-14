#!/usr/bin/env python3
"""The six UML diagrams of docs/uml/, drawn as HTML for the site.

The Mermaid files in the rustinfer tree stay the committed source of every
diagram; this site renders no Mermaid. A small parser for the subset of
Mermaid those files use reads each block and draws it in the site's own
diagram style (cards, numbered steps, state chips), with the file's prose
copied around it and a link to the block in the tree:

- a class diagram becomes cards per type, grouped by crate: the type's
  kind, up to six key members, and its relations as "contains / holds /
  uses" lines under the card instead of a web of lines;
- a sequence diagram becomes numbered steps: from, to, what is passed, and
  the requirement ids the step names; `par`, `loop`, `alt` and `critical`
  blocks become labelled groups;
- the component diagram becomes cards in bands computed from its edges, so
  every dependency points down; the activity diagram becomes numbered step
  cards with their branches; a state diagram becomes state cards with their
  transitions.

No view holds more than MAX_BOXES cards or MAX_STEPS steps: a larger diagram
is split into several views, each with its own title. Anything the parser
does not recognise stops the script (exit 1) rather than being dropped, and
build.py refuses a page that still holds a Mermaid fence.
"""
import html
import re
import sys

from common import RUSTINFER, WEB, commit, header, write

ORDER = ["component", "class", "sequence", "state", "activity", "concurrency"]
UML = RUSTINFER / "docs/uml"
MAX_BOXES = 9
MAX_STEPS = 10
KEY_MEMBERS = 6
REQ = re.compile(r"\bRI-[A-Z]+-\d{3}\b")
e = html.escape


class ParseError(Exception):
    pass


def sha():
    return commit().split()[0]


def src_link(kind, line):
    return (f'<a class="ud-src" href="{WEB}/blob/{sha()}/docs/uml/{kind}-diagram.md#L{line}">'
            f'view source</a>')


def label(text):
    """Mermaid label text as plain text: entity codes and <br/> decoded."""
    t = re.sub(r"<br\s*/?>", " · ", text)
    t = re.sub(r"#(\d+);", lambda m: chr(int(m.group(1))), t)
    return t.replace("~", "")


def generic(name):
    """Mermaid generics `Vec~T~` as Rust's `Vec<T>`."""
    out, opened = [], False
    for ch in name:
        if ch == "~":
            out.append(">" if opened else "<")
            opened = not opened
        else:
            out.append(ch)
    return "".join(out)


def chunks(items, size):
    n = max(1, -(-len(items) // size))
    per = -(-len(items) // n)
    return [items[i:i + per] for i in range(0, len(items), per)]


def view(vid, title, lede, body, keyitems, source):
    keyhtml = ""
    if keyitems:
        keyhtml = ('<div class="c4-key" aria-label="Key"><span class="c4-key-head">Key</span>'
                   + "".join(f'<span class="c4-key-item">{k}</span>' for k in keyitems) + "</div>")
    return (f'<section class="ud-view" id="{vid}">'
            f'<div class="ud-head"><h4 class="ud-title">{e(title)}</h4>{source}</div>'
            f'<p class="ud-lede">{lede}</p>{body}{keyhtml}</section>')


# ------------------------------------------------------------------ class
REL = re.compile(r'^(\S+?)\s+(?:"([^"]*)"\s+)?(<\|--|--\|>|\.\.\|>|<\|\.\.|\*--|--\*|o--|--o|-->|<--|\.\.>|<\.\.|--|\.\.)'
                 r'\s+(?:"([^"]*)"\s+)?(\S+?)(?:\s*:\s*(.*))?$')
REL_WORD = {"*--": "contains", "--*": "contained in", "o--": "holds", "--o": "held by",
            "-->": "uses", "<--": "used by", "..>": "depends on", "<..": "needed by",
            "<|--": "is implemented by", "--|>": "implements", "..|>": "implements",
            "<|..": "is implemented by", "--": "is linked to", "..": "is linked to"}


def parse_class(src):
    lines = src.split("\n")
    if lines[0].strip() != "classDiagram":
        raise ParseError(f"not a class diagram: {lines[0]!r}")
    classes, rels, i = {}, [], 1
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        if not s or s.startswith("%%"):
            continue
        m = re.match(r"^class (\S+?)\s*\{$", s)
        if m:
            c = classes.setdefault(m.group(1), {"ann": [], "fields": [], "methods": [], "values": []})
            while True:
                if i >= len(lines):
                    raise ParseError(f"class {m.group(1)} is not closed")
                b = lines[i].strip()
                i += 1
                if b == "}":
                    break
                if not b:
                    continue
                if b.startswith("<<") and b.endswith(">>"):
                    a_ = b[2:-2]
                    if ":" in a_:
                        # <<enumeration: A, B, C>>: the kind, then its values
                        a_, vals = a_.split(":", 1)
                        c["values"] += [v.strip() for v in vals.split(",") if v.strip()]
                    c["ann"].append(a_.strip())
                elif re.match(r"^[A-Z]\w*\([^()]*\)$", b):
                    # an enum variant with data, Replace(op name): no visibility, no return type
                    c["values"].append(b)
                elif re.match(r"^[+\-#~]?\w[^()]*\(.*\)", b):
                    c["methods"].append(b.lstrip("+-#~"))
                elif re.match(r"^[+\-#~]\S", b):
                    c["fields"].append(b.lstrip("+-#~"))
                elif re.match(r"^\w[^{}]*$", b):
                    c["values"].append(b)
                else:
                    raise ParseError(f"class {m.group(1)}: member line not understood: {b!r}")
            continue
        m = re.match(r"^class (\S+)$", s)
        if m:
            classes.setdefault(m.group(1), {"ann": [], "fields": [], "methods": [], "values": []})
            continue
        m = re.match(r"^<<(.+)>>\s+(\S+)$", s)
        if m:
            classes.setdefault(m.group(2), {"ann": [], "fields": [], "methods": [], "values": []})["ann"].append(m.group(1))
            continue
        m = REL.match(s)
        if m:
            a, _, arrow, _, b, lab = m.groups()
            rels.append((a, arrow, b, label(lab or "")))
            for n in (a, b):
                classes.setdefault(n, {"ann": [], "fields": [], "methods": [], "values": []})
            continue
        raise ParseError(f"class diagram line not understood: {s!r}")
    return classes, rels


def render_class(n, src, where, crate, kind, line):
    classes, rels = parse_class(src)
    out_rel = {c: [] for c in classes}
    for a, arrow, b, lab in rels:
        word = REL_WORD[arrow]
        if arrow in ("<|--", "<--", "<..", "--*", "--o", "<|.."):
            # written right to left: state it from the right-hand type
            a, b = b, a
            word = {"<|--": "implements", "<--": "uses", "<..": "depends on", "--*": "contains",
                    "--o": "holds", "<|..": "implements"}[arrow]
        out_rel[a].append((word, b, lab))
    # order the cards by a walk of the relations, so related types sit together
    adj = {c: [] for c in classes}
    for a, _, b, _ in rels:
        adj[a].append(b)
        adj[b].append(a)
    order, seen = [], set()
    for start in classes:
        queue = [start]
        while queue:
            c = queue.pop(0)
            if c in seen:
                continue
            seen.add(c)
            order.append(c)
            queue += [x for x in adj[c] if x not in seen]
    slug = f"ud{n}"
    groups = chunks(order, MAX_BOXES)
    views = []
    for k, grp in enumerate(groups, 1):
        cards = []
        for c in grp:
            d = classes[c]
            ann = d["ann"][0] if d["ann"] else ""
            word = re.split(r"[ ,;]", ann.strip(), 1)[0].lower() if ann else ""
            tag = {"enumeration": "enum", "interface": "trait", "trait": "trait", "function": "function",
                   "functions": "function", "module": "module"}.get(word)
            if tag is None:
                tag = "enum" if d["values"] and not d["fields"] else "struct"
            rest = ann[len(word):].lstrip(" ,;") if tag != "struct" or word == "struct" else ann
            notes = [x for x in [rest] + d["ann"][1:] if x]
            members = d["fields"] + d["methods"]
            shown = members[:KEY_MEMBERS]
            more = len(members) - len(shown)
            body = ""
            if shown:
                body += '<ul class="ud-members">' + "".join(
                    f"<li><code>{e(generic(m))}</code></li>" for m in shown) + "</ul>"
            if d["values"]:
                vals = d["values"][:8]
                body += ('<ul class="parts ud-values">' + "".join(f"<li>{e(generic(v))}</li>" for v in vals)
                         + (f'<li class="ud-more">+{len(d["values"]) - 8} more</li>' if len(d["values"]) > 8 else "")
                         + "</ul>")
            if more:
                body += f'<p class="ud-more">and {more} more member{"s" if more > 1 else ""} in the source</p>'
            rl = out_rel[c]
            if rl:
                body += '<ul class="ud-rels">' + "".join(
                    f'<li><span class="ud-relword">{e(w)}</span> <a href="#{slug}-{re.sub(r"[^A-Za-z0-9]", "", t)}">'
                    f'{e(generic(t))}</a>{(" — " + e(lab)) if lab else ""}</li>' for w, t, lab in rl) + "</ul>"
            cards.append(f'<div class="c4-box ud-type ud-{e(tag)}" id="{slug}-{re.sub(r"[^A-Za-z0-9]", "", c)}">'
                         f'<div class="c4-box-head"><span class="c4-name"><code>{e(generic(c))}</code></span>'
                         f'<span class="ud-tag">{e(tag)}</span></div>'
                         f'<span class="c4-type">{e(crate)}</span>'
                         + "".join(f'<p class="ud-more">{e(x)}</p>' for x in notes) + f'{body}</div>')
        title = f"Figure {n}{chr(96 + k) if len(groups) > 1 else ''}. {where}"
        if len(groups) > 1:
            title += f", types {k} of {len(groups)}"
        names = ", ".join(generic(c) for c in grp[:4]) + (f" and {len(grp) - 4} more" if len(grp) > 4 else "")
        lede = (f"The types of {e(where)}: {e(names)}. Each card gives the type's kind, up to "
                f"{KEY_MEMBERS} of its members, and what it contains or uses; a name links to its card.")
        views.append(view(f"{slug}{chr(96 + k)}", title, lede, '<div class="c4-row ud-row">' + "".join(cards) + "</div>",
                          ['<span class="ud-tag ud-struct">struct</span> <span class="ud-tag ud-enum">enum</span> '
                           '<span class="ud-tag ud-trait">trait</span> the kind of type',
                           '<span class="ud-relword">contains</span> owns it · <span class="ud-relword">holds</span> '
                           'refers to it · <span class="ud-relword">uses</span>, <span class="ud-relword">depends on</span> calls or names it'],
                          src_link(kind, line) if k == 1 else ""))
    return "\n".join(views), len(groups)


# --------------------------------------------------------------- sequence
MSG = re.compile(r"^([A-Za-z0-9_]+)\s*(-->>|->>|-->|->|--x|-x|--\)|-\))\s*([A-Za-z0-9_]+)\s*:\s*(.*)$")


def parse_sequence(src):
    lines = src.split("\n")
    if lines[0].strip() != "sequenceDiagram":
        raise ParseError(f"not a sequence diagram: {lines[0]!r}")
    parts, items = {}, []
    for raw in lines[1:]:
        s = raw.strip()
        if not s or s.startswith("%%"):
            continue
        m = re.match(r"^(participant|actor)\s+(\S+)(?:\s+as\s+(.+))?$", s)
        if m:
            parts[m.group(2)] = label(m.group(3) or m.group(2))
            continue
        m = MSG.match(s)
        if m:
            a, arrow, b, text = m.groups()
            for x in (a, b):
                parts.setdefault(x, x)
            items.append(("msg", a, arrow, b, label(text)))
            continue
        m = re.match(r"^(par|and|loop|alt|else|opt|critical|break|rect)\b\s*(.*)$", s)
        if m:
            items.append(("open" if m.group(1) not in ("and", "else") else "next", m.group(1), label(m.group(2))))
            continue
        if s == "end":
            items.append(("end",))
            continue
        m = re.match(r"^[Nn]ote (over|left of|right of) ([^:]+):\s*(.*)$", s)
        if m:
            items.append(("note", m.group(2).strip(), label(m.group(3))))
            continue
        raise ParseError(f"sequence diagram line not understood: {s!r}")
    depth = sum(1 for x in items if x[0] == "open") - sum(1 for x in items if x[0] == "end")
    if depth:
        raise ParseError("sequence diagram blocks are not balanced")
    return parts, items


BLOCK_WORD = {"par": "in parallel", "and": "and at the same time", "loop": "repeated",
              "alt": "if", "else": "otherwise", "opt": "only if", "critical": "critical section",
              "break": "stop if", "rect": "group"}


def render_sequence(n, src, where, kind, line, reqs):
    parts, items = parse_sequence(src)
    lane = {p: i % 6 for i, p in enumerate(parts)}
    rows, step, depth, stack = [], 0, 0, []
    for it in items:
        if it[0] == "msg":
            step += 1
            _, a, arrow, b, text = it
            ret = arrow.startswith("--")
            ids = REQ.findall(text)
            rows.append(("step", depth, list(stack),
                         f'<li class="ud-step" style="--d:{depth}"><span class="c4-step-no">{step}</span>'
                         f'<div class="ud-step-body"><span class="ud-lanes"><span class="ud-lane ud-l{lane[a]}">{e(parts[a])}</span>'
                         f'<span class="ud-dir" aria-label="{"returns to" if ret else "calls"}">{"⟵ returns to" if ret else "→"}</span>'
                         f'<span class="ud-lane ud-l{lane[b]}">{e(parts[b])}</span></span>'
                         f'<span class="ud-what">{e(text)}</span>'
                         + "".join(f'<span class="ud-req">{r}</span>' for r in dict.fromkeys(ids)) + "</div></li>"))
        elif it[0] in ("open", "next"):
            _, word, text = it
            head = BLOCK_WORD[word] + ((": " + text) if text else "")
            if it[0] == "open":
                depth += 1
                stack.append(head)
            else:
                stack[-1] = head
            rows.append(("block", depth, list(stack), f'<li class="ud-block" style="--d:{depth - 1}"><span>{e(head)}</span></li>'))
        elif it[0] == "end":
            depth -= 1
            stack.pop()
        elif it[0] == "note":
            rows.append(("note", depth, list(stack), f'<li class="ud-note" style="--d:{depth}">{e(it[2])}</li>'))
    # views of at most MAX_STEPS steps: break where no block is open if one comes
    # soon enough, else inside the block, which the next view names again
    pieces, cur, count = [], [], 0
    for r in rows:
        if r[0] == "step" and count >= MAX_STEPS and (r[1] == 0 or count >= MAX_STEPS + 2):
            pieces.append(cur)
            cur, count = [], 0
            for d, head in enumerate(r[2]):
                cur.append(("block", d + 1, [], f'<li class="ud-block" style="--d:{d}"><span>{e(head)}, continued</span></li>'))
        cur.append(r)
        if r[0] == "step":
            count += 1
    if cur:
        pieces.append(cur)
    if len(pieces) > 1 and sum(1 for r in pieces[-1] if r[0] == "step") < 3 \
            and sum(1 for r in pieces[-2] if r[0] == "step") + sum(1 for r in pieces[-1] if r[0] == "step") <= MAX_STEPS + 2:
        last = pieces.pop()
        pieces[-1] += [r for r in last if not (r[0] == "block" and r[3].endswith(", continued</span></li>"))]
    total = step
    views, first = [], 1
    lanes = "".join(f'<span class="ud-lane ud-l{lane[p]}">{e(t)}</span>' for p, t in parts.items())
    for k, piece in enumerate(pieces, 1):
        nsteps = sum(1 for r in piece if r[0] == "step")
        title = f"Figure {n}{chr(96 + k) if len(pieces) > 1 else ''}. {where}"
        if len(pieces) > 1:
            title += f", steps {first} to {first + nsteps - 1} of {total}"
        lede = (f"Who calls whom, in order: each numbered step names the caller, the callee and what is passed; "
                f"a step that answers is marked <em>returns to</em>.{(' Requirements: ' + ', '.join(reqs) + '.') if reqs and k == 1 else ''}")
        body = f'<div class="ud-parts">{lanes}</div><ol class="ud-steps">' + "".join(r[3] for r in piece) + "</ol>"
        views.append(view(f"ud{n}{chr(96 + k)}", title, lede, body,
                          ["a colour is one participant, named in the row above the steps",
                           '<span class="ud-block-key">in parallel</span> a group of steps: in parallel, repeated, if / otherwise, critical section',
                           '<span class="ud-req">RI-…</span> the requirement a step names'],
                          src_link(kind, line) if k == 1 else ""))
        first += nsteps
    return "\n".join(views), len(pieces)


# ------------------------------------------------------------------ state
def parse_state(src):
    lines = src.split("\n")
    if lines[0].strip() not in ("stateDiagram-v2", "stateDiagram"):
        raise ParseError(f"not a state diagram: {lines[0]!r}")
    order, trans = [], []
    for raw in lines[1:]:
        s = raw.strip()
        if not s or s.startswith("%%"):
            continue
        m = re.match(r"^(\[\*\]|\w+)\s*-->\s*(\[\*\]|\w+)(?:\s*:\s*(.*))?$", s)
        if not m:
            raise ParseError(f"state diagram line not understood: {s!r}")
        a, b, lab = m.groups()
        for x in (a, b):
            if x != "[*]" and x not in order:
                order.append(x)
        trans.append((a, b, label(lab or "")))
    return order, trans


def render_state(n, src, where, kind, line):
    order, trans = parse_state(src)
    start = [b for a, b, _ in trans if a == "[*]"]
    cls = {s: ("ud-bad" if re.search(r"Refused|Failed|Cancelled", s) else "ud-good" if s in ("Loaded", "Serving", "Finished", "Opened", "Verified") else "") for s in order}
    groups = chunks(order, MAX_BOXES)
    views = []
    for k, grp in enumerate(groups, 1):
        cards = []
        for s in grp:
            outs = [(b, lab) for a, b, lab in trans if a == s]
            ins = sum(1 for a, b, _ in trans if b == s)
            lis = "".join(
                f'<li><span class="ud-relword">{"ends" if b == "[*]" else "→"}</span> '
                + ("" if b == "[*]" else f'<a class="ud-state-ref" href="#ud{n}-{b}">{e(b)}</a>')
                + (f' <span class="ud-when">{"when " if b != "[*]" else ""}{e(lab)}</span>' if lab else "")
                + "</li>" for b, lab in outs)
            cards.append(f'<div class="c4-box ud-state {cls[s]}" id="ud{n}-{s}"><div class="c4-box-head">'
                         f'<span class="c4-name">{e(s)}</span>'
                         + ('<span class="ud-tag">start</span>' if s in start else "")
                         + f'</div><span class="c4-type">{ins} way{"s" if ins != 1 else ""} in</span>'
                         + (f'<ul class="ud-rels">{lis}</ul>' if lis else '<p class="ud-more">no way out</p>') + "</div>")
        title = f"Figure {n}{chr(96 + k) if len(groups) > 1 else ''}. {where}"
        lede = (f"Each card is one state; its lines are the ways out of it and what causes each. "
                f"It starts in {e(', '.join(start))}.")
        views.append(view(f"ud{n}{chr(96 + k)}", title, lede, '<div class="c4-row ud-row">' + "".join(cards) + "</div>",
                          ['<span class="kshape ud-kgood"></span> a state the work is meant to reach',
                           '<span class="kshape ud-kbad"></span> a refusal or failure',
                           '<span class="ud-relword">→</span> a transition, <span class="ud-relword">ends</span> the end'],
                          src_link(kind, line) if k == 1 else ""))
    return "\n".join(views), len(groups)


# ------------------------------------------------------- graph / flowchart
NODE = re.compile(r"^(\w+)\s*(\[\(.*?\)\]|\[\[.*?\]\]|\[.*?\]|\{.*?\}|\(\(.*?\)\)|\(.*?\))?(?::::(\w+))?$")
EDGE = re.compile(r"\s*(-->|-\.->|==>|--\s+[^-].*?\s+-->|-- .*? -->|-->\|.*?\|)\s*")


def parse_graph(src):
    lines = src.split("\n")
    head = lines[0].strip().split()
    if head[0] not in ("graph", "flowchart") or len(head) != 2:
        raise ParseError(f"not a graph: {lines[0]!r}")
    nodes, edges, classes = {}, [], {}

    def node(tok):
        m = NODE.match(tok.strip())
        if not m:
            raise ParseError(f"graph node not understood: {tok!r}")
        nid, shape, cl = m.groups()
        d = nodes.setdefault(nid, {"label": nid, "shape": "box", "cls": None})
        if shape:
            if shape.startswith("[("):
                d["shape"], d["label"] = "store", shape[2:-2]
            elif shape.startswith("{"):
                d["shape"], d["label"] = "decision", shape[1:-1]
            else:
                d["label"] = shape.strip("[]()")
        if cl:
            d["cls"] = cl
        return nid
    for raw in lines[1:]:
        s = raw.strip()
        if not s or s.startswith("%%"):
            continue
        if s.startswith("classDef "):
            classes[s.split()[1]] = s
            continue
        toks = re.split(r"\s*(-\.->|-->|-- [^>]*? -->)\s*", s)
        if len(toks) == 1:
            node(toks[0])
            continue
        prev = node(toks[0])
        for i in range(1, len(toks), 2):
            arrow, nxt = toks[i], node(toks[i + 1])
            lab = ""
            m = re.match(r"^-- (.*) -->$", arrow)
            if m:
                lab = m.group(1)
            edges.append((prev, nxt, lab, arrow == "-.->"))
            prev = nxt
    return nodes, edges


def render_component(n, src, where, kind, line):
    nodes, edges = parse_graph(src)
    deps = {k: [b for a, b, _, _ in edges if a == k] for k in nodes}
    memo = {}

    def rank(k, seen=()):
        if k in memo:
            return memo[k]
        if k in seen:
            raise ParseError(f"dependency cycle through {k}")
        memo[k] = 0 if not deps[k] else 1 + max(rank(d, seen + (k,)) for d in deps[k])
        return memo[k]
    for k in nodes:
        rank(k)
    order = sorted(nodes, key=lambda k: (-memo[k], list(nodes).index(k)))

    def name(k):
        return label(nodes[k]["label"]).split(" · ")[0]
    views_nodes = []
    cur = []
    for k in order:
        if len(cur) >= MAX_BOXES and memo[k] != memo[cur[-1]]:
            views_nodes.append(cur)
            cur = []
        cur.append(k)
    if cur:
        views_nodes.append(cur)
    # a view of more than MAX_BOXES cards still: split it evenly
    split = []
    for v in views_nodes:
        split += chunks(v, MAX_BOXES)
    views = []
    for j, grp in enumerate(split, 1):
        bands, body = sorted({memo[k] for k in grp}, reverse=True), ""
        for i, b in enumerate(bands):
            cards = []
            for k in [x for x in grp if memo[x] == b]:
                lab = label(nodes[k]["label"]).split(" · ")
                ext = nodes[k]["cls"] == "ext" or nodes[k]["shape"] == "store"
                uses = " ".join(f'<a href="#ud{n}-{d}">{e(name(d).replace("rustinfer-", ""))}</a>' for d in deps[k])
                cards.append(f'<div class="c4-box {"c4-external" if ext else "c4-container"}" id="ud{n}-{k}">'
                             f'<div class="c4-box-head"><span class="c4-name">{e(lab[0])}</span></div>'
                             f'<span class="c4-type">[{"external library" if ext else "crate"}]</span>'
                             + (f'<p class="c4-desc">{e(" · ".join(lab[1:]))}</p>' if len(lab) > 1 else "")
                             + (f'<p class="c4-uses"><span>depends on</span> {uses}</p>' if uses else
                                '<p class="c4-uses"><span>depends on</span> nothing</p>') + "</div>")
            body += f'<div class="c4-row">{"".join(cards)}</div>'
            if i < len(bands) - 1:
                body += ('<div class="bound"><span class="bound-rule"></span><span class="bound-label">'
                         'depends only on the cards below</span></div>')
        title = f"Figure {n}{chr(96 + j) if len(split) > 1 else ''}. {where}"
        if len(split) > 1:
            title += f", part {j} of {len(split)}"
        lede = ("Each card is one crate, or a library the tree links; the cards are in bands so that every "
                "dependency points down the page, and each card names what it depends on.")
        views.append(view(f"ud{n}{chr(96 + j)}", title, lede, body,
                          ['<span class="kshape kshape-container"></span> crate',
                           '<span class="kshape kshape-external"></span> external library',
                           '<span class="bound-rule"></span> dependencies point down'],
                          src_link(kind, line) if j == 1 else ""))
    return "\n".join(views), len(split)


def render_activity(n, src, where, kind, line):
    nodes, edges = parse_graph(src)
    outs = {k: [(b, lab) for a, b, lab, _ in edges if a == k] for k in nodes}
    order = [k for k in nodes if not k.startswith("X")]
    errors = [k for k in nodes if k.startswith("X")]
    num = {k: i for i, k in enumerate(order, 1)}
    groups = chunks(order, MAX_BOXES)
    views = []
    for j, grp in enumerate(groups, 1):
        cards = []
        for k in grp:
            d = nodes[k]
            lis = []
            for b, lab in outs[k]:
                tgt = (f'step {num[b]}' if b in num else label(nodes[b]["label"]))
                if lab or b not in num or num[b] != num[k] + 1:
                    lis.append(f'<li><span class="ud-relword">{e(lab) if lab else "then"}</span> → '
                               f'<a href="#ud{n}-{b}">{e(tgt)}</a></li>')
            cls = "ud-decision" if d["shape"] == "decision" else ("c4-store" if d["shape"] == "store" else "")
            cards.append(f'<div class="c4-box ud-act {cls}" id="ud{n}-{k}"><div class="c4-box-head">'
                         f'<span class="c4-step-no">{num[k]}</span><span class="c4-name">{e(label(d["label"]))}</span></div>'
                         + (f'<ul class="ud-rels">{"".join(lis)}</ul>' if lis else "") + "</div>")
        title = f"Figure {n}{chr(96 + j) if len(groups) > 1 else ''}. {where}"
        if len(groups) > 1:
            title += f", steps {num[grp[0]]} to {num[grp[-1]]}"
        lede = ("The build, step by step, read in number order; a card lists only the ways out that are not "
                "simply the next step.")
        views.append(view(f"ud{n}{chr(96 + j)}", title, lede,
                          '<div class="c4-row ud-row">' + "".join(cards) + "</div>",
                          ['<span class="kshape ud-kdecision"></span> a check that can refuse',
                           '<span class="kshape kshape-store"></span> a file', 'numbers: the order of the steps'],
                          src_link(kind, line) if j == 1 else ""))
    errs = "".join(f'<div class="c4-box ud-state ud-bad" id="ud{n}-{k}"><div class="c4-box-head"><span class="c4-name">'
                   f'{e(label(nodes[k]["label"]))}</span></div></div>' for k in errors)
    views.append(view(f"ud{n}z", f"Figure {n}{chr(97 + len(groups)) if len(groups) > 1 else ''}. {where}, the refusals",
                      "Where the build stops: each refusal names what it refused.",
                      f'<div class="c4-row ud-row">{errs}</div>', ['<span class="kshape ud-kbad"></span> a refusal'], ""))
    return "\n".join(views), len(groups) + 1


# ------------------------------------------------------------------- page
def present(kind, body, section, counter, base_line, splits):
    fence = re.compile(r"```mermaid\n(.*?)```", re.S)
    pos = 0
    out = []
    for m in fence.finditer(body):
        counter[0] += 1
        n = counter[0]
        before = body[:m.start()]
        h = re.findall(r"^#{3,4} (.+)$", before, re.M)
        where = re.sub(r"[`*]", "", h[-1]) if h else section
        crate = re.search(r"\((rustinfer-[a-z-]+)", where)
        crate = crate.group(1) if crate else "rustinfer-core, rustinfer-cli"
        short = re.sub(r"\s*\(.*$", "", where).strip() or where
        short = re.sub(r"\s+—.*$", "", short)
        reqs = list(dict.fromkeys(REQ.findall(where)))
        line = base_line(m.group(1))
        src = m.group(1).strip("\n")
        k = src.split("\n", 1)[0].strip().split()[0]
        try:
            if k == "classDiagram":
                html_, nviews = render_class(n, src, short, crate, kind, line)
            elif k == "sequenceDiagram":
                html_, nviews = render_sequence(n, src, short, kind, line, reqs)
            elif k.startswith("stateDiagram"):
                html_, nviews = render_state(n, src, short, kind, line)
            elif kind == "component":
                html_, nviews = render_component(n, src, short, kind, line)
            elif k in ("flowchart", "graph"):
                html_, nviews = render_activity(n, src, short, kind, line)
            else:
                raise ParseError(f"diagram type {k!r} not supported")
        except ParseError as err:
            sys.exit(f"gen_diagrams: docs/uml/{kind}-diagram.md line {line}: {err}")
        if nviews > 1:
            splits.append(f"Figure {n} ({short}): {nviews} views")
        out.append(body[pos:m.start()])
        out.append('<div class="ud">' + html_.replace("\n\n", "\n") + "</div>\n")
        pos = m.end()
    out.append(body[pos:])
    return "".join(out)


def close_fences(body):
    """A ```mermaid fence the next heading reaches first is closed before it."""
    out, inside, fixed = [], False, 0
    for line in body.split("\n"):
        if line.startswith("```mermaid"):
            inside = True
        elif inside and line.startswith("```"):
            inside = False
        elif inside and line.startswith("#"):
            out += ["```", ""]
            inside, fixed = False, fixed + 1
        out.append(line)
    return "\n".join(out), fixed


out = header("Design diagrams", "Design", 3,
             "The six UML diagrams the tree keeps under docs/uml, drawn as cards, numbered steps "
             "and states from their Mermaid source, with the date and pull request each was last updated by.",
             script="gen_diagrams.py")
page, counter, splits, unclosed = "", [0], [], 0
for kind in ORDER:
    p = UML / f"{kind}-diagram.md"
    text = p.read_text(encoding="utf-8")
    head = re.match(r"<!--\n(.*?)\n-->", text, re.S)
    meta = dict(l.split(": ", 1) for l in head.group(1).splitlines() if ": " in l) if head else {}
    body = text[head.end():] if head else text
    body = re.sub(r"^# .*\n", "", body.strip(), count=1, flags=re.M)
    body = re.sub(r"^> Last updated:.*\n", "", body, flags=re.M)
    body = re.sub(r"^---\n", "", body, flags=re.M)
    body = re.sub(r"^## ", "### ", body, flags=re.M)
    body, fixed = close_fences(body)
    unclosed += fixed
    title = re.search(r"^# rustinfer — (.*)$", text, re.M)
    name = title.group(1) if title else kind.title()

    def base_line(src, text=text):
        i = text.find(src.split("\n", 1)[0] + "\n" + src.split("\n")[1])
        return text[:i].count("\n") + 1 if i >= 0 else 1
    body = present(kind, body, name, counter, base_line, splits)
    page += f"## {name}\n\n"
    page += (f"*{meta.get('diagram', kind)} diagram, last updated {meta.get('last_updated', '?')} "
             f"by {meta.get('last_updated_by', '?')} in PR {meta.get('pr', '?')}; "
             f"[source]({WEB}/blob/{sha()}/docs/uml/{kind}-diagram.md).*\n\n")
    page += body.strip() + "\n\n"

out += f"""# Design diagrams

Drawn from `docs/uml/*.md` at commit [`{sha()}`]({WEB}/tree/{sha()}/docs/uml). The
Mermaid in those files is the committed source of each diagram, and the tree's CI
checks that it parses (`scripts/ci/validate_mermaid.py`) and that each file carries
the date, author and pull request of its last update (SWG-001 §17.3,
`scripts/ci/check_doc_freshness.py`); that header is under each title below. This
page does not render the Mermaid: `scripts/reference/gen_diagrams.py` reads it and
draws each diagram as cards, numbered steps or states, with a *view source* link to
the block. A diagram too big to read on one screen is split into views of at most
{MAX_BOXES} cards or {MAX_STEPS} steps. Items the diagrams mark *planned* have no code
behind them yet; the [design](design.html) page says which do. The
[architecture diagram](architecture-diagram.html) draws the same system in the C4
model, down to these class diagrams.

"""
if unclosed:
    out += (f"The source leaves {unclosed} Mermaid fence{'s' if unclosed > 1 else ''} open before the next "
            "heading; the parser closes each there and reads the block as it stands.\n\n")
write("design-diagrams.md", out + page)
print(f"{counter[0]} diagrams; split: " + ("; ".join(splits) or "none"))
