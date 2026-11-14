---
title: "MLIR (LLVM 23) requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / MLIR (LLVM 23)"
order: 21
summary: What the MLIR dialect definitions of LLVM 23 require of the operations rustinfer emits and the passes it runs.
---

# MLIR (LLVM 23) requirements

Source: `specs/compiler/mlir-23.1.0/` at tag `llvmorg-23.1.0`: the dialect
documents `GPU.md`, `LLVM.md`, `SPIR-V.md`, `IRDL.md` and the operation and
pass definitions `GPUOps.td`, `VectorOps.td`, `AMDGPUOps.td`, `ROCDLOps.td`,
`Passes.td`. MLIR has no clause numbers; each item names the operation, pass
or section and its line in that copy. An operation's verifier is part of its
definition: text that does not verify is not valid IR. Only the dialects of
the SRS scope are listed, plus IRDL, which defines the Kernel IR.

## Version and dialect definition (R1)

| id | requirement | source |
|---|---|---|
| ML-R1 | The MLIR of the pinned LLVM (major 23), through a binding built for that major; `mlir-sys` refuses any other | SRS §1.4 MLIR; ADR-007 points 1 and 2 |
| ML-R2 | IRDL "allows defining MLIR dialects as MLIR programs": `irdl.dialect` holds `irdl.operation`s whose `irdl.operands`, `irdl.results` and attributes are constrained by `irdl.is`, `irdl.any_of` and similar constraint values; a loaded IRDL dialect verifies every operation against them | `IRDL.md`, *Basics* (line 5), *Constraints and combinators* (line 71) |

## `vector` (R1)

| id | requirement | source |
|---|---|---|
| ML-R3 | `vector.load` and `vector.store`: base memref with one index per dimension. "No assumptions should be made on the value of elements loaded out of bounds" | `VectorOps.td`, `Vector_LoadOp` (line 1670; text at 1723 to 1727), `Vector_StoreOp` (line 1792) |
| ML-R4 | `vector.maskedload`: mask of `i1` and a pass-through vector; "If a mask bit is set and the corresponding index is out-of-bounds for the given base, the behavior is undefined. If a mask bit is not set, the value comes from the pass-through vector regardless of the index, and the index is allowed to be out-of-bounds" | `VectorOps.td`, `Vector_MaskedLoadOp` (line 1903) |
| ML-R5 | `vector.maskedstore`: operands base, indices, mask, value to store; "When the mask is set, the corresponding element from the vector is written to memory. Otherwise, no action is taken for the element" | `VectorOps.td`, `Vector_MaskedStoreOp` (line 2002) |
| ML-R6 | `vector.contract`: `indexing_maps`, `iterator_types` (parallel or reduction) and combining `kind`, with an accumulator of the result's shape | `VectorOps.td`, `Vector_ContractionOp` (line 48) |
| ML-R7 | `vector.multi_reduction`: `kind`, `source`, an accumulator and `reduction_dims`, reducing "an n-D vector into an (n-k)-D vector (or a scalar when k == n)"; `vector.broadcast`; `vector.create_mask`, where each operand "specifies a range [0, operand-value)" of its dimension | `VectorOps.td`, `Vector_MultiDimReductionOp` (line 309), `Vector_BroadcastOp` (line 379), `Vector_CreateMaskOp` (line 2648) |

## Lowering passes and `llvm` (R1)

| id | requirement | source |
|---|---|---|
| ML-R8 | The conversion passes named in a pipeline must exist with that name and anchor: `convert-scf-to-cf`, `convert-vector-to-llvm`, `finalize-memref-to-llvm`, `convert-func-to-llvm`, `convert-arith-to-llvm`, `convert-cf-to-llvm`, `reconcile-unrealized-casts` | `Passes.td` (for example `ConvertVectorToLLVMPass`, line 1608) |
| ML-R9 | The `llvm` dialect lives in a built-in module and does not depend on an `LLVMContext`; the module translates to LLVM IR (`mlirTranslateModuleToLLVMIR`), and `llvm.data_layout` and `llvm.target_triple` carry the LangRef syntax | `LLVM.md`, *Dependency on LLVM IR* (line 21), *Data Layout and Triple* (line 35); `LLVMIR.h` |

## `gpu`, `amdgpu`, `rocdl` (R1)

| id | requirement | source |
|---|---|---|
| ML-R10 | Kernels are `gpu.func` with the `kernel` attribute inside a `gpu.module`; work-group buffers are memory attributions (`workgroup(...)`) with the right memory space on the memref, "live throughout the execution of the GPU function body" | `GPU.md`, *GPU address spaces* (line 28), *Memory attribution* (line 47); `GPUOps.td`, `GPU_GPUFuncOp` (line 348), `GPU_GPUModuleOp` (line 1542) |
| ML-R11 | `gpu.barrier` (default scope work-group) "waits until all work items in the workgroup have reached the operation and all memory accesses made by these work items prior to the op are visible to all work items in the workgroup" | `GPUOps.td`, `GPU_BarrierOp` (line 1429) |
| ML-R12 | `amdgpu.mfma`: `m`, `n` in {4, 16, 32}, `k` in {1, 2, 4, 8, 16, 32, 64, 128}, sources of the MFMA input types, accumulator and result of the same type; `cbsz`, `abid` and `blgp` select lane permutations; "For information on the layouts of the input and output matrices ... see the CDNA ISA documentation" | `AMDGPUOps.td`, `AMDGPU_MFMAOp` (line 1017) |
| ML-R13 | `amdgpu.raw_buffer_load` and `amdgpu.raw_buffer_store` with `boundsCheck` (default true): "When a load is out of bounds, the instruction returns zero"; "The number of records is the size of the memref, in bytes"; "Partially-out of bounds have chipset-dependent behavior" | `AMDGPUOps.td`, `AMDGPU_RawBufferLoadOp` (line 370), `AMDGPU_RawBufferStoreOp` (line 421) |
| ML-R14 | `convert-gpu-to-rocdl` runs on a `gpu.module`, with option `chipset` (the target architecture) and `use-bare-ptr-memref-call-conv`: "Replace memref arguments in GPU functions with bare pointers. All memrefs must have static shape" | `Passes.td`, `ConvertGpuOpsToROCDLOps` (line 684) |
| ML-R15 | The MXFP4 paths of RI-KC-003 use `amdgpu.scaled_mfma`, whose sources may be 32-element vectors of `f8E4M3FN`, `f8E5M2`, `f6E2M3FN`, `f6E3M2FN` or `f4E2M1FN`, with per-operand scales; and the ROCDL scaled conversions (`rocdl.cvt.scalef32.*`) | `AMDGPUOps.td`, `ScaledMFMAInTypes` (line 996), `AMDGPU_ScaledMFMAOp` (line 1571); `ROCDLOps.td` (line 2685 onwards) |

## `spirv` (R2)

| id | requirement | source | release |
|---|---|---|---|
| ML-R16 | A `spirv.module` declares its version, capabilities and extensions (the VCE triple) and is lowered against a target environment; its binary comes from the dialect's serializer | `SPIR-V.md`, *Version, extensions, capabilities* (line 861), *Target environment* (line 897), *Serialization and deserialization* (line 1049) | R2 |
