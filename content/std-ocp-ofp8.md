---
title: "OCP OFP8 Revision 1.1"
navtitle: Overview
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 20
summary: The OCP E4M3 8-bit float and its conversion rounding and saturation, as the CPU reference and the Kernel IR use them.
---

# OCP OFP8 Revision 1.1

**Scope (SRS §1.4, OCP-OFP8):** the E4M3 encoding and its conversion
rounding and saturation; E5M2 is used by no requirement. The requirements
that cite it are RI-MIR-003 (the `fp8` dtype, OCP E4M3), RI-CLI-002
(`fp8` and `mxfp8` elements are OCP E4M3), RI-KC-003 (OCP fp8 MFMA on gfx950)
and RI-KVC-008 (`--kv-dtype fp8` is OCP E4M3 on gfx950 and cpu). RI-MIR-012
uses E4M3 as the element of `mxfp8` activation quantization.

**Implementation:**

- The dtype `fp8_e4m3` (`crates/rustinfer-mir/src/dtype.rs:24-26`).
- The CPU reference codec, `crates/rustinfer-target/src/numeric.rs`: the format
  row `MiniFloat::E4M3` (bias 7, no infinity, `:49-56`), the NaN `0x7F` and
  the maximum 448 (`:18-24`), decode (`:96-128`), encode with roundTiesToEven
  and saturation (`:131-181`), and `f32_to_fp8` and `fp8_to_f32` (`:296-306`).
  It saturates: there is no non-saturating mode.
- The MX reference uses the same encoder for E4M3 elements
  (`crates/rustinfer-target/src/reference/mx.rs:106-118`).
- The Kernel IR names the type `f8E4M3FN` (`crates/rustinfer-kc/src/dialect/types.rs:19-20`)
  and uses 0xFE (−448) as the identity of a `max` reduction
  (`crates/rustinfer-kc/src/mlir/lower.rs:19-28`).
- Pending: the gfx950 OCP fp8 MFMA (PR #44, issue #8), fp8 KV storage (PR #48,
  issue #37) and in-kernel `mxfp8` activation quantization (issue #38).

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
| Conformance | mandatory R1 (RI-MIR-003, RI-CLI-002, RI-KC-003, RI-KVC-008) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and its tests against the specification text |
| Result | the E4M3 encoding, roundTiesToEven and saturating conversion conform; the required non-saturating mode is missing; the GPU users are in open PRs |
| Open gaps | 3 |
