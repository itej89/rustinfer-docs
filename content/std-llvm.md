---
title: "LLVM 23.1"
navtitle: Overview
section: Standards
group: "Compiler and code generation / LLVM 23.1"
order: 10
summary: The pinned LLVM 23.1.x that rustinfer links as a library for its AMDGPU back end and lld (R1), SPIR-V back end (R2) and RISC-V back end (R3).
---

# LLVM 23.1

**Scope (SRS §1.4, LLVM):** the pinned 23.1.x release line, linked as a
library through `melior` 0.29.1 and `mlir-sys` 230.0.2 (ADR-007): the AMDGPU
back end and `lld` as a library (R1), the SPIR-V back end (R2) and the RISC-V
back end (R3). The parts of the LLVM language that rustinfer's lowering
depends on (target triple, data layout, module flags, the masked memory
intrinsics) are part of that scope. Nothing else of LLVM is claimed.

**Implementation:** `crates/rustinfer-kc`, behind the Cargo feature `mlir`.
On `origin/main` (`ccf02b3`):

- `scripts/ci/install_llvm.sh:13` pins the major (23) and lines 22 to 23 pin
  the exact `apt.llvm.org` build per Ubuntu codename (23.1.6 for noble and
  resolute); CI runs it in every job that builds with `--all-features`
  (`.github/workflows/ci.yml:40`, `:65`, `:96`, `:117`).
- `Cargo.toml:58` to `:59` pin `melior = "=0.29.1"` and
  `mlir-sys = "=230.0.2"`; `crates/rustinfer-core/src/config/constants.rs:426`
  holds `KC_PINNED_LLVM_MAJOR = 23`.
- `crates/rustinfer-kc/src/mlir/raw.rs:17` reads the linked version with
  `LLVMGetVersion`; `crates/rustinfer-kc/src/mlir/mod.rs:154` refuses a
  context whose LLVM is not major 23.
- `crates/rustinfer-kc/src/mlir/raw.rs:26` translates an `llvm` dialect
  module to LLVM IR in-process. No LLVM code generation happens on `main`:
  the AMDGPU target machine and the `lld` link are in open PR #44
  (branch `feat/8-amd-lowering`, head `10b8b1b`), whose GPU test #45 has
  not been run.

See also the [kernel compiler](kernel-compiler.html) page.

**Conformance:** mandatory from **R1** (RI-KC-003, RI-KC-008, RI-KC-011,
RI-ART-008); the SPIR-V back end from R2 and the RISC-V back end from R3.

**Source:** the LLVM documentation at tag `llvmorg-23.1.0` of
<https://github.com/llvm/llvm-project>, downloaded 2026-11-13 into
`specs/compiler/`: *LLVM 23.1.0 Release Notes*
(`llvm-23.1.0-ReleaseNotes.md`, rendered at
<https://releases.llvm.org/23.1.0/docs/ReleaseNotes.html>), *LLVM Language
Reference Manual* (`llvm-23.1.0-LangRef.md`) and *User Guide for AMDGPU
Backend* (`llvm-23.1.0-AMDGPUUsage.rst`). The LLVM documents have no clause
numbers, so requirements cite the section heading and its line in these
copies. The installed build is 23.1.6; the 23.1.0 text is the reference the
SRS names, and a patch release of the line changes no item below.

| | |
|---|---|
| Pages | [requirements](std-llvm-requirements.html) · [audit](std-llvm-audit.html) · [tracker](std-llvm-tracker.html) |
| Conformance | mandatory R1 (AMDGPU back end, `lld`); R2 (SPIR-V back end); R3 (RISC-V back end) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3`, PR #44 at `10b8b1b` and the specification text; no test run locally |
| Result | part: the pin, the version check, the masked intrinsics and the AMDGPU address spaces conform on `main`; AMDGPU code generation and the `lld` link are pending PR #44 |
| Open gaps | 2 (both in PR #44); 2 more items recorded as later release (R2, R3) |
