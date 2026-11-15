---
title: "HIP memory management 7.2.4 audit"
navtitle: Audit
section: Standards
group: "Runtime / HIP memory management 7.2.4"
order: 16
summary: The 2026-11-15 audit at main 5a6db49 of rustinfer's host memory against HIP 7.2.4's memory-management how-to; nothing is pinned, uploads block the host from pageable memory and Sluice stages in Vec<u8> chunks (#93, #94).
---

# HIP memory management audit

**Audit of 2026-11-15**, against the [requirements](std-hip-mem-requirements.html),
on `main` `5a6db49` (PR #74 merged over SRS v0.5, PR #80 at `4ee01b6`). First
audit.

**Method.** Read the HIP 7.2.4 pages *Host memory*, *Coherence control* and
*Virtual memory management* in full and the `hipHostRegister` entry of the
API reference. Read on `5a6db49`: `crates/rustinfer-target/src/target.rs`
(the `Device` trait), `crates/rustinfer-target-rocm/src/hip.rs`,
`src/ffi/symbols.rs`, `src/ffi/library.rs`, `src/device/mod.rs` and
`src/device/lifetime.rs`, and `crates/rustinfer-sluice/src/staging.rs`,
`pipeline.rs` and `convert.rs`; searched every crate for `hipHost`,
`hipMemSetAccess`, `hipDeviceEnablePeerAccess`, `pinned`, `page-locked` and
`NonCoherent` (none in code). Read the plans of #93, #94, #100 and #104, and
the diffs of the open PRs #68, #73, #75, #76 and #77 (none touches host
memory). No tests were run.

| id | requirement | result | evidence |
|---|---|---|---|
| HMEM-R1 | Uploads staged in pinned memory | **missing** (HMEM-1, HMEM-3) | No host allocation call is bound: the function table is `hipMalloc`, `hipFree`, `hipMemcpyWithStream`, `hipMemcpyAsync` for memory (`crates/rustinfer-target-rocm/src/ffi/symbols.rs:72-75`). `copy_to_device` takes the caller's `&[u8]` (`crates/rustinfer-target/src/target.rs:102`), pageable whatever it is, and Sluice's chunks are `Vec::with_capacity` (`crates/rustinfer-sluice/src/staging.rs:35-38`) copied with `copy_to_device` (`pipeline.rs:333-343`) |
| HMEM-R2 | `hipHostMalloc` with `hipHostMallocNonCoherent` | **missing** (HMEM-1) | Not bound; no flag constant exists |
| HMEM-R3 | Coarse-grained, so not mapped | **missing** (HMEM-1) | As HMEM-R2. The document disagrees with itself here: the table of [COH] lists `hipHostMalloc` with `hipHostMallocDefault` as fine-grained, while its footnote says that with no flag and `HIP_HOST_COHERENT` unset or 0 (the HIP runtime's default, `rocm-7.2.4-clr-flags.hpp:176`) the allocation is coarse-grained. RI-ROC-008's explicit `hipHostMallocNonCoherent` does not depend on which is right. **Not verified** which one the 7.2.4 runtime does |
| HMEM-R4 | Coarse-grained for bulk transfers | **missing** (HMEM-1) | As HMEM-R2 |
| HMEM-R5 | A staging buffer reused only after its copy's event | **missing** (HMEM-2) | Uploads are `hipMemcpyWithStream`, which returns after the copy, so there is nothing to hold: "`hipMemcpyAsync` from or to pageable host memory is synchronous with the host ... so an upload's source may be dropped when the call returns" (`crates/rustinfer-target-rocm/src/device/mod.rs:10-12`, `:320-332`), and every upload is counted as a host synchronisation (`:330`, RI-RT-010). The last-use events of device buffers exist (`src/device/lifetime.rs`), with default flags (`src/ffi/library.rs:27`, `:406-407`); none is attached to a host buffer. A readback into a coarse-grained buffer would need `hipEventReleaseToSystem` or a stream synchronisation (HMEM-R5); no readback is planned into a staging buffer (RI-TGT-006 names buffers "that the device copies from") |
| HMEM-R6 | `hipHostRegister` for a registered upload | **not due** (R2) | RI-WST-007 is R2 (#104). The flags HIP 7.2.4 documents include no coarse-grained registration (see the requirement); #104 will have to settle how its "coarse-grained" is obtained. **Not verified** from a primary source |
| HMEM-R7 | Per-buffer peer mapping with `hipMemSetAccess` | **not due** (R2) | RI-ROC-013 is R2 (#100); no peer call is bound (the [HIP](std-hip-tracker.html) tracker's HIP-12 records `hipDeviceCanAccessPeer`, R2) |

**PR #110, opened during this audit.** At 21:47 UTC on 2026-11-15 PR
[#110](https://github.com/itej89/rustinfer/pull/110) (#93, `feat/93-pinned-staging`
→ `main`) opened. Read at its head `82c9ab3`: it binds `hipHostMalloc`,
`hipHostFree` and `hipEventQuery`, allocates every staging buffer with
`hipHostMallocNonCoherent` and no mapped flag (`crates/rustinfer-target-rocm/src/hip.rs:40-43`;
the value `0x80000000` is the one `hip_runtime_api.h:868` defines at
`rocm-7.2.4`, downloaded as `specs/runtime/rocm-7.2.4-hip_runtime_api.h`),
adds staging buffers, copy classes and stream classes to the `Device` trait
(`crates/rustinfer-target/src/target.rs:65-185`), uploads from them with
`hipMemcpyAsync`, and refuses a buffer for reuse while its copy's event is
pending (`crates/rustinfer-target-rocm/src/device/mod.rs:485-540`,
`src/device/staging.rs:1-7`, `:222-227`). That
meets HMEM-R1 to HMEM-R5 for the target; Sluice stays on pageable chunks
("Moving Sluice's pipeline onto the staging buffers is #94"). Not merged and
not run here, so the result below is `main`'s, and HMEM-1 and HMEM-2 are
marked In PR #110 on the tracker.

## Result

Nothing of the R1 scope is implemented on `5a6db49`: there is no pinned host
memory, an upload blocks the host and is copied from whatever slice the
caller holds, and Sluice's staging pool is pageable. That matches the plan:
the standard came with SRS v0.5 on 2026-11-15, and the staging buffers, the
copy classes and the asynchronous upload are #93, Sluice on them #94.
**Missing.** HMEM-1 to HMEM-3 are open R1 gaps, the first two in PR #110; HMEM-4 (registered upload) and
HMEM-5 (per-buffer peer mapping) are R2. Gaps are on the
[tracker](std-hip-mem-tracker.html).
