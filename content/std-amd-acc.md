---
title: "AMD Instinct system acceptance (accessed 2026-11-15)"
navtitle: Overview
section: Standards
group: "Runtime / AMD Instinct system acceptance (accessed 2026-11-15)"
order: 28
summary: AMD's Instinct system acceptance guides (OS tuning, kernel parameters, xGMI topology), for the host settings RI-OBS-005 records, NUMA balancing and the IOMMU mode; no record carries them on main yet (#97).
---

# AMD Instinct system acceptance (accessed 2026-11-15)

**Scope (SRS §1.4, AMD-ACC):** "the host settings RI-OBS-005 records". Added
by SRS v0.5 (PR #80). RI-OBS-005 (R1 for `tune` and GPU test results, R2 for
`bench`) puts in every record "the host settings AMD's acceptance guides name
(NUMA balancing, IOMMU mode)", read where present and absent otherwise, and
"rustinfer SHALL NOT change any of them". The device state of the same
records is [AMD SMI](std-amd-smi.html)'s scope; the environment is
[HIP-ENV](std-hip-env.html)'s.

**Implementation on `main` (`5a6db49`):** none. No crate reads
`/proc/sys/kernel/numa_balancing`, `/proc/cmdline` or the kernel log, and
there is no `tune` record or GPU test result format to hold the values (see
the [audit](std-amd-acc-audit.html)). Planned in issue
[#97](https://github.com/itej89/rustinfer/issues/97) (open, R1), with the
device state.

**The guides are not versioned.** SRS §1.4 cites them as "latest
(accessed)", 2026-11-15; the pages carry no release number, so what this
audit read can change under the same URL. The copies in `specs/` are the
text this audit holds rustinfer to.

**Conformance:** mandatory from **R1** (RI-OBS-005).

**Source:** *AMD Instinct Customer Acceptance Guide*,
<https://instinct.docs.amd.com/projects/system-acceptance/en/latest/>, and
its pages *OS Tuning* (`common/os-tuning.html`), *Kernel Parameters*
(`common/kernel-parameters.html`), *Interpreting GPU fabric topology*
(`common/xgmi-topology.html`), *BIOS Settings* (`common/bios-settings.html`),
*AMD Instinct MI300X* and *MI350X* (`gpus/mi300x.html`, `gpus/mi350x.html`),
downloaded 2026-11-15 into `specs/observability/` as `amd-acc-*.html` with
text copies (`.txt`, cited by section and line).

| | |
|---|---|
| Pages | [requirements](std-amd-acc-requirements.html) · [audit](std-amd-acc-audit.html) · [tracker](std-amd-acc-tracker.html) |
| Conformance | mandatory R1 (RI-OBS-005: `tune`, GPU test results); R2 for `bench` |
| Audited | 2026-11-15, by reading `main` `5a6db49` and the guides as accessed that day; no test run |
| Result | missing: no record carries the NUMA balancing state or the IOMMU mode; nothing changes them |
| Open gaps | 1 of 2 (ACC-1 the host settings in `tune` and GPU test records, #97); ACC-2 (`bench`) is R2 |
