---
title: "HIP memory management 7.2.4"
navtitle: Overview
section: Standards
group: "Runtime / HIP memory management 7.2.4"
order: 14
summary: The HIP 7.2.4 memory-management how-to (host memory, coherence control, virtual memory), for RI-ROC-008's pinned coarse-grained staging buffers and asynchronous uploads (R1) and per-buffer peer mapping (R2); no host memory is pinned on main yet (#93, #94).
---

# HIP memory management 7.2.4

**Scope (SRS §1.4, HIP-MEM):** "the `hipHostMalloc` and `hipHostRegister`
flags, coarse- and fine-grained memory (R1, RI-ROC-008); virtual memory peer
access (R2, RI-ROC-013)". Added by SRS v0.5 (PR #80). RI-ROC-008 (R1): the
host staging buffers of RI-TGT-006 are "page-locked, coarse-grained host
memory (`hipHostMalloc` with `hipHostMallocNonCoherent`)", copied from with
`hipMemcpyAsync`, each held against reuse until its copy's event completes;
RI-WST-006 (R1) makes Sluice's chunks such buffers. RI-WST-007 (R2) may
register the page cache with `hipHostRegister`; RI-ROC-013 (R2) maps buffers
across ranks per buffer with `hipMemSetAccess` instead of device-wide peer
access.

**Implementation on `main` (`5a6db49`):** none. The ROCm target binds
`hipMalloc`, `hipFree`, `hipMemcpyWithStream` and `hipMemcpyAsync` and no
host-memory call (`crates/rustinfer-target-rocm/src/ffi/symbols.rs:72-75`);
an upload is `hipMemcpyWithStream` from a caller's slice, synchronous with
the host (`crates/rustinfer-target-rocm/src/device/mod.rs:320-332`), and the
`Device` trait offers no staging buffer and no copy class
(`crates/rustinfer-target/src/target.rs:58-112`). Sluice's staging chunks are
pageable `Vec<u8>`s (`crates/rustinfer-sluice/src/staging.rs:33-40`). Planned
in issues [#93](https://github.com/itej89/rustinfer/issues/93) (pinned
staging buffers and copy classes) and
[#94](https://github.com/itej89/rustinfer/issues/94) (Sluice on them), both
open, R1; the R2 parts in #104 and #100. PR
[#110](https://github.com/itej89/rustinfer/pull/110) for #93 opened during
this audit and, on its head, adds the pinned coarse-grained staging buffers
and their asynchronous uploads (see the [audit](std-hip-mem-audit.html)).

**Conformance:** mandatory from **R1** (RI-ROC-008, RI-WST-006); the
virtual-memory peer mapping and the registered upload are R2.

**Source:** the HIP 7.2.4 how-to *Memory management*,
<https://rocm.docs.amd.com/projects/HIP/en/docs-7.2.4/how-to/hip_runtime_api/memory_management.html>,
and its pages *Host memory*, *Coherence control* and *Virtual memory
management* (`.../memory_management/host_memory.html`,
`coherence_control.html`, `virtual_memory.html`), downloaded 2026-11-15 into
`specs/runtime/` as `hip-7.2.4-memory_management-howto.html`,
`hip-7.2.4-host_memory.html`, `hip-7.2.4-coherence_control.html` and
`hip-7.2.4-virtual_memory.html`, with text copies cited by line. The
`hipHostRegister` flags are read from the HIP 7.2.4 API reference already in
`specs/runtime/hip-7.2.4-memory_management.txt` (the [HIP](std-hip.html)
standard's source).

| | |
|---|---|
| Pages | [requirements](std-hip-mem-requirements.html) · [audit](std-hip-mem-audit.html) · [tracker](std-hip-mem-tracker.html) |
| Conformance | mandatory R1 (RI-ROC-008, RI-WST-006); R2 for RI-WST-007 and RI-ROC-013 |
| Audited | 2026-11-15, by reading `main` `5a6db49` and the documents; no test run |
| Result | missing: no host memory is pinned, every upload blocks the host, and Sluice stages in pageable memory |
| Open gaps | 3 of 5 (HMEM-1 staging buffers and HMEM-2 asynchronous uploads held to their event, both in PR #110 for #93; HMEM-3 Sluice, #94); HMEM-4 and HMEM-5 are R2 |
