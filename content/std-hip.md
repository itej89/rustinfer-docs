---
title: "HIP runtime API ROCm 7.2"
navtitle: Overview
section: Standards
group: "Runtime / HIP runtime API ROCm 7.2"
order: 10
summary: The HIP runtime as rustinfer's ROCm target must use it from R1, and how little of it is bound so far.
---

# HIP runtime API ROCm 7.2

**Scope (SRS §1.4, HIP):** memory, streams, events, modules, launches, graphs and
error codes. **Conformance:** mandatory R1. The requirements that cite it are
RI-ROC-001 to RI-ROC-004, RI-ROC-007 (R2), RI-PLN-002 (R2), RI-SEC-001 and
RI-NFR-017.

**Implementation:** `rustinfer-target-rocm`. On origin/main (`ccf02b3`) the crate is
a stub: `src/lib.rs:3-5` says so, `RocmTarget::devices` returns no device
(`src/lib.rs:59-61`) and `device` and `launcher` refuse every index
(`src/lib.rs:63-69`). The `rocm` feature that is to link HIP is empty
(`Cargo.toml:22-25`). The only error is `NotImplemented` (`src/error.rs:13-20`).
The binding itself is issue [#12](https://github.com/itej89/rustinfer/issues/12), open.

Open PR [#44](https://github.com/itej89/rustinfer/pull/44) (feature `rocm-test`)
adds a minimal HIP harness, `src/ffi/hip.rs`: it opens `libamdhip64.so` with
`dlopen`, loads a code object, allocates and copies buffers, launches one kernel on
a one-dimensional grid and maps a failed call to `Error::Hip { call, detail }` with
HIP's error string. It is a test harness for the AMD lowering, not the target's
binding, and it waits for the GPU run of [#45](https://github.com/itej89/rustinfer/issues/45).
Everything it covers is "pending PR #44" here.

**Source:** `specs/runtime/hip-7.2.4-*.html` (AMD, *HIP Runtime API Reference*, HIP
7.2.53211 documentation for ROCm 7.2.4, 2026-05-29,
https://rocm.docs.amd.com/projects/HIP/en/docs-7.2.4/reference/hip_runtime_api_reference.html),
its module pages (device, memory, stream, event, module, execution control, graph,
error handling, initialization and version, peer access) and the `hipDeviceProp_t`
structure page. The SRS pins ROCm 7.0 to 7.2; the 7.2.4 text is read as the
reference for that range.

| | |
|---|---|
| Pages | [requirements](std-hip-requirements.html) · [audit](std-hip-audit.html) · [tracker](std-hip-tracker.html) |
| Audited | 2026-11-13, by reading origin/main, PR #44 at `10b8b1b` and the HIP 7.2.4 reference |
| R1 items | 10 in scope; none conforms; 4 pending PR #44 (memory, modules, launch, errors) |
| R2 items | 2 (graph replay per bucket, peer access), later release |
| Open gaps | 10, the R1 work of issue #12 (4 in PR #44, 6 open); 2 more items recorded as later release (R2) |
