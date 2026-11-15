---
title: "AMDGPU DMA Operations (LLVM 23.1)"
navtitle: Overview
section: Standards
group: "Compiler and code generation / AMDGPU DMA Operations (LLVM 23.1)"
order: 38
summary: LLVM 23.1's AMDGPU DMA Operations: the per-lane global-to-LDS load widths (1, 2, 4 bytes; 12 and 16 on gfx950) and the gfx1250 tensor load and store, the tile movers of RI-KC-015; none is described or emitted on main yet (#64).
---

# AMDGPU DMA Operations (LLVM 23.1)

**Scope (SRS §1.4, LLVM-AMDGPU-DMA):** "for RI-KC-015, the per-lane
global-to-LDS load widths (1, 2 or 4 bytes; 12 or 16 on gfx950) and the
gfx1250 tensor load and store (`llvm.amdgcn.tensor.load.to.lds`, four
descriptor groups on gfx1250, the fifth reserved)". Added by SRS v0.4.11
(PR #65, ADR-011). RI-KC-015 (i) requires each target to report its
asynchronous tile movers (none, per-lane direct-to-shared loads with their
byte widths, or a descriptor-based tensor mover with its maximum tile rank)
and its lowering to map the Kernel IR's asynchronous tile copy (RI-KC-002) to
one of them. R1 covers cpu, gfx942 and gfx950; the tensor-mover lowering
ships "with the first target that has one (gfx1250; section 2.4, 'AMD
next')", which has no release tag yet.

**Implementation on `main` (`b057ef5`):** none. The capability description
(`crates/rustinfer-kc/src/capabilities.rs:47-64`, PR #63) has no mover
field, the Kernel IR has no asynchronous copy
(`crates/rustinfer-kc/src/dialect/ops.rs:8-21`), and no lowering emits a
`load.to.lds`, `global.load.lds` or `tensor.load.to.lds`. Planned in issue
[#64](https://github.com/itej89/rustinfer/issues/64) (open, R1): the mover
field with the widths of this document, the copy and its wait, and the
ROCDL lowering for gfx942 and gfx950; for gfx1250, the field and a synthetic
capability set only.

**Conformance:** mandatory from **R1** (RI-KC-015).

**Source:** *AMDGPU DMA Operations*, LLVM 23.1.0 documentation,
<https://releases.llvm.org/23.1.0/docs/AMDGPUDMAOperations.html> ("Last
updated on 2026-08-25"), downloaded 2026-11-15 with its Markdown source as
`specs/compiler/llvm-23.1.0-AMDGPUDMAOperations.md` (146 lines; cited by
line) and the page it refers to for completion tracking, *AMDGPU Async
Operations*, as `specs/compiler/llvm-23.1.0-AMDGPUAsyncOperations.rst`. The
operations as the pinned MLIR exposes them are read from
`specs/compiler/mlir-23.1.0/ROCDLOps.td` and `AMDGPUOps.td`.

| | |
|---|---|
| Pages | [requirements](std-llvm-amdgpu-dma-requirements.html) · [audit](std-llvm-amdgpu-dma-audit.html) · [tracker](std-llvm-amdgpu-dma-tracker.html) |
| Conformance | mandatory R1 (RI-KC-015 (i); RI-KC-002's tile copy) |
| Audited | 2026-11-15, by reading `main` `b057ef5` and the documentation; no test run locally |
| Result | missing: no mover is described, no tile copy exists and nothing is lowered to a DMA operation; the generator deny-list already keeps the DMA spellings out of generators |
| Open gaps | 3 of 3 (DMA-1 per-lane widths, DMA-2 tile copy and its lowering, DMA-3 tensor-mover field), all planned in #64 |
