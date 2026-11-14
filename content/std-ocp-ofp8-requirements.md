---
title: "OCP OFP8 Revision 1.1 requirements"
navtitle: Requirements
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 21
summary: What OFP8 Revision 1.1 requires of the E4M3 and E5M2 encodings and of conversion to them, the parts in rustinfer's scope.
---

# OCP OFP8 Revision 1.1 requirements

Source: `specs/number-formats/ocp-ofp8-rev1.1.pdf` (*OCP 8-bit Floating Point
Specification (OFP8), Revision 1.1*, effective June 22, 2026). Sections
cited are those of that document. Scope (SRS §1.4 on `origin/main` since
v0.4.3, PR #50): "the E4M3 and E5M2 encodings with saturating conversion
(roundTiesToEven) only; the non-saturating mode of Revision 1.1 section 5.2.1
is out of scope" (owner decision 2026-11-13). OFP8-R1 to R11 are those of
E4M3, the format of RI-MIR-003's `fp8`, RI-CLI-002, RI-KC-003 and
RI-KVC-008. OFP8-R12 to R18 are those of E5M2, which RI-MIR-003 adds as the
dtype `fp8_e5m2` since SRS v0.4.6 (PR #55, issue #51, owner decision
2026-11-13: implement E5M2); no kernel, KV dtype or checkpoint dtype of R1
reads it.

The specification defines formats and conversion only. §4 puts out of scope
conversion between OFP8 and other 8-bit formats or integers, arithmetic, and
"scaling factor selection, representation, or maintenance". §5.2.1: "The
specification does not require any exception handling during these
conversions, nor does it require using status flags for exceptions."

## The E4M3 encoding (§4.2, §5.1, Tables 1 and 2)

| item | requirement | section |
|---|---|---|
| OFP8-R1 | E4M3 is "1 sign bit, 4 biased exponent bits, 3 mantissa bits, and an exponent bias of 7"; the sign is the most significant bit. emax 8, emin −6. | §4.2, §5.1, Table 1 |
| OFP8-R2 | A normal value is v = (−1)^S × 2^(E−bias) × (1 + 2^−m × M); a subnormal (E = 0, M > 0) is v = (−1)^S × 2^(1−bias) × (0 + 2^−m × M). | §5.1 |
| OFP8-R3 | "The E4M3 format does not represent infinities and uses only two bit patterns for NaN (a single mantissa-exponent bit pattern but allowing both values of the sign bit)": NaN is S.1111.111. Zeros are S.0000.000. Max normal S.1111.110 = ±448; min normal S.0001.000 = ±2^−6; max subnormal S.0000.111 = ±0.875 × 2^−6; min subnormal S.0000.001 = ±2^−9. | §5.1, Table 2 |

## Conversion to E4M3 (§5.2.1, Table 3)

| item | requirement | section |
|---|---|---|
| OFP8-R4 | Conversion is defined "from wider floating point types (IEEE binary32, binary16 [1] ...; bfloat16 [2]) to OFP8 formats". | §5.2.1 |
| OFP8-R5 | "This specification requires implementation of Round-to-Nearest-Ties-to-Even mode." | §5.2.1 |
| OFP8-R6 | "This specification requires implementation of saturating and non-saturating modes." | §5.2.1 |
| OFP8-R7 | "Conversion from a NaN produces an implementation-defined OFP8 NaN." | §5.2.1, Table 3 |
| OFP8-R8 | ±Inf converts to ±max_E4M3 in saturating mode and to NaN in non-saturating mode. | §5.2.1, Table 3 |
| OFP8-R9 | "If a normal source value rounded to the precision of the destination OFP8 format exceeds the max destination magnitude": saturating mode generates "the max normal OFP8 magnitude"; non-saturating mode, for an E4M3 destination, generates a NaN. | §5.2.1, Table 3 |
| OFP8-R10 | "Otherwise, the source value rounded to a destination format OFP8 value shall be generated." "The sign bit of the source value is preserved except in the cases where a NaN is produced." | §5.2.1 |
| OFP8-R11 | Consequence of R5 at the top of the range: 448 has an even mantissa LSB, so "source format magnitudes up to and including 1/2 an ULP greater (i.e. 448 < x <= 464) round down to 448". | Appendix A (non-normative, §1 Notes) |

OFP8-R6 requires both modes of every implementation. The SRS uses only the
saturating mode (RI-KVC-008's fp8 KV, RI-MIR-012's `mxfp8` elements), and
since v0.4.3 (PR #50, owner decision 2026-11-13) its Scope phrase is
"saturating conversion (roundTiesToEven) only". R6 is therefore in scope for
its saturating mode only, and the non-saturating halves of R8 and R9 are out
of scope: rustinfer claims conformance to saturating conversion, a documented
deviation from §5.2.1's "requires ... saturating and non-saturating modes".

## The E5M2 encoding (§3, §4.2, §5.1, Tables 1 and 2)

| item | requirement | section |
|---|---|---|
| OFP8-R12 | "E5M2: An OFP8 format with 1 sign bit, 5 biased exponent bits, 2 mantissa bits, and an exponent bias of 15." emax 15, emin −14. | §3, §4.2, Table 1 |
| OFP8-R13 | The value formulas of OFP8-R2 with bias 15 and m = 2: a normal value is (−1)^S × 2^(E−15) × (1 + M/4), a subnormal (E = 0, M > 0) (−1)^S × 2^−14 × (M/4). | §5.1 |
| OFP8-R14 | "The E5M2 format represents infinities and NaNs. Interpretation of the three mantissa values for NaNs is not defined." Infinities S.11111.00; NaN S.11111.{01, 10, 11}; zeros S.00000.00; max normal S.11110.11 = ±57,344; min normal S.00001.00 = ±2^−14; max subnormal S.00000.11 = ±0.75 × 2^−14; min subnormal S.00000.01 = ±2^−16. | §5.1, Table 2 |

## Conversion to E5M2 (§5.2.1, Table 3, Appendix A)

| item | requirement | section |
|---|---|---|
| OFP8-R15 | OFP8-R4 and R5 for an E5M2 destination: conversion from binary32, binary16 and bfloat16 with Round-to-Nearest-Ties-to-Even. | §5.2.1 |
| OFP8-R16 | "Conversion from a NaN produces an implementation-defined OFP8 NaN"; ±Inf gives ±max_E5M2 in saturating mode (±Inf in non-saturating mode, out of scope). | §5.2.1, Table 3 |
| OFP8-R17 | A value that rounded to E5M2 precision exceeds 57,344 gives "the max normal OFP8 magnitude" in saturating mode (an infinity in non-saturating mode, out of scope); otherwise the rounded value, the sign of the source preserved. | §5.2.1, Table 3 |
| OFP8-R18 | "The maximum finite magnitude (57,344) has an odd mantissa LSB in its binary representation (S.11110.11). Therefore, a value with 1/2 an ULP greater (61,440) rounds up resulting in overflow (or saturation)": 57,344 < x < 61,440 rounds to 57,344, and 61,440 saturates to it. | Appendix A |

The saturating-only scope of OFP8-R6 applies to E5M2 as to E4M3: SRS
RI-MIR-003 (v0.4.6) requires conversion to `fp8_e5m2` to "saturate: a value
whose rounded magnitude exceeds 57344, and ±Inf, give ±57344".
