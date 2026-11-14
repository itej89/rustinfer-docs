---
title: "IEEE 754-2019"
navtitle: Overview
section: Standards
group: "Number formats / IEEE 754-2019"
order: 10
summary: The binary16 and binary32 encodings, their NaN and infinity rules and roundTiesToEven conversion, as the CPU reference implements them.
---

# IEEE 754-2019

**Scope (SRS §1.4, IEEE-754):** binary16 and binary32 encodings, NaN and Inf,
roundTiesToEven conversion. The requirements that cite it are RI-MIR-003
(`fp16` is binary16 and `fp32` is binary32; the CPU reference converts with
roundTiesToEven) and RI-TGT-003 (the oracle's `fp32` is binary32 and its
conversions round ties to even).

**Implementation:** the CPU reference in `rustinfer-target`.

- `fp32` is Rust's `f32`, which is binary32. The dtype is declared in
  `crates/rustinfer-mir/src/dtype.rs:21-23` ("IEEE single").
- `fp16` is declared in `crates/rustinfer-mir/src/dtype.rs:18-20` ("IEEE
  half"). Its codec is `crates/rustinfer-target/src/numeric.rs`: the format
  row `MiniFloat::FP16` (`:41-48`), decode (`:96-128`), encode with
  roundTiesToEven and overflow to infinity (`:131-168`), and the public
  `f32_to_fp16` and `fp16_to_f32` (`:286-294`).
- The operand codec of the CPU target, `crates/rustinfer-target/src/cpu/codec.rs:60-81`,
  decodes every float dtype exactly to `f32` and encodes results with these
  functions.

`bf16` is not an IEEE 754 format. The SRS defines it as binary32 with the low
16 mantissa bits dropped; `f32_to_bf16` (`numeric.rs:268-276`) rounds ties to
even and keeps NaN a NaN. It is listed in the audit as a related check only.

**Conformance:** mandatory from **R1**.

**Source:** IEEE Std 754-2019, *IEEE Standard for Floating-Point Arithmetic*,
published 2019-07-22, <https://standards.ieee.org/ieee/754/6210/>. **The
standard is paywalled and was not obtained.** The requirements are taken only
from freely available secondary sources, each marked as such: the IEEE SA
abstract page (`specs/number-formats/ieee754-abstract.html`), the IEEE 754
working group's public background notes
(`specs/number-formats/ieee754-conformance-and-options.txt`), LLVM APFloat at
`llvmorg-23.1.0` (`specs/number-formats/llvm-23.1.0-APFloat.h` and `.cpp`),
the definitions of OCP MX v1.1 §4.1 and OCP OFP8 Revision 1.1 §4, and the FP16
row of Table 30 of the AMD CDNA3 ISA guide. All downloaded 2026-11-13.

| | |
|---|---|
| Pages | [requirements](std-ieee-754-requirements.html) · [audit](std-ieee-754-audit.html) · [tracker](std-ieee-754-tracker.html) |
| Conformance | mandatory R1 (RI-MIR-003, RI-TGT-003) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and its tests, against secondary sources |
| Result | every in-scope item conforms; exhaustive round-trip tests cover all 65,536 binary16 patterns |
| Open gaps | 0 |
