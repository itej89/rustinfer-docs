---
title: "HIP and ROCm environment variables 7.2.4 tracker"
navtitle: Tracker
section: Standards
group: "Runtime / HIP and ROCm environment variables 7.2.4"
order: 21
summary: Gaps between rustinfer's version manifest and RI-ROC-015's 13 HIP and HSA variables; recording them set or unset and warning on a non-default value are R1 work planned in #95.
---

# HIP and ROCm environment variables tracker

Gaps found by the [audit](std-hip-env-audit.html) of 2026-11-15 against
`main` `5a6db49`. Both are R1 (RI-ROC-015) and planned in issue
[#95](https://github.com/itej89/rustinfer/issues/95) (open, milestone
`R1 — foundation`), "This issue reads and records them in the ROCm target;
logging them on every subcommand's CLI path is #14's". #95 is blocked by #93.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| HENV-1 | The version manifest records none of the 13 variables, set or unset (HENV-R1 to HENV-R14) | SRS RI-ROC-015 and its Acceptance ("the default environment records every variable as unset"); [HIPENV], [ROCMENV] for their meaning | **Open** | Planned in #95. Manifest on `5a6db49`: `crates/rustinfer-core/src/manifest.rs:36-136`, logged by `crates/rustinfer-cli/src/main.rs:46-47`. RI-OBS-005 then copies the same lines into `tune` and GPU test records ([AMD SMI](std-amd-smi-tracker.html), SMI-1) |
| HENV-2 | No value is compared with the runtime default, so nothing is logged at `warn` (HENV-R15) | SRS RI-ROC-015 ("running with `GPU_MAX_HW_QUEUES=2` logs it at `warn`") | **Open** | Planned in #95. The defaults: ten from the references, three (`HSA_FORCE_SDMA_SIZE` 1048576 bytes, `GPU_FORCE_BLIT_COPY_SIZE` 16 KiB, `ROC_P2P_SDMA_SIZE` 1024 KiB) from the rocm-7.2.4 source only; for the tri-state ROCr flags the default is "unset" (see the audit) |
