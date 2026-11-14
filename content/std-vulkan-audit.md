---
title: "Vulkan 1.4.368 audit"
navtitle: Audit
section: Standards
group: "Runtime / Vulkan 1.4.368"
order: 32
summary: The 2026-11-13 audit of rustinfer's Vulkan use: the spirv-vulkan target is the R1 stub, nothing is required before R2, and the minimum version is undecided.
---

# Vulkan 1.4.368 audit

**Audit of 2026-11-13**, against the [requirements](std-vulkan-requirements.html).

**Method.** Read `crates/rustinfer-target-spirv-vulkan` on origin/main (`ccf02b3`)
and its tests, searched the workspace for any Vulkan API use (none), and read the
1.4.368 text in `specs/runtime/`. Nothing was run.

**State on origin/main.** The crate is the R1 stub of RI-RV-001. Its tests pin that:
`tests/stub.rs:34` `test_stub_registers_under_its_architecture_string`,
`tests/stub.rs:46` `test_stub_catalog_is_empty_and_requests_fail_naming_the_target`,
`tests/stub.rs:70` `test_stub_has_no_device`. That is the expected R1 state, not a
Vulkan item.

| id | result | evidence |
|---|---|---|
| V1 SPIR-V version for the core version | **later release** (R2), **blocked on OI-016** | no minimum core version in SRS §1.4; the emitted SPIR-V version is open too |
| V2 code size | **later release** (R2) | no shader module is created |
| V3 valid SPIR-V | **later release** (R2) | RI-KC-004 emits through MLIR's `spirv` dialect; no validation step is planned yet |
| V4 capabilities and extensions | **later release** (R2) | |
| V5 compute pipeline | **later release** (R2) | |
| V6 compute queue | **later release** (R2) | |
| V7 group counts | **later release** (R2) | |
| V8 work-group size and shared memory | **later release** (R2) | the Kernel IR's tiles decide these; they must be checked against the device |

**Result.** Nothing required yet; state *later*. OI-016 must be decided before the
R2 work can start, because V1 and the limits of V8 depend on it.
