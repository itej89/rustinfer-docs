---
title: "SPIR-V 1.6 rev 8 audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / SPIR-V 1.6 rev 8"
order: 42
summary: The 2026-11-13 audit of rustinfer against the SPIR-V module requirements; every item is Release 2 work and nothing is emitted yet.
---

# SPIR-V 1.6 rev 8 audit

**Audit of 2026-11-13**, against the [requirements](std-spir-v-requirements.html).

**Method.** Searched `origin/main` at `ccf02b3` for any `spirv` operation,
SPIR-V word or serializer call (none), and read the stub crate
`crates/rustinfer-target-spirv-vulkan/` and its tests. Read the SRS on
branch `docs/srs-standards-conformance` (RI-KC-004, RI-RV-001, OI-016).
Nothing was run.

| id | result | evidence |
|---|---|---|
| SV-R1 to SV-R5 | **later release** (R2) | No SPIR-V binary is produced. The serializer is MLIR's (`specs/compiler/mlir-23.1.0/SPIR-V.md`, *Serialization and deserialization*, line 1049), reached through the linked MLIR once the lowering exists |
| SV-R6 to SV-R8 | **later release** (R2) | No `spirv.module` is built; `crates/rustinfer-target-spirv-vulkan/src/lib.rs:25` to `:38` is a target with an empty catalog |
| SV-R9, SV-R10 | **later release** (R2) | As above. The Kernel IR's structured control flow (RI-KC-002) maps onto SV-R10's structured loops and selections; nothing checks it yet |
| SV-R11 | **later release** (R2) | The version is undecided (SRS OI-016, status Open). The stub's tests (`crates/rustinfer-target-spirv-vulkan/tests/stub.rs`) prove only the R1 stub of RI-RV-001 and RI-RV-002, which ask nothing of SPIR-V |

## Result

Nothing is required in R1 and nothing is implemented. When the R2 lowering
lands, a SPIR-V validator run over every emitted module (for example
`spirv-val` from SPIRV-Tools in a test, outside the product, since
RI-KC-008 forbids an external process only in compilation) would turn this
audit into a pass or fail count. Gaps are on the
[tracker](std-spir-v-tracker.html).
