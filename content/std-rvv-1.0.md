---
title: "RISC-V V 1.0"
navtitle: Overview
section: Standards
group: "Compiler and code generation / RISC-V V 1.0"
order: 50
summary: The ratified RISC-V V vector extension 1.0 that the riscv-vector lowering will target with vector-length-agnostic code from R3; nothing is required in R1.
---

# RISC-V V 1.0

**Scope (SRS §1.4, RVV-1.0):** the V extension's instructions, used with
vector-length-agnostic code (RI-RV-004: "a vector-length-agnostic tile
mapping"). The embedded subsets (Zve\*), the privileged state (`mstatus.VS`,
trap handling) and any matrix extension a core adds are out of the claim;
a core's matrix extension is used only when its catalog entry records it.

**Implementation:** none yet. On `origin/main` (`ccf02b3`)
`crates/rustinfer-target-riscv-vector/src/lib.rs:1` to `:5` is the R1 stub
of RI-RV-001 with an empty catalog, so a build for it fails at kernel
selection (RI-RV-002). No code emits RISC-V instructions; the lowering is R3
(RI-KC-004, RI-RV-004) through the LLVM RISC-V back end
([LLVM](std-llvm.html), LL-R12). See also the
[kernel compiler](kernel-compiler.html) page.

**Conformance:** mandatory from **R3**. The current release is R1, so
nothing is required yet.

**Source:** `specs/compiler/riscv-v-spec-1.0.pdf`, *RISC-V "V" Vector
Extension, Version 1.0* (frozen 2021-09-20, ratified 2021-12-02), the
release asset of tag `v1.0` of <https://github.com/riscvarchive/riscv-v-spec>
(formerly `github.com/riscv/riscv-v-spec`; the text now lives in
<https://github.com/riscv/riscv-isa-manual>), downloaded 2026-11-13.
Sections cited are those of that document.

| | |
|---|---|
| Pages | [requirements](std-rvv-1.0-requirements.html) · [audit](std-rvv-1.0-audit.html) · [tracker](std-rvv-1.0-tracker.html) |
| Conformance | mandatory R3 (RI-RV-004, RI-KC-004) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and the specification text |
| Result | later release: every item is R3 work; no R1 requirement depends on this standard |
| Open gaps | 0 (3 items recorded as later release R3) |
