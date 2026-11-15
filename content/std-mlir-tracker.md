---
title: "MLIR (LLVM 23) tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / MLIR (LLVM 23)"
order: 23
summary: Gaps between rustinfer's MLIR lowering and the LLVM 23 dialect definitions; the AMD path merged with PR #44 and its gfx950 layouts are verified on hardware, gfx942 (#61) and the MXFP4 operations (#38) remain.
---

# MLIR (LLVM 23) tracker

Gaps found by the [audit](std-mlir-audit.html) of 2026-11-13, re-audited
against `origin/main` `81fbcba` on 2026-11-14 after PR #44 (issue #8, merge
`38f2f60`) and PR #58 (issue #12, merge `53dac5b`) merged. The later-release
row is R2 work, listed so it stays visible and not counted as an open gap.
Issues from `gh issue view`, 2026-11-14.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| MLIR-1 | No `gpu`, `amdgpu` or `rocdl` lowering on `main` (ML-R10 to ML-R14) | `GPU.md` *Memory attribution*; `GPUOps.td` `GPU_GPUFuncOp`, `GPU_BarrierOp`; `AMDGPUOps.td` `AMDGPU_MFMAOp`, `AMDGPU_RawBufferLoadOp`; `Passes.td` `ConvertGpuOpsToROCDLOps` | Fixed 2026-11-14 38f2f60 | Issue [#8](https://github.com/itej89/rustinfer/issues/8) (closed), PR #44. Flavours `RocdlGfx942` and `RocdlGfx950` (`crates/rustinfer-kc/src/dialect/mod.rs:33-41`) run `convert-gpu-to-rocdl{chipset=gfx942 use-bare-ptr-memref-call-conv=true}` (and `gfx950`) inside `gpu.module(...)` (`:59-68`) and lower `kir.barrier` to `gpu.barrier` (`:95-100`); the kernel moves into `gpu.module @kir_kernels` as a `gpu.func` with shared buffers as work-group attributions (`crates/rustinfer-kc/src/mlir/rocdl/wrap.rs:1-27`, `:106-130`); `amdgpu.mfma` (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:186-192`) and `amdgpu.raw_buffer_load` and `raw_buffer_store` with `boundsCheck = true` (`:329`, `:351`). Host tests (Groundwork for RI-KC-003): the ten MFMA disassembly tests `crates/rustinfer-kc/tests/amd_lowering.rs:208-262`, `test_shared_tile_lowers_to_lds` (`:331`), `test_masked_load_lowers_to_a_bounds_checked_buffer_load` (`:370`); `test_rocdl_flavours_name_their_architecture_and_pipeline` (`crates/rustinfer-kc/tests/amd_target.rs:140`, Verifies ADR-005) |
| MLIR-2 | The MFMA operand and accumulator lane layouts, the zero read of an out-of-bounds buffer load and the LDS plus barrier round trip are not checked on gfx942 hardware (ML-R11 to ML-R13) | `AMDGPUOps.td` `AMDGPU_MFMAOp` (layouts per the CDNA ISA), `AMDGPU_RawBufferLoadOp`; `GPUOps.td` `GPU_BarrierOp` | **Open** | gfx950 verified on hardware: GPU test [#45](https://github.com/itej89/rustinfer/issues/45) on an MI350X under ROCm 10.1 (10.1.0-3), results in [#54](https://github.com/itej89/rustinfer/issues/54) (2026-11-15 UTC): 4 passed, all 18 `mma` lines (bf16, OCP E4M3 and E5M2, three shapes, 64 and 256 work items) and the masked, readback and LDS lines `max_abs_err=0`. gfx942 (bf16 and FNUZ fp8 MFMA layouts, 64 KiB LDS) not yet run: [#61](https://github.com/itej89/rustinfer/issues/61). The gfx950 run was at `821a57e`, the PR #44 head before its rebase onto the ROCm target of #58; on `main` the tests load through `RocmTarget` (`crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:1-6`), and #61 also asks for a gfx950 re-run on `main` |
| MLIR-3 | No `amdgpu.scaled_mfma` and no ROCDL scaled fp4 conversions for the MXFP4 paths of RI-KC-003 (ML-R15) | `AMDGPUOps.td` `AMDGPU_ScaledMFMAOp`; `ROCDLOps.td` `cvt.scalef32.*` | **Open** | Issue [#38](https://github.com/itej89/rustinfer/issues/38) (open), no longer blocked now that #8 is closed. Nothing on `81fbcba` emits either operation |
| MLIR-4 | No `spirv` dialect lowering (ML-R16) | `SPIR-V.md` *Version, extensions, capabilities*, *Target environment*, *Serialization and deserialization* | Later release R2 | No issue yet. The VCE version depends on OI-016 (SPIR-V 1.5 for Vulkan 1.2, or 1.6 for Vulkan 1.3); see [SPIR-V](std-spir-v.html) |
