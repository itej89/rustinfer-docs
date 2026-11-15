---
title: "AMD SMI 7.2.4 requirements"
navtitle: Requirements
section: Standards
group: "Runtime / AMD SMI 7.2.4"
order: 25
summary: What AMD SMI 7.2.4 offers for RI-OBS-005's device state, the GPU metrics fields, the determinism level, the power cap and the partition modes, with the getters to read them and the setters rustinfer must never call.
---

# AMD SMI requirements

Sources: the library header `specs/observability/amdsmi-7.2.4-amdsmi.h`,
cited as **[H]** with its lines, and the CLI page
`specs/observability/amdsmi-7.2.4-cli-tool.txt`, as **[CLI]**. The
requirement on rustinfer is RI-OBS-005's: read these values over the run of a
`tune` (and, from R2, `bench`) and for a GPU test result, from the library or
the CLI where present, leave them absent otherwise, and never set any.

## The device state RI-OBS-005 records

| id | requirement | source |
|---|---|---|
| SMI-R1 | GPU metrics come from `amdsmi_get_gpu_metrics_info(processor_handle, amdsmi_gpu_metrics_t *)`, "not supported on virtual machine guest" (`@platform{gpu_bm_linux}`). The structure is versioned by its `common_header`, and "Depending on the version, some data members will hold data, and some will not": up to version 1.3 the clocks are single values (`current_gfxclk`), from 1.4 arrays (`current_gfxclks[]`) | [H] lines 1838 to 2028, 4140 to 4164 |
| SMI-R2 | Clocks per compute die: `current_gfxclks[AMDSMI_MAX_NUM_GFX_CLKS]` (8), one per XCC, with `gfxclk_lock_status` ("Each bit corresponds to clock instance"); also `average_gfxclk_frequency`. The header's unit comment on `current_gfxclks` reads "In KB" | [H] lines 125, 1883, 1940, 1960 |
| SMI-R3 | Power: `current_socket_power`, "In Watts" (version 1.4 on, the MI300 series and later), and `average_socket_power` | [H] lines 1870 to 1874, 1934 to 1936 |
| SMI-R4 | Energy: `energy_accumulator`, 64-bit since version 1, under the comment "Power (W) /Energy (15.259uJ per 1ns)"; a run's energy is the difference of two reads, with `system_clock_counter` ("Driver attached timestamp (in ns)") or `firmware_timestamp` (10 ns) for the interval | [H] lines 1870 to 1878, 1922 |
| SMI-R5 | Throttling: `throttle_status`, `indep_throttle_status`, and the accumulated residencies `prochot_residency_acc`, `ppt_residency_acc`, `socket_thm_residency_acc`, `vr_thm_residency_acc`, `hbm_thm_residency_acc` over `accumulation_counter`; per partition, `xcp_stats[]`. The CLI shows them with `amd-smi metric --violation` ("Only available for MI300 or newer ASICs") | [H] lines 1902, 1931, 1975 to 2018; [CLI] lines 416 to 421 |
| SMI-R6 | Performance determinism: `amdsmi_get_gpu_perf_level` returns `AMDSMI_DEV_PERF_LEVEL_DETERMINISM` while the mode is on; the mode is entered by `amdsmi_set_gpu_perf_determinism_mode(handle, clkvalue)`, "a GFXCLK frequency SoftMax limit", or `amd-smi set -d SCLKMAX`, and left by `amd-smi reset -d`. The header names no getter for the SoftMax value | [H] lines 1229, 3960 to 3998; [CLI] lines 638 to 642, 734 |
| SMI-R7 | Power cap: `amdsmi_get_power_cap_info(handle, sensor_ind, amdsmi_power_cap_info_t *)` returns `power_cap`, `default_power_cap`, `min_power_cap`, `max_power_cap` in µW on bare-metal Linux; set by `amdsmi_set_power_cap` or `amd-smi set -o WATTS` | [H] lines 834 to 841, 3320 to 3333, 6240 to 6256; [CLI] line 648 |
| SMI-R8 | Partition modes: `amdsmi_get_gpu_compute_partition` and `amdsmi_get_gpu_memory_partition` (strings, `AMDSMI_STATUS_INSUFFICIENT_SIZE` if the buffer is short), shown by `amd-smi partition`; set by `amdsmi_set_gpu_compute_partition`, `amdsmi_set_gpu_memory_partition` or `amd-smi set -C`, `-M` | [H] lines 5760 to 5772, 5802, 5847, 5879; [CLI] lines 643 to 647, 860 to 880 |

## Read only, and absent when missing

| id | requirement | source |
|---|---|---|
| SMI-R9 | No setter is called: not `amdsmi_set_gpu_perf_determinism_mode`, `amdsmi_set_power_cap`, `amdsmi_set_gpu_perf_level`, the partition setters, nor `amd-smi set` or `amd-smi reset` ("Requires 'sudo' privileges") | SRS RI-OBS-005 ("rustinfer SHALL NOT change any of them"; Acceptance: "no rustinfer code path calls an AMD SMI setter (a test over the sources)"); [H] lines 3331, 3998, 4495, 5802, 5879; [CLI] lines 615 to 630 |
| SMI-R10 | Where AMD SMI is absent, or a call returns `AMDSMI_STATUS_NOT_SUPPORTED` (a field a version does not fill, a VM guest), the field is absent and the record is still written | SRS RI-OBS-005 and its Acceptance ("on a host without AMD SMI the fields are absent and the record is still written"); [H] line 307 |
