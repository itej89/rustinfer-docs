---
title: "SPIR-V 1.6 rev 8"
navtitle: Overview
section: Standards
group: "Compiler and code generation / SPIR-V 1.6 rev 8"
order: 40
summary: The Khronos SPIR-V module binary form that the spirv-vulkan lowering will emit through MLIR's spirv dialect from R2; nothing is required in R1.
---

# SPIR-V 1.6 rev 8

**Scope (SRS §1.4, SPIR-V):** the module binary form emitted through MLIR's
`spirv` dialect. The version emitted is open (OI-016): SPIR-V 1.5 if the
first Vulkan-class device stays at Vulkan 1.2, or 1.6 with Vulkan 1.3.
Extended instruction sets, kernel (OpenCL) capabilities and graphics stages
are out of the claim. The Vulkan side (which SPIR-V a device consumes) is the
VULKAN row's.

**Implementation:** none yet. On `origin/main` (`ccf02b3`)
`crates/rustinfer-target-spirv-vulkan/src/lib.rs:1` to `:5` is the R1 stub
of RI-RV-001: it implements `Target` with an empty catalog
(`:25` to `:38`), so a build for it fails at kernel selection (RI-RV-002).
No code emits a `spirv` operation or a SPIR-V word. The lowering is R2
(RI-KC-004, RI-RV-001). See also the [kernel compiler](kernel-compiler.html)
page.

**Conformance:** mandatory from **R2**. The current release is R1, so
nothing is required yet.

**Source:** `specs/compiler/SPIRV-unified1.pdf` and `SPIRV-unified1.html`,
*SPIR-V Specification*, The Khronos SPIR Working Group, version 1.6,
Revision 8, Unified (no revision date is printed), from
<https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html>, downloaded
2026-11-13 (CC-BY-4.0). Sections cited are those of that document.

| | |
|---|---|
| Pages | [requirements](std-spir-v-requirements.html) · [audit](std-spir-v-audit.html) · [tracker](std-spir-v-tracker.html) |
| Conformance | mandatory R2 (RI-KC-004, RI-RV-001) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and the specification text |
| Result | later release: every item is R2 work; no R1 requirement depends on this standard |
| Open gaps | 0 (3 items recorded as later release R2) |
