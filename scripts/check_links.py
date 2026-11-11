#!/usr/bin/env python3
"""Every internal href and src in out/ must resolve to a built file, and every
#fragment to an id on the target page."""
import pathlib, re, sys
OUT = pathlib.Path(__file__).resolve().parent.parent / "out"
pages = {p.relative_to(OUT).as_posix(): p.read_text(encoding="utf-8") for p in OUT.rglob("*.html")}
ids = {name: set(re.findall(r'id="([^"]+)"', html)) for name, html in pages.items()}
bad = []
for name, html in pages.items():
    base = pathlib.PurePosixPath(name).parent
    for attr, target in re.findall(r'(href|src)="([^"]+)"', html):
        if target.startswith(("http://", "https://", "mailto:", "data:")):
            continue
        path, _, frag = target.partition("#")
        dest = name if not path else (base / path).as_posix()
        dest = pathlib.PurePosixPath(dest)
        parts = []
        for part in dest.parts:
            if part == "..": parts.pop()
            elif part != ".": parts.append(part)
        dest = "/".join(parts)
        if dest not in pages and not (OUT / dest).exists():
            bad.append(f"{name}: {attr} {target} -> missing {dest}")
        elif frag and dest in ids and frag not in ids[dest]:
            bad.append(f"{name}: fragment #{frag} not on {dest}")
print(f"checked {len(pages)} pages")
for b in bad: print("  " + b)
sys.exit(1 if bad else 0)
