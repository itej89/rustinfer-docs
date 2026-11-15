---
title: "MLIR (LLVM 23)"
navtitle: Overview
section: Standards
group: "Compiler and code generation / MLIR (LLVM 23)"
order: 20
summary: The MLIR dialects and passes of LLVM 23 that the Kernel IR is defined in and lowered through: gpu, amdgpu, rocdl, vector and llvm in R1, spirv in R2.
---

# MLIR (LLVM 23)

**Scope (SRS §1.4, MLIR):** the `gpu`, `amdgpu`, `rocdl`, `vector` and
`llvm` dialects and their lowering passes (R1), and the `spirv` dialect
(R2), as shipped with the LLVM of ADR-007 (23.1.x). The Kernel IR itself is
defined in MLIR's `irdl` dialect (ADR-007 point 6), so IRDL is audited here
too. Nothing else of MLIR is claimed.

**Implementation:** `crates/rustinfer-kc`, feature `mlir`. On `origin/main`
(`81fbcba`):

- `crates/rustinfer-kc/src/dialect/irdl.rs:16` generates the `kir` dialect
  as IRDL from the operation table; `crates/rustinfer-kc/src/mlir/mod.rs:220`
  loads it at context creation and checks every operation registered.
- `crates/rustinfer-kc/src/mlir/lower.rs:31` rewrites each `kir` operation
  into `vector` and `arith` operations; `crates/rustinfer-kc/src/dialect/mod.rs:71`
  is the host pipeline to `llvm`; `crates/rustinfer-kc/src/mlir/raw.rs:27`
  translates the result to LLVM IR.
- Since PR #44 (issue #8, merge `38f2f60`) the flavours `RocdlGfx942` and
  `RocdlGfx950` (`crates/rustinfer-kc/src/dialect/mod.rs:33-41`): the
  `mlir/rocdl` preparation moves the kernel into a `gpu.module`, emits
  `amdgpu.mfma` (picked by `crates/rustinfer-kc/src/amd.rs:71`) and
  bounds-checked `amdgpu.raw_buffer_load` and `raw_buffer_store`, and runs
  `convert-gpu-to-rocdl` (`dialect/mod.rs:59-68`). GPU test #45 passed on an
  MI350X (gfx950), results in #54; gfx942 is not yet run (#61). The MXFP4
  paths (`amdgpu.scaled_mfma`, scaled conversions) are issue #38.

See also the [kernel compiler](kernel-compiler.html) page.

**Conformance:** mandatory from **R1** (RI-KC-002, RI-KC-003, RI-KC-008);
the `spirv` dialect from R2 (RI-KC-004).

**Source:** the MLIR dialect documentation and operation definitions at tag
`llvmorg-23.1.0` of <https://github.com/llvm/llvm-project>, downloaded
2026-11-13 into `specs/compiler/mlir-23.1.0/`: `GPU.md`, `Vector.md`,
`LLVM.md`, `SPIR-V.md`, `IRDL.md` (from `mlir/docs/Dialects/`) and
`GPUOps.td`, `VectorOps.td`, `AMDGPUOps.td`, `ROCDLOps.td`, `Passes.td`
(the TableGen sources the rendered pages at <https://mlir.llvm.org/docs/Dialects/>
are generated from; the website shows only the latest version). MLIR has no
clause numbers, so requirements cite the operation or section and its line
in these copies.

| | |
|---|---|
| Pages | [requirements](std-mlir-requirements.html) · [audit](std-mlir-audit.html) · [tracker](std-mlir-tracker.html) |
| Conformance | mandatory R1 (`gpu`, `amdgpu`, `rocdl`, `vector`, `llvm`, passes); R2 (`spirv`) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3`, PR #44 at `10b8b1b` and the specification text; re-audited 2026-11-14 at `81fbcba` after PR #44 merged, with the gfx950 results of #45 (#54); no test run locally |
| Result | part: IRDL, `vector`, the host passes, `llvm` translation and since PR #44 `gpu`, `amdgpu` and `rocdl` conform; the MFMA layouts, bounds-checked loads and LDS barrier are verified on gfx950 (#45, results in #54), gfx942 not yet run (#61); the MXFP4 operations are missing (#38) |
| Open gaps | 2 (gfx942 hardware, #61; MXFP4 operations, #38); MLIR-1 fixed by PR #44; 1 more item recorded as later release (R2) |
