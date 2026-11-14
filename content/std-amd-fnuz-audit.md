---
title: "AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025) audit"
navtitle: Audit
section: Standards
group: "Number formats / AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
order: 32
summary: The 2026-11-13 audit of rustinfer's FP8 E4M3 FNUZ encoding against the CDNA3 ISA guide and LLVM APFloat; the encoding conforms.
---

# AMD FP8 FNUZ audit

**Audit of 2026-11-13**, against the [requirements](std-amd-fnuz-requirements.html).

**Method.** Read §7.2 of the ISA guide (`pdftotext -layout` of
`specs/number-formats/amd-cdna3-isa.pdf`, pages 50 and 51) and LLVM APFloat
at `llvmorg-23.1.0` (`semFloat8E4M3FNUZ`, `fltNonfiniteBehavior`,
`fltNanEncoding`, `handleOverflow`, `convert`). Read `origin/main` at
`ccf02b3`: `crates/rustinfer-target/src/numeric.rs`,
`crates/rustinfer-mir/src/dtype.rs`, `crates/rustinfer-kc/src/dialect/types.rs`,
`crates/rustinfer-kc/src/mlir/lower.rs`, and the tests in
`crates/rustinfer-target/tests/numeric.rs`. Read the SRS on branch
`docs/srs-standards-conformance` (v0.4.3, open PR #50) and the descriptions of
open PRs #44 and #48. No tests were run.

**Test tags.** `tests/numeric.rs` tags `Verifies RI-MIR-003` and `Verifies
RI-TGT-003`.

**The exhaustive check.** `test_every_fp8_pattern_round_trips`
(`tests/numeric.rs:140`) decodes all 256 FNUZ patterns and requires each
non-NaN one to encode back to itself. Since the encoder gives 0x80 only for a
NaN, and 0x00 for every zero (`numeric.rs:141-146`), the test proves that 0x80
is the only pattern decoding to NaN, and that 0x00 to 0x7F and 0x81 to 0xFF
decode to 255 distinct values the encoder maps back to them. Together with
the explicit assertion that 0x7F is 240, no pattern is an infinity.

| item | requirement | result | evidence |
|---|---|---|---|
| FNUZ-R1 | S1E4M3, bias 8 | conforms | `MiniFloat::E4M3FNUZ` 4 exponent bits, 3 mantissa bits, bias 8 (`numeric.rs:57-64`). Asserted: 1.0 is 0x40 (`tests/numeric.rs:122-123`) |
| FNUZ-R2 | IEEE-like values; min normal 2^−7, min subnormal 2^−10 | conforms | the shared decode, `min_exponent` 1 − 8 = −7 (`numeric.rs:79-81`, `:103-108`). Asserted: 2^−10 round-trips, −3.5 round-trips (`tests/numeric.rs:130-134`). Min normal 2^−7 is not asserted by value; it follows from the formula and the exhaustive round trip |
| FNUZ-R3 | no infinity | conforms | `special` returns a value only for the NaN pattern when `fnuz` (`numeric.rs:113-115`); exponent 15 decodes as a normal binade |
| FNUZ-R4 | one zero, no negative zero | conforms | a zero result is 0x00 whatever the sign (`numeric.rs:141-146`). Asserted: −0.0 encodes to 0 (`tests/numeric.rs:129`). A negative value that rounds to zero takes the same branch |
| FNUZ-R5 | one NaN, 0x80 | conforms | decode: only `bits == 0x80` is NaN (`numeric.rs:113-114`); encode: a NaN gives 0x80 (`:21`, `:132-133`). Asserted (`tests/numeric.rs:127-128`) and by the exhaustive round trip |
| FNUZ-R6 | max 240 | conforms | `max` uses all-ones exponent and mantissa when `fnuz` (`numeric.rs:87-88`). Asserted: 240 is 0x7F and decodes to 240 (`tests/numeric.rs:121`, `:124-125`), `test_format_maxima` (`numeric.rs:336`) |

## Other users of FNUZ on `origin/main`

- The Kernel IR's `max` identity for `f8E4M3FNUZ` is 0xFF, S.1111.111 =
  −240, the most negative FNUZ value (`crates/rustinfer-kc/src/mlir/lower.rs:25`).
  Correct by FNUZ-R6; no test asserts the constant (FNUZ-1).

## Conversion behaviour, outside the scope

Recorded for the gfx942 work, not judged:

- The CPU reference rounds to nearest even and **saturates**: overflow and
  ±Inf give ±240 (`numeric.rs:137-139`, `:161-168`; asserted for 1e9,
  `tests/numeric.rs:126`). This is the ISA's FP16_OVFL = 1 column, not the
  FP16_OVFL = 0 column (NaN), and not LLVM APFloat's conversion, which gives
  NaN on overflow under round-to-nearest (`APFloat.cpp:1490-1503`).
- RI-KVC-008 requires the cached K and V to equal the CPU reference
  bit-exactly. A gfx942 cache-write kernel therefore has to saturate the same
  way: run its `V_CVT_PK_FP8_F32` with FP16_OVFL = 1, or clamp to ±240 before
  converting, and not rely on MLIR constant folding (APFloat semantics) for
  out-of-range values. This belongs to issue #37 and #38.

## Requirements of the SRS not yet on `origin/main`

| SRS requirement | what needs FNUZ | where it is |
|---|---|---|
| RI-KC-003 | fp8 FNUZ MFMA operands on gfx942 | PR #44 (issue #8), open |
| RI-KVC-008 | `--kv-dtype fp8` on gfx942: FNUZ KV written by the cache-write kernel, read by attention | PR #48 (issue #37), open: configuration and CPU reference; GPU kernels issue #38 |

Recorded as FNUZ-2.

## Result

Every in-scope item conforms on `origin/main`. One constant is right but
untested (FNUZ-1), and the gfx942 users of the encoding are still in open PRs
(FNUZ-2). **Partial**, for the R1 coverage, not for any wrong encoding.
