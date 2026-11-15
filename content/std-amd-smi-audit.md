---
title: "AMD SMI 7.2.4 audit"
navtitle: Audit
section: Standards
group: "Runtime / AMD SMI 7.2.4"
order: 26
summary: The 2026-11-15 audit at main 5a6db49 of rustinfer's tune and GPU test records against AMD SMI 7.2.4; tune is not implemented, no record carries device state and the gpu-test template does not ask for it (#97); nothing calls an AMD SMI setter.
---

# AMD SMI audit

**Audit of 2026-11-15**, against the [requirements](std-amd-smi-requirements.html),
on `main` `5a6db49` (PR #74 merged over SRS v0.5, PR #80 at `4ee01b6`). First
audit.

**Method.** Read the `amdsmi_gpu_metrics_t` structure and the getters and
setters of the scope in `specs/observability/amdsmi-7.2.4-amdsmi.h`, and the
`metric`, `set`, `reset` and `partition` sections of the CLI page. Read on
`5a6db49`: `crates/rustinfer-cli/src/commands.rs`, `cli.rs` and `main.rs`,
`.github/ISSUE_TEMPLATE/gpu-test.md`, `docs/gpu-testing.md` and
`docs/observability.md`; searched every crate, script and workflow for
`amdsmi`, `amd-smi`, `rocm-smi`, `gpu_metrics`, `power_cap` and
`determinism` (only the template's `rocm-smi --showproductname`). Read the
plan of #97 and the diff of the open PR #68 (the tuning catalog and
`rustinfer tune`), which records no device state. No tests were run.

| id | requirement | result | evidence |
|---|---|---|---|
| SMI-R1 | Metrics from `amdsmi_get_gpu_metrics_info` | **missing** (SMI-1) | No AMD SMI library is loaded and no CLI is run by any crate. `rustinfer tune` stops at `NotImplemented { feature: "RI-CLI-007 tune" }` after resolving its target (`crates/rustinfer-cli/src/commands.rs:100-108`), so there is no `tune` record to put the fields in |
| SMI-R2 to SMI-R5 | Clocks per die, power, energy delta, throttling over the run | **missing** (SMI-1) | As SMI-R1 |
| SMI-R6 to SMI-R8 | Determinism level, power cap, partition modes | **missing** (SMI-1) | As SMI-R1 |
| SMI-R9 | No setter called | **conforms** | Nothing calls AMD SMI at all; no source test asserts it yet (RI-OBS-005's acceptance asks for "a test over the sources"; RI-OBS-005 is untagged) |
| SMI-R10 | Absent when missing, record still written | **missing** (SMI-1) | No record exists to be written |
| — | The GPU test template asks for the record | **missing** (SMI-2) | The template's "Report back" asks for `rocminfo | grep -m1 gfx`, `rocm-smi --showproductname`, the run's output and listed files (`.github/ISSUE_TEMPLATE/gpu-test.md:42-48`); `docs/gpu-testing.md` asks for no device state either. RI-OBS-005's acceptance: "the gpu-test template asks for the record" |

**What the header does not settle.** Three things a record writer needs are
not stated by a primary source read here, and #97 should measure or cite
them: the unit of `current_gfxclks`, whose comment reads "In KB" (`[H]`
line 1960; MHz is the likely unit, not verified); the unit of
`energy_accumulator`, whose comment reads "Power (W) /Energy (15.259uJ per
1ns)" (`[H]` lines 1870 to 1875; a count of 15.259 µJ units is the likely
reading, not verified); and the SoftMax value of performance determinism,
which the header sets (`amdsmi_set_gpu_perf_determinism_mode`, line 3998) but
reads back only as the level `AMDSMI_DEV_PERF_LEVEL_DETERMINISM` (line 1229),
so a record can say the mode is on but not, from this header, its limit.

## Result

No `tune` record and no GPU test result carries device state on `5a6db49`,
and the template does not ask for it; nothing reads or changes AMD SMI.
**Missing.** SMI-1 and SMI-2 are open R1 gaps, planned in #97 (blocked by #92
for the device description, #95 for the environment lines and #9 for
`tune`); SMI-3, the `bench` record, is R2. Gaps are on the
[tracker](std-amd-smi-tracker.html).
