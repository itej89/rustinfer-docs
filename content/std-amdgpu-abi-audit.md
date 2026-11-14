---
title: "AMDGPU code object V5 audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / AMDGPU code object V5"
order: 32
summary: The 2026-11-13 audit of rustinfer's AMD code objects against AMDGPUUsage code object V5; everything is pending PR #44 or untested.
---

# AMDGPU code object V5 audit

**Audit of 2026-11-13**, against the [requirements](std-amdgpu-abi-requirements.html).

**Method.** Searched `origin/main` at `ccf02b3` for any code that emits,
links or reads a code object (none). Read open PR #44 (branch
`feat/8-amd-lowering`, head `10b8b1b`): `crates/rustinfer-kc/src/mlir/llvm.rs`,
`emit.rs`, `code_object.rs`, `lld_shim.cpp`,
`crates/rustinfer-target-rocm/src/ffi/hip.rs` and the tests
`crates/rustinfer-kc/tests/amd_lowering.rs` and
`crates/rustinfer-target-rocm/tests/gpu_code_objects.rs`. PR #44's CI run
43520689140 passed; its GPU test request #45 has not been run. Each field
was compared with the AMDGPUUsage text at `llvmorg-23.1.0`. No code object
was built or inspected locally. Test tags follow `docs/testing.md`.

| id | result | evidence |
|---|---|---|
| AB-R1 | **pending PR #44** | `crates/rustinfer-kc/src/mlir/code_object.rs:80` to `:93` refuse anything but a little-endian ELF64 with `EM_AMDGPU`. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:431` reaches that check through `elf_flags()` for both architectures (Groundwork for RI-KC-003) |
| AB-R2 | **pending PR #44**, untested | PR #44 builds for the `amdhsa` OS (`crates/rustinfer-kc/src/mlir/llvm.rs:28`), for which the back end writes `ELFOSABI_AMDGPU_HSA`; no test reads `EI_OSABI` (byte 7). ABI-2 |
| AB-R3 | **pending PR #44** | `crates/rustinfer-kc/src/mlir/llvm.rs:32` pins version 500 through the `amdhsa_code_object_version` module flag (`:279` to `:286`) instead of relying on the default. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:431` asserts `EI_ABIVERSION` = 3 (`ELFABIVERSION_AMDGPU_HSA_V5`) |
| AB-R4 | **pending PR #44** | `crates/rustinfer-kc/src/mlir/llvm.rs:348` to `:360` link with `ld.lld -shared --no-undefined`; `crates/rustinfer-kc/src/mlir/emit.rs:28` to `:40`. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:400` asserts `e_type` = `ET_DYN` (Groundwork for RI-KC-008). The loader's acceptance is `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:227`, not run (#45) |
| AB-R5 | **pending PR #44**, partly untested | `e_machine` = 224 is asserted at `crates/rustinfer-kc/tests/amd_lowering.rs:400` and checked by the reader (`code_object.rs:87` to `:92`). No test reads `e_entry`. ABI-2 |
| AB-R6 | **pending PR #44** | The processor is the target machine's CPU (`crates/rustinfer-kc/src/mlir/llvm.rs:242` to `:257`). Test: `crates/rustinfer-kc/tests/amd_lowering.rs:431` asserts `e_flags & 0x0ff` is 0x04c for gfx942 and 0x04f for gfx950 |
| AB-R7 | **pending PR #44** | No feature string is forced (`crates/rustinfer-kc/src/mlir/llvm.rs:252`, `c""`), so XNACK and SRAMECC are `ANY` and one object serves a device in either mode. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:431` asserts `e_flags & 0x300` = 0x100 and `e_flags & 0xc00` = 0x400 |
| AB-R8 | **pending PR #44**, partly untested | Relocation model PIC (`crates/rustinfer-kc/src/mlir/llvm.rs:43`, `:254`); the reader finds `SHF_EXECINSTR` sections and the disassembly tests read them (`code_object.rs:96` to `:114`; `amd_lowering.rs:205` to `:259`). No test checks `.note`, `.rodata` or the dynamic sections. ABI-2 |
| AB-R9 | **pending PR #44**, untested | Written by the back end for an `amdhsa` triple; no test looks for the `NT_AMDGPU_METADATA` note. ABI-2 |
| AB-R10 | **pending PR #44**, untested on the host | No host test reads the symbol table. The hardware harness resolves the kernel by name with `hipModuleGetFunction` (`crates/rustinfer-target-rocm/src/ffi/hip.rs:150`), which would fail without the symbols; not run (#45). ABI-2, ABI-3 |
| AB-R11 | **pending PR #44**, untested | Written by the back end; no test decodes the metadata. ABI-2 |
| AB-R12 | **pending PR #44**, untested | As AB-R11. With XNACK and SRAMECC `ANY` the canonical target ID is `amdgcn-amd-amdhsa--gfx942` (or `gfx950`) with no feature suffix; not checked. ABI-2 |
| AB-R13 | **missing** on the reading side; **pending PR #44**, untested, on the writing side | No code reads `.group_segment_fixed_size`, `.sgpr_count`, `.vgpr_count` or `.agpr_count`, which RI-ROC-004's check of LDS and registers before the first launch needs (ABI-4, issue #12). The kernels take bare pointers (`use-bare-ptr-memref-call-conv=true`, PR #44 `crates/rustinfer-kc/src/dialect/mod.rs:59`), so the explicit arguments are global buffers; the hidden V5 arguments are filled by HIP at launch |
| AB-R14 | **pending PR #44**, untested | Written by the back end and placed by `lld`; no test checks the descriptor's size, alignment, entry offset or reserved fields. ABI-2 |
| AB-R15 | **pending PR #44** | No `amdgpu.buffer.oob.mode` flag is set (`crates/rustinfer-kc/src/mlir/llvm.rs:268` to `:289`), so the strict per-element guarantee holds, which RI-KC-003's bounds-checked masked loads need. Test: `crates/rustinfer-kc/tests/amd_lowering.rs:367`; on hardware `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:322`, not run (#45) |

## Result

On `main` rustinfer produces no code object, so no item conforms. PR #44
configures the back end for exactly the V5 `amdhsa` form (triple, pinned
version, processor, unforced XNACK and SRAMECC, PIC, `lld -shared`) and its
host tests pin the header fields the HIP loader checks first. The parts of
the object the loader reads next (the metadata note, the `.kd` symbols and
the kernel descriptor) are produced by LLVM and are not checked by any test;
the hardware run of #45 would exercise them by loading and launching each
object. Gaps are on the [tracker](std-amdgpu-abi-tracker.html).
