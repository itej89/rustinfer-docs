---
title: "AMDGPU DMA Operations (LLVM 23.1) audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / AMDGPU DMA Operations (LLVM 23.1)"
order: 40
summary: The 2026-11-15 audit at main b057ef5 of rustinfer's tile movers against LLVM 23.1's AMDGPU DMA Operations; no mover is described and no tile copy exists, so nothing is lowered to a DMA operation yet (#64).
---

# AMDGPU DMA Operations audit

**Audit of 2026-11-15**, against the [requirements](std-llvm-amdgpu-dma-requirements.html),
on `main` `b057ef5` (SRS v0.4.12; the standard was added to SRS §1.4 by
v0.4.11, PR #65). First audit.

**Method.** Read the whole of `specs/compiler/llvm-23.1.0-AMDGPUDMAOperations.md`
and the *Asyncmarks* part of `llvm-23.1.0-AMDGPUAsyncOperations.rst`, and the
operations `ROCDL_LoadToLDSOp`, `ROCDL_LoadAsyncToLDSOp`,
`ROCDL_GlobalLoadLDSOp`, `ROCDL_TensorLoadToLDSOp`, `ROCDL_WaitTensorcntOp`
(`specs/compiler/mlir-23.1.0/ROCDLOps.td:1687`, `:1707`, `:1754`, `:1967`,
`:658`) and `AMDGPU_GatherToLDSOp` (`AMDGPUOps.td:1372`) of the pinned MLIR.
Read on `b057ef5`: `crates/rustinfer-kc/src/capabilities.rs`, `amd.rs`,
`dialect/ops.rs`, `mlir/rocdl/`, `mlir/llvm.rs`, the interpreter, and
`crates/rustinfer-kc/tests/generator_sources.rs`; searched every crate for
`load.to.lds`, `load.async.to.lds`, `global.load.lds`, `gather_to_lds`,
`tensor.load`, `asyncmark` and `tensorcnt` (none found). Read the plan of
#64. No tests were run.

| id | requirement | result | evidence |
|---|---|---|---|
| DMA-R1 | Per-lane widths 1, 2, 4 (gfx942) and 1, 2, 4, 12, 16 (gfx950) in the description | **missing** (DMA-1) | `Capabilities` (`crates/rustinfer-kc/src/capabilities.rs:47-64`) holds matrix ops, shared-memory bytes, lane width, native fp8, `vector_bytes` and the tile limit; no mover. `AmdArch::capabilities` (`crates/rustinfer-kc/src/amd.rs:102-128`) and `Capabilities::cpu` (`capabilities.rs:78-88`) therefore report none, which RI-KC-015 allows for cpu but not for gfx942 and gfx950 ("gfx942 and gfx950 report per-lane direct-to-shared loads with their widths") |
| DMA-R2 | LDS slot per lane, wave-uniform base, immediate size | **missing** (DMA-2) | No lowering to a DMA operation exists, so no shared layout is chosen for one. Shared tiles become `gpu.func` workgroup attributions (`crates/rustinfer-kc/src/mlir/rocdl/wrap.rs:106-143`) written by ordinary stores |
| DMA-R3 | Flat, global or buffer source; bounds-checked buffer form | **missing** (DMA-2) | No DMA operation emitted. The masked global loads use `amdgpu.raw_buffer_load {boundsCheck = true}` (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:321-330`; `test_masked_load_lowers_to_a_bounds_checked_buffer_load`, `crates/rustinfer-kc/tests/amd_lowering.rs:372`), so the buffer form of DMA-R3 (`buffer.load.lds`, offsets inside the bounds check) is the one that would keep a ragged tile's masks |
| DMA-R4 | Asynchronous completion through asyncmarks, or the synchronous form | **missing** (DMA-2) | The Kernel IR's operations are `tile_load`, `tile_store`, `make_mask`, `mma`, `reduce`, `barrier` (`crates/rustinfer-kc/src/dialect/ops.rs:8-21`): no asynchronous copy and no completion wait, which RI-KC-002 (amended by v0.4.11) adds. Until it exists, there is nothing to map onto `asyncmark` and `wait.asyncmark` or onto the synchronous `load.to.lds` |
| DMA-R5 | Cache modifiers as for ordinary loads; nontemporal as metadata | **missing** (DMA-2) | No cache modifier is set on any access (see [AMD CDNA4 ISA](std-amd-cdna4-isa-audit.html), C4-R2); the DMA form inherits whatever the `cache-hints` pass of #64 gives it |
| DMA-R6 | gfx1250 tensor load and store: groups 0 to 3, group 4 reserved, asynchronous, wave-uniform | **not due** | Belongs to the gfx1250 target, which SRS §2.4 lists under "AMD next" with no release tag; RI-KC-015's Release ships the tensor-mover lowering "with the first target that has one (gfx1250)". #64 keeps it out of R1 ("The tensor-mover lowering ... is not in R1"). Recorded, not counted as a gap until gfx1250 has a release |
| DMA-R7 | The description can report a tensor mover with its maximum rank; generators unchanged across mover sets | **missing** (DMA-3) | No mover type to hold "descriptor-based, maximum rank"; no synthetic capability set with a tensor mover. #64 adds both ("Here only the capability field and the synthetic-set test exist") |

**Generators cannot name a mover.** RI-KC-015: "no generator or pass SHALL
name a mover, an instruction or a cache-policy bit". The deny-list test over
the generator sources already refuses the spellings a DMA operation would
need: `rocdl`, `amdgpu`, `amdgcn`, `llvm.` (`crates/rustinfer-kc/tests/generator_sources.rs:17-43`)
and the word prefixes `global_load`, `buffer_load`, `ds_` (`:55-66`). This
holds on `b057ef5` and needs no change for #64.

**The rank of gfx1250's tensor mover.** The SRS scope quotes the DMA page,
"four descriptor groups on gfx1250, the fifth reserved"; the pinned MLIR's
`amdgpu` operations say they move "tensors of up to five dimensions"
(`AMDGPUOps.td:1967`, `:1983`). The page does not say how many dimensions
four groups describe, so the gfx1250 maximum rank is not stated by either
source; #64 leaves it to the gfx1250 target description, "cited when
added". RI-KC-015's synthetic set of rank 5 tests the field, not a gfx1250
value.

## Result

Nothing in the scope is implemented on `b057ef5`: the capability
description has no mover, the Kernel IR has no asynchronous tile copy, and
no lowering emits a DMA operation. That is consistent with the plan: the
standard was added with ADR-011 on 2026-11-15, and the movers, the copy, its
lowering and the tensor-mover field are R1 work in #64. The gfx1250 tensor
lowering is not due in any release yet. **Missing.** Gaps are on the
[tracker](std-llvm-amdgpu-dma-tracker.html).
