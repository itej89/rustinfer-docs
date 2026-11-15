---
title: "LLVM 23.1 audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / LLVM 23.1"
order: 12
summary: The 2026-11-14 re-audit at main 81fbcba of rustinfer's LLVM link, AMDGPU code generation and lld link against the LLVM 23.1 documentation; R1 conforms, verified on gfx950, gfx942 not yet run.
---

# LLVM 23.1 audit

**Audit of 2026-11-14**, against the [requirements](std-llvm-requirements.html);
it replaces the audit of 2026-11-13, which read PR #44 before it merged.

**Method.** Read `main` at `81fbcba` (after PR #44, merge `38f2f60`, issue
#8): `crates/rustinfer-kc/src/` (`mlir/llvm.rs`, `emit.rs`, `raw.rs`,
`mod.rs`, `lower.rs`, `lld_shim.cpp`), `build.rs`, its tests,
`scripts/ci/install_llvm.sh`, `.github/workflows/ci.yml`, `Cargo.toml` and
ADR-007 (amended by #8). Read the result of GPU test #45 in #54: an MI350X
(gfx950) under ROCm 10.1 (10.1.0-3), 2026-11-15 (UTC), at `821a57e`, PR #44
before its rebase onto #58's target. Compared each item with the LLVM 23.1.0
text in `specs/compiler/`. No test was run locally. Test tags follow
`docs/testing.md` (`Verifies`, `Groundwork for`, `Reserved`).

| id | result | evidence |
|---|---|---|
| LL-R1 | **conforms** | `scripts/ci/install_llvm.sh:22` (`LLVM_MAJOR=23`), `:32-34` (exact 23.1.6 builds for jammy, noble and resolute); CI runs it in four jobs (`.github/workflows/ci.yml:46`, `:76`, `:114`, `:143`); `Cargo.toml:66-67` pin `melior` 0.29.1 and `mlir-sys` 230.0.2; `crates/rustinfer-core/src/config/constants.rs:574` (`KC_PINNED_LLVM_MAJOR = 23`); `crates/rustinfer-kc/src/mlir/mod.rs:205-215` refuses another major; `crates/rustinfer-kc/src/mlir/raw.rs:18-24` reads the version for the artifact (`crates/rustinfer-artifact/src/metadata.rs:59`). Test: `test_context_reports_the_pinned_llvm_major` (`crates/rustinfer-kc/tests/mlir_link.rs:31`, Groundwork for RI-KC-011) |
| LL-R2 | **not applicable** | rustinfer builds no branch and reads no operand through the C API: `crates/rustinfer-kc/src/mlir/llvm.rs` imports context, module-flag, target, data-layout, pass, emit and disassembler functions, none of them `LLVMBr`, `LLVMCondBr` or `LLVMGetOperand` |
| LL-R3 | **conforms** | `crates/rustinfer-kc/src/mlir/llvm.rs:28` (`amdgcn-amd-amdhsa`), set at `:274`. The legacy `amdgcn` spelling is accepted by 23.1. Test: `amd_lowering.rs:403` (Groundwork for RI-KC-008) |
| LL-R4 | **conforms** | `llvm.rs:275-277` set the module's data layout from the target machine |
| LL-R5 | **conforms** | `llvm.rs:278-285` add one `amdhsa_code_object_version` flag (500) with behaviour Error. Test: `test_code_object_elf_flags_name_the_architecture` (`crates/rustinfer-kc/tests/amd_lowering.rs:434`, the resulting `EI_ABIVERSION` 3) |
| LL-R6 | **conforms** | `crates/rustinfer-kc/src/mlir/lower.rs:111-136` lower masked `kir` loads and stores to `vector.maskedload` (zero pass-through) and `vector.maskedstore` on the host path. Test: `test_masked_axpy_lowers_to_masked_llvm_intrinsics` (`crates/rustinfer-kc/tests/mlir_link.rs:192`, Verifies RI-KC-002). The AMD path uses bounds-checked buffer loads instead and leaves no masked intrinsic (`amd_lowering.rs:370`) |
| LL-R7 | **conforms** | `crates/rustinfer-core/src/config/constants.rs:581` (global 1) and `:584` (shared 3); `crates/rustinfer-kc/src/dialect/types.rs:80-81`. Test: `test_memory_spaces_map_to_amdgpu_address_spaces` (`crates/rustinfer-kc/tests/dialect.rs:134`, Verifies RI-KC-002); the LDS tile lowers to address space 3 (`test_shared_tile_lowers_to_lds`, `amd_lowering.rs:331`) |
| LL-R8 | **conforms**; hardware: gfx950 verified (#45), gfx942 open (LLVM-5) | `llvm.rs:241-265` create the AMDGPU target machine for the processor with O3 and `LLVMRelocPIC` (`:43`) and no forced features. Tests: `amd_lowering.rs:208` to `:262` (the exact MFMA per R1 pair, Groundwork for RI-KC-003), `:403`. On gfx950 the generated code gave every matrix-op, masked and LDS result exactly (`max_abs_err=0`) |
| LL-R9 | **conforms**; hardware: gfx950 verified (#45), gfx942 open (LLVM-5) | No `amdgpu.buffer.oob.mode` flag (`llvm.rs:268-287`), so the back end is strict, which RI-KC-003's bounds-checked masked loads need. Test: `test_masked_load_lowers_to_a_bounds_checked_buffer_load` (`amd_lowering.rs:370`: record count 0x100 and a load at `offset:256`). On gfx950 `masked_readback` read zeros past the bound |
| LL-R10 | **conforms**; hardware: gfx950 verified (#45, #59), gfx942 open (LLVM-5) | `scripts/ci/install_llvm.sh:45`, `:48` install `lld-23` and `liblld-23-dev`, checked by `check_lld` (`:80-83`); `crates/rustinfer-kc/build.rs` builds `src/mlir/lld_shim.cpp`, which calls `lld::lldMain` with the ELF driver (`:47-63`), and links `liblldELF.a` and `liblldCommon.a`; `llvm.rs:348-358` pass `-shared --no-undefined --build-id=none --threads=1`. Tests: `llvm.rs:486` (lld's message on failure, Groundwork for RI-KC-008), `amd_lowering.rs:403` (`ET_DYN`), `:473` (byte identical across processes, Groundwork for RI-KC-011). The shared objects loaded with `hipModuleLoadData` on gfx950 |
| LL-R11 | **later release** (R2) | `crates/rustinfer-target-spirv-vulkan/src/lib.rs` is a stub with an empty catalog (RI-RV-001) |
| LL-R12 | **later release** (R3) | `crates/rustinfer-target-riscv-vector/src/lib.rs` is a stub with an empty catalog (RI-RV-001) |

## Result

Every R1 item conforms on `main`: one exact 23.1 build is installed and
linked, another major is refused, and since PR #44 the AMDGPU target machine,
the IR configuration it needs and the in-process `lld` link generate the
shared code objects the HIP loader takes. On gfx950 that output loaded and
computed exactly (#45, #59, results in #54). The gfx942 output has been seen
only as disassembly on the host; its hardware run is #61 (LLVM-5), which also
re-runs #45 on gfx950 at `main`. Gaps are on the
[tracker](std-llvm-tracker.html).
