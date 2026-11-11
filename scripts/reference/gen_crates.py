#!/usr/bin/env python3
"""Every crate of the workspace: its description, what it depends on inside
the workspace, its features, and how many tests it carries."""
import re

from common import RUSTINFER, commit, header, write

root = (RUSTINFER / "Cargo.toml").read_text(encoding="utf-8")
members = re.findall(r'"crates/([^"]+)"', root.split("members")[1].split("]")[0])
pins = re.findall(r'^(\w[\w-]*) = (?:\{ version = )?"(=[^"]+)"', root.split("[workspace.dependencies]")[1].split("[workspace.lints")[0], re.M)
lints_rust = re.findall(r"^(\w+) = (?:\"(\w+)\"|\{ level = \"(\w+)\")",
                        root.split("[workspace.lints.rust]")[1].split("[workspace.lints.clippy]")[0], re.M)
lints_clippy = re.findall(r"^(\w+) = (?:\"(\w+)\"|\{ level = \"(\w+)\")",
                          root.split("[workspace.lints.clippy]")[1].split("[profile")[0], re.M)

rows = []
for name in members:
    d = RUSTINFER / "crates" / name
    toml = (d / "Cargo.toml").read_text(encoding="utf-8")
    desc = re.search(r'^description = "(.*)"', toml, re.M)
    deps = re.findall(r"^(rustinfer-[\w-]+)\s*=", toml.split("[dependencies]")[1].split("[dev-dependencies]")[0] if "[dependencies]" in toml else "", re.M)
    feats = re.search(r"\[features\](.*?)(?:\n\[|\Z)", toml, re.S)
    feat_names = re.findall(r"^(\w+)\s*=", feats.group(1), re.M) if feats else []
    src_lines = sum(len(p.read_text().splitlines()) for p in (d / "src").rglob("*.rs"))
    tests = 0
    for p in list(d.rglob("*.rs")):
        tests += len(re.findall(r"#\[test\]", p.read_text()))
    rows.append((name, desc.group(1) if desc else "", deps, feat_names, src_lines, tests))

out = header("Crates", "Reference", 4,
             "Every crate of the workspace with its purpose, in-workspace dependencies, "
             "features, source size and test count, generated from the Cargo manifests.",
             script="gen_crates.py")
out += f"""# Crates

Generated from `Cargo.toml` and each `crates/*/Cargo.toml` at commit {commit()}.
{len(members)} members. Dependencies listed are the in-workspace ones; they point
downward only, which Cargo enforces by refusing a cycle. Source lines count
`src/**/*.rs`; tests count `#[test]` functions anywhere in the crate.

| crate | purpose | depends on | features | source lines | tests |
|---|---|---|---|---|---|
"""
for name, desc, deps, feats, lines, tests in rows:
    out += (f"| `{name}` | {desc} | {', '.join(f'`{d}`' for d in deps) or '—'} | "
            f"{', '.join(f'`{f}`' for f in feats) or '—'} | {lines} | {tests} |\n")

out += """
## Pinned external dependencies

Declared once in the workspace manifest and inherited; the manifest's comment
says exact pins because every crate is part of one binary (SWG-001 §18.3).

| crate | pin |
|---|---|
"""
for name, pin in pins:
    out += f"| `{name}` | `{pin}` |\n"

out += """
## Workspace lints

The design rules the compiler enforces (ADR-001). Every crate opts in with
`[lints] workspace = true`.

| group | lint | level |
|---|---|---|
"""
for n, a, b in lints_rust:
    out += f"| rust | `{n}` | {a or b} |\n"
for n, a, b in lints_clippy:
    out += f"| clippy | `{n}` | {a or b} |\n"
write("ref-crates.md", out)
