#!/usr/bin/env python3
"""Every named constant in rustinfer-core's constants.rs, with its type, value
and the doc comment above it."""
import re

from common import RUSTINFER, commit, header, write

SRC = RUSTINFER / "crates/rustinfer-core/src/config/constants.rs"
text = SRC.read_text(encoding="utf-8")

rows = []
for m in re.finditer(
    r"((?:^///[^\n]*\n)+)pub const (\w+): ([^=]+?) = ([^;]+);", text, re.M):
    doc = " ".join(l[3:].strip() for l in m.group(1).strip().splitlines())
    rows.append((m.group(2), m.group(3).strip(), m.group(4).strip(), doc))

out = header("Constants", "Reference", 2,
             "Every named constant of rustinfer-core, the single definition of each "
             "domain string and threshold, generated from constants.rs.",
             script="gen_constants.py")
out += f"""# Constants

Generated from `crates/rustinfer-core/src/config/constants.rs` at commit
{commit()}. The file's own header says a literal that encodes a concept appears
there and nowhere else (design heuristics G25 and G35 of SWG-001); {len(rows)}
constants are defined. The requirement id in a note is the one the source cites.

| constant | type | value | what it is for |
|---|---|---|---|
"""
for name, typ, value, doc in rows:
    out += f"| `{name}` | `{typ}` | `{value}` | {doc} |\n"
write("ref-constants.md", out)
