---
title: "AMD Instinct system acceptance (accessed 2026-11-15) tracker"
navtitle: Tracker
section: Standards
group: "Runtime / AMD Instinct system acceptance (accessed 2026-11-15)"
order: 31
summary: Gaps between rustinfer's tune and GPU test records and the host settings of AMD's Instinct acceptance guides; NUMA balancing and the IOMMU mode are R1 work planned in #97, the bench record is R2.
---

# AMD Instinct system acceptance tracker

Gaps found by the [audit](std-amd-acc-audit.html) of 2026-11-15 against
`main` `5a6db49`. ACC-1 is R1 (RI-OBS-005) and planned in issue
[#97](https://github.com/itej89/rustinfer/issues/97) (open, milestone
`R1 — foundation`, blocked by #92, #95 and #9), with the device state of
[AMD SMI](std-amd-smi-tracker.html).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| ACC-1 | No `tune` record or GPU test result carries the NUMA balancing state (`/proc/sys/kernel/numa_balancing`) or the IOMMU mode (`iommu=` on `/proc/cmdline`), and none says they are absent (ACC-R1, ACC-R2) | [OS] *NUMA Configuration*, *IOMMU Configuration for Large Systems*; [KP] *Required Kernel Parameters*; SRS RI-OBS-005 and its Acceptance | **Open** | Planned in #97. No reader on `5a6db49`; `rustinfer tune` is `NotImplemented` (`crates/rustinfer-cli/src/commands.rs:100-108`). Whether C-states and the other kernel parameters the guides name also belong in the record is for the owner (audit) |
| ACC-2 | No `bench` record carries the host settings | SRS RI-OBS-005 (R2 with RI-CLI-008) | Later release R2 | `bench` is RI-CLI-008, R2 |
