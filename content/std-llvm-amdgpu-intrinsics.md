---
title: "AMDGPU intrinsics (LLVM 23.1)"
navtitle: Overview
section: Standards
group: "Compiler and code generation / AMDGPU intrinsics (LLVM 23.1)"
order: 42
summary: LLVM 23.1's IntrinsicsAMDGPU.td, for the intrinsics the lowering must reach through llvm.call_intrinsic because MLIR 23.1 has no op for them (wave.reduce, fdot2c.f32.bf16; s.memrealtime and s.getreg in R2); none is emitted on main yet (#83, #84, #105).
---

# AMDGPU intrinsics (LLVM 23.1)

**Scope (SRS §1.4, LLVM-AMDGPU-INTRINSICS):** "the AMDGPU intrinsics the
lowering emits through `llvm.call_intrinsic` because MLIR 23.1 has no op for
them: `fdot2c.f32.bf16` and `wave.reduce.*` (R1, RI-KC-020, RI-KC-021),
`s.memrealtime` and `s.getreg` (R2, RI-OBS-006)". Added by SRS v0.5 (PR #80,
from the AMD feature inventory AMD-INV, row SC-07 and the cross-lane and
vector-unit rows). RI-KC-020 lowers the reductions of a distributed tile to the
target's cross-lane exchanges; RI-KC-021 selects the vector-unit forms,
among them a native dot product for a length-K row; RI-OBS-006 (R2) records a
constant-rate timestamp and the compute die per work group.

**Implementation on `main` (`5a6db49`):** none. No crate emits
`llvm.call_intrinsic`, and none of the four intrinsics appears in the tree.
That follows from the lowering of R1 so far: a tile is a value every lane
holds whole (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:4-22`), so a
reduction is a lane-local `vector.reduction` per row (`:504-555`) and there is
nothing to exchange across lanes. Distributing tiles over lanes is #64
(RI-KC-019 (a), open PR #77); the cross-lane reductions are #83, the
vector-unit selection #84, the per-work-group timestamps #105 (R2).

**Conformance:** mandatory from **R1** (RI-KC-020, RI-KC-021); the timer
intrinsics are R2 (RI-OBS-006).

**Source:** `llvm/include/llvm/IR/IntrinsicsAMDGPU.td` at tag
`llvmorg-23.1.0`, downloaded 2026-11-15 from
<https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-23.1.0/llvm/include/llvm/IR/IntrinsicsAMDGPU.td>
as `specs/compiler/llvm-23.1.0-IntrinsicsAMDGPU.td` (4295 lines; cited by
line). Read with it, at the same tag: MLIR's `LLVMOps.td` (the
`llvm.call_intrinsic` op) and the pinned `ROCDLOps.td` and `AMDGPUOps.td`
(which ops exist), and, to see what an intrinsic becomes on gfx942 and
gfx950, the AMDGPU target's `AMDGPU.td`, `VOP2Instructions.td`,
`VOP3PInstructions.td`, `VOP3Instructions.td`, `SIInstructions.td` and
`SIISelLowering.cpp`, all under `specs/compiler/`.

| | |
|---|---|
| Pages | [requirements](std-llvm-amdgpu-intrinsics-requirements.html) · [audit](std-llvm-amdgpu-intrinsics-audit.html) · [tracker](std-llvm-amdgpu-intrinsics-tracker.html) |
| Conformance | mandatory R1 (RI-KC-020, RI-KC-021); R2 for `s.memrealtime` and `s.getreg` (RI-OBS-006) |
| Audited | 2026-11-15, by reading `main` `5a6db49`, the open PR #77 and the LLVM and MLIR sources; no test run |
| Result | missing: no intrinsic of the scope is emitted, and there is no `llvm.call_intrinsic` path on `main` yet |
| Open gaps | 2 of 3 (AIN-1 `wave.reduce`, #83; AIN-2 `fdot2c.f32.bf16`, #84); AIN-3, the timer intrinsics, is R2 (#105) |
