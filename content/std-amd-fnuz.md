---
title: "AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
navtitle: Overview
section: Standards
group: "Number formats / AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
order: 30
summary: The FP8 E4M3 FNUZ encoding of gfx942 (bias 8, max 240, NaN 0x80, no infinity, one zero), as the CPU reference and the Kernel IR use it.
---

# AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)

**Scope (SRS §1.4, AMD-FNUZ):** the FP8 E4M3 FNUZ encoding (bias 8, max 240,
NaN 0x80, no Inf). The requirements that cite it are RI-MIR-003 (the `fp8`
dtype, FNUZ e4m3), RI-CLI-002 (`fp8` is FNUZ on gfx942), RI-KC-003 (fp8 FNUZ
MFMA on gfx942) and RI-KVC-008 (`--kv-dtype fp8` is FNUZ E4M3 on gfx942).

**Implementation:**

- The dtype `fp8_e4m3fnuz` (`crates/rustinfer-mir/src/dtype.rs:27-29`).
- The CPU reference codec, `crates/rustinfer-target/src/numeric.rs`: the format
  row `MiniFloat::E4M3FNUZ` (bias 8, `fnuz` true, `:57-64`), the NaN 0x80 and
  the maximum 240 (`:20-25`), decode (`:96-115`), encode with no negative zero
  (`:131-149`), `Fp8Format::E4m3Fnuz` (`:234-235`).
- The Kernel IR type `f8E4M3FNUZ` (`crates/rustinfer-kc/src/dialect/types.rs:23-24`),
  with 0xFF (−240) as the identity of a `max` reduction
  (`crates/rustinfer-kc/src/mlir/lower.rs:25`).
- Pending: the gfx942 FNUZ MFMA (PR #44, issue #8) and fp8 KV storage
  (PR #48, issue #37; GPU kernels issue #38).

**Conformance:** mandatory from **R1**.

**Source:** `specs/number-formats/amd-cdna3-isa.pdf`, *"AMD Instinct MI300"
Instruction Set Architecture: Reference Guide*, 5-August-2025, §7.2 "BF8 and
FP8 Formats and Conversions" (Tables 30 and 31 and the FP16_OVFL table),
<https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/instruction-set-architectures/amd-instinct-mi300-cdna3-instruction-set-architecture.pdf>.
Executable definition: LLVM APFloat `Float8E4M3FNUZ` at `llvmorg-23.1.0`
(`specs/number-formats/llvm-23.1.0-APFloat.h` and `.cpp`). Both downloaded
2026-11-13.

| | |
|---|---|
| Pages | [requirements](std-amd-fnuz-requirements.html) · [audit](std-amd-fnuz-audit.html) · [tracker](std-amd-fnuz-tracker.html) |
| Conformance | mandatory R1 (RI-MIR-003, RI-CLI-002, RI-KC-003, RI-KVC-008) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and its tests against the ISA guide and LLVM |
| Result | the encoding conforms in the CPU reference and the Kernel IR; one constant is untested; the gfx942 users are in open PRs |
| Open gaps | 2 |
