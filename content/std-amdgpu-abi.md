---
title: "AMDGPU code object V5"
navtitle: Overview
section: Standards
group: "Compiler and code generation / AMDGPU code object V5"
order: 30
summary: The AMDHSA code object V5 ABI of LLVM 23.1's AMDGPUUsage: the ELF header, e_flags, note records, symbols and kernel descriptor the HIP module loader reads; emitted and read on main, loaded on gfx950.
---

# AMDGPU code object V5

**Scope (SRS §1.4, AMDGPU-ABI):** code object V5: the ELF layout, the
kernel descriptor and the metadata, as the HIP module loader reads them.
Code object V5 (`ELFABIVERSION_AMDGPU_HSA_V5`) is the LLVM 23.1 default.
Other code object versions, PAL and Mesa ABIs, the trap handler and debug
information are out of the claim.

**Implementation:** on `main` (`81fbcba`) the kernel compiler emits gfx942
and gfx950 code objects in-process (PR #44, merge `38f2f60`, issue #8) and
the ROCm target reads each one before HIP loads it (PR #58, merge `53dac5b`,
issue #12):

- `crates/rustinfer-kc/src/mlir/llvm.rs:28` (triple `amdgcn-amd-amdhsa`),
  `:32` (code-object version 500, pinned through a module flag at
  `:268-287`), `:348-358` (the in-process `ld.lld -shared` link through the
  C++ shim `src/mlir/lld_shim.cpp`);
- `crates/rustinfer-kc/src/mlir/code_object.rs:80-93` (a bounded reader of
  the ELF header, `e_flags` and executable sections);
- `crates/rustinfer-target-rocm/src/code_object/` (the header, `PT_NOTE`
  metadata note and MessagePack map), checked against the device in
  `src/device/kernels.rs:102-120` before `hipModuleLoadData`.

On hardware the objects loaded and ran on an MI350X (gfx950) under ROCm 10.1
(10.1.0-3): GPU tests #45 and #59 passed on 2026-11-15 (results in #54).
gfx942 has not been run (#61). See also the
[kernel compiler](kernel-compiler.html) page.

**Conformance:** mandatory from **R1** (RI-ART-013, RI-ROC-004, RI-KC-008).

**Source:** *User Guide for AMDGPU Backend* (AMDGPUUsage) at tag
`llvmorg-23.1.0`, `llvm/docs/AMDGPUUsage.rst`, downloaded 2026-11-13 as
`specs/compiler/llvm-23.1.0-AMDGPUUsage.rst`; rendered at
<https://releases.llvm.org/23.1.0/docs/AMDGPUUsage.html>. The guide has no
numbered clauses; requirements cite the section, the table name and the line
in that copy.

| | |
|---|---|
| Pages | [requirements](std-amdgpu-abi-requirements.html) · [audit](std-amdgpu-abi-audit.html) · [tracker](std-amdgpu-abi-tracker.html) |
| Conformance | mandatory R1 |
| Audited | 2026-11-14, by reading `main` `81fbcba`, the results of #45 and #59 in #54 and the specification text; no test run locally |
| Result | part: the header, `e_flags`, `EI_OSABI`, `e_entry`, the metadata note, `amdhsa.version` and the descriptor's segment sizes are tested, and the ROCm target reads the metadata before every load; verified on gfx950 (#45, #59); gfx942 not yet run (#61); `amdhsa.target`, the symbol types and the descriptor's entry offset, alignment and reserved fields have no test |
| Open gaps | 2 of 4 (ABI-2 untested fields, ABI-3 gfx942 load); ABI-1 fixed by PR #44, ABI-4 by PR #58 |
