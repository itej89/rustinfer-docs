---
title: "IEEE 754-2019 requirements"
navtitle: Requirements
section: Standards
group: "Number formats / IEEE 754-2019"
order: 11
summary: The binary16 and binary32 items in scope, each taken from a named secondary source because the standard itself is paywalled.
---

# IEEE 754-2019 requirements

**The standard is paywalled and was not obtained.** No clause of IEEE Std
754-2019 is quoted here from the standard itself, and no clause number is
given unless a secondary source states it. Every item below is marked with
the secondary source it is taken from:

- **[SA]** the IEEE SA abstract page of 754-2019 (`specs/number-formats/ieee754-abstract.html`).
- **[WG]** the IEEE 754 working group's public note *Conformance and options*
  (`specs/number-formats/ieee754-conformance-and-options.txt`, from
  <https://grouper.ieee.org/groups/msc/ANSI_IEEE-Std-754-2019/background/>).
- **[LLVM]** LLVM APFloat at `llvmorg-23.1.0`: `semIEEEhalf = {15, -14, 11, 16}`
  and `semIEEEsingle = {127, -126, 24, 32}` (maximum exponent, minimum
  exponent, precision with the hidden bit, size in bits; `APFloat.cpp:71`,
  `:73`; the field meanings at `APFloat.h:1005-1016` say they "match the
  definition of IEEE 754"); `fltNonfiniteBehavior::IEEE754` (`APFloat.h:959-963`);
  `IEEEFloat::handleOverflow` (`APFloat.cpp:1490`).
- **[MX]** OCP MX v1.1 §4.1, which defines Float32 as "Binary32 format defined
  in the IEEE Standard for Floating-Point Arithmetic" and roundTiesToEven as
  "a method for rounding to nearest, where ties are broken by rounding them to
  the value with an even least-significant digit. See IEEE Standard for
  Floating-Point Arithmetic [4], Section 4.3.1".
- **[OFP8]** OCP OFP8 Revision 1.1 §4 and §4.1, which name binary16 and
  binary32 as IEEE formats and take the terms subnormal, NaN and trailing
  significand field from IEEE 754.
- **[AMD]** the FP16 row of Table 30, AMD CDNA3 ISA guide §7.2: "E5M10, bias
  15, +0 0x0000, -0 0x8000, INF 0x7C00, -INF 0xFC00, max 65504, min (norm)
  6.10352E-05, min (denorm) 5.96046E-08".

The abstract [SA] states the standard "specifies interchange and arithmetic
formats and methods for binary and decimal floating-point arithmetic" and
"exception conditions and their default handling". Our scope is the binary16
and binary32 interchange encodings, their NaN and Inf, and conversion with
roundTiesToEven.

| item | requirement | source |
|---|---|---|
| IEEE-R1 | **binary16 encoding.** 1 sign bit, 5 exponent bits with bias 15, 10 trailing significand bits; emax 15, emin −14, precision 11; largest finite 65504, smallest normal 2^−14, smallest subnormal 2^−24. | [LLVM] `semIEEEhalf`; [AMD] Table 30 |
| IEEE-R2 | **binary32 encoding.** 1 sign bit, 8 exponent bits with bias 127, 23 trailing significand bits; emax 127, emin −126, precision 24. | [LLVM] `semIEEEsingle`; [MX] §4.1 |
| IEEE-R3 | **Subnormals.** An encoding with a zero exponent field and a non-zero trailing significand is subnormal: magnitude 2^emin × (0 + M × 2^(1−p)). | [OFP8] §4.1 (term from IEEE 754); [MX] §4.1 definition of subnormal; [AMD] min (denorm) |
| IEEE-R4 | **Signed zeros.** +0 and −0 are distinct encodings (binary16 0x0000 and 0x8000). | [AMD] Table 30 |
| IEEE-R5 | **Infinities.** An all-ones exponent field with a zero trailing significand is ±Inf (binary16 0x7C00 and 0xFC00). | [LLVM] `fltNonfiniteBehavior::IEEE754`: "A value is nonfinite if the exponent field is all 1s. In such cases, a value is Inf if the significand bits are all zero, and NaN otherwise"; [AMD] Table 30 |
| IEEE-R6 | **NaNs.** An all-ones exponent field with a non-zero trailing significand is NaN, of either sign. A conversion of a NaN delivers a NaN; a converted signalling NaN delivers a quiet NaN. | [LLVM] as IEEE-R5, and `IEEEFloat::convert` (`APFloat.cpp:2450`), which returns `opInvalidOp` for a signalling source and makes the result quiet |
| IEEE-R7 | **roundTiesToEven conversion.** A conversion to a narrower format rounds to the nearest representable value; a tie goes to the value with an even least significant digit. | [MX] §4.1, citing IEEE 754-2019 §4.3.1 |
| IEEE-R8 | **Overflow under roundTiesToEven** delivers ±Inf, with the sign of the source. | [LLVM] `handleOverflow`: "Sign is preserved. We either become infinity or the largest finite number", infinity for `rmNearestTiesToEven` |
| IEEE-R9 | **Widening is exact.** Every binary16 value is a binary32 value, so binary16 to binary32 is exact. | [LLVM] the two semantics: binary32's precision and exponent range contain binary16's |

## Outside the scope

Exception flags and their default handling, the other rounding-direction
attributes, arithmetic operations, NaN payload propagation, binary64 and
wider, and the decimal formats. The working group note [WG] says new 2019
features are "always recommended rather than required" (for example
minimum/maximum operations); none is in scope.
