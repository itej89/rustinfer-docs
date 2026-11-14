---
title: "OCP MX v1.1.0 requirements"
navtitle: Requirements
section: Standards
group: "Number formats / OCP MX v1.1.0"
order: 41
summary: What OCP MX v1.1 requires of MXFP4 blocks, the E2M1 and UE8M0 types and the §6.3 conversion, the parts in rustinfer's scope.
---

# OCP MX v1.1.0 requirements

Source: `specs/number-formats/ocp-mx-v1.1.0.pdf` (*OCP MicroXcaling (MX)
Specification, Version 1.1*, October 9, 2026). Sections, tables and equations
cited are those of that document. Word usage (§4.2): "must" is required,
"should" recommended, "may" optional.

Scope: MXFP4 only (SRS §1.4). MXFP8, MXFP6 and MXINT8 are outside it, and so
are the dot products of §6.1 and §6.2. §3.1 puts out of scope the FP8
encodings (taken from OFP8), "binary encodings for the element when the block
scale is NaN", "detailed algorithms for computing the block scale" and the
memory layout of a block (§5.1: "The layout of the block in physical memory is
not prescribed").

## Blocks and MXFP4 (§5.1, §5.2)

| item | requirement | section |
|---|---|---|
| MX-R1 | A block is a scale X shared by k elements P_i. Its values: "If X = NaN, then v_i = NaN for 1 ≤ i ≤ k regardless of P_i"; if X·P_i is beyond ±VmaxFloat32, v_i "is implementation-defined"; otherwise v_i = X·P_i. | §5.1 |
| MX-R2 | MXFP4 is FP4 (E2M1) elements, d = 4, block size k = 32, UE8M0 scale, w = 8. "For each supported format, an implementation must support the parameters listed in Table 1." | §5.2, Table 1, §5.2.1 |

## E2M1 elements (§5.3, §5.3.3)

| item | requirement | section |
|---|---|---|
| MX-R3 | E2M1: bias 1, no Inf, no NaN; zeros S 00 0; max normal ±6.0; min normal ±1.0; subnormal ±0.5. Value: E > 0 gives (−1)^S × 2^(E−bias) × (1 + 2^−m × M); E = 0 gives (−1)^S × 2^(1−bias) × (0 + 2^−m × M). "FP4 implementations must adhere to the table below, with support for subnormals." | §5.3, §5.3.3, Table 5 |
| MX-R4 | "An implementation must support the roundTiesToEven rounding mode for converting values to FP4." | §5.3.3 |
| MX-R5 | If a value exceeds the FP4 range after rounding with unbounded exponent, "an implementation must support clamping (saturating) the value to the maximum FP4 magnitude, preserving the sign". "Out-of-range values can be normal numbers or Infs in a wider data format." | §5.3.3 |
| MX-R6 | "Conversion from NaNs is implementation-defined." | §5.3.3 |

## UE8M0 scales (§5.4.1)

| item | requirement | section |
|---|---|---|
| MX-R7 | UE8M0: exponent bias 127, exponent range −127 to 127, no Inf, no zero, one NaN 11111111. | §5.4.1, Table 7 |

## Conversion to MX (§6.3)

| item | requirement | section |
|---|---|---|
| MX-R8 | "A mechanism must be provided for converting a k-length vector V of scalar elements to an MX-compliant format {X, [P_i]} by producing the block scale X and the elements P_i." | §6.3 |
| MX-R9 | Equation 1 for X, with SF(V) = 2^(⌊log2 max\|V_i\|⌋ − maxExp + expAdj(V)), max as IEEE 754-2019 maximum, SFmax 2^127 and SFmin 2^−127 for UE8M0: if all V_i are zero, X is "non-NaN implementation-defined"; "If the scalar-values of V include a NaN or Infinity value, the value of X is NaN"; if SF(V) > SFmax, X is implementation-defined; "If SF(V) is smaller than the minimum representable value in the scale data type, it is set to the minimum representable value"; "Otherwise, X = SF(V)". | §6.3, Equation 1 |
| MX-R10 | expAdj(V) ∈ {0, 1} "may be used"; the SRS mandates Equation 4: 1 if ⌊log2 round(max\|V_i\|)⌋ > ⌊log2 max\|V_i\|⌋, "where round(·) signifies rounding to the destination precision, with unbounded exponent"; 1 for FP8 E4M3 if round(max\|V_i\|) is 1.875 × 2^n; else 0. For E2M1 the first case is max\|V_i\| ≥ 1.75 × 2^⌊log2 max⌋. | §6.3, Equation 4; SRS RI-MIR-012 |
| MX-R11 | "Set P_i to be the scaled inputs V_i / X quantized to the element data type. For this quantization, normal numbers that exceed the max normal representation of the element data type should be clamped to the max normal, preserving the sign. If the scale factor, X, is NaN, the private elements, P_i, in the block are implementation-defined." | §6.3, step 2 |
| MX-R12 | "For quantization to the element data type, implementations must support roundTiesToEven as a rounding mode." | §6.3 |
| MX-R13 | "An input of ±Inf results in a NaN block scale factor, even in SAT rounding mode for FP8 scalar formats." | §6.3, footnote 1 |

The semantics of §6.3 are stated as "at least the following semantics should
be supported", and "other algorithms ... may be supported". RI-MIR-012 turns
them, with Equation 4, into a requirement, and fixes the implementation-defined
cases: scale 0x7F and codes 0x0 for an all-zero block, 0xFF and codes 0x0 for
a NaN or Inf block, the clamp at s = 127.
