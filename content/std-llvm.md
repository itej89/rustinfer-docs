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
On `main` (`81fbcba`, after PR #44, merge `38f2f60`, issue #8):

- `scripts/ci/install_llvm.sh:22` pins the major (23) and lines 32 to 34 pin
  the exact `apt.llvm.org` build per Ubuntu codename (23.1.6 for jammy,
  noble and resolute), with `lld-23` and `liblld-23-dev` (`:45`, `:48`);
  CI runs it in every job that builds with `--all-features`
  (`.github/workflows/ci.yml:46`, `:76`, `:114`, `:143`).
- `Cargo.toml:66` to `:67` pin `melior = "=0.29.1"` and
  `mlir-sys = "=230.0.2"`; `crates/rustinfer-core/src/config/constants.rs:574`
  holds `KC_PINNED_LLVM_MAJOR = 23`, and `crates/rustinfer-kc/src/mlir/mod.rs:205`
  refuses a context whose LLVM is not major 23.
- `crates/rustinfer-kc/src/mlir/llvm.rs` generates AMDGPU code in-process:
  triple `amdgcn-amd-amdhsa` (`:28`), a target machine per processor
  (`:241-265`), the data layout and code-object version flag (`:268-287`),
  and the `ld.lld -shared` link (`:348-358`) through the C++ shim
  `src/mlir/lld_shim.cpp`, built by `build.rs` (ADR-007 point 9).

On hardware the output ran on an MI350X (gfx950) under ROCm 10.1
(10.1.0-3): GPU test #45 passed on 2026-11-15 (results in #54). gfx942 has
not been run (#61).

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
| Audited | 2026-11-14, by reading `main` `81fbcba`, the result of #45 in #54 and the specification text; no test run locally |
| Result | part: every R1 item conforms on `main` (pin, version check, masked intrinsics, address spaces, AMDGPU code generation, `lld`); verified on gfx950 (#45, #59); gfx942 not yet run (#61, LLVM-5) |
| Open gaps | 1 (LLVM-5, the gfx942 hardware run); LLVM-1 and LLVM-2 fixed by PR #44; 2 more items recorded as later release (R2, R3) |
