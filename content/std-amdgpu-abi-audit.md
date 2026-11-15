---
title: "AMDGPU code object V5 audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / AMDGPU code object V5"
order: 32
summary: The 2026-11-14 re-audit at main 81fbcba of rustinfer's AMD code objects against AMDGPUUsage code object V5; the header, flags, note and metadata reader conform, gfx950 objects load on hardware, gfx942 is not yet run.
---

# AMDGPU code object V5 audit

**Audit of 2026-11-14**, against the [requirements](std-amdgpu-abi-requirements.html);
it replaces the audit of 2026-11-13, which read PR #44 before it merged.

**Method.** Read `main` at `81fbcba` (after the merges of PR #58,
`53dac5b`, and PR #44, `38f2f60`): `crates/rustinfer-kc/src/mlir/llvm.rs`,
`emit.rs`, `code_object.rs`, `lld_shim.cpp`, `build.rs`, the tests
`crates/rustinfer-kc/tests/amd_lowering.rs` and `tests/code_object/mod.rs`;
the ROCm target's reader `crates/rustinfer-target-rocm/src/code_object/`,
`src/device/kernels.rs`, `src/resources.rs` and its tests `code_object.rs`,
`code_object_golden.rs`, `resources.rs`, `architecture.rs`,
`gpu_code_objects.rs` and `gpu.rs`. Read the hardware results of #45 and #59
in #54: an MI350X (gfx950) under ROCm 10.1 (10.1.0-3), 2026-11-15 (UTC);
#45 ran at `821a57e` (PR #44 before its rebase onto #58's target), #59 at
`bb0ce2f` (the head PR #58 merged). Compared each field with the AMDGPUUsage
text at `llvmorg-23.1.0`. Nothing was built or run locally. Test tags follow
`docs/testing.md`. "Hardware" below means gfx950 verified (#45, #59) and
gfx942 not yet run (#61).

| id | result | evidence |
|---|---|---|
| AB-R1 | **conforms** | The kernel compiler's reader refuses anything but a little-endian ELF64 with `EM_AMDGPU` (`crates/rustinfer-kc/src/mlir/code_object.rs:80-93`); the ROCm target's reader does the same before a load (`crates/rustinfer-target-rocm/src/code_object/elf.rs:107-119`). Tests: `test_code_object_elf_flags_name_the_architecture` (`crates/rustinfer-kc/tests/amd_lowering.rs:434`, Groundwork for RI-KC-003); `test_header_refusals` (`crates/rustinfer-target-rocm/tests/code_object.rs:98`, Verifies RI-ROC-004) |
| AB-R2 | **conforms** | Built for the `amdhsa` OS (`crates/rustinfer-kc/src/mlir/llvm.rs:28`). Test: `test_code_object_header_is_hsa_dynamic_with_no_entry` (`amd_lowering.rs:543`) asserts `EI_OSABI` 64 for both architectures; the target refuses any other value (`elf.rs:120`) |
| AB-R3 | **conforms** | Version 500 through the `amdhsa_code_object_version` flag (`llvm.rs:32`, `:268-287`). Test: `amd_lowering.rs:434` asserts `EI_ABIVERSION` 3; the target refuses another (`elf.rs:121-125`) |
| AB-R4 | **conforms**; hardware: gfx950 verified, gfx942 open (ABI-3) | `ld.lld -shared --no-undefined --build-id=none --threads=1` in-process (`llvm.rs:348-358`, `emit.rs:28-40`). Tests: `test_trivial_module_compiles_in_process_byte_identically` (`amd_lowering.rs:403`, Groundwork for RI-KC-008) and `:543` assert `ET_DYN`; the target refuses another type (`elf.rs:128-133`). On gfx950 `hipModuleLoadData` accepted the objects (#45 4 passed, #59 11 passed) |
| AB-R5 | **conforms** | `e_machine` 224 at `amd_lowering.rs:403`, `e_entry` 0 at `:543` |
| AB-R6 | **conforms** | The processor is the target machine's CPU (`llvm.rs:241-265`). Test: `amd_lowering.rs:434` asserts 0x04c and 0x04f. The target maps the field to a processor (`crates/rustinfer-target-rocm/src/code_object/mod.rs:19-22`, `:130-137`) and refuses one that is not the device's (`src/device/kernels.rs:105`; `test_code_object_machine_must_match_the_device`, `tests/architecture.rs:125`, Verifies RI-ROC-003) |
| AB-R7 | **conforms** | No feature string is forced (`llvm.rs:252`, `c""`), so XNACK and SRAMECC are `ANY`; asserted at `amd_lowering.rs:434`. The target reads both settings (`mod.rs:139-145`) and refuses one the device's mode excludes (`kernels.rs:106-107`; `tests/architecture.rs:143`, Verifies RI-ROC-003). #59 ran on `gfx950:sramecc+:xnack-` |
| AB-R8 | **conforms**, dynamic sections untested on the host | PIC (`llvm.rs:43`, `:254`). The `.note` and `.rodata` sections are read by `amd_lowering.rs:519-535` and `:585`; no test reads `.dynamic`, `.dynstr`, `.dynsym` or `.hash` of the compiler's objects. ABI-2 |
| AB-R9 | **conforms** | Test: `test_code_object_metadata_note_lists_the_kernel` (`amd_lowering.rs:560`) finds exactly one `NT_AMDGPU_METADATA` note with vendor `AMDGPU` and decodes it. The target reads the note from the `PT_NOTE` segments (`elf.rs:185-198`) |
| AB-R10 | **partly tested**; hardware: gfx950 verified, gfx942 open (ABI-3) | `test_kernel_descriptor_symbol_holds_the_declared_lds` (`amd_lowering.rs:585`) finds `<name>.kd`, 64 bytes, in `.rodata`; its symbol type (`STT_OBJECT`) is read (`crates/rustinfer-kc/tests/code_object/mod.rs:116`) but not asserted, and the `STT_FUNC` entry symbol is not checked. `hipModuleGetFunction` found every kernel on gfx950 (#45, #59). ABI-2 |
| AB-R11 | **conforms** | Present and decoded for both architectures (`amd_lowering.rs:560`); the target refuses an object without it (`elf.rs:185-198`; `test_metadata_refusals`, `tests/code_object.rs:142`, Verifies RI-ROC-004) |
| AB-R12 | **partly tested** | `amdhsa.version` `[1, 2]` is asserted for the compiler's objects (`amd_lowering.rs:519-535`) and required by the target (`crates/rustinfer-target-rocm/src/code_object/metadata.rs:31-43`). `amdhsa.target` must be present (`metadata.rs:22-25`) but is not compared with the device, and its value is asserted only for the test writer's objects (`tests/code_object.rs:38`, `amdgcn-amd-amdhsa--gfx942` and `--gfx950`). ABI-2 |
| AB-R13 | **conforms** | Writing: `amd_lowering.rs:560` asserts `.symbol`, `.kernarg_segment_size`, `.group_segment_fixed_size`, `.vgpr_count`, `.sgpr_count`. Reading (ABI-4, fixed by PR #58): every required kernel key but `.kernarg_segment_align` is read and its absence refused (`metadata.rs:46-64`), with each argument's `.offset`, `.size`, `.value_kind` (`:97-113`); the LDS, register, work-group and wavefront needs are checked against the device before HIP loads the object (`src/device/kernels.rs:102-120`, `src/resources.rs:63-81`). Tests: `tests/resources.rs:56` and following (Verifies RI-ROC-004). On gfx950 #59 refused 163844 LDS bytes against 163840 and launched at the limit |
| AB-R14 | **partly tested** | `amd_lowering.rs:585` asserts the descriptor's size (64 bytes), `GROUP_SEGMENT_FIXED_SIZE` and `KERNARG_SIZE`. Not checked: the 64-byte alignment, `KERNEL_CODE_ENTRY_BYTE_OFFSET` and the 256-byte alignment of the entry, the reserved fields, `COMPUTE_PGM_RSRC1` to `RSRC3`. The gfx950 dispatches of #45 ran correctly, which they could not with a wrong entry offset. ABI-2 |
| AB-R15 | **conforms**; hardware: gfx950 verified, gfx942 open | No `amdgpu.buffer.oob.mode` flag is set (`llvm.rs:268-287`). Test: `test_masked_load_lowers_to_a_bounds_checked_buffer_load` (`amd_lowering.rs:370`, Groundwork for RI-KC-003). On gfx950 #45 read zeros past the bound (`masked_readback`, `max_abs_err=0`) |

## Cache-policy bits, audit of 2026-11-15

Against AB-R16, added to the scope by SRS v0.4.11 (PR #65), on `main`
`b057ef5`. Read the Load-Visible and Store-Available tables and the
non-atomic code sequences of *Memory Model GFX942* and *Memory Model
GFX125x*; read `crates/rustinfer-kc/src/capabilities.rs` and the ROCDL
lowering (`crates/rustinfer-kc/src/mlir/rocdl/`) and searched every crate
for `sc0`, `sc1`, `nt`, nontemporal and cache-policy spellings. No test run.

| id | result | evidence |
|---|---|---|
| AB-R16 | **missing** (ABI-5) | The capability description has no cache-policy hint (`capabilities.rs:47-64`), and no lowered access carries a cache-policy attribute or `!nontemporal` (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:78`, `:154`, `:321-330`), so the back end emits every global access at wavefront scope with no bit, the first column of both tables. Correct for the kernels on `b057ef5`, none of which needs a wider scope or a streaming hint; the `cache-hints` pass (RI-KC-016 (h)) and the hint field are planned in #64. The gfx950 ISA side is [CDNA4-2](std-amd-cdna4-isa-tracker.html), the gfx942 side FNUZ-3 |

## Result

The kernel compiler on `main` writes code object V5 in the form the HIP
loader requires, and its host tests now pin the header, the flags, the
metadata note and the descriptor's segment sizes. The ROCm target reads
every object before HIP sees it and refuses one that is not V5 `ET_DYN` for
the device, or whose LDS or registers exceed it. On gfx950 the objects
loaded and ran exactly (#45, #59). Two gaps remain: a few fields written by
LLVM and `lld` still have no test (ABI-2), and no object has been loaded on
gfx942 (ABI-3, #61); #61 also re-runs #45 on gfx950 at `main`, since PR #44
was rebased onto #58's target after the run. Gaps are on the
[tracker](std-amdgpu-abi-tracker.html).
