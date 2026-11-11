#!/usr/bin/env python3
"""The error codes of rustinfer-core::error::ErrorCode (the wire values of the
structured error line) and every component's error variants."""
import re

from common import RUSTINFER, commit, header, write

CORE = RUSTINFER / "crates/rustinfer-core/src/error.rs"
text = CORE.read_text(encoding="utf-8")

enum = re.search(r"pub enum ErrorCode \{(.*?)\n\}", text, re.S).group(1)
variants = re.findall(r"((?:\s*///[^\n]*\n)+)\s*(\w+),", enum)
wire = dict(re.findall(r"Self::(\w+) => \"(\w+)\"", text))
codes = [(name, wire.get(name, "?"), " ".join(l.strip()[3:].strip() for l in doc.strip().splitlines()))
         for doc, name in variants]

# Per-crate error enums: variant name, its code, its component.
crates = []
for err in sorted(RUSTINFER.glob("crates/*/src/error.rs")):
    crate = err.parent.parent.name
    src = err.read_text(encoding="utf-8")
    comp = re.search(r'COMPONENT: &str = "(\w+)"', (err.parent / "lib.rs").read_text()
                     if (err.parent / "lib.rs").exists() else
                     (err.parent / "main.rs").read_text())
    enum_m = re.search(r"pub enum Error \{(.*?)\n\}", src, re.S)
    if not enum_m:
        continue
    names = re.findall(r"^\s{4}(\w+)\s*[{(,]", enum_m.group(1), re.M)
    code_map = dict(re.findall(r"Self::(\w+)\s*(?:\{[^}]*\}|\([^)]*\))?\s*=>\s*ErrorCode::(\w+)", src))
    rows = []
    for n in names:
        rows.append((n, wire.get(code_map.get(n, ""), code_map.get(n, "delegated"))))
    crates.append((crate, comp.group(1) if comp else "?", rows))

out = header("Error codes", "Reference", 3,
             "The stable error codes of the structured failure line and the error "
             "variants of every crate, generated from the sources.",
             script="gen_errors.py")
out += f"""# Error codes

Generated from `crates/rustinfer-core/src/error.rs` and each crate's
`src/error.rs` at commit {commit()}. A failure leaves the command as one line on
stderr, `error=<code> component=<name> detail="<text>"`, and the code column
below is the wire value. The source marks the enum `#[non_exhaustive]` and says
a class may be added but never renamed (SWG-001 §14.4).

## Codes

| variant | wire value | meaning |
|---|---|---|
"""
for name, w, doc in codes:
    out += f"| `{name}` | `{w}` | {doc} |\n"
out += """
## Variants per crate

The component column is the `COMPONENT` constant the crate prints. *delegated*
means the variant carries another crate's error and reports that crate's code
and component.

| crate | component | variant | code |
|---|---|---|---|
"""
for crate, comp, rows in crates:
    for n, c in rows:
        out += f"| `{crate}` | `{comp}` | `{n}` | `{c}` |\n"
write("ref-error-codes.md", out)
