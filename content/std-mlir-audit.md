---
title: "MLIR (LLVM 23) audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / MLIR (LLVM 23)"
order: 22
summary: The 2026-11-14 audit of the Kernel IR dialect and its lowering against the MLIR dialect definitions of LLVM 23, on main 81fbcba after PR #44; the AMD path conforms, its gfx950 layouts verified on hardware, gfx942 and the MXFP4 operations open.
---

# MLIR (LLVM 23) audit

**Audit of 2026-11-14**, against the [requirements](std-mlir-requirements.html),
on `origin/main` `81fbcba` (after PR #44, issue #8, merge `38f2f60`: the
`gpu`, `amdgpu` and `rocdl` lowering; PR #58, issue #12, merge `53dac5b`: the
ROCm target its hardware tests load through). First audited 2026-11-13 on
`ccf02b3`, with PR #44 read at `10b8b1b`.

**Method.** Read `origin/main` at `81fbcba`: `crates/rustinfer-kc/src/`
(`dialect/`, `builder.rs`, `amd.rs`, `mlir/`, `mlir/rocdl/`) and
`crates/rustinfer-kc/tests/` (`mlir_link.rs`, `dialect.rs`, `amd_lowering.rs`,
`amd_target.rs`), and `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs`.
Compared every operation and pass name the code emits with its definition in
`specs/compiler/mlir-23.1.0/`. Hardware evidence is the owner's run of GPU
test #45 on an MI350X (gfx950) under ROCm 10.1 (10.1.0-3), posted in #54 on
2026-11-15 (UTC): 4 passed, every line `max_abs_err=0`. It ran at `821a57e`,
the PR #44 head before its rebase onto #58's ROCm target; the inputs,
assertions and expected lines are unchanged on `main`, and #61 asks for a
gfx950 re-run there as well as the gfx942 run. No test was run locally. Test
tags follow `docs/testing.md`.

