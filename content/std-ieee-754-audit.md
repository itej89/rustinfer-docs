---
title: "IEEE 754-2019 audit"
navtitle: Audit
section: Standards
group: "Number formats / IEEE 754-2019"
order: 12
summary: The 2026-11-13 audit of the CPU reference's binary16 and binary32 handling against secondary sources; every in-scope item conforms.
---

# IEEE 754-2019 audit

**Audit of 2026-11-13**, against the [requirements](std-ieee-754-requirements.html).

**Method.** Read `origin/main` at `ccf02b3`: `crates/rustinfer-mir/src/dtype.rs`,
`crates/rustinfer-target/src/numeric.rs`, `crates/rustinfer-target/src/cpu/codec.rs`
and the tests in `crates/rustinfer-target/tests/numeric.rs`. Read the SRS on
branch `docs/srs-standards-conformance` (v0.4.3, open PR #50): §1.4 row
IEEE-754, RI-MIR-003, RI-TGT-003. Checked each item against the secondary
sources named on the requirements page; the standard itself was not
available. Open PRs #44, #48 and #49 do not change `numeric.rs` or `codec.rs`.
No tests were run: the tests read are exhaustive over binary16 and their
assertions are stated below.

**Test tags.** The tests cited carry `Verifies RI-MIR-003` or `Verifies
RI-TGT-003` (rule of `docs/testing.md`).

**A note on the round-trip test.** `test_every_half_pattern_round_trips`
(`tests/numeric.rs:158`) decodes all 65,536 binary16 patterns and requires
each one that does not decode to NaN to encode back to itself. A NaN pattern
that decoded to a number would then have to encode back to a NaN pattern,
which the encoder never produces from a number, so the test also proves that
every NaN pattern decodes to NaN, and every finite and infinite pattern decodes
to the value the encoder maps back to it.

| item | requirement | result | evidence |
|---|---|---|---|
| IEEE-R1 | binary16 layout and parameters | conforms | `MiniFloat::FP16` 5 exponent bits, 10 mantissa bits, bias 15, IEEE specials (`numeric.rs:41-48`); value formula `numeric.rs:96-110`. `test_format_maxima` (`numeric.rs:336`) asserts the maximum 65504; `test_fp16_round_trips_subnormals_and_overflows_to_infinity` (`tests/numeric.rs:65`) asserts 1.0 is 0x3C00, 65504 exact and 2^−24 exact; the exhaustive round trip covers every pattern |
| IEEE-R2 | binary32 layout and parameters | conforms | `fp32` is Rust `f32` (`dtype.rs:21-23`), which the Rust language defines as binary32; `codec.rs:62` and `:74` read and write it as little-endian `f32` bits. Nothing in rustinfer re-implements binary32 |
| IEEE-R3 | subnormals | conforms | decode with a zero exponent field: `M × 2^(emin − 10)` (`numeric.rs:103-104`); encode below the normal range on the 2^−24 grid (`numeric.rs:156-158`, `:173-176`). Asserted: 2^−24 round-trips, 2^−25 (a tie with zero) gives 0 (`tests/numeric.rs:71-75`) |
| IEEE-R4 | signed zeros | conforms | the sign bit is kept for a zero result (`numeric.rs:141-146`, `fnuz` false for fp16). Asserted: −0.0 round-trips with its sign bit (`tests/numeric.rs:83-86`) |
| IEEE-R5 | infinities | conforms | all-ones exponent and zero mantissa decode to ±Inf (`numeric.rs:116-125`); ±Inf encodes to 0x7C00 or 0xFC00 (`numeric.rs:153-154`, `:161-164`). Asserted: 1e6 converts to Inf (`tests/numeric.rs:70`); 0x7C00 and 0xFC00 round-trip in the exhaustive test |
| IEEE-R6 | NaNs; a converted NaN is a quiet NaN | conforms | all-ones exponent and non-zero mantissa decode to NaN, either sign (`numeric.rs:125`); a NaN encodes to 0x7E00 (`numeric.rs:17`, `:132-133`), a quiet NaN, so a signalling source is quieted. Asserted: NaN converts to a NaN (`tests/numeric.rs:82`); every NaN pattern decodes to NaN (the exhaustive test, above). The payload and sign of a NaN are not kept; payload propagation is outside the scope |
| IEEE-R7 | roundTiesToEven conversion | conforms | the magnitude is divided by the grid quantum and rounded with `round_ties_even` (`numeric.rs:152-159`), exact in `f64`. Asserted: 1 + 2^−11 (a tie) gives 1.0, 1 + 3 × 2^−11 gives 1 + 2^−9 (`tests/numeric.rs:76-80`) |
| IEEE-R8 | overflow gives ±Inf with the sign | conforms | a rounded magnitude above 65504 takes the overflow branch, the all-ones exponent with the sign (`numeric.rs:138-139`, `:161-168`). Asserted: 65520, the tie between 65504 and 2^16, gives 0x7C00 (`tests/numeric.rs:69`) |
| IEEE-R9 | binary16 to binary32 is exact | conforms | `fp16_to_f32` computes the value in `f64` and narrows a value every binary16 holds exactly (`numeric.rs:218-227`, `:292-294`); the exhaustive round trip asserts it for every pattern |

## Related check: `bf16`

Not an IEEE 754 item. `f32_to_bf16` (`numeric.rs:268-276`) adds `0x7FFF` plus
the lowest kept bit and truncates, which is roundTiesToEven on the top 16 bits
of binary32, including overflow to ±Inf; a NaN keeps its sign and top bits and
gets the quiet bit (`:271-273`). `test_bf16_round_trips_and_rounds_to_nearest_even`
(`tests/numeric.rs:41`) asserts the ties and Inf, NaN and −0;
`test_every_half_pattern_round_trips` covers every `bf16` pattern.

## Result

Every in-scope item conforms on `origin/main`. All the code is in the CPU
reference, which is where the citing requirements (RI-MIR-003, RI-TGT-003)
place it. No gap is recorded. The audit's limit is its source: the items were
checked against secondary sources, not the standard's text.
