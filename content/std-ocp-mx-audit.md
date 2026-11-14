---
title: "OCP MX v1.1.0 audit"
navtitle: Audit
section: Standards
group: "Number formats / OCP MX v1.1.0"
order: 42
summary: The 2026-11-13 audit of rustinfer's MXFP4 types and conversion against OCP MX v1.1; the Model IR and the CPU reference oracle conform, the paths that apply it are pending.
---

# OCP MX v1.1.0 audit

**Audit of 2026-11-13**, against the [requirements](std-ocp-mx-requirements.html).

**Method.** Read the specification text (`pdftotext -layout` of
`specs/number-formats/ocp-mx-v1.1.0.pdf`), §3 to §6.3. Read `origin/main` at
`ccf02b3`: `crates/rustinfer-target/src/reference/mx.rs`,
`crates/rustinfer-mir/src/dtype.rs`, `crates/rustinfer-mir/src/mx.rs`, the
tests `crates/rustinfer-target/tests/mx.rs` and `crates/rustinfer-mir/tests/mx.rs`,
the golden file `crates/rustinfer-target/tests/data/mx_golden.txt` and its
generator `crates/rustinfer-target/tests/mx_golden/mod.rs`. Worked the
Equation 4 thresholds by hand: for E2M1 (one mantissa bit) a significand
rounds up to 2 exactly from 1.75, a tie that goes to the even 10.0; for E4M3
1.8125 is a tie that goes to the even 1.75, anything above it and below
1.9375 rounds to 1.875, and 1.9375 itself carries to 2. Read the SRS on branch `docs/srs-standards-conformance`
(v0.4.3, open PR #50) and the file lists of open PRs #44, #48 and #49. No
tests were run.

**Test tags.** The E2M1 decode, UE8M0 decode, `fp4x2` packing and storage
tests carry `Verifies RI-MIR-003`. The conversion tests and the golden file
carry `Groundwork for RI-MIR-012`, and the `mx` encoding checks `Groundwork for
RI-MIR-011`: by the rule of `docs/testing.md` those clauses count as not
implemented until their build-time and kernel parts land (#36, #38). The
module header of `tests/mx.rs` says so (`:5-10`). The assertions themselves
bind the CPU reference and are the evidence below.

**The independent check.** The golden generator shares no code with
`reference/mx.rs` and uses no floating-point arithmetic: it decomposes each
`f32` from its bits, builds the E2M1 and E4M3 grids from their bit fields
(`mx_golden/mod.rs:53-94`), and applies §6.3 with Equation 4 on integers
(`:1-18`). `test_golden_file_is_the_independent_generator_output`
(`tests/mx.rs:306`) requires the committed file to be its output, and
`test_golden_blocks_quantize_bit_exactly` (`tests/mx.rs:320`) requires the
reference to reproduce all 51 blocks (25 E2M1, 26 E4M3) bit for bit.

| item | requirement | result | evidence |
|---|---|---|---|
| MX-R1 | X NaN gives NaN everywhere; otherwise X·P_i; beyond Float32 implementation-defined | conforms | `mx_dequantize_block` multiplies by the decoded scale, NaN for 0xFF (`mx.rs:297-303`, `:225-227`). `test_nan_or_inf_block_has_nan_scale_and_dequantizes_to_nan` (`tests/mx.rs:235`); beyond the range rustinfer gives ±Inf, `test_dequantize_beyond_the_f32_range_is_infinite` (`tests/mx.rs:276`) |
| MX-R2 | MXFP4: E2M1, k = 32, UE8M0 | conforms | `MX_BLOCK` 32 (`mx.rs:33`, from `constants.rs:136`), `test_block_constants_agree` (`mx.rs:565`); the Model IR refuses another block size, scale dtype or element dtype, or an axis not a multiple of 32 (`mir/src/mx.rs:52-86`): `tests/mx.rs` of `rustinfer-mir`, `:192`, `:204`, `:216`, `:225` |
| MX-R3 | E2M1 table, subnormals | conforms | `E2M1_VALUES` and `e2m1_to_f32` (`mx.rs:69`, `:188-197`); the dtype doc (`dtype.rs:30-35`). `test_e2m1_decodes_all_sixteen_codes` (`tests/mx.rs:116`, Verifies RI-MIR-003): 0x1 is the subnormal 0.5, 0x8 is −0. The golden grid derives the same values from the bit fields |
| MX-R4 | roundTiesToEven to FP4 | conforms | `e2m1_magnitude` counts the exact midpoints below the value and moves an odd code at a tie to the even one (`mx.rs:211-221`). `test_e2m1_rounds_every_midpoint_tie_to_even` (`tests/mx.rs:144`), `test_e2m1_rounds_one_ulp_either_side_of_every_midpoint` (`:154`); golden `e2m1 midpoints_positive`, `midpoints_negative`, `midpoints_scale_2^-3` |
| MX-R5 | clamp to ±6 keeping the sign, Infs included | conforms | above the last midpoint the code is 7 (`mx.rs:214-215`), the sign kept (`:207-208`). `test_e2m1_clamps_to_six_keeping_the_sign` (`tests/mx.rs:168`): 6⁺, 7, 8, 1e30, Inf, both signs |
| MX-R6 | NaN implementation-defined | conforms | a NaN gives 0x0 (`mx.rs:204-206`); never reached in a block, whose NaN gives the NaN scale |
| MX-R7 | UE8M0: bias 127, −127 to 127, NaN 0xFF | conforms | `ue8m0_to_f32` (`mx.rs:225-231`), 2^−127 as the `f32` subnormal 0x00400000; the stored scale is clamped to −127..127 so it never reaches 0xFF (`:276-278`). `test_ue8m0_decodes_as_a_power_of_two_or_nan` (`tests/mx.rs:131`, all 256 codes); `test_stored_scale_clamps_at_both_ends` (`mx.rs:555`) |
| MX-R8 | a conversion mechanism | conforms | `mx_quantize_block` (`mx.rs:233-255`) and `mx_quantize` along any axis (`:423-446`). `test_mx_quantize_along_the_last_axis_matches_the_block_rule` (`tests/mx.rs:409`), `test_mx_quantize_along_a_strided_axis_round_trips_the_layout` (`:432`) |
| MX-R9 | Equation 1: zero, NaN/Inf, above SFmax, below SFmin, SF(V) | conforms | NaN or Inf anywhere gives 0xFF (`mx.rs:236-241`), the same as an IEEE maximum that propagates NaN; all zero gives 0x7F (`:242-248`); SF from an exact `floor(log2 amax)`, subnormals included (`:257-261`, `:280-289`); clamp at both ends (`:276-278`): above SFmax rustinfer saturates, which §6.3 footnote 2 gives as an example. `test_all_zero_block_has_scale_one_and_zero_codes` (`tests/mx.rs:222`), `test_nan_or_inf_block_has_nan_scale_and_dequantizes_to_nan` (`:235`), `test_scale_clamps_at_minus_127_and_tops_out_at_126` (`:258`), `test_floor_log2_and_pow2_are_exact` (`mx.rs:572`); golden `scale_min_clamp`, `scale_max_reachable`, `all_zero`, `nan`, `nan_and_inf` |
| MX-R10 | Equation 4 | conforms | `exp_adj` rounds the significand to the element's mantissa width, ties to even, exact in `f64`, and tests the carry and the E4M3 1.875 case (`mx.rs:263-273`). `test_exp_adj_boundary_at_1_75_and_one_ulp_below` (`tests/mx.rs:190`, seven binades from 2^−100 to 2^126), `test_plain_floor_differs_on_the_1_75_boundary` (`:206`), `test_e4m3_exp_adj_boundaries` (`:289`); golden `exp_adj_at_1.75x2^2`, `exp_adj_below_1.75x2^2` and the ±2^−20 pair |
| MX-R11 | P_i = V_i / X quantized, normals clamped with the sign; NaN-scale elements implementation-defined | conforms | each element is `v / 2^s` encoded (`mx.rs:249-254`), exact in `f32` as the module header argues (`:18-24`); a NaN-scale block's codes are 0x0 (`:237-240`). One permitted difference: in an all-zero block a −0 input gets code 0x0, not the 0x8 that step 2 would give; the value is equal, §6.3 is "should" with "other algorithms ... may", and RI-MIR-012 (2) requires 0x0 |
| MX-R12 | roundTiesToEven to the element | conforms | as MX-R4 for E2M1 |
| MX-R13 | ±Inf gives a NaN scale | conforms | `mx.rs:236` (`!is_finite`). Golden `pos_inf`, `neg_inf` for both element formats; `tests/mx.rs:238-239` |

**Additional checks.** `test_dequantize_after_quantize_is_within_half_a_step`
(`tests/mx.rs:348`) bounds the round-trip error on every finite golden
block. `fp4x2` packing (low nibble first, `mx.rs:305-339`) is the SRS's
layout choice, which §5.1 leaves open: `test_fp4x2_packs_low_nibble_first`
(`tests/mx.rs:371`). The `mx` matmul reference (`mx.rs:486-507`) computes the
§6.2 general dot product by dequantizing the weight and accumulating in `f32`;
the dot products are outside the scope.

## Outside the scope, noted

- The reference also converts with E4M3 elements (MXFP8, `MxElement::E4m3`).
  MXFP8 is not in the Scope phrase. If it were claimed, §5.3.1 would require
  both the SAT and NONSAT FP8 modes, which rustinfer lacks (OFP8-1).
- Checkpoint import (PR #49, issue #35) reads Quark and compressed-tensors
  MXFP4 tensors as `fp4x2` and `ue8m0`; that is the QUARK and CT standards.
  `test_quark_compressed_tensors_convention_hand_built` (`tests/mx.rs:535`)
  decodes a hand-built tensor; OI-014 (Quark's own unpacking) is still open.

## Requirements of the SRS not yet on `origin/main`

| SRS requirement | what must apply §6.3 | where it is |
|---|---|---|
| RI-GC-004, RI-CLI-002, RI-MIR-012 | `build --precision mxfp4`: RTN quantization of weights at build, recorded as the load-time transform | issue #36, no PR |
| RI-KVC-008, RI-MIR-012 | `--kv-dtype mxfp4`: the cache-write kernel computes each block's UE8M0 scale | PR #48 (issue #37), open: CPU reference path; GPU kernels issue #38 |
| RI-KC-003, RI-MIR-011, RI-MIR-012 | in-kernel MXFP4 dequantization on gfx950 and gfx942; in-kernel `mxfp4` activation quantization on gfx950 | issue #38, no PR (blocked by #8, PR #44) |

Recorded as MX-1 to MX-3.

## Result

Every in-scope item conforms in the Model IR and the CPU reference, the
oracle the other targets are checked against. The paths that must apply the
same rule at build time, in the KV cache and in kernels are not on
`origin/main`. **Partial**, for the R1 coverage, not for any wrong value.
