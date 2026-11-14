---
title: "OCP OFP8 Revision 1.1 audit"
navtitle: Audit
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 22
summary: The 2026-11-13 audit of rustinfer's E4M3 encoding and conversion against OFP8 Revision 1.1; saturating conversion conforms, the non-saturating mode is missing.
---

# OCP OFP8 Revision 1.1 audit

**Audit of 2026-11-13**, against the [requirements](std-ocp-ofp8-requirements.html).

**Method.** Read the specification text (`pdftotext -layout` of
`specs/number-formats/ocp-ofp8-rev1.1.pdf`). Read `origin/main` at `ccf02b3`:
`crates/rustinfer-target/src/numeric.rs`, `crates/rustinfer-target/src/reference/mx.rs`,
`crates/rustinfer-mir/src/dtype.rs`, `crates/rustinfer-kc/src/dialect/types.rs`,
`crates/rustinfer-kc/src/mlir/lower.rs`, and the tests in
`crates/rustinfer-target/tests/numeric.rs`, `tests/mx.rs` and the golden file
`tests/data/mx_golden.txt`. Read the SRS on branch
`docs/srs-standards-conformance` (v0.4.3, open PR #50) and the open PRs #44
and #48 (file lists and descriptions). No tests were run.

**Test tags.** `tests/numeric.rs` tags `Verifies RI-MIR-003` and `Verifies
RI-TGT-003`. The E4M3 cases in `tests/mx.rs` and the golden file are tagged
`Groundwork for RI-MIR-012`, because RI-MIR-012 is not complete (#36, #38);
their assertions still bind the E4M3 encoder, which they call.

**Two independent checks.** `test_every_fp8_pattern_round_trips`
(`tests/numeric.rs:140`) decodes all 256 E4M3 patterns and requires every
non-NaN one to encode back to itself; since the encoder never yields 0xFF or
0x7F from a number, this also proves that both NaN patterns decode to NaN. The
golden file's generator (`tests/mx_golden/mod.rs:66-77`) builds the E4M3 grid
from the bit fields with integers only, sharing no code with `numeric.rs`, and
the 26 E4M3 golden lines of `mx_golden.txt` must match the encoder bit
for bit (`test_golden_blocks_quantize_bit_exactly`, `tests/mx.rs:320`).

| item | requirement | result | evidence |
|---|---|---|---|
| OFP8-R1 | 1-4-3 layout, bias 7, emax 8, emin −6 | conforms | `MiniFloat::E4M3` (`numeric.rs:49-56`); the sign is bit 7 (`:66-68`). `test_fp8_e4m3_encodes_ocp_values` (`tests/numeric.rs:92`): 1.0 is 0x38 |
| OFP8-R2 | normal and subnormal value formulas | conforms | `numeric.rs:103-108` is the §5.1 formula, with `min_exponent` 1 − bias (`:79-81`). Asserted: 2^−9 round-trips (`tests/numeric.rs:103-106`); the golden grid is built independently from the same formula |
| OFP8-R3 | no Inf; NaN S.1111.111 only; zeros; max ±448 | conforms | `special` treats only exponent 15 with mantissa 7 as NaN, either sign, and nothing as Inf (`numeric.rs:116-127`); `max` is S.1111.110 (`:89-90`). Asserted: 448 is 0x7E, 0x7F is NaN (`tests/numeric.rs:94-101`), `test_format_maxima` (`numeric.rs:336`); 0xFF is NaN by the exhaustive round trip. Min normal and max subnormal are not asserted by value but follow from R2 and the round trip |
| OFP8-R4 | from binary32, binary16 and bfloat16 | conforms | the codec widens `bf16` and `fp16` exactly to `f32`, then encodes once (`cpu/codec.rs:60-81`), so the single rounding is from the source value. Exact widening: `test_every_half_pattern_round_trips` (`tests/numeric.rs:158`) |
| OFP8-R5 | roundTiesToEven | conforms | `numeric.rs:152-159`. Asserted: 1.0625 gives 1.0 and 1.1875 gives 1.25 (`tests/numeric.rs:108-109`); six E4M3 midpoints (one subnormal, two near 1, three near the top), each with its neighbours one ulp either side, for both signs, in the golden lines `e4m3 midpoints_positive` and `midpoints_negative` (scale 2^0, so each element is its input) |
| OFP8-R6 | saturating **and** non-saturating modes | **missing** (OFP8-1) | `f32_to_fp8` has no mode parameter and always saturates (`numeric.rs:296-300`, `:161-168`). No non-saturating conversion exists anywhere on `origin/main` |
| OFP8-R7 | NaN gives an implementation-defined NaN | conforms | a NaN encodes to 0x7F (`numeric.rs:132-133`). Asserted (`tests/numeric.rs:102`) |
| OFP8-R8 | ±Inf gives ±448 when saturating | conforms by reading; **untested** (OFP8-2) | `round` passes Inf through (`numeric.rs:153-154`), the comparison with 448 sends it to `overflow`, which returns the maximum with the sign (`:138-139`, `:161-168`). No test converts ±Inf to E4M3: the MX tests with Inf stop at the NaN scale before any element is encoded |
| OFP8-R9 | overflow after rounding gives ±448 when saturating | conforms | `numeric.rs:137-139`. Asserted: ±1e9 give 0x7E and 0xFE (`tests/numeric.rs:99-100`) |
| OFP8-R10 | the rounded value otherwise; the sign preserved | conforms | `numeric.rs:141-148`, a negative zero result keeps the sign (`:142-143`). Asserted: −0.0 keeps its sign (`tests/numeric.rs:110-113`); negative golden lines; `test_e4m3_exp_adj_boundaries` asserts a tiny negative element is 0x80 (`tests/mx.rs:296-298`) |
| OFP8-R11 | 448 < x ≤ 464 rounds to 448 (Appendix A) | conforms | ties to even at the top binade (`numeric.rs:152-159`). Asserted: 464 encodes to 0x7E and decodes to 448 (`tests/mx.rs:296-299`, scale 2^0); golden line `e4m3 exp_adj_at_1.8125x2^8` (input 464, code 7e) |

## Other users of E4M3 on `origin/main`

- The Kernel IR's `max` identity for `f8E4M3FN` is 0xFE, −448, the most
  negative finite E4M3 value (`crates/rustinfer-kc/src/mlir/lower.rs:23`).
  Correct by Table 2; no test asserts the constant (OFP8-2).
- `MxElement::E4m3` encodes with the same function (`reference/mx.rs:109`),
  so MXFP8 elements inherit the saturating behaviour.

## Requirements of the SRS not yet on `origin/main`

| SRS requirement | what needs E4M3 | where it is |
|---|---|---|
| RI-KC-003 | OCP fp8 MFMA operands on gfx950 | PR #44 (issue #8), open |
| RI-KVC-008 | `--kv-dtype fp8`: E4M3 KV on gfx950 and cpu, written by the cache-write kernel | PR #48 (issue #37), open: the CPU reference path; GPU kernels issue #38 |
| RI-MIR-012, RI-CLI-002 | `--activations mxfp8`: in-kernel E4M3 activation quantization on gfx950 | issue #38, no PR |

These are recorded as OFP8-3: the conversions they perform must meet R5 to
R10, and bit-exact agreement with the CPU reference is their acceptance test.

## Result

The encoding (R1 to R3) and saturating conversion (R4, R5, R7 to R11)
conform; R8 is correct by reading but untested. R6 is not met: only the
saturating mode exists. **Partial.**
