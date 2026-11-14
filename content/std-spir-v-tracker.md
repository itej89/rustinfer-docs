---
title: "SPIR-V 1.6 rev 8 tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / SPIR-V 1.6 rev 8"
order: 43
summary: The Release 2 work for SPIR-V module emission; no open gap, since nothing is due before R2.
---

# SPIR-V 1.6 rev 8 tracker

From the [audit](std-spir-v-audit.html). No gap is open: every item is
Release 2 work. The rows below list that work so it stays visible; they are
not counted as gaps. No GitHub issue covers them yet
(`gh issue list -R itej89/rustinfer --state all`, 2026-11-13).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| SPV-1 | No SPIR-V module is emitted: header words, instruction form, logical layout (SV-R1 to SV-R8) | §2.3, §2.4, §2.2.4, §3.1 | Later release R2 | RI-KC-004 (SPIR-V through MLIR's `spirv` dialect), RI-RV-001. The MLIR side is [MLIR-4](std-mlir-tracker.html) |
| SPV-2 | No validation of emitted modules (SV-R9, SV-R10) | §2.16.1, §2.16.2 | Later release R2 | A validator in the tests would catch what the MLIR serializer does not check |
| SPV-3 | The emitted version is not chosen (SV-R11) | §1.3.1, §2.22 | Later release R2 | SRS OI-016, open: SPIR-V 1.5 with Vulkan 1.2 (runs on the K3's BXM-4-64 today) or 1.6 with Vulkan 1.3. Must be decided before the R2 lowering |
