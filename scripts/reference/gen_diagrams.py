#!/usr/bin/env python3
"""The six UML diagrams of docs/uml/, copied with their prose and their
freshness headers, so the site shows the tree's diagrams and not a redrawing."""
import re

from common import RUSTINFER, commit, header, write

ORDER = ["component", "class", "sequence", "state", "activity", "concurrency"]
UML = RUSTINFER / "docs/uml"

out = header("Design diagrams", "Design", 2,
             "The six UML diagrams the tree keeps under docs/uml, rendered as they are "
             "committed, with the date and pull request each was last updated by.",
             script="gen_diagrams.py")
out += f"""# Design diagrams

Copied from `docs/uml/*.md` at commit {commit()}. SWG-001 §17.3 requires each
diagram file to carry a header naming the date, author and pull request of its
last update, and the tree's CI checks that header (`scripts/ci/check_doc_freshness.py`)
and that every Mermaid block parses (`scripts/ci/validate_mermaid.py`). The
headers are reproduced below each title. Items the diagrams mark *planned* have
no code behind them yet; the [design](design.html) page says which do.

"""
for kind in ORDER:
    p = UML / f"{kind}-diagram.md"
    text = p.read_text(encoding="utf-8")
    head = re.match(r"<!--\n(.*?)\n-->", text, re.S)
    meta = dict(l.split(": ", 1) for l in head.group(1).splitlines() if ": " in l) if head else {}
    body = text[head.end():] if head else text
    body = re.sub(r"^# .*\n", "", body.strip(), count=1, flags=re.M)
    body = re.sub(r"^> Last updated:.*\n", "", body, flags=re.M)
    body = re.sub(r"^---\n", "", body, flags=re.M)
    # Demote the file's own sub-headings so the page's H2s are the six diagrams.
    body = re.sub(r"^## ", "### ", body, flags=re.M)
    title = re.search(r"^# rustinfer — (.*)$", text, re.M)
    out += f"## {title.group(1) if title else kind.title()}\n\n"
    out += (f"*{meta.get('diagram', kind)} diagram, last updated {meta.get('last_updated', '?')} "
            f"by {meta.get('last_updated_by', '?')} in PR {meta.get('pr', '?')}.*\n\n")
    out += body.strip() + "\n\n"
write("design-diagrams.md", out)
