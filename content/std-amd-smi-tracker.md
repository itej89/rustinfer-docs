---
title: "AMD SMI 7.2.4 tracker"
navtitle: Tracker
section: Standards
group: "Runtime / AMD SMI 7.2.4"
order: 27
summary: Gaps between rustinfer's tune and GPU test records and AMD SMI 7.2.4's device state; the fields and the gpu-test template are R1 work planned in #97, the bench record is R2.
---

# AMD SMI tracker

Gaps found by the [audit](std-amd-smi-audit.html) of 2026-11-15 against
`main` `5a6db49`. SMI-1 and SMI-2 are R1 (RI-OBS-005) and planned in issue
[#97](https://github.com/itej89/rustinfer/issues/97) (open, milestone
`R1 — foundation`), blocked by #92 (partition modes), #95 (the environment
record) and #9 (the `tune` command, open PR #68).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| SMI-1 | No `tune` record or GPU test result carries the device's clocks per die, power, energy delta and throttle status over the run, the determinism level, the power cap or the partition modes; AMD SMI is neither linked nor run, and no record is written without it (SMI-R1 to SMI-R8, SMI-R10) | [H] lines 834 to 841, 1838 to 2028, 3960 to 3998, 4140 to 4164, 5760 to 5772, 5847, 6240 to 6256; SRS RI-OBS-005 and its Acceptance ("with a mock AMD SMI a `tune` record carries every field; on a host without AMD SMI the fields are absent and the record is still written") | **Open** | Planned in #97. `rustinfer tune` is `NotImplemented` on `5a6db49` (`crates/rustinfer-cli/src/commands.rs:100-108`); PR #68's catalog has no device fields. The source test that no setter is called (SMI-R9, which holds today) is part of #97's acceptance. Units to settle: `current_gfxclks` ("In KB" in the header) and `energy_accumulator` (audit) |
| SMI-2 | The GPU test template does not ask for the device and host state record | SRS RI-OBS-005 Acceptance ("the gpu-test template asks for the record") | **Open** | Planned in #97. `.github/ISSUE_TEMPLATE/gpu-test.md:42-48` asks for `rocminfo`, `rocm-smi --showproductname` and the run's output |
| SMI-3 | No `bench` record carries the device state | SRS RI-OBS-005 (R2 with RI-CLI-008) | Later release R2 | `bench` is RI-CLI-008, R2 |
