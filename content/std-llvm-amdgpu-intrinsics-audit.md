---
title: "AMDGPU intrinsics (LLVM 23.1) audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / AMDGPU intrinsics (LLVM 23.1)"
order: 44
summary: The 2026-11-15 audit at main 5a6db49 of rustinfer's lowering against LLVM 23.1's IntrinsicsAMDGPU.td; no intrinsic of the scope is emitted because tiles are not yet distributed over lanes (#64), so the reductions and the dot product are still R1 work (#83, #84).
---

# AMDGPU intrinsics audit

**Audit of 2026-11-15**, against the [requirements](std-llvm-amdgpu-intrinsics-requirements.html),
on `main` `5a6db49` (PR #74 merged over SRS v0.5, PR #80 at `4ee01b6`; the
standard was added to SRS §1.4 by v0.5). First audit.

**Method.** Read the definitions of the scope in
`specs/compiler/llvm-23.1.0-IntrinsicsAMDGPU.td`, `llvm.call_intrinsic` in
`mlir-23.1.0/LLVMOps.td`, and searched the pinned `ROCDLOps.td`,
`AMDGPUOps.td` and `GPUOps.td` for an op of each intrinsic (none for
`wave.reduce`, `fdot2c.f32.bf16`, `s.memrealtime` or `s.getreg`; one for
`fdot2.f32.bf16`). Read the AMDGPU target files listed on the
[requirements](std-llvm-amdgpu-intrinsics-requirements.html) for what each
intrinsic selects. Read on `5a6db49`: `crates/rustinfer-kc/src/capabilities.rs`,
`amd.rs`, `mlir/lower.rs`, `mlir/rocdl/` and `mlir/llvm.rs`; searched every
crate for `call_intrinsic`, `llvm.amdgcn`, `wave.reduce`, `fdot2`,
`memrealtime`, `getreg`, `subgroup_reduce`, `amdgpu.dpp`, `permlane` and
`gpu.shuffle` (none found). Read the head of the open PR #77 (`56d4382`,
#64) for what it adds, and the plans of #83, #84 and #105. No tests were run.

| id | requirement | result | evidence |
|---|---|---|---|
| AIN-R1 | Intrinsics without an op go through `llvm.call_intrinsic`, immediates constant | **missing** (AIN-1, AIN-2) | No `llvm.call_intrinsic` in any crate on `5a6db49`; the AMD lowering writes MLIR text of `vector`, `memref`, `arith`, `amdgpu` and `rocdl` ops only (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs`, `mod.rs`). The open PR #77 emits the first one, for `llvm.amdgcn.implicitarg.ptr` (`crates/rustinfer-kc/src/mlir/rocdl/emit.rs:387` at `56d4382`), the work-group count of code-object V5; it is not an intrinsic of this scope, but it is the path #83 and #84 will use |
| AIN-R2 | The exchanges themselves as ops | **not due yet** | Nothing exchanges values across lanes on `main`: a tile is held whole by every lane (`helpers.rs:4-22`). PR #77 distributes tiles and exchanges values with `gpu.shuffle` (`emit.rs:318-333` at `56d4382`), an op, which is consistent with AIN-R2 |
| AIN-R3 | `wave.reduce.*` for the wave-wide reductions | **missing** (AIN-1) | `kir.reduce` becomes `vector.multi_reduction` (`crates/rustinfer-kc/src/mlir/lower.rs:159-179`) and then a private helper of one `vector.reduction` per row or one combine per row (`helpers.rs:504-562`), inside each lane. RI-KC-020 is not tagged by any test (the [requirements page](ref-requirements.html) shows it planned). See the note on row reductions below |
| AIN-R4 | `fdot2c.f32.bf16` for the length-K dot product | **missing** (AIN-2) | No dot-product path: `kir.mma` lowers to `amdgpu.mfma` whatever M is (`helpers.rs:186-192`), and no lowering emits a dot instruction. `Capabilities` (`crates/rustinfer-kc/src/capabilities.rs:47-64`) has no vector-unit field to say the target has a dot product (RI-KC-015 (v), #81) |
| AIN-R5 | Only where the target has it (gfx950) | **not due yet** | Nothing is emitted, so nothing is emitted for gfx942 by mistake. #84 makes the choice "a compiler setting the tuner measures", gated by the capability |
| AIN-R6 | `s.memrealtime` | **not due** (R2) | RI-OBS-006 is R2 (#105); no timestamp setting exists |
| AIN-R7 | `s.getreg` | **not due** (R2) | As AIN-R6 |

**`wave.reduce` reduces a whole wave, a row is often less.** The AMDGPU
lowering of `wave.reduce` returns one value for all active lanes of the wave,
in a scalar register (`SIISelLowering.cpp:5871-6420`). A row of a distributed
tile spans the whole wave only for some layouts; when it spans 16 or 32 lanes
(an MFMA output fragment), the per-row reduction needs the exchanges of
AIN-R2 (DPP row operations, `ds_swizzle`, the gfx950 lane-half swaps) with a
mask, not `wave.reduce`. RI-KC-020's "choosing per exchange the cheapest kind
the target lists" covers both, so this is a design note for #83, not a gap of
its own.

**`fdot2c.f32.bf16` and `rocdl.fdot2.f32.bf16`.** The SRS names the `c`
intrinsic because MLIR has no op for it. The neighbouring
`llvm.amdgcn.fdot2.f32.bf16`, with the same signature, has one
(`rocdl.fdot2.f32.bf16`, `ROCDLOps.td:1455-1458`, "Available from gfx11 and
gfx950"), and on gfx950 it selects `V_DOT2C_F32_BF16_e32` when no modifier is
set (`VOP2Instructions.td:1321-1324`, `AddedComplexity = 30`) or the VOP3P
`V_DOT2_F32_BF16` (`VOP3PInstructions.td:722-727`). In the four AMDGPU
instruction files read here (`VOP2`, `VOP3`, `VOP3P`, `SIInstructions.td`) no
selection pattern names `int_amdgcn_fdot2c_f32_bf16`; clang emits it for
gfx950 (`clang/test/CodeGenOpenCL/builtins-amdgcn-gfx950.cl:263`, downloaded
as `specs/compiler/llvm-23.1.0-builtins-amdgcn-gfx950.cl`). **Not verified:**
which instruction `fdot2c.f32.bf16` selects, and whether RI-KC-021's
acceptance text (`v_dot2_f32_bf16` in the gfx950 code object) is met by
either intrinsic or by the `c` form `v_dot2c_f32_bf16`; that needs the
pinned LLVM to compile one, which #84's offline test will do.

## Result

Nothing in the scope is emitted on `5a6db49`, and nothing could be: the two R1
intrinsics serve reductions across lanes and a per-lane dot product, and R1
tiles are not yet distributed over lanes (RI-KC-019 (a), #64, open PR #77).
**Missing.** AIN-1 (`wave.reduce`, #83) and AIN-2 (`fdot2c.f32.bf16`, #84)
are open R1 gaps, both blocked by #64 and #81; AIN-3 (the timer intrinsics) is
R2 (#105). Gaps are on the [tracker](std-llvm-amdgpu-intrinsics-tracker.html).
