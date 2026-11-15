---
title: "LLVM 23.1 tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / LLVM 23.1"
order: 13
summary: Gaps between rustinfer's use of LLVM and the 23.1 documentation; AMDGPU code generation and the lld link are fixed by PR #44 and verified on gfx950; the gfx942 hardware run (#61) remains.
---

# LLVM 23.1 tracker

Gaps found by the [audit](std-llvm-audit.html) of 2026-11-13, re-audited on
2026-11-14 against `main` `81fbcba` after PR #44 (merge `38f2f60`, issue #8)
merged. Rows marked later release are R2 and R3 work; they are listed so they
stay visible and are not counted as open gaps. Hardware: GPU test
[#45](https://github.com/itej89/rustinfer/issues/45) passed on an MI350X
(gfx950) under ROCm 10.1 (10.1.0-3) on 2026-11-15 (UTC), results in
[#54](https://github.com/itej89/rustinfer/issues/54); gfx942 is
[#61](https://github.com/itej89/rustinfer/issues/61).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| LLVM-1 | No AMDGPU code generation on `main`: no target triple, data layout, code-object version flag or target machine (LL-R3, LL-R4, LL-R5, LL-R8, LL-R9) | LangRef *Target Triple*, *Data Layout*, *Module Flags Metadata*; AMDGPUUsage *ELF Code Object*, *Module Flags* | Fixed 2026-11-14 38f2f60 | PR #44 (issue [#8](https://github.com/itej89/rustinfer/issues/8)). `crates/rustinfer-kc/src/mlir/llvm.rs:28` (triple), `:241-265` (target machine for the processor, O3, `LLVMRelocPIC`, no forced features), `:268-287` (`LLVMSetTarget`, the machine's data layout, one `amdhsa_code_object_version` flag of 500 with behaviour Error), no `amdgpu.buffer.oob.mode` flag (strict). Tests: `crates/rustinfer-kc/tests/amd_lowering.rs:208` to `:262` (one per R1 MFMA pair), `:370` (bounds-checked buffer load), `:434` (`EI_ABIVERSION` 3), all Groundwork for RI-KC-003. gfx950 output verified on hardware by #45 (every line `max_abs_err=0`); gfx942 is LLVM-5. The legacy triple spelling `amdgcn-amd-amdhsa` stays; 23.1 accepts it and moving to `amdgpu` is optional |
| LLVM-2 | No `lld` on `main`: the install script did not install `liblld-23-dev` and nothing linked a shared code object (LL-R10) | AMDGPUUsage *ELF Code Object* | Fixed 2026-11-14 38f2f60 | PR #44 (issue [#8](https://github.com/itej89/rustinfer/issues/8)). `scripts/ci/install_llvm.sh:45` and `:48` add `lld-23` and `liblld-23-dev` at the pinned build per codename (jammy, noble, resolute, `:32-34`) and `check_lld` (`:80-83`) fails unless `liblldELF.a` and `liblldCommon.a` are present; `crates/rustinfer-kc/build.rs` compiles `src/mlir/lld_shim.cpp` (one `extern "C"` call of `lld::lldMain` with the ELF driver, `:47-63`) and links it with those archives (ADR-007 point 9). `llvm.rs:348-358` pass `-shared --no-undefined --build-id=none --threads=1`. Tests: `test_lld_link_failure_carries_the_lld_message` (`llvm.rs:486`, Groundwork for RI-KC-008), `amd_lowering.rs:403` (`ET_DYN`), `:473` (byte identical across processes, Groundwork for RI-KC-011). The linked objects loaded on gfx950 (#45) |
| LLVM-3 | SPIR-V back end not used (LL-R11) | SRS §1.4 LLVM scope | Later release R2 | No issue yet. RI-KC-004 sends the SPIR-V path through MLIR's `spirv` dialect, which serializes SPIR-V itself; the SRS may want to say whether the LLVM SPIR-V back end is used at all |
| LLVM-4 | RISC-V back end not used (LL-R12) | SRS §1.4 LLVM scope | Later release R3 | No issue yet. ADR-007 also leaves open an LLVM 23 build for RISC-V hosts |
| LLVM-5 | The gfx942 output of the AMDGPU back end has not run on hardware: the strict buffer bounds check reading zero past the bound (LL-R9) and the linked shared object loading (LL-R10) are shown on gfx950 only | AMDGPUUsage *Module Flags*, *Buffer Fat Pointer out of bounds (OOB) handling*; *ELF Code Object* | **Open** | GPU test [#61](https://github.com/itej89/rustinfer/issues/61) (MI300X), not run. On gfx950 #45 passed at `821a57e`, PR #44 before its rebase onto #58's target; #61 also re-runs #45 on gfx950 at `main`. The host tests see the gfx942 disassembly only (record count 0x100, `offset:256`, `amd_lowering.rs:370`) |

## Notes

- `apt.llvm.org` keeps only its latest build per suite, so the exact pins in
  `scripts/ci/install_llvm.sh:32` to `:34` go stale when it rebuilds (ADR-007,
  Consequences). That is a supply risk, not a conformance gap: the pinned
  line stays 23.1.
