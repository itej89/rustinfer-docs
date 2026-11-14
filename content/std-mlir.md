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
(`ccf02b3`):

- `crates/rustinfer-kc/src/dialect/irdl.rs:16` generates the `kir` dialect
  as IRDL from the operation table; `crates/rustinfer-kc/src/mlir/mod.rs:169`
  loads it at context creation and checks every operation registered.
- `crates/rustinfer-kc/src/mlir/lower.rs:31` rewrites each `kir` operation
  into `vector` and `arith` operations; `crates/rustinfer-kc/src/dialect/mod.rs:47`
  is the host pipeline to `llvm`; `crates/rustinfer-kc/src/mlir/raw.rs:26`
  translates the result to LLVM IR.
- The only flavour on `main` is `Flavor::Host`
  (`crates/rustinfer-kc/src/dialect/mod.rs:29`). The `gpu`, `amdgpu` and
  `rocdl` lowering (flavours `RocdlGfx942`, `RocdlGfx950`, the
  `mlir/rocdl` preparation) is open PR #44 (branch `feat/8-amd-lowering`,
  head `10b8b1b`); its GPU test #45 has not been run. The MXFP4 paths
  (`amdgpu.scaled_mfma`, scaled conversions) are issue #38.

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
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3`, PR #44 at `10b8b1b` and the specification text; no test run locally |
| Result | part: IRDL, `vector`, the host passes and `llvm` translation conform on `main`; `gpu`, `amdgpu` and `rocdl` are pending PR #44; the MXFP4 operations are missing (#38) |
| Open gaps | 3 (one in PR #44, two open); 1 more item recorded as later release (R2) |
