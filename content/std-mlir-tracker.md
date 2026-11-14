---
title: "MLIR (LLVM 23) tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / MLIR (LLVM 23)"
order: 23
summary: Gaps between rustinfer's MLIR lowering and the LLVM 23 dialect definitions: the AMD path in PR #44, its hardware check and the MXFP4 operations.
---

# MLIR (LLVM 23) tracker

Gaps found by the [audit](std-mlir-audit.html). The later-release row is R2
work, listed so it stays visible and not counted as an open gap. Issues from
`gh issue list -R itej89/rustinfer --state all`, 2026-11-13.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| MLIR-1 | No `gpu`, `amdgpu` or `rocdl` lowering on `main` (ML-R10 to ML-R14) | `GPU.md` *Memory attribution*; `GPUOps.td` `GPU_GPUFuncOp`, `GPU_BarrierOp`; `AMDGPUOps.td` `AMDGPU_MFMAOp`, `AMDGPU_RawBufferLoadOp`; `Passes.td` `ConvertGpuOpsToROCDLOps` | **In PR #44** | Issue [#8](https://github.com/itej89/rustinfer/issues/8). Host tests pass in CI at `10b8b1b`; the PR waits for #45 per `docs/gpu-testing.md` |
| MLIR-2 | The MFMA operand and accumulator lane layouts, the zero read of an out-of-bounds buffer load and the LDS plus barrier round trip are not checked on hardware (ML-R11 to ML-R13) | `AMDGPUOps.td` `AMDGPU_MFMAOp` (layouts per the CDNA ISA), `AMDGPU_RawBufferLoadOp`; `GPUOps.td` `GPU_BarrierOp` | **Open** | GPU test request [#45](https://github.com/itej89/rustinfer/issues/45) (MI300X gfx942, MI355X gfx950), not run. The host tests see only mnemonics, counts and offsets |
| MLIR-3 | No `amdgpu.scaled_mfma` and no ROCDL scaled fp4 conversions for the MXFP4 paths of RI-KC-003 (ML-R15) | `AMDGPUOps.td` `AMDGPU_ScaledMFMAOp`; `ROCDLOps.td` `cvt.scalef32.*` | **Open** | Issue [#38](https://github.com/itej89/rustinfer/issues/38), blocked by #8 |
| MLIR-4 | No `spirv` dialect lowering (ML-R16) | `SPIR-V.md` *Version, extensions, capabilities*, *Target environment*, *Serialization and deserialization* | Later release R2 | No issue yet. The VCE version depends on OI-016 (SPIR-V 1.5 for Vulkan 1.2, or 1.6 for Vulkan 1.3); see [SPIR-V](std-spir-v.html) |
