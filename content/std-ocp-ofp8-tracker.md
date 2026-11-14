---
title: "OCP OFP8 Revision 1.1 tracker"
navtitle: Tracker
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 23
summary: Gaps between rustinfer's E4M3 handling and OFP8 Revision 1.1.
---

# OCP OFP8 Revision 1.1 tracker

Gaps found by the [audit](std-ocp-ofp8-audit.html).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| OFP8-1 | No non-saturating conversion mode: overflow and ±Inf always give ±448, never NaN | §5.2.1 ("requires implementation of saturating and non-saturating modes"), Table 3 | Open | No issue covers it. Two ways out: add a mode to `f32_to_fp8` (`numeric.rs:296-300`) whose overflow branch returns the NaN 0x7F (or 0xFF) for E4M3, with tests for both rows of Table 3; or amend the SRS §1.4 Scope phrase of OCP-OFP8 to "saturating mode only" and record the deviation. The SRS uses only saturation today (RI-KVC-008, RI-MIR-012) |
| OFP8-2 | Two correct behaviours have no test: ±Inf to ±448 (saturating), and the Kernel IR `max` identity 0xFE | Table 3 (±Inf row); Table 2 (max normal) | Open | Test gap only. Assert `f32_to_fp8(±Inf, E4m3)` is 0x7E and 0xFE in `tests/numeric.rs`; assert the identity in a kc test against `fp8_to_f32` or a literal −448 |
| OFP8-3 | The R1 GPU users of E4M3 are not on `origin/main`: gfx950 fp8 MFMA, fp8 KV write, `mxfp8` activation quantization | §5.2.1 for each conversion; SRS RI-KC-003, RI-KVC-008, RI-MIR-012 | In PR #44 (MFMA, [#8](https://github.com/itej89/rustinfer/issues/8)), In PR #48 (KV, CPU reference, [#37](https://github.com/itej89/rustinfer/issues/37)); Open ([#38](https://github.com/itej89/rustinfer/issues/38), GPU KV and `mxfp8`) | Each must convert with roundTiesToEven and saturation and match the CPU reference bit for bit; audit them when they land |
