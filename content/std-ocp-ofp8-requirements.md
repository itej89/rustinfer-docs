---
title: "OCP OFP8 Revision 1.1 requirements"
navtitle: Requirements
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 21
summary: What OFP8 Revision 1.1 requires of the E4M3 encoding and of conversion to it, the parts in rustinfer's scope.
---

# OCP OFP8 Revision 1.1 requirements

Source: `specs/number-formats/ocp-ofp8-rev1.1.pdf` (*OCP 8-bit Floating Point
Specification (OFP8), Revision 1.1*, effective June 22, 2026). Sections
cited are those of that document. Scope: E4M3 only (SRS §1.4); E5M2 is
outside it.

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
saturating mode (RI-KVC-008's fp8 KV, RI-MIR-012's `mxfp8` elements), but its
Scope phrase covers "conversion rounding and saturation" without narrowing
the modes, so R6 is in scope.
