---
title: "AMDGPU code object V5"
navtitle: Overview
section: Standards
group: "Compiler and code generation / AMDGPU code object V5"
order: 30
summary: The AMDHSA code object V5 ABI of LLVM 23.1's AMDGPUUsage: the ELF header, e_flags, note records, symbols and kernel descriptor the HIP module loader reads.
---

# AMDGPU code object V5

**Scope (SRS §1.4, AMDGPU-ABI):** code object V5: the ELF layout, the
kernel descriptor and the metadata, as the HIP module loader reads them.
Code object V5 (`ELFABIVERSION_AMDGPU_HSA_V5`) is the LLVM 23.1 default.
Other code object versions, PAL and Mesa ABIs, the trap handler and debug
information are out of the claim.

**Implementation:** none on `origin/main` (`ccf02b3`): nothing on `main`
emits or reads a code object. The kernel binaries an artifact carries are
opaque bytes there. Open PR #44 (branch `feat/8-amd-lowering`, head
`10b8b1b`, closing issue #8) emits gfx942 and gfx950 code objects
in-process:

- `crates/rustinfer-kc/src/mlir/llvm.rs:28` (triple `amdgcn-amd-amdhsa`),
  `:32` (code-object version 500, pinned through a module flag at `:279`);
- `crates/rustinfer-kc/src/mlir/llvm.rs:348` (the `lld -shared` link);
- `crates/rustinfer-kc/src/mlir/code_object.rs:80` (a bounded reader of the
  ELF header, `e_flags` and executable sections);
- `crates/rustinfer-target-rocm/src/ffi/hip.rs` (a `rocm-test` harness that
  loads the object with `hipModuleLoadData`).

The GPU test of PR #44, issue #45, has not been run, so no code object has
yet been loaded by the HIP loader. Reading the metadata for the LDS and
register check of RI-ROC-004 is issue #12. Per the audit rule, every item
met only in PR #44 is "pending PR #44". See also the
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
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3`, PR #44 at `10b8b1b` and the specification text; no test run locally |
| Result | gap: nothing conforms on `main`. PR #44 checks the ELF class, byte order, `ET_DYN`, `EM_AMDGPU`, `EI_ABIVERSION` 3 and the `e_flags` processor, XNACK and SRAMECC fields; no test checks `EI_OSABI`, the metadata note or the kernel descriptor, and no code object has been loaded on a GPU |
| Open gaps | 4 (one in PR #44, three open) |