| id | result | evidence |
|---|---|---|
| ML-R1 | **conforms** | `Cargo.toml:66` to `:67` (`melior =0.29.1`, `mlir-sys =230.0.2`, both for LLVM 23); `crates/rustinfer-kc/src/mlir/mod.rs:205` to `:217` refuse another major. Test: `crates/rustinfer-kc/tests/mlir_link.rs:31` |
| ML-R2 | **conforms** | `crates/rustinfer-kc/src/dialect/irdl.rs:16` writes one `irdl.operation` per table entry with one constraint value per position; `crates/rustinfer-kc/src/mlir/mod.rs:220` to `:240` loads it and refuses a missing operation. Tests: `crates/rustinfer-kc/tests/dialect.rs:84`, `crates/rustinfer-kc/tests/mlir_link.rs:44`, `:82` (ill-typed operand refused by the IRDL verifier), `:109`, `:129` (all Verifies RI-KC-002) |
| ML-R3 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:116` (`vector.load`), `:132` (`vector.store`). The builder refuses a tile larger than its buffer (`crates/rustinfer-kc/src/builder.rs:163` to `:164`); in-bounds dynamic indices of an unmasked access are the generator's obligation, as the definition leaves out-of-bounds values unspecified. Test: `crates/rustinfer-kc/tests/mlir_link.rs:178` (Groundwork for RI-KC-008) |
| ML-R4 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:112` to `:126`: a masked `kir.tile_load` becomes `vector.maskedload` with a zero pass-through, so masked-off lanes may index past the buffer. Test: `crates/rustinfer-kc/tests/mlir_link.rs:192` (Verifies RI-KC-002) |
| ML-R5 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:129` to `:137` reorder the `kir` operands to base, indices, mask, value. Test: `crates/rustinfer-kc/tests/mlir_link.rs:192` |
| ML-R6 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:140` to `:155`: `(m, k) x (k, n) -> (m, n)` maps, parallel, parallel, reduction, kind `add`. Test: `crates/rustinfer-kc/tests/mlir_link.rs:257` (Verifies RI-KC-002) |
| ML-R7 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:81` to `:89` (`vector.create_mask`), `:159` to `:200` (`vector.multi_reduction` with the identity as accumulator and `reduction_dims`; a rank-1 reduction to a scalar is broadcast back with `vector.broadcast`). Test: `crates/rustinfer-kc/tests/mlir_link.rs:257` |
| ML-R8 | **conforms** | `crates/rustinfer-kc/src/dialect/mod.rs:71` to `:79` (the seven host passes, each defined in `Passes.td`); `crates/rustinfer-kc/src/mlir/mod.rs:272` to `:276` parse the pipeline, so an unknown pass name is a `lower` refusal. Test: `crates/rustinfer-kc/tests/mlir_link.rs:178` |
| ML-R9 | **conforms** | `crates/rustinfer-kc/src/mlir/raw.rs:27` to `:45` (`mlirTranslateModuleToLLVMIR` into a fresh `LLVMContext`, disposed on every path). Test: `crates/rustinfer-kc/tests/mlir_link.rs:206` (Groundwork for RI-KC-008; byte identical across contexts) |
| ML-R10 | **conforms** | `crates/rustinfer-kc/src/mlir/rocdl/wrap.rs:1` to `:27` move the one `func.func` into `gpu.module @kir_kernels` as a `gpu.func` kernel; shared buffers become `workgroup(...)` attributions (`skeleton`, `:106` to `:130`), global ones stay arguments. Test: `test_shared_tile_lowers_to_lds` (`crates/rustinfer-kc/tests/amd_lowering.rs:331`, Groundwork for RI-KC-003) |
| ML-R11 | **conforms**; verified on gfx950 hardware, gfx942 not yet run | The host flavour erases the barrier and the ROCDL flavours replace it with `gpu.barrier` (`crates/rustinfer-kc/src/dialect/mod.rs:95` to `:100`). Hardware: `test_shared_tile_round_trips_through_lds_on_the_gpu` (`crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:400`, Groundwork for RI-KC-003) passed on gfx950 in #45 (`shared_staging` at 64 and 256 work items, `max_abs_err=0`, #54); gfx942 is #61. MLIR-2 |
| ML-R12 | **conforms**; layouts verified on gfx950 hardware, gfx942 not yet run | `crates/rustinfer-kc/src/amd.rs:71` picks the MFMA per (architecture, dtype, tile) from the table at `:150` to `:171` (gfx942: bf16 32x32x8 and 16x16x16, FNUZ fp8 32x32x16 and 16x16x32; gfx950: bf16 32x32x16 and 16x16x32, OCP E4M3 and E5M2 32x32x64 and 16x16x128 with format codes 0 and 1); `crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:186` to `:192` emit `amdgpu.mfma` with `m`, `n`, `k` in the allowed sets. Host tests (Groundwork for RI-KC-003): `crates/rustinfer-kc/tests/amd_lowering.rs:208` to `:262` (each pair disassembles to its instruction), `:271` and `:314` (other pairs and unaligned tiles refused), `crates/rustinfer-kc/tests/amd_target.rs:16`, `:72`, `:90`, `:122`. The lane layouts, which the definition delegates to the CDNA ISA: `test_matrix_op_matches_the_cpu_on_the_gpu` (`crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:257`) passed on gfx950 in #45, all 18 `mma` lines exact (#54); gfx942 is #61. MLIR-2 |
| ML-R13 | **conforms**; verified on gfx950 hardware, gfx942 not yet run | `crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:329` and `:351` emit `amdgpu.raw_buffer_load` and `amdgpu.raw_buffer_store` with `boundsCheck = true`; a masked-off lane is addressed past the record count. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:370`. Hardware: `test_masked_load_and_store_honour_the_mask_on_the_gpu` and `test_masked_load_reads_zero_past_the_bound_on_the_gpu` (`crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:303`, `:352`) passed on gfx950 in #45 (`masked_axpy`, `masked_readback`, `max_abs_err=0`, #54); gfx942 is #61. MLIR-2 |
| ML-R14 | **conforms** | `crates/rustinfer-kc/src/dialect/mod.rs:59` to `:68` run `convert-gpu-to-rocdl{chipset=gfx942 use-bare-ptr-memref-call-conv=true}` (and `gfx950`) inside `gpu.module(...)`. The static-shape precondition holds: every `BufferType` has a static shape (`crates/rustinfer-kc/src/dialect/types.rs:190`). Test: `crates/rustinfer-kc/tests/amd_target.rs:140` (Verifies ADR-005) |
| ML-R15 | **missing** | Nothing on `81fbcba` emits `amdgpu.scaled_mfma` or a scaled conversion; the MFMA table has no fp4 or fp6 entry (`crates/rustinfer-kc/src/amd.rs:150` to `:171`). Issue #38. MLIR-3 |
| ML-R16 | **later release** (R2) | `crates/rustinfer-target-spirv-vulkan/src/lib.rs:1` to `:5` is a stub (RI-RV-001); no `spirv` operation is emitted |

## Result

Everything `main` emits is valid against the LLVM 23 definitions: the
IRDL-defined dialect, the `vector` operations it rewrites into, the host and
ROCDL pass names, the `llvm` translation, and since PR #44 the `gpu`,
`amdgpu` and `rocdl` path (ML-R10 to ML-R14; MLIR-1 fixed). The operand
layouts it assumes for `amdgpu.mfma`, which the definition delegates to the
CDNA ISA, the zero read of a bounds-checked load and the LDS round trip
across `gpu.barrier` are verified on gfx950 hardware (#45, results in #54);
on gfx942 they are not yet run (#61, MLIR-2). The MXFP4 operations are not
written yet (#38, MLIR-3). **Partial.** Gaps are on the [tracker](std-mlir-tracker.html).
