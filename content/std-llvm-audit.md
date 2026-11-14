---
title: "LLVM 23.1 audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / LLVM 23.1"
order: 12
summary: The 2026-11-13 audit of rustinfer's LLVM link and AMDGPU code generation against the LLVM 23.1 documentation.
---

# LLVM 23.1 audit

**Audit of 2026-11-13**, against the [requirements](std-llvm-requirements.html).

**Method.** Read `origin/main` at `ccf02b3`: `crates/rustinfer-kc/src/`,
its tests, `scripts/ci/install_llvm.sh`, `Cargo.toml` and ADR-007. Read open
PR #44 (branch `feat/8-amd-lowering`, head `10b8b1b`) for the items it
implements; its CI run 43520689140 passed (lint, msrv, test, build,
security), and its GPU test request #45 has not been run. Compared each item
with the LLVM 23.1.0 text in `specs/compiler/`. No test was run locally.
Test tags follow `docs/testing.md` (`Verifies`, `Groundwork for`,
`Reserved`).

| id | result | evidence |
|---|---|---|
| LL-R1 | **conforms** | `scripts/ci/install_llvm.sh:13` (`LLVM_MAJOR=23`), `:22` to `:23` (exact 23.1.6 builds); `Cargo.toml:58` to `:59`; `crates/rustinfer-kc/src/mlir/mod.rs:154` refuses another major; `crates/rustinfer-kc/src/mlir/raw.rs:17` reads the version for the artifact (`crates/rustinfer-artifact/src/metadata.rs:41`). Test: `crates/rustinfer-kc/tests/mlir_link.rs:31` (Groundwork for RI-KC-011, since the code object half of RI-KC-011 is PR #44) |
| LL-R2 | **not applicable** | rustinfer calls no branch-building or operand API: `crates/rustinfer-kc/src/mlir/raw.rs:10` to `:14` imports only context, module, print, translate and version functions; PR #44's `crates/rustinfer-kc/src/mlir/llvm.rs` adds target, pass, emit and disassembler functions, none of them `LLVMBr` or `LLVMGetOperand` |
| LL-R3 | **pending PR #44** | On `main` the host lowering only translates to LLVM IR text and sets no triple. PR #44: `crates/rustinfer-kc/src/mlir/llvm.rs:28` (`amdgcn-amd-amdhsa`), `:274` (`LLVMSetTarget`). It uses the legacy `amdgcn` spelling, which 23.1 accepts. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:400` (Groundwork for RI-KC-008) |
| LL-R4 | **pending PR #44** | PR #44: `crates/rustinfer-kc/src/mlir/llvm.rs:275` to `:277` set the module's data layout from the target machine. Not applicable to the host path on `main`, which is never compiled to machine code |
| LL-R5 | **pending PR #44** | PR #44: `crates/rustinfer-kc/src/mlir/llvm.rs:279` to `:286` add one `amdhsa_code_object_version` flag (value 500) with behaviour Error. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:431` (the resulting `EI_ABIVERSION`) |
| LL-R6 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:112` to `:126` and `:129` to `:137` lower masked `kir` loads and stores to `vector.maskedload` (zero pass-through) and `vector.maskedstore`, which `convert-vector-to-llvm` turns into these intrinsics. Test: `crates/rustinfer-kc/tests/mlir_link.rs:192` (Verifies RI-KC-002) |
| LL-R7 | **conforms** | `crates/rustinfer-core/src/config/constants.rs:433` (global 1) and `:436` (shared 3); `crates/rustinfer-kc/src/dialect/types.rs:78` to `:83`. Test: `crates/rustinfer-kc/tests/dialect.rs:134` (Verifies RI-KC-002) |
| LL-R8 | **pending PR #44** | No target machine exists on `main`. PR #44: `crates/rustinfer-kc/src/mlir/llvm.rs:242` to `:265` create the AMDGPU target machine for the processor with O3 and `LLVMRelocPIC` (`:43`) and no forced features. Tests: `crates/rustinfer-kc/tests/amd_lowering.rs:205` to `:259` (one per R1 MFMA pair, Groundwork for RI-KC-003), `:400` |
| LL-R9 | **pending PR #44** | PR #44 sets no `amdgpu.buffer.oob.mode` flag (`crates/rustinfer-kc/src/mlir/llvm.rs:268` to `:289`), so the back end uses strict semantics, which the bounds-checked masked buffer loads of RI-KC-003 need. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:367` (record count and past-the-bound offset in the disassembly, Groundwork for RI-KC-003); the zero read on hardware is `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:322`, not run (#45) |
| LL-R10 | **pending PR #44** | `main` installs no `lld` (`scripts/ci/install_llvm.sh:25` lists no `liblld-23-dev`; ADR-007 point 1 defers it to #8). PR #44: `crates/rustinfer-kc/src/mlir/lld_shim.cpp` calls `lld::lldMain` with the ELF driver; `crates/rustinfer-kc/src/mlir/llvm.rs:348` to `:360` pass `-shared --no-undefined --build-id=none --threads=1`. Tests: `crates/rustinfer-kc/tests/amd_lowering.rs:400` (`ET_DYN`), `:470` (byte identical across processes, Groundwork for RI-KC-011) |
| LL-R11 | **later release** (R2) | `crates/rustinfer-target-spirv-vulkan/src/lib.rs:1` to `:5` is a stub with an empty catalog (RI-RV-001) |
| LL-R12 | **later release** (R3) | `crates/rustinfer-target-riscv-vector/src/lib.rs:1` to `:5` is a stub with an empty catalog (RI-RV-001) |

## Result

The pinned link conforms: CI installs one exact 23.1 build, the binding
refuses any other major, and the masked intrinsics and address spaces the
Kernel IR relies on match the LangRef and AMDGPUUsage text. Nothing on `main`
generates machine code. The AMDGPU target machine, the IR configuration it
needs and the `lld` link all arrive with PR #44, whose host tests pass in CI
but whose hardware run (#45) is outstanding. Gaps are on the
[tracker](std-llvm-tracker.html).
