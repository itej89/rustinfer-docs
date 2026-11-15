---
title: "AMD SMI 7.2.4"
navtitle: Overview
section: Standards
group: "Runtime / AMD SMI 7.2.4"
order: 24
summary: AMD SMI of ROCm 7.2.4, for the device state RI-OBS-005 puts in every tune and GPU test record (clocks per die, power, energy, throttling, determinism, power cap, partitions), read only; no record carries any of it on main yet (#97).
---

# AMD SMI 7.2.4

**Scope (SRS §1.4, AMD-SMI):** "the `amdsmi_get_gpu_metrics_info` fields
and the `amd-smi set` determinism and power-cap settings RI-OBS-005 records
(read only)". Added by SRS v0.5 (PR #80). RI-OBS-005: "Every `tune` record,
every result a GPU test request asks for (`docs/gpu-testing.md`) and, with
RI-CLI-008, every `bench` record SHALL include: the device's clocks (per
compute die), power, energy-accumulator delta and throttle status over the
run; the performance-determinism and power-cap settings; the partition
modes; the environment of RI-ROC-015; and the host settings AMD's acceptance
guides name (NUMA balancing, IOMMU mode). They SHALL be read from the AMD SMI
library or CLI where present and SHALL be absent otherwise. rustinfer SHALL
NOT change any of them." R1 for `tune` and GPU test results, R2 for `bench`.
The environment is the [HIP-ENV](std-hip-env.html) standard's, the host
settings [AMD-ACC](std-amd-acc.html)'s; this page covers the device state.

**Implementation on `main` (`5a6db49`):** none. No crate links or runs AMD
SMI; `rustinfer tune` resolves its target and returns `NotImplemented`
(`crates/rustinfer-cli/src/commands.rs:100-108`), so no `tune` record exists
yet, and the GPU test template asks only for `rocminfo | grep -m1 gfx` and
`rocm-smi --showproductname` (`.github/ISSUE_TEMPLATE/gpu-test.md:46`). The
tuning catalog of the open PR #68 records timings and no device state.
Planned in issue [#97](https://github.com/itej89/rustinfer/issues/97) (open,
R1, blocked by #92, #95 and #9).

**Conformance:** mandatory from **R1** (RI-OBS-005 for `tune` and GPU test
results); `bench` records are R2.

**Source:** *AMD SMI* documentation for ROCm 7.2.4,
<https://rocm.docs.amd.com/projects/amdsmi/en/docs-7.2.4/>: the index and
the *AMD SMI CLI tool usage* page, downloaded 2026-11-15 as
`specs/observability/amdsmi-7.2.4-index.html` and
`amdsmi-7.2.4-cli-tool.html` (text copy cited by line); and the library
header the documentation's C++ reference is generated from,
`projects/amdsmi/include/amd_smi/amdsmi.h` of `ROCm/rocm-systems` at tag
`rocm-7.2.4`, as `specs/observability/amdsmi-7.2.4-amdsmi.h` (7491 lines;
cited by line).

| | |
|---|---|
| Pages | [requirements](std-amd-smi-requirements.html) · [audit](std-amd-smi-audit.html) · [tracker](std-amd-smi-tracker.html) |
| Conformance | mandatory R1 (RI-OBS-005: `tune`, GPU test results); R2 for `bench` (RI-CLI-008) |
| Audited | 2026-11-15, by reading `main` `5a6db49`, the open PR #68 and the documents; no test run |
| Result | missing: no record carries device state, and nothing reads AMD SMI; the "read only" rule holds because nothing calls it |
| Open gaps | 2 of 3 (SMI-1 device state in `tune` and GPU test records, SMI-2 the gpu-test template), planned in #97; SMI-3 (`bench`) is R2 |
