---
title: "AMDGPU DMA Operations (LLVM 23.1) tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / AMDGPU DMA Operations (LLVM 23.1)"
order: 41
summary: Gaps between rustinfer and LLVM 23.1's AMDGPU DMA Operations; the per-lane mover widths, the asynchronous tile copy with its direct-to-LDS lowering, and the tensor-mover field are R1 work planned in #64.
---

# AMDGPU DMA Operations tracker

Gaps found by the [audit](std-llvm-amdgpu-dma-audit.html) of 2026-11-15
against `main` `b057ef5`. All three are R1 (RI-KC-015, RI-KC-002) and
planned in issue [#64](https://github.com/itej89/rustinfer/issues/64) (open,
milestone R1). The gfx1250 tensor load and store themselves (DMA-R6) are
not a gap yet: they ship with the gfx1250 target, which SRS §2.4 lists under
"AMD next" with no release tag.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| DMA-1 | The gfx942 and gfx950 descriptions report no tile mover: not the per-lane direct-to-LDS loads, nor their widths, 1, 2, 4 bytes on gfx942 and also 12 and 16 on gfx950 (DMA-R1) | *GFX9 DMA*, lines 36, 41 to 42; SRS RI-KC-015 (i) and its Acceptance ("gfx942 and gfx950 report per-lane direct-to-shared loads with their widths and no tensor mover, and cpu reports no mover") | **Open** | Planned in #64 (capability model, completed), with the widths of its table cited to this page, `IntrinsicsAMDGPU.td` and the ISA guides, and one test per field. `Capabilities` on `b057ef5`: `crates/rustinfer-kc/src/capabilities.rs:47-64`. The ISA side of the same widths is [CDNA4-3](std-amd-cdna4-isa-tracker.html) (gfx950) and the CDNA3 guide in [AMD-FNUZ](std-amd-fnuz-tracker.html) (gfx942) |
| DMA-2 | No asynchronous tile copy in the Kernel IR and no lowering of one to a DMA operation: no copy and completion wait, no `rocdl.load.to.lds` / `load.async.to.lds` / `global.load.lds` or `amdgpu.gather_to_lds`, no asyncmark wait, no per-lane LDS slot layout, no cache modifier on it (DMA-R2 to DMA-R5) | *Introduction*, *GFX9 DMA* (lines 11 to 89); *AMDGPU Async Operations*, *Asyncmarks*; SRS RI-KC-002 (the copy), RI-KC-015 (the lowering picks the mover) | **Open** | Planned in #64 (asynchronous tile copy and its lowering): the operation, its builder methods and interpreter semantics ("a copy then a wait equals a load then a store"), lowered "at a width the capability lists, or plain loads and stores when the width or the layout does not fit"; acceptance: the lowered module of a staged GEMM holds the direct-to-LDS load at a capability width. The `pipeline` and `prefetch` passes (RI-KC-016 (a), (b)) emit their staged copies as this operation. Operation table on `b057ef5`: `crates/rustinfer-kc/src/dialect/ops.rs:8-21` |
| DMA-3 | No way to describe a descriptor-based tensor mover with its maximum tile rank, and no synthetic capability set with one, so RI-KC-015's mover-independence check cannot be written (DMA-R7) | *GFX1250*, *Tensor Addressing* (lines 126 to 146); SRS RI-KC-015 (i) and its Acceptance ("a tensor mover of rank 5") | **Open** | Planned in #64 ("Here only the capability field and the synthetic-set test exist"); the gfx1250 lowering (`rocdl.tensor.load.to.lds`, `rocdl.tensor.store.from.lds`, `rocdl.s.wait.tensorcnt`) is outside R1. The gfx1250 maximum rank is stated by neither this page (four descriptor groups, the fifth reserved) nor MLIR ("up to five dimensions"); see the audit |
