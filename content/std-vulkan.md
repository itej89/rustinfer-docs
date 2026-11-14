---
title: "Vulkan 1.4.368"
navtitle: Overview
section: Standards
group: "Runtime / Vulkan 1.4.368"
order: 30
summary: Vulkan compute dispatch of SPIR-V modules, mandatory from R2 for the spirv-vulkan target; the minimum core version is still undecided (OI-016).
---

# Vulkan 1.4.368

**Scope (SRS §1.4, VULKAN):** compute dispatch of SPIR-V modules. **Conformance:**
mandatory R2. The requirements that cite it are RI-KC-004 (the SPIR-V path for
Vulkan-class devices through MLIR's `spirv` dialect, R2 compile-tested) and
RI-RV-001 (the `spirv-vulkan` target crate: a stub in R1, the lowering in R2).

**Minimum version: not decided.** The SRS row records "1.4.368 text (accessed); no
minimum core version recorded". Open item **OI-016** (open, the owner has not
decided) chooses between (a) Vulkan 1.2 with SPIR-V 1.5 modules, which runs on the
first Vulkan-class device, the Imagination BXM-4-64 of the SpacemiT K3, today, and
(b) Vulkan 1.3 with SPIR-V 1.6, which needs a Vulkan 1.3 driver. Until it is decided,
the requirements below are those of the 1.4.368 text that hold for any core version,
and anything conditioned on the version is listed as open.

**Implementation:** `crates/rustinfer-target-spirv-vulkan` on origin/main
(`ccf02b3`) is the R1 stub of RI-RV-001: an empty catalog and no device
(`src/lib.rs:1-5`, `src/lib.rs:25-29`). There is no Vulkan loader, instance, device,
shader module or dispatch, and none is due before R2.

**Source:** `specs/runtime/vkspec-1.4.368.html` (Khronos, *Vulkan 1.4.368 - A
Specification*, the "latest" text at
https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html, accessed
2026-11-13). Chapter numbers are those of that text.

| | |
|---|---|
| Pages | [requirements](std-vulkan-requirements.html) · [audit](std-vulkan-audit.html) · [tracker](std-vulkan-tracker.html) |
| Audited | 2026-11-13, by reading origin/main and the 1.4.368 text |
| R1 items | none (the stub target is RI-RV-001's R1 part, not a Vulkan item) |
| R2 items | 8, all later release |
| Open gaps | 1: the minimum-version decision (OI-016); 4 more items recorded as later release (R2) |
