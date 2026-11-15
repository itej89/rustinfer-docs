---
title: "AMDGPU intrinsics (LLVM 23.1) requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / AMDGPU intrinsics (LLVM 23.1)"
order: 43
summary: What LLVM 23.1's IntrinsicsAMDGPU.td defines for wave.reduce, fdot2c.f32.bf16, s.memrealtime and s.getreg, and how MLIR's llvm.call_intrinsic reaches an intrinsic that has no op, the part in rustinfer's scope.
---

# AMDGPU intrinsics requirements

Source: `specs/compiler/llvm-23.1.0-IntrinsicsAMDGPU.td`, cited as
**[TD]** with its lines. The intrinsics are reached from MLIR through
`llvm.call_intrinsic`, defined in `specs/compiler/mlir-23.1.0/LLVMOps.td`
(**[LLVMOps]**); which intrinsics already have an op is read from the
pinned `ROCDLOps.td` and `AMDGPUOps.td` (**[ROCDL]**, **[AMDGPU]**). What an
intrinsic selects on gfx942 and gfx950 is read from the AMDGPU target at the
same tag (**[ISel]**: `llvm-23.1.0-SIISelLowering.cpp`,
`llvm-23.1.0-VOP2Instructions.td`, `llvm-23.1.0-VOP3PInstructions.td`,
`llvm-23.1.0-Target-AMDGPU.td`). The requirement on rustinfer is the
lowering's: emit the intrinsic with the signature the `.td` declares, and
only where the target has it.

## The call path

| id | requirement | source |
|---|---|---|
| AIN-R1 | An intrinsic with no MLIR op is emitted as `llvm.call_intrinsic "<name>"(args) : (types) -> result`: "Call the specified llvm intrinsic. If the intrinsic is overloaded, use the MLIR function type of this op to determine which intrinsic to call." An immediate argument (`ImmArg`) must be a constant at the call | [LLVMOps] lines 2578 to 2598; [TD] `ImmArg` on each definition below |
| AIN-R2 | The cross-lane exchanges themselves are not in this scope: DPP, `ds_swizzle`, `ds_bpermute` and the gfx950 `permlane16.swap` / `permlane32.swap` have ops (`rocdl.update.dpp`, `rocdl.ds_swizzle`, `rocdl.ds_bpermute`, `rocdl.permlane16.swap`, `rocdl.permlane32.swap`; `amdgpu.dpp`, `amdgpu.swizzle_bitmode`, `amdgpu.permlane_swap`), so they are emitted as ops, not as calls | [ROCDL] lines 168, 191, 2311, 2365, 2386; [AMDGPU] lines 668, 778, 799; [TD] lines 2404, 2784, 2811, 3729, 3736 |

## R1: cross-lane reduction and dot product (RI-KC-020, RI-KC-021)

| id | requirement | source |
|---|---|---|
| AIN-R3 | `llvm.amdgcn.wave.reduce.<op>` for `umin`, `fmin`, `min`, `umax`, `fmax`, `max`, `add`, `fadd`, `sub`, `fsub`, `and`, `or`, `xor`: overloaded on the value type, two arguments, the value and an `i32` reduction strategy ("0: Default, 1: Iterative strategy, and 2. DPP"), the strategy an immediate; `IntrConvergent`. It reduces over the active lanes of the whole wave: the AMDGPU lowering returns one wave-uniform value (a scalar register), by an iterative loop over the active lanes or, when the target has DPP and the strategy is not iterative, by DPP row shifts and row broadcasts | [TD] lines 2493 to 2510; [ISel] `SIISelLowering.cpp` lines 5871 to 5885 (`lowerWaveReduce`, the strategy enum), 6154 to 6156 (iterative when asked or without DPP), 6404 to 6420 (the DPP form), 6797 to 6845 (the f32 forms on `V_MIN_F32`, `V_MAX_F32`, `V_ADD_F32`, `V_SUB_F32`) |
| AIN-R4 | `llvm.amdgcn.fdot2c.f32.bf16(<2 x bfloat> a, <2 x bfloat> b, float c, i1 clamp) -> float`, `%r = a[0] * b[0] + a[1] * b[1] + c`, `clamp` an immediate; `PureIntrinsic`. Its neighbour `fdot2.f32.bf16` has the same signature and does have an op (`rocdl.fdot2.f32.bf16`, "Available from gfx11 and gfx950") | [TD] lines 3309 to 3340 (the `.td` notes "This actually is similar to llvm.amdgcn.fdot2 intrinsics which produces v_dot2c_f32_f16 on gfx942. Maybe we can consolidate these."); [ROCDL] lines 1455 to 1458 |
| AIN-R5 | Emitted only for a target that has the instruction: the bf16 dot instructions are gfx950's (`FeatureDot12Insts`, `FeatureDot13Insts` are in `FeatureISAVersion9_5_Common` and not in `FeatureISAVersion9_4_Common`), so a gfx942 lowering of a length-K dot product uses the matrix op or fused multiply-adds instead (RI-KC-021: "MAY use a native dot product") | [ISel] `Target-AMDGPU.td` lines 1828 to 1888; `VOP2Instructions.td` lines 1307 to 1308 (`V_DOT2C_F32_BF16`, `HasDot13Insts`), 2940 to 2943 (its gfx950 encoding); `VOP3PInstructions.td` lines 722 to 727 (`V_DOT2_F32_BF16`, `HasDot12Insts`) |

## R2: kernel timelines (RI-OBS-006)

| id | requirement | source |
|---|---|---|
| AIN-R6 | `llvm.amdgcn.s.memrealtime() -> i64`, with side effects (`IntrHasSideEffects`), so it is not moved or merged; the counter's 100 MHz rate is the ISA guide's (AMD-FNUZ section 8.2.5), not the `.td`'s | [TD] lines 2800 to 2802 |
| AIN-R7 | `llvm.amdgcn.s.getreg(i32 imm) -> i32`, the hardware-register selector an immediate, with side effects ("so it can be used to read cycle counters"); the die id is `HW_REG` 20 per the ISA guide (AMD-FNUZ section 3.12) | [TD] lines 2242 to 2247 |
