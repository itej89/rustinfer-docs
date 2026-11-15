---
title: "AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025) tracker"
navtitle: Tracker
section: Standards
group: "Number formats / AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
order: 33
summary: Gaps between rustinfer's FP8 E4M3 FNUZ handling and the CDNA3 ISA guide; the gfx942 FNUZ MFMA merged with PR #44 but is not yet run on hardware (#61), the GPU fp8 KV kernels are #38, and the gfx942 cache bits and direct-to-LDS loads are #64.
---

# AMD FP8 FNUZ tracker

Gaps found by the [audit](std-amd-fnuz-audit.html) of 2026-11-13, re-audited
against `origin/main` `b99720a` the same day after PRs #48 and #52 merged, and
on 2026-11-14 against `81fbcba` after PR #44 (issue #8, merge `38f2f60`) added
the gfx942 FNUZ MFMA; on 2026-11-15 against `b057ef5` for the gfx942 capability values SRS v0.4.11 added to the scope (FNUZ-3).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| FNUZ-1 | The Kernel IR `max` identity for `f8E4M3FNUZ`, 0xFF (−240), has no test | ISA §7.2 Table 30 (max 240) | Fixed 2026-11-13 b99720a | PR #52 (issue #51). `test_max_identity_of_fnuz_e4m3_is_minus_240` (`crates/rustinfer-kc/src/mlir/lower.rs:454`) checks the constant 0xFF (`lower.rs:25`) decodes to −240 with bias 8 by an independent bit-field decoder and is the most negative of all 256 FNUZ patterns. Also new: `test_fp8_e4m3fnuz_infinity_saturates_to_240` (`crates/rustinfer-target/tests/numeric.rs:199`): ±Inf give 0x7F and 0xFF, never the NaN 0x80 |
| FNUZ-2 | The R1 gfx942 users of FNUZ are not proven on hardware or not written: the FNUZ fp8 MFMA has not run on a gfx942, and the GPU fp8 KV kernels do not exist | ISA §7.2 Table 30 for every value they read or write; SRS RI-KC-003, RI-KVC-008 | **Open** | MFMA merged 2026-11-14 with PR #44 (`38f2f60`): `F8E4M3Fnuz` maps to `v_mfma_f32_32x32x16_fp8_fp8` and `v_mfma_f32_16x16x32_fp8_fp8` on gfx942 (`crates/rustinfer-kc/src/amd.rs:154-156`), checked on the host by disassembly only (`test_matrix_op_disassembles_to_the_mfma_of_gfx942_fp8_fnuz_16x16` and `_32x32`, `crates/rustinfer-kc/tests/amd_lowering.rs:220`, `:226`, Groundwork for RI-KC-003). gfx942 not yet run on hardware: the gfx942 half of GPU test #45, whose inputs are encoded by the CPU reference's FNUZ encoder (`crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:149`, `:237-238`), is [#61](https://github.com/itej89/rustinfer/issues/61); the gfx950 run of #45 (results in #54) uses no FNUZ. The fp8 KV configuration and CPU reference landed with PR #48 (issue #37, merge `e218b8a`): `kv_fp8_dtype` picks FNUZ E4M3 on gfx942 (`crates/rustinfer-mir/src/kv.rs:15-25`, `test_fp8_kv_dtype_follows_the_target`, `crates/rustinfer-mir/tests/kv_dtypes.rs:88`), and the cache write saturates through `f32_to_fp8` (`crates/rustinfer-target/src/reference/kv.rs:277`), checked bit for bit against the oracle for FNUZ storage (`crates/rustinfer-target/tests/kv.rs:57`, `:212`). Still to land: the GPU cache-write kernel ([#38](https://github.com/itej89/rustinfer/issues/38), open), which must saturate like the CPU reference (FP16_OVFL = 1 or a clamp to ±240); see the audit's conversion note |
| FNUZ-3 | The gfx942 capability values the scope gained with SRS v0.4.11 are incomplete: the description has no SC1, SC0 and NT cache hints and no per-lane direct-to-LDS mover (`GLOBAL_LOAD_LDS_*`, 1, 2, 4 bytes), and its 64 KiB LDS value has no per-field test (FNUZ-R7 to FNUZ-R9) | ISA §3.1 Table 2, §9.1.10.2 Table 48, §12.15; SRS RI-KC-015, RI-KC-016 (h) | **Open** | Found 2026-11-15 on `b057ef5`. Planned in [#64](https://github.com/itej89/rustinfer/issues/64) (open, R1): the mover and hint fields with one test per field, the asynchronous tile copy lowered to the direct-to-LDS loads, and the `cache-hints` pass mapped to SC1, SC0 and NT. The LDS value itself is right (`KC_GFX942_LDS_BYTES`, `crates/rustinfer-core/src/config/constants.rs:717-719`; refused past 65536 by the back end, `crates/rustinfer-kc/tests/amd_lowering.rs:437`). gfx942 hardware runs no longer gate R1 (SRS v0.4.12), so these are closed by offline tests. The gfx950 counterparts are [CDNA4-1 to CDNA4-3](std-amd-cdna4-isa-tracker.html) |
