---
title: "AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025) tracker"
navtitle: Tracker
section: Standards
group: "Number formats / AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
order: 33
summary: Gaps between rustinfer's FP8 E4M3 FNUZ handling and the CDNA3 ISA guide.
---

# AMD FP8 FNUZ tracker

Gaps found by the [audit](std-amd-fnuz-audit.html) of 2026-11-13, re-audited
against `origin/main` `b99720a` the same day after PRs #48 and #52 merged.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| FNUZ-1 | The Kernel IR `max` identity for `f8E4M3FNUZ`, 0xFF (−240), has no test | ISA §7.2 Table 30 (max 240) | Fixed 2026-11-13 b99720a | PR #52 (issue #51). `test_max_identity_of_fnuz_e4m3_is_minus_240` (`crates/rustinfer-kc/src/mlir/lower.rs:454`) checks the constant 0xFF (`lower.rs:25`) decodes to −240 with bias 8 by an independent bit-field decoder and is the most negative of all 256 FNUZ patterns. Also new: `test_fp8_e4m3fnuz_infinity_saturates_to_240` (`crates/rustinfer-target/tests/numeric.rs:199`): ±Inf give 0x7F and 0xFF, never the NaN 0x80 |
| FNUZ-2 | The R1 gfx942 users of FNUZ are not on `origin/main`: the FNUZ fp8 MFMA and fp8 KV storage | ISA §7.2 Table 30 for every value they read or write; SRS RI-KC-003, RI-KVC-008 | In PR #44 (MFMA, [#8](https://github.com/itej89/rustinfer/issues/8)); Open ([#38](https://github.com/itej89/rustinfer/issues/38), GPU KV kernels); KV CPU reference merged 2026-11-13 e218b8a | The fp8 KV configuration and CPU reference landed with PR #48 (issue #37, merge `e218b8a`): `kv_fp8_dtype` picks FNUZ E4M3 on gfx942 (`crates/rustinfer-mir/src/kv.rs:15-25`, `test_fp8_kv_dtype_follows_the_target`, `crates/rustinfer-mir/tests/kv_dtypes.rs:88`), and the cache write saturates through `f32_to_fp8` (`crates/rustinfer-target/src/reference/kv.rs:277`), checked bit for bit against the oracle for FNUZ storage (`crates/rustinfer-target/tests/kv.rs:57`, `:212`). Still to land: the FNUZ MFMA (PR #44) and the GPU cache-write kernel (#38), which must saturate like the CPU reference (FP16_OVFL = 1 or a clamp to ±240); see the audit's conversion note |
