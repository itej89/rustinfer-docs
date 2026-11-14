---
title: "OCP OFP8 Revision 1.1"
navtitle: Overview
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 20
summary: The OCP E4M3 and E5M2 8-bit floats and conversion to them, rounding and saturation, as the Model IR, the CPU reference and the Kernel IR use them.
---

# OCP OFP8 Revision 1.1

**Scope (SRS §1.4, OCP-OFP8, v0.4.3):** the E4M3 and E5M2 encodings with
saturating conversion (roundTiesToEven) only; the non-saturating mode of
Revision 1.1 §5.2.1 is out of scope (owner decision 2026-11-13, PR #50). The
requirements that cite it are RI-MIR-003 (the `fp8` dtype, OCP E4M3, and since
SRS v0.4.6 the `fp8_e5m2` dtype, OCP E5M2, PR #55), RI-CLI-002
(`fp8` and `mxfp8` elements are OCP E4M3), RI-KC-003 (OCP fp8 MFMA on gfx950)
and RI-KVC-008 (`--kv-dtype fp8` is OCP E4M3 on gfx950 and cpu). RI-MIR-012
uses E4M3 as the element of `mxfp8` activation quantization.

**Implementation:**

- The dtypes `fp8_e4m3` (`crates/rustinfer-mir/src/dtype.rs:24-26`) and,
  since PR #55 (merge `6a18042`), `fp8_e5m2`, quantized, read by no `matmul`
  or KV write (`dtype.rs:30-35`, `:84-94`).
- The CPU reference codec, `crates/rustinfer-target/src/numeric.rs`: the format
  rows `MiniFloat::E4M3` (bias 7, no infinity, `:60-68`) and `MiniFloat::E5M2`
  (bias 15, Inf and NaN, saturating, `:78-88`), the NaNs `0x7F` and `0x7E` and
  the maxima 448 and 57344 (`:19-29`), decode (`:120-152`), encode with
  roundTiesToEven and saturation (`:155-192`), and `f32_to_fp8` and
  `fp8_to_f32` (`:327-337`). Both saturate, as the narrowed scope requires;
  ±Inf to ±448 is asserted (`crates/rustinfer-target/tests/numeric.rs:186`),
  and E5M2 is checked against an independent integer-only golden table of all
  256 codes and 758 rounding cases (`crates/rustinfer-target/tests/e5m2.rs`).
  The CPU `quantize` and `dequantize` kernels take both (`src/cpu/codec.rs:60-83`).
- The MX reference uses the same encoder for E4M3 elements
  (`crates/rustinfer-target/src/reference/mx.rs:106-118`).
- The Kernel IR names the type `f8E4M3FN` (`crates/rustinfer-kc/src/dialect/types.rs:19-20`)
  and uses 0xFE (−448) as the identity of a `max` reduction
  (`crates/rustinfer-kc/src/mlir/lower.rs:19-28`), asserted by
  `test_max_identity_of_ocp_e4m3_is_minus_448` (`lower.rs:441`).
- The fp8 KV CPU reference (PR #48): the cache write quantizes with
  `f32_to_fp8` (`crates/rustinfer-target/src/reference/kv.rs:263-285`).
- Pending: the gfx950 OCP fp8 MFMA (PR #44, issue #8), and the GPU fp8 KV and
  in-kernel `mxfp8` activation quantization kernels (issue #38).

**Conformance:** mandatory from **R1**.

**Source:** `specs/number-formats/ocp-ofp8-rev1.1.pdf`, *OCP 8-bit Floating
Point Specification (OFP8), Revision 1.1*, effective June 22, 2026 (version
table entry January 29, 2026), Open Compute Project,
<https://www.opencompute.org/documents/ocp-8-bit-floating-point-specification-ofp8-revision-1-1-final-pdf/>.
Revision 1.0 as corrected 2023-12-01 was also read
(`specs/number-formats/ocp-ofp8-rev1.0-2023-12-01.pdf`). Both downloaded
2026-11-13. Revision 1.1 "adjusts the conversion description in Section 5.2
and adds Appendix A".

| | |
|---|---|
| Pages | [requirements](std-ocp-ofp8-requirements.html) · [audit](std-ocp-ofp8-audit.html) · [tracker](std-ocp-ofp8-tracker.html) |
| Conformance | mandatory R1 (RI-MIR-003 for E4M3 and E5M2, RI-CLI-002, RI-KC-003, RI-KVC-008) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and its tests against the specification text; re-audited at `b99720a` after PRs #48, #50 and #52, and on 2026-11-14 at `8c7d47e` after PR #55 (E5M2) |
| Result | the E4M3 and E5M2 encodings, roundTiesToEven and saturating conversion conform and are tested; the non-saturating mode is out of scope (PR #50); the GPU users are pending (PR #44, #38) |
| Open gaps | 1 |
