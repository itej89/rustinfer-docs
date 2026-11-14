---
title: "RISC-V V 1.0 audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / RISC-V V 1.0"
order: 52
summary: The 2026-11-13 audit of rustinfer against the RISC-V V 1.0 requirements; every item is Release 3 work and no RISC-V code is emitted yet.
---

# RISC-V V 1.0 audit

**Audit of 2026-11-13**, against the [requirements](std-rvv-1.0-requirements.html).

**Method.** Searched `origin/main` at `ccf02b3` for any RISC-V target
machine, vector intrinsic or `vset` emission (none), and read the stub crate
`crates/rustinfer-target-riscv-vector/` and its tests. Read the SRS on
branch `docs/srs-standards-conformance` (RI-KC-004, RI-RV-001 to RI-RV-004).
Nothing was run.

| id | result | evidence |
|---|---|---|
| RV-R1, RV-R2 | **later release** (R3) | No RISC-V code is generated. `crates/rustinfer-target-riscv-vector/src/lib.rs:1` to `:5` is a stub with an empty catalog |
| RV-R3 to RV-R6 | **later release** (R3) | No lowering exists. RI-RV-004 requires the vector-length-agnostic mapping these items describe |
| RV-R7, RV-R8 | **later release** (R3) | As above. The Kernel IR's masked loads and stores (RI-KC-002) would map to `v0`-masked accesses |
| RV-R9, RV-R10 | **later release** (R3) | As above |

## Result

Nothing is required in R1 and nothing is implemented. Two points matter
before the R3 lowering is designed; they are on the
[tracker](std-rvv-1.0-tracker.html):

- RVV 1.0's V extension has vector floating point only for 32- and 64-bit
  elements (RV-R2). The R1 generator set is bf16-first (RI-KC-005), so a
  bf16 kernel on RVV needs either conversion to f32 or the separate bf16
  vector extensions, which are not part of the RVV-1.0 reference.
- `vfredusum` may sum in any tree order (RV-R10), so a reduction that uses it
  can give different bits on cores with different VLEN. RI-KC-011 asks for
  deterministic compilation, not deterministic results, but RI-KC-007's
  per-dtype tolerance has to cover it, or the lowering uses `vfredosum`.
