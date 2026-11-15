---
title: "AMD CDNA4 ISA (5 August 2025) tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / AMD CDNA4 ISA (5 August 2025)"
order: 37
summary: Gaps between rustinfer's gfx950 capability description and the CDNA4 ISA guide; the per-field tests, the SC1, SC0 and NT cache bits and the GLOBAL_LOAD_LDS direct-to-LDS loads are all R1 work planned in #64.
---

# AMD CDNA4 ISA tracker

Gaps found by the [audit](std-amd-cdna4-isa-audit.html) of 2026-11-15
against `main` `b057ef5`. All three belong to RI-KC-015 (R1 for gfx950) and
RI-KC-016 (h) (R1), and all three are planned in issue
[#64](https://github.com/itej89/rustinfer/issues/64) (open, milestone R1),
which builds on the `Capabilities` description of PR #63. Hardware: gfx950
results are from an MI350X under ROCm 10.1 (10.1.0-3), GPU tests #45 and
#59, results in [#54](https://github.com/itej89/rustinfer/issues/54).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| CDNA4-1 | The gfx950 description's values are not tested per field against the guide: no test reads `shared_memory_bytes` (160 KiB), `lane_width`, `vector_bytes` or the registers per lane, which the description lacks (C4-R1; Table 2) | §3.1 Table 2 (p. 8); SRS RI-KC-015 Acceptance ("tested per field, each value cited in #64") | **Open** | Planned in #64 ("One test per field per description, with each value cited to the table below"). The LDS value itself is right: `KC_GFX950_LDS_BYTES` (`crates/rustinfer-core/src/config/constants.rs:721-723`), refused past the limit by the back end (`crates/rustinfer-kc/tests/amd_lowering.rs:437`) and by the ROCm target (`crates/rustinfer-target-rocm/tests/resources.rs:106`, `:125`), and on an MI350X the device reported 163840 bytes, a kernel at the limit launched and one at 163844 was refused (#59). What is missing is a test that the capability field carries the cited value, so a change to the constant or the field would pass unnoticed by RI-KC-015's test |
| CDNA4-2 | No cache-policy hints: the description has no hint field, and no load or store carries SC1, SC0 or NT; every access is wave scope, NT = 0 (C4-R2, C4-R3, C4-R4, C4-R7) | §9.1.10.2, Tables 49 and 50 (pp. 84 to 85); SRS RI-KC-015 (iii), RI-KC-016 (h) | **Open** | Planned in #64: the hint field (non-temporal or streaming, expected reuse, coherence scope) and the `cache-hints` pass, lowered to SC1, SC0 and NT through the ROCDL `gfx942_cache_policy` attribute (MLIR `ROCDLEnums.td`); its acceptance: streamed-weight loads carry NT on gfx950, reused tiles do not, no bit with the switch off. On `b057ef5` the lowering's accesses carry no attribute (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:78`, `:154`, `:321-330`). AMDGPUUsage's Load-Visible and Store-Available tables list gfx950 with `sc0` and `sc1`, see the [AMDGPU code object V5](std-amdgpu-abi-tracker.html) tracker |
| CDNA4-3 | No direct-to-LDS loads: no tile-mover field with gfx950's widths (1, 2, 4, 12, 16 bytes), no asynchronous tile copy in the Kernel IR, and no lowering to `GLOBAL_LOAD_LDS_*` (C4-R5, C4-R6, C4-R7) | §10.1 Tables 54 and 55 (pp. 90 to 91), §10.2 (p. 93); SRS RI-KC-002, RI-KC-015 (i) | **Open** | Planned in #64: the mover field ("per-lane direct-to-shared loads with their byte widths"), a Kernel IR copy and its completion wait with CPU interpreter semantics, and the ROCDL lowering to `rocdl.load.to.lds` / `rocdl.global.load.lds` or `amdgpu.gather_to_lds` "at a width the capability lists", with plain loads and stores where the width or the layout does not fit. On `b057ef5` the operation table has no copy (`crates/rustinfer-kc/src/dialect/ops.rs:8-21`) and shared tiles are staged through registers. The same widths in LLVM's words are [DMA-1](std-llvm-amdgpu-dma-tracker.html) |
