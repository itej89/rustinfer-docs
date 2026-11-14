---
title: "OCP OFP8 Revision 1.1 audit"
navtitle: Audit
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 22
summary: The 2026-11-14 audit of rustinfer's E4M3 and E5M2 encodings and conversion against OFP8 Revision 1.1 on 8c7d47e; both encodings and saturating conversion conform and are tested, the non-saturating mode is out of scope, the GPU users of E4M3 are pending.
---

# OCP OFP8 Revision 1.1 audit

**Audit of 2026-11-14**, against the [requirements](std-ocp-ofp8-requirements.html),
on `origin/main` `8c7d47e` (after PR #55, merge `6a18042`: the `fp8_e5m2`
dtype and its CPU conversion, SRS v0.4.6; PRs #53 and #49 change no OFP8
code). History: first audited 2026-11-13 on `ccf02b3` (E4M3 only), re-audited
the same day on `b99720a` after PRs #48, #50 (scope narrowed to saturating
conversion) and #52 (OFP8-2 fixed). PR #55 added the `saturating` field to the
shared `MiniFloat` row and moved every line of `numeric.rs` below it; the E4M3
results below are unchanged and their line numbers are those of `8c7d47e`.

**Method.** Read the specification text (`pdftotext -layout` of
`specs/number-formats/ocp-ofp8-rev1.1.pdf`): §3, §4.2, §5.1 with Tables 1
and 2, §5.2.1 with Table 3, and Appendix A. Read `origin/main` at `8c7d47e`:
`crates/rustinfer-target/src/numeric.rs`, `src/cpu/codec.rs`,
`src/reference/mx.rs`, `src/reference/kv.rs`, `crates/rustinfer-mir/src/dtype.rs`,
`crates/rustinfer-kc/src/dialect/types.rs` and `src/mlir/lower.rs`; the tests
`crates/rustinfer-target/tests/numeric.rs`, `tests/mx.rs`, `tests/kv.rs`,
`tests/e5m2.rs`, the E5M2 golden generator `tests/e5m2_golden/mod.rs` and its
output `tests/data/e5m2_golden.txt`, and `crates/rustinfer-mir/tests/e5m2.rs`.
Read SRS v0.4.8 RI-MIR-003 (`docs/SRS-RI-v0.1.md:591-634`) and the state of
PR #44 (open). No tests were run.

