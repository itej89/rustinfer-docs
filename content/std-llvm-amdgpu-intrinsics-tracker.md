---
title: "AMDGPU intrinsics (LLVM 23.1) tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / AMDGPU intrinsics (LLVM 23.1)"
order: 45
summary: Gaps between rustinfer and LLVM 23.1's IntrinsicsAMDGPU.td; wave.reduce (#83) and fdot2c.f32.bf16 (#84) are open R1 work after the tile distribution of #64, the timer intrinsics are R2 (#105).
---

# AMDGPU intrinsics tracker

Gaps found by the [audit](std-llvm-amdgpu-intrinsics-audit.html) of
2026-11-15 against `main` `5a6db49`. AIN-1 and AIN-2 are R1 and wait on the
tile distribution of [#64](https://github.com/itej89/rustinfer/issues/64)
(open PR #77) and the capability fields of
[#81](https://github.com/itej89/rustinfer/issues/81). AIN-3 is R2; its issue
[#105](https://github.com/itej89/rustinfer/issues/105) sits on the milestone
`R1 — foundation` only because no R2 milestone exists yet (the Epic #1
checklist lists it under "later releases ... not R1 gates").

| id | gap | required by | status | notes |
|---|---|---|---|---|
| AIN-1 | No `llvm.amdgcn.wave.reduce.*` and no `llvm.call_intrinsic` path: row reductions are lane-local `vector.reduction`s because a tile is held whole by every lane (AIN-R1, AIN-R3) | [TD] lines 2493 to 2510; SRS RI-KC-020 and its Acceptance ("reduce within a wave by cross-lane exchanges only and across waves through shared memory") | **Open** | Planned in [#83](https://github.com/itej89/rustinfer/issues/83) (cross-lane reductions and broadcasts), blocked by #64 and #81. On `5a6db49`: `crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:504-562`. The first `llvm.call_intrinsic` arrives with PR #77 (`emit.rs:387` at `56d4382`, `implicitarg.ptr`). `wave.reduce` gives one value per wave; rows narrower than a wave need the masked exchanges of AIN-R2 (see the audit) |
| AIN-2 | No `llvm.amdgcn.fdot2c.f32.bf16` (nor `rocdl.fdot2.f32.bf16`): no dot-product lowering and no vector-unit capability to gate it to gfx950 (AIN-R1, AIN-R4, AIN-R5) | [TD] lines 3309 to 3340; SRS RI-KC-021 ("a length-K dot product of one row MAY use a native dot product ... a compiler setting the tuner measures") and its Acceptance (`v_dot2_f32_bf16` in the gfx950 code object) | **Open** | Planned in [#84](https://github.com/itej89/rustinfer/issues/84) (vector-unit selection), blocked by #64 and #81. Not verified: which instruction the `c` intrinsic selects; the op-backed `fdot2.f32.bf16` selects `v_dot2c_f32_bf16` without modifiers and `v_dot2_f32_bf16` otherwise (audit) |
| AIN-3 | No `llvm.amdgcn.s.memrealtime` or `s.getreg` for per-work-group timestamps and die ids (AIN-R6, AIN-R7) | [TD] lines 2242 to 2247, 2800 to 2802; SRS RI-OBS-006 | Later release R2 | [#105](https://github.com/itej89/rustinfer/issues/105) (device timestamps and compute-die ids per work group, R2) |
