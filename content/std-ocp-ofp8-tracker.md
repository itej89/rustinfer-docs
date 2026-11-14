---
title: "OCP OFP8 Revision 1.1 tracker"
navtitle: Tracker
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 23
summary: Gaps between rustinfer's E4M3 handling and OFP8 Revision 1.1 in its saturating-only scope; the test gap is fixed, the non-saturating mode is out of scope, the GPU users remain.
---

# OCP OFP8 Revision 1.1 tracker

Gaps found by the [audit](std-ocp-ofp8-audit.html) of 2026-11-13, re-audited
against `origin/main` `b99720a` the same day after PRs #48, #50 and #52 merged.
OFP8-1 is out of the narrowed scope and counts in no total.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| OFP8-1 | No non-saturating conversion mode: overflow and ±Inf always give ±448, never NaN | §5.2.1 ("requires implementation of saturating and non-saturating modes"), Table 3 | Out of scope (owner decision 2026-11-13, PR #50) | The second way out was taken: SRS v0.4.3 (merge `48c2820`) scopes OCP-OFP8 to "saturating conversion (roundTiesToEven) only; the non-saturating mode of Revision 1.1 section 5.2.1 is out of scope" (`docs/SRS-RI-v0.1.md:154`). `f32_to_fp8` stays saturating (`crates/rustinfer-target/src/numeric.rs:296-300`). Reopen only if a requirement needs NaN on overflow |
| OFP8-2 | Two correct behaviours have no test: ±Inf to ±448 (saturating), and the Kernel IR `max` identity 0xFE | Table 3 (±Inf row); Table 2 (max normal) | Fixed 2026-11-13 b99720a | PR #52 (issue #51). ±Inf: `test_fp8_e4m3_infinity_saturates_to_448` (`crates/rustinfer-target/tests/numeric.rs:186`) asserts 0x7E and 0xFE and −448 back, for the encoder `numeric.rs:296-300` (overflow `:161-168`). Identity: `test_max_identity_of_ocp_e4m3_is_minus_448` (`crates/rustinfer-kc/src/mlir/lower.rs:441`) checks the constant 0xFE (`lower.rs:23`) decodes to −448 by an independent bit-field decoder and is the most negative of all 256 patterns |
| OFP8-3 | The R1 GPU users of E4M3 are not on `origin/main`: gfx950 fp8 MFMA, fp8 KV write, `mxfp8` activation quantization | §5.2.1 for each conversion; SRS RI-KC-003, RI-KVC-008, RI-MIR-012 | In PR #44 (MFMA, [#8](https://github.com/itej89/rustinfer/issues/8)); Open ([#38](https://github.com/itej89/rustinfer/issues/38), GPU KV and `mxfp8`); KV CPU reference merged 2026-11-13 e218b8a | The fp8 KV CPU reference landed with PR #48 (issue #37, merge `e218b8a`): the cache write encodes `x / scale` with the saturating `f32_to_fp8` (`crates/rustinfer-target/src/reference/kv.rs:263-285`, `:277`), and `test_cached_k_and_v_equal_the_oracle_conversion_bit_exactly` (`crates/rustinfer-target/tests/kv.rs:212`, `Groundwork for RI-KVC-008`) checks it against the oracle for OCP E4M3 (`tests/kv.rs:51`). Still to land: the gfx950 MFMA (PR #44) and the GPU KV and `mxfp8` kernels (#38), each to match the CPU reference bit for bit |
