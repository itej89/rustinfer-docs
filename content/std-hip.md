---
title: "HIP runtime API ROCm 7.2"
navtitle: Overview
section: Standards
group: "Runtime / HIP runtime API ROCm 7.2"
order: 10
summary: The HIP runtime as rustinfer's ROCm target uses it from R1; bound by PR #58, verified on gfx950 (#59), gfx942 not yet run (#61).
---

# HIP runtime API ROCm 7.2

**Scope (SRS §1.4, HIP):** memory, streams, events, modules, launches, graphs and
error codes. **Conformance:** mandatory R1. **Version (SRS v0.4.10):** HIP runtime
major version 7 (`libamdhip64.so.7`), checked at startup; documented against ROCm
7.2.4; verified on ROCm 10.1 (10.1.0-3) (MI350X, #59). The requirements that cite
it are RI-ROC-001 to RI-ROC-004, RI-ROC-007 (R2), RI-PLN-002 (R2), RI-SEC-001 and
RI-NFR-017.

**Implementation:** `rustinfer-target-rocm`, bound by PR
[#58](https://github.com/itej89/rustinfer/pull/58) (issue
[#12](https://github.com/itej89/rustinfer/issues/12), merge `53dac5b`). With the
`rocm` feature, `src/ffi/` opens `libamdhip64.so.7` with `dlopen` by absolute path
from the system library directories, or exactly the validated file named by
`RUSTINFER_HIP_LIBRARY`, and resolves 28 entry points (`src/ffi/symbols.rs:66-97`).
The target refuses a HIP runtime whose major version is not 7, reads each device's
architecture from `gcnArchName`, checks every code object's LDS and register needs
from its metadata before loading it, and maps every failed call to
`Error::Hip { operation, code, message }`. Device memory, streams, events,
modules, launches and graph capture and replay are bound, with per-resource
last-use events so nothing is freed or destroyed while the device still uses it.
Since PR #44 (merge `38f2f60`) the AMD lowering's GPU tests load and launch through
this binding instead of their own harness. The host tests run against a mock of the
same function table.

**Hardware:** GPU test [#59](https://github.com/itej89/rustinfer/issues/59) passed
on an MI350X (gfx950) under ROCm 10.1 (10.1.0-3), HIP runtime major 7, at
`bb0ce2f`, the head PR #58 merged: 11 passed (results in
[#54](https://github.com/itej89/rustinfer/issues/54)). gfx942 is not yet run:
[#61](https://github.com/itej89/rustinfer/issues/61).

**Source:** `specs/runtime/hip-7.2.4-*.html` (AMD, *HIP Runtime API Reference*, HIP
7.2.53211 documentation for ROCm 7.2.4, 2026-05-29,
https://rocm.docs.amd.com/projects/HIP/en/docs-7.2.4/reference/hip_runtime_api_reference.html),
its module pages (device, memory, stream, event, module, execution control, graph,
error handling, initialization and version, peer access) and the `hipDeviceProp_t`
structure page. SRS v0.4.10 states support by HIP runtime major version rather than
a ROCm release range; the 7.2.4 text is read as the reference for major version 7.

| | |
|---|---|
| Pages | [requirements](std-hip-requirements.html) · [audit](std-hip-audit.html) · [tracker](std-hip-tracker.html) |
| Audited | 2026-11-14, by reading `main` at `81fbcba`, the #45 and #59 results on #54, and the HIP 7.2.4 reference |
| R1 items | 10 in scope; all 10 conform with host tests; 9 exercised on gfx950 hardware (#59); none on gfx942 (#61) |
| R2 items | 2 (graph replay per bucket, peer access), later release |
| Open gaps | 1 (HIP-13: the gfx942 run, #61); HIP-1 to HIP-10 fixed by PR #58; 2 more items recorded as later release (R2) |
