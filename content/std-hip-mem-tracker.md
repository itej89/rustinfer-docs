---
title: "HIP memory management 7.2.4 tracker"
navtitle: Tracker
section: Standards
group: "Runtime / HIP memory management 7.2.4"
order: 17
summary: Gaps between rustinfer's host memory and HIP 7.2.4's memory-management how-to; pinned coarse-grained staging, asynchronous uploads held to their events and Sluice on them are R1 work in #93 and #94; registration and per-buffer peer mapping are R2.
---

# HIP memory management tracker

Gaps found by the [audit](std-hip-mem-audit.html) of 2026-11-15 against
`main` `5a6db49`. HMEM-1 to HMEM-3 are R1 (RI-ROC-008, RI-WST-006) and planned
in [#93](https://github.com/itej89/rustinfer/issues/93) (blocked by #92 for
the alignment only) and [#94](https://github.com/itej89/rustinfer/issues/94)
(blocked by #93), both open. PR
[#110](https://github.com/itej89/rustinfer/pull/110) (#93, opened
2026-11-15 21:47 UTC, during this audit) closes HMEM-1 and HMEM-2 on its head
`82c9ab3`; it is open and unmerged, so they stay open gaps until it merges.
HMEM-4 and HMEM-5 are R2; their issues #104 and
#100 sit on the milestone `R1 — foundation` only because no R2 milestone
exists yet (the Epic #1 checklist lists them under later releases).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| HMEM-1 | No page-locked host memory: `hipHostMalloc` and `hipHostFree` are not bound, the `Device` trait has no host staging buffer, so no coarse-grained (`hipHostMallocNonCoherent`, not mapped) buffer exists (HMEM-R1 to HMEM-R4) | [HOST] lines 229 to 347; [COH] lines 195 to 330; SRS RI-ROC-008, RI-TGT-006 | **In PR #110** | #93. On `82c9ab3`: `hipHostMalloc` with `HIP_HOST_MALLOC_NON_COHERENT = 0x8000_0000` (`crates/rustinfer-target-rocm/src/hip.rs:40-43`; the value matches `#define hipHostMallocNonCoherent 0x80000000`, `hip_runtime_api.h:868` at `rocm-7.2.4`), no mapped flag, and `alloc_staging` / `free_staging` on the `Device` trait (`crates/rustinfer-target/src/target.rs:90`). Function table on `5a6db49`: `crates/rustinfer-target-rocm/src/ffi/symbols.rs:66-97`; trait `crates/rustinfer-target/src/target.rs:58-112` |
| HMEM-2 | Uploads are `hipMemcpyWithStream` from the caller's slice, synchronous with the host; no `hipMemcpyAsync` from a staging buffer and no hold of the buffer until its copy's event (HMEM-R5) | [COH] lines 332 to 440; SRS RI-ROC-008 ("a weight upload from a staging buffer returns before the copy completes; the buffer is refused for reuse until its event completes") | **In PR #110** | #93. On `82c9ab3`: `copy_from_staging` is a `hipMemcpyAsync` that returns at once, each copy records the buffer's last-use event, and a host access or reuse is refused with `StagingBusy` while `hipEventQuery` says the copy is pending (`crates/rustinfer-target/src/target.rs:65-120`, `:185`; `crates/rustinfer-target-rocm/src/device/mod.rs:485-540`, `src/device/staging.rs:1-7`, `:196`, `:222-227`). Read, not run. `crates/rustinfer-target-rocm/src/device/mod.rs:10-12`, `:320-332` on `5a6db49`. The gfx950 GPU test of RI-ROC-008 records the pageable and pinned bandwidths |
| HMEM-3 | Sluice's staging chunks are pageable `Vec<u8>`s and every upload blocks its copier (HMEM-R1) | [HOST] lines 229 to 243; SRS RI-WST-006 | **Open** | PR #110 only threads the copy classes through Sluice ("Moving Sluice's pipeline onto the staging buffers is #94"). Planned in #94 (Sluice on pinned staging, asynchronous uploads, copy streams a setting). `crates/rustinfer-sluice/src/staging.rs:35-38`, `pipeline.rs:333-343` on `5a6db49` |
| HMEM-4 | No registered upload from the page cache (`hipHostRegister`) (HMEM-R6) | [API] lines 346 to 366; SRS RI-WST-007 | Later release R2 | #104 (R2). Not verified: how a coarse-grained registration is made; HIP 7.2.4 documents none (audit) |
| HMEM-5 | No per-buffer peer mapping by virtual memory (`hipMemSetAccess`) (HMEM-R7) | [VMM] lines 238 to 263; SRS RI-ROC-013 | Later release R2 | #100 (R2), with the peer copies of RI-ROC-013 |