**Test tags.** `tests/numeric.rs` and `tests/e5m2.rs` tag `Verifies RI-MIR-003`
and `Verifies RI-TGT-003`; `crates/rustinfer-mir/tests/e5m2.rs` tags `Verifies
RI-MIR-003`. The E4M3 cases in `tests/mx.rs` and the MX golden file are tagged
`Groundwork for RI-MIR-012`, because RI-MIR-012 is not complete (#36, #38);
their assertions still bind the E4M3 encoder, which they call.

**Independent checks.** E4M3: `test_every_fp8_pattern_round_trips`
(`tests/numeric.rs:141`) decodes all 256 patterns and requires every non-NaN
one to encode back to itself; since the encoder never yields 0xFF or 0x7F
from a number, this also proves that both NaN patterns decode to NaN. The MX
golden generator (`tests/mx_golden/mod.rs:66-77`) builds the E4M3 grid from
the bit fields with integers only, and the 26 E4M3 golden lines must match
the encoder bit for bit (`test_golden_blocks_quantize_bit_exactly`,
`tests/mx.rs:320`). E5M2: the generator `tests/e5m2_golden/mod.rs` shares no
code with `numeric.rs` and uses no floating point (every value an integer
count of 2^−16 or 2^−17 units, every `f32` assembled from its bits,
`:1-17`). It writes a `decode` line for each of the 256 codes and, for every
pair of adjacent finite codes and for 57344 and the next binade's 65536, the
midpoint with the `f32` one ULP either side, both signs (`midpoints`,
`:123-141`), plus the clamp boundary, `f32::MAX`, ±Inf, ±0 and the smallest
`f32` subnormal (`boundaries`, `:144-153`): 758 `round` lines.
`test_golden_file_is_the_independent_generator_output` (`tests/e5m2.rs:87`)
requires the committed file to be its output.

## E4M3 (OFP8-R1 to R11)

| item | requirement | result | evidence |
|---|---|---|---|
| OFP8-R1 | 1-4-3 layout, bias 7, emax 8, emin −6 | conforms | `MiniFloat::E4M3` (`numeric.rs:60-68`); the sign is bit 7 (`:90-92`). `test_fp8_e4m3_encodes_ocp_values` (`tests/numeric.rs:93`): 1.0 is 0x38 |
| OFP8-R2 | normal and subnormal value formulas | conforms | `numeric.rs:127-132` is the §5.1 formula, with `min_exponent` 1 − bias (`:103-105`). Asserted: 2^−9 round-trips (`tests/numeric.rs:104-107`); the golden grid is built independently from the same formula |
| OFP8-R3 | no Inf; NaN S.1111.111 only; zeros; max ±448 | conforms | `special` treats only exponent 15 with mantissa 7 as NaN, either sign, and nothing as Inf (`numeric.rs:136-152`, `:151`); `max` is S.1111.110 (`:108-117`, `:114`). Asserted: 448 is 0x7E, 0x7F is NaN (`tests/numeric.rs:95-102`), `test_format_maxima` (`numeric.rs:367`); 0xFF is NaN by the exhaustive round trip. Min normal and max subnormal are not asserted by value but follow from R2 and the round trip |
| OFP8-R4 | from binary32, binary16 and bfloat16 | conforms | the codec widens `bf16` and `fp16` exactly to `f32`, then encodes once (`cpu/codec.rs:60-83`), so the single rounding is from the source value. Exact widening: `test_every_half_pattern_round_trips` (`tests/numeric.rs:159`) |
| OFP8-R5 | roundTiesToEven | conforms | `numeric.rs:176-183`. Asserted: 1.0625 gives 1.0 and 1.1875 gives 1.25 (`tests/numeric.rs:109-110`); six E4M3 midpoints (one subnormal, two near 1, three near the top), each with its neighbours one ulp either side, for both signs, in the golden lines `e4m3 midpoints_positive` and `midpoints_negative` (scale 2^0, so each element is its input) |
| OFP8-R6 | saturating **and** non-saturating modes; in scope: saturating only | conforms in scope; non-saturating **out of scope** (OFP8-1) | `f32_to_fp8` has no mode parameter and always saturates (`numeric.rs:327-331`); every fp8 row sets `saturating: true` (`:66`, `:75`, `:86`) and `overflow` returns the maximum for them (`:185-192`). No non-saturating conversion exists on `origin/main`; SRS §1.4 scopes OCP-OFP8 to saturating conversion only (`docs/SRS-RI-v0.1.md:160`, PR #50, owner decision 2026-11-13) |
| OFP8-R7 | NaN gives an implementation-defined NaN | conforms | a NaN encodes to 0x7F (`numeric.rs:156-158`, `:20`). Asserted (`tests/numeric.rs:103`) |
| OFP8-R8 | ±Inf gives ±448 when saturating | conforms | `round` passes Inf through (`numeric.rs:177-179`), the comparison with 448 sends it to `overflow`, which returns the maximum with the sign (`:162-164`, `:185-192`). Asserted: `test_fp8_e4m3_infinity_saturates_to_448` (`tests/numeric.rs:186`): ±Inf give 0x7E and 0xFE, decode to ±448, and `round_to_fp8` agrees (OFP8-2, fixed 2026-11-13) |
| OFP8-R9 | overflow after rounding gives ±448 when saturating | conforms | `numeric.rs:161-164`. Asserted: ±1e9 give 0x7E and 0xFE (`tests/numeric.rs:100-101`) |
| OFP8-R10 | the rounded value otherwise; the sign preserved | conforms | `numeric.rs:165-172`, a negative zero result keeps the sign (`:166-167`). Asserted: −0.0 keeps its sign (`tests/numeric.rs:111-114`); negative golden lines; `test_e4m3_exp_adj_boundaries` asserts a tiny negative element is 0x80 (`tests/mx.rs:296-298`) |
| OFP8-R11 | 448 < x ≤ 464 rounds to 448 (Appendix A) | conforms | ties to even at the top binade (`numeric.rs:176-183`). Asserted: 464 encodes to 0x7E and decodes to 448 (`tests/mx.rs:296-299`, scale 2^0); golden line `e4m3 exp_adj_at_1.8125x2^8` (input 464, code 7e) |

## E5M2 (OFP8-R12 to R18), new since PR #55

The dtype is `DType::Fp8E5m2`, token `fp8_e5m2`, one byte, quantized
(`crates/rustinfer-mir/src/dtype.rs:30-35`, `:74-81`, `:141-151`); it is
left out of `FLOAT_OR_QUANTIZED`, so no `matmul` or KV write reads it
(`:84-94`), as RI-MIR-003 says nothing in R1 does. The conversion is the
shared `MiniFloat` encoder with the row `MiniFloat::E5M2`
(`crates/rustinfer-target/src/numeric.rs:78-88`), reached through
`Fp8Format::E5m2` (`:253-295`) and the CPU codec (`src/cpu/codec.rs:67`, `:80`).

| item | requirement | result | evidence |
|---|---|---|---|
| OFP8-R12 | 1-5-2 layout, bias 15, emax 15, emin −14 | conforms | `MiniFloat::E5M2`: 5 exponent bits, 2 mantissa bits, bias 15 (`numeric.rs:80-88`); sign bit 7 (`:90-92`); `min_exponent` −14 (`:103-105`). `test_fp8_e5m2_token_and_element_size` (`crates/rustinfer-mir/tests/e5m2.rs:68`): element size 1 |
| OFP8-R13 | normal and subnormal value formulas | conforms | the shared decoder (`numeric.rs:127-132`). `test_every_code_decodes_to_the_golden_value` (`tests/e5m2.rs:100`): all 256 codes equal the generator's integer-built values bit for bit |
| OFP8-R14 | Inf S.11111.00, NaN S.11111.{01,10,11}, zeros, max ±57344, min normal 2^−14, max subnormal 0.75 × 2^−14, min subnormal 2^−16 | conforms | `ieee_specials: true` makes the all-ones exponent Inf at mantissa 0 and NaN otherwise, either sign (`numeric.rs:84`, `:143-150`); `max` is exponent 30 with mantissa 3 (`:108-110`), `E5M2_MAX` 57344 (`:27`). `test_table_2_values` (`tests/e5m2.rs:137`) asserts every Table 2 row by value, both signs of max and of the three NaN codes; `test_format_maxima` (`numeric.rs:367`) |
| OFP8-R15 | from binary32, binary16, bfloat16 with roundTiesToEven | conforms | `round` (`numeric.rs:176-183`); the codec widens `bf16` and `fp16` exactly before the single rounding (`cpu/codec.rs:60-83`). `test_every_golden_rounding_case_encodes_to_the_golden_code` (`tests/e5m2.rs:120`): every midpoint goes to the even code, one `f32` ULP either side to the near code, both signs, subnormals included; `test_every_code_round_trips` (`:202`) |
| OFP8-R16 | NaN gives a NaN; ±Inf gives ±57344 (saturating) | conforms | a NaN encodes to 0x7E, `S.11111.10` (`numeric.rs:25`, `:156-158`); ±Inf passes `round` (`:177-179`) and reaches `overflow`, which with `saturating: true` returns the maximum, not the Inf pattern (`:86`, `:185-192`). `test_nan_input_gives_a_nan_code` (`tests/e5m2.rs:176`): either sign and a signalling payload; `test_saturation_clamps_to_57344` (`:156`): ±Inf give 0x7B and 0xFB, and `round_to_fp8` agrees |
| OFP8-R17 | overflow after rounding gives ±57344 (saturating); otherwise the rounded value, the sign kept | conforms | `numeric.rs:161-172`, a negative result rounding to zero keeps the sign (`:166-167`). `test_saturation_clamps_to_57344` (`tests/e5m2.rs:156`): 57344 + 1 ULP, 65536, `f32::MAX`, both signs; `test_negative_zero_keeps_its_sign` (`:187`): −0 is 0x80 and decodes to −0, −2^−18 and the tie −2^−17 give 0x80; the golden boundary lines (`e5m2_golden/mod.rs:144-153`) |
| OFP8-R18 | 57344 < x < 61440 rounds to 57344; 61440 rounds up and saturates (Appendix A) | conforms | ties to even at the top binade: 0x7B has an odd mantissa, so the tie at 61440 goes up to 65536, above `max`, and saturates (`numeric.rs:176-183`, `:161-164`). The generator's last midpoint pair is 57344 and 65536 with saturation (`e5m2_golden/mod.rs:123-141`), giving 0x7B one ULP below, at and above 61440; `test_saturation_clamps_to_57344` asserts 61440 itself (`tests/e5m2.rs:161`, `:166-167`) |

Beyond the clause's conversion: `test_fp8_format_of_e5m2` (`tests/e5m2.rs:219`)
maps the dtype to the format, and `test_cpu_quantize_and_dequantize_launches_use_e5m2`
(`:226`) runs the CPU `quantize` and `dequantize` kernels on `fp8_e5m2` (per
channel amax to 57344, back exactly). In the Model IR, an E5M2 tensor without a
`linear` encoding is refused (`crates/rustinfer-mir/tests/e5m2.rs:102`), only
`quantize` outputs and `dequantize` inputs admit it (`:123`, `:167`), and
`matmul` and a KV group refuse it (`:147`, `:204`). Every acceptance line of
RI-MIR-003 for `fp8_e5m2` (`docs/SRS-RI-v0.1.md:624-628`) has its test.

## Other users of the formats on `origin/main`

- The Kernel IR's `max` identity for `f8E4M3FN` is 0xFE, −448, the most
  negative finite E4M3 value (`crates/rustinfer-kc/src/mlir/lower.rs:23`),
  asserted by `test_max_identity_of_ocp_e4m3_is_minus_448` (`lower.rs:441`)
  (OFP8-2, fixed 2026-11-13). The Kernel IR also names `f8E5M2`
  (`crates/rustinfer-kc/src/dialect/types.rs:21-22`) with `max` identity 0xFC,
  −Inf (`lower.rs:24`), correct since E5M2 has infinities (Table 2); no kernel
  of R1 uses it.
- The fp8 KV CPU reference (PR #48, `e218b8a`) writes each K and V value as
  `f32_to_fp8(x / scale, format)` (`crates/rustinfer-target/src/reference/kv.rs:277`)
  and reads it back as `bf16(scale × fp8(code))`, so it inherits R4, R5 and
  R7 to R11; `test_cached_k_and_v_equal_the_oracle_conversion_bit_exactly`
  (`tests/kv.rs:212`) covers OCP E4M3 storage (`tests/kv.rs:51`). Since PR #49
  (`8c7d47e`) the frontend can fill the per-layer scales of that KV group from
  a checkpoint's KV scale tensors (`crates/rustinfer-frontend/src/kv_scales.rs:102-121`);
  the stored E4M3 conversion is unchanged.
- `MxElement::E4m3` encodes with the same function (`reference/mx.rs:109`),
  so MXFP8 elements inherit the saturating behaviour.
- E5M2 is not a checkpoint dtype: the safetensors reader has no `F8_E5M2`
  entry (`crates/rustinfer-artifact/src/safetensors.rs:56-67`), so an E5M2
  weight is refused as an unknown dtype. That is by design: SRS v0.4.6 adds
  no "KV dtype, kernel or checkpoint dtype" (`docs/SRS-RI-v0.1.md:29`).

## Requirements of the SRS not yet on `origin/main`

| SRS requirement | what needs E4M3 | where it is |
|---|---|---|
| RI-KC-003 | OCP fp8 MFMA operands on gfx950 | PR #44 (issue #8), open |
| RI-KVC-008 | `--kv-dtype fp8`: E4M3 KV on gfx950 and cpu, written by the cache-write kernel | CPU reference merged (PR #48, `e218b8a`); GPU kernels issue #38 |
| RI-MIR-012, RI-CLI-002 | `--activations mxfp8`: in-kernel E4M3 activation quantization on gfx950 | issue #38, no PR |

These are recorded as OFP8-3: the conversions they perform must meet R5 to
R10, and bit-exact agreement with the CPU reference is their acceptance test.
No requirement needs E5M2 on a GPU in R1.

## Result

The E4M3 encoding (R1 to R3) and the E5M2 encoding (R12 to R14), and
saturating conversion to both (R4 to R11 and R15 to R18, in the
saturating-only scope of SRS v0.4.3), conform and are tested; E5M2 against an
independent integer-only golden table of all 256 codes and 758 rounding
cases. The non-saturating mode (OFP8-1) is out of scope. The one open gap is
coverage: the gfx950 fp8 MFMA (PR #44) and the GPU KV and `mxfp8` kernels
(#38) are not on `origin/main` (OFP8-3). **Partial**, for the R1 coverage,
not for any wrong value.
