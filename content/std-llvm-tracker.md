---
title: "LLVM 23.1 tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / LLVM 23.1"
order: 13
summary: Gaps between rustinfer's use of LLVM and the 23.1 documentation; AMDGPU code generation and the lld link wait on PR #44.
---

# LLVM 23.1 tracker

Gaps found by the [audit](std-llvm-audit.html). Rows marked later release
are R2 and R3 work; they are listed so they stay visible and are not counted
as open gaps. Issues from `gh issue list -R itej89/rustinfer --state all`,
2026-11-13.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| LLVM-1 | No AMDGPU code generation on `main`: no target triple, data layout, code-object version flag or target machine (LL-R3, LL-R4, LL-R5, LL-R8, LL-R9) | LangRef *Target Triple*, *Data Layout*, *Module Flags Metadata*; AMDGPUUsage *ELF Code Object*, *Module Flags* | **In PR #44** | Issue [#8](https://github.com/itej89/rustinfer/issues/8). CI on `10b8b1b` passes; the PR stays unmerged until GPU test [#45](https://github.com/itej89/rustinfer/issues/45) reports. PR #44 uses the legacy triple `amdgcn-amd-amdhsa`, which 23.1 accepts; moving to the `amdgpu` spelling is optional |
| LLVM-2 | No `lld` on `main`: the install script does not install `liblld-23-dev` and nothing links a shared code object (LL-R10) | AMDGPUUsage *ELF Code Object* | **In PR #44** | Issue [#8](https://github.com/itej89/rustinfer/issues/8). PR #44 links through a C++ shim around `lld::lldMain` and adds `liblld-23-dev` at the pinned version for noble, resolute and jammy |
| LLVM-3 | SPIR-V back end not used (LL-R11) | SRS §1.4 LLVM scope | Later release R2 | No issue yet. RI-KC-004 sends the SPIR-V path through MLIR's `spirv` dialect, which serializes SPIR-V itself; the SRS may want to say whether the LLVM SPIR-V back end is used at all |
| LLVM-4 | RISC-V back end not used (LL-R12) | SRS §1.4 LLVM scope | Later release R3 | No issue yet. ADR-007 also leaves open an LLVM 23 build for RISC-V hosts |

## Notes

- `apt.llvm.org` keeps only its latest build per suite, so the exact pins in
  `scripts/ci/install_llvm.sh:22` to `:23` go stale when it rebuilds (ADR-007,
  Consequences). That is a supply risk, not a conformance gap: the pinned
  line stays 23.1.
