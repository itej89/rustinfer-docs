---
title: "MLIR (LLVM 23) audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / MLIR (LLVM 23)"
order: 22
summary: The 2026-11-13 audit of the Kernel IR dialect and its lowering against the MLIR dialect definitions of LLVM 23.
---

# MLIR (LLVM 23) audit

**Audit of 2026-11-13**, against the [requirements](std-mlir-requirements.html).

**Method.** Read `origin/main` at `ccf02b3`: `crates/rustinfer-kc/src/`
(`dialect/`, `builder.rs`, `mlir/`) and `crates/rustinfer-kc/tests/`. Read
open PR #44 (branch `feat/8-amd-lowering`, head `10b8b1b`) for the `gpu`,
`amdgpu` and `rocdl` items; its CI run 43520689140 passed, and its GPU test
request #45 has not been run. Compared every operation and pass name the code
emits with its definition in `specs/compiler/mlir-23.1.0/`. No test was run
locally. Test tags follow `docs/testing.md`.

| id | result | evidence |
|---|---|---|
| ML-R1 | **conforms** | `Cargo.toml:58` to `:59` (`melior =0.29.1`, `mlir-sys =230.0.2`, both for LLVM 23); `crates/rustinfer-kc/src/mlir/mod.rs:154` refuses another major. Test: `crates/rustinfer-kc/tests/mlir_link.rs:31` |
| ML-R2 | **conforms** | `crates/rustinfer-kc/src/dialect/irdl.rs:16` writes one `irdl.operation` per table entry with one constraint value per position; `crates/rustinfer-kc/src/mlir/mod.rs:169` to `:188` loads it and refuses a missing operation. Tests: `crates/rustinfer-kc/tests/dialect.rs:84`, `crates/rustinfer-kc/tests/mlir_link.rs:44`, `:82` (ill-typed operand refused by the IRDL verifier), `:109`, `:129` (all Verifies RI-KC-002) |
| ML-R3 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:116` (`vector.load`), `:132` (`vector.store`). The builder refuses a tile larger than its buffer (`crates/rustinfer-kc/src/builder.rs:163` to `:164`); in-bounds dynamic indices of an unmasked access are the generator's obligation, as the definition leaves out-of-bounds values unspecified. Test: `crates/rustinfer-kc/tests/mlir_link.rs:178` (Groundwork for RI-KC-008) |
| ML-R4 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:112` to `:126`: a masked `kir.tile_load` becomes `vector.maskedload` with a zero pass-through, so masked-off lanes may index past the buffer. Test: `crates/rustinfer-kc/tests/mlir_link.rs:192` (Verifies RI-KC-002) |
| ML-R5 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:129` to `:137` reorder the `kir` operands to base, indices, mask, value. Test: `crates/rustinfer-kc/tests/mlir_link.rs:192` |
| ML-R6 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:140` to `:155`: `(m, k) x (k, n) -> (m, n)` maps, parallel, parallel, reduction, kind `add`. Test: `crates/rustinfer-kc/tests/mlir_link.rs:257` (Verifies RI-KC-002) |
| ML-R7 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:81` to `:89` (`vector.create_mask`), `:159` to `:200` (`vector.multi_reduction` with the identity as accumulator and `reduction_dims`; a rank-1 reduction to a scalar is broadcast back with `vector.broadcast`). Test: `crates/rustinfer-kc/tests/mlir_link.rs:257` |
| ML-R8 | **conforms** | `crates/rustinfer-kc/src/dialect/mod.rs:47` to `:55` (the seven host passes, each defined in `Passes.td`); `crates/rustinfer-kc/src/mlir/mod.rs:221` to `:229` parse the pipeline, so an unknown pass name is a `lower` refusal. Test: `crates/rustinfer-kc/tests/mlir_link.rs:178` |
| ML-R9 | **conforms** | `crates/rustinfer-kc/src/mlir/raw.rs:26` to `:45` (`mlirTranslateModuleToLLVMIR` into a fresh `LLVMContext`, disposed on every path). Test: `crates/rustinfer-kc/tests/mlir_link.rs:206` (Groundwork for RI-KC-008; byte identical across contexts) |
| ML-R10 | **pending PR #44** | Not on `main` (only `Flavor::Host`, `crates/rustinfer-kc/src/dialect/mod.rs:29`). PR #44: `crates/rustinfer-kc/src/mlir/rocdl/wrap.rs:1` to `:7` move the kernel into the `gpu.module` `kir_kernels` as a `gpu.func` kernel; `crates/rustinfer-kc/src/mlir/rocdl/mod.rs:4` to `:5` make shared buffers work-group attributions. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:328` (Groundwork for RI-KC-003) |
| ML-R11 | **pending PR #44** | On `main` the host flavour erases the barrier (`crates/rustinfer-kc/src/dialect/mod.rs:71`), which is right for a target without work groups. PR #44: `crates/rustinfer-kc/src/dialect/mod.rs:98` lowers it to `gpu.barrier`. Hardware test `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:370` not run (#45) |
| ML-R12 | **pending PR #44** | PR #44: `crates/rustinfer-kc/src/amd.rs:71` picks the MFMA per (architecture, dtype, tile); `crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:186` to `:192` emit `amdgpu.mfma`. Tests: `crates/rustinfer-kc/tests/amd_lowering.rs:205` to `:259`, `crates/rustinfer-kc/tests/amd_target.rs:16` (Groundwork for RI-KC-003). The lane layouts the lowering assumes are checked only on hardware: `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:227`, not run (#45) |
| ML-R13 | **pending PR #44** | PR #44: `crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:329` and `:351` emit `amdgpu.raw_buffer_load` and `amdgpu.raw_buffer_store` with `boundsCheck = true`; a masked-off lane is addressed past the record count. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:367`. Hardware tests `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:273`, `:322` not run (#45) |
| ML-R14 | **pending PR #44** | PR #44: `crates/rustinfer-kc/src/dialect/mod.rs:59` and `:65` run `convert-gpu-to-rocdl{chipset=gfx942 use-bare-ptr-memref-call-conv=true}` (and `gfx950`) inside `gpu.module(...)`. The static-shape precondition holds on `main`: every `BufferType` has a static shape (`crates/rustinfer-kc/src/dialect/types.rs:190`). Test: `crates/rustinfer-kc/tests/amd_target.rs:140` (Verifies ADR-005) |
| ML-R15 | **missing** | Neither `main` nor PR #44 emits `amdgpu.scaled_mfma` or a scaled conversion; PR #44 states "MXFP4 is #38 (not here)" |
| ML-R16 | **later release** (R2) | `crates/rustinfer-target-spirv-vulkan/src/lib.rs:1` to `:5` is a stub (RI-RV-001); no `spirv` operation is emitted |

## Result

Everything `main` emits is valid against the LLVM 23 definitions: the
IRDL-defined dialect, the `vector` operations it rewrites into (with the
masked forms used exactly where the definitions allow out-of-bounds
indices), the host pass names and the `llvm` translation. The `gpu`,
`amdgpu` and `rocdl` path is complete on the host in PR #44, but the
operand layouts it assumes for `amdgpu.mfma`, which the definition delegates
to the CDNA ISA, are proven only by the hardware run of #45. The MXFP4
operations are not written yet. Gaps are on the [tracker](std-mlir-tracker.html).
