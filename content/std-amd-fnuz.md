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
Since SRS v0.4.11 (PR #65, ADR-011) the scope adds, "for RI-KC-015, the
gfx942 capability values: section 3.1 (LDS 64 kB), section 9.1.10.2 'Memory
Scope and Temporal Control' (SC1, SC0, NT; Table 48) and section 12.15 (the
`GLOBAL_LOAD_LDS_*` direct-to-LDS loads)"; the CDNA3 guide is cited for
them under this id, as the CDNA4 guide is for gfx950 under
[AMD-CDNA4-ISA](std-amd-cdna4-isa.html).

**Implementation:**

- The dtype `fp8_e4m3fnuz` (`crates/rustinfer-mir/src/dtype.rs:27-29`).
- The CPU reference codec, `crates/rustinfer-target/src/numeric.rs`: the format
  row `MiniFloat::E4M3FNUZ` (bias 8, `fnuz` true, `:57-64`), the NaN 0x80 and
  the maximum 240 (`:20-25`), decode (`:96-115`), encode with no negative zero
  (`:131-149`), `Fp8Format::E4m3Fnuz` (`:234-235`).
- The Kernel IR type `f8E4M3FNUZ` (`crates/rustinfer-kc/src/dialect/types.rs:23-24`),
  with 0xFF (−240) as the identity of a `max` reduction
  (`crates/rustinfer-kc/src/mlir/lower.rs:25`), asserted by
  `test_max_identity_of_fnuz_e4m3_is_minus_240` (`lower.rs:454`).
- fp8 KV is FNUZ on gfx942 (`crates/rustinfer-mir/src/kv.rs:15-25`), written by
  the CPU reference cache write (`crates/rustinfer-target/src/reference/kv.rs:263-285`),
  PR #48.
- The gfx942 FNUZ MFMA, `v_mfma_f32_32x32x16_fp8_fp8` and
  `v_mfma_f32_16x16x32_fp8_fp8` (`crates/rustinfer-kc/src/amd.rs:154-156`),
  merged with PR #44 (issue #8, `38f2f60`); not yet run on gfx942 hardware
  (#61).
- Pending: the GPU fp8 KV kernels (issue #38).
- The gfx942 capability values: the LDS size `KC_GFX942_LDS_BYTES` = 64 KiB
  citing the §3.1 table (`crates/rustinfer-core/src/config/constants.rs:717-719`,
  `crates/rustinfer-kc/src/amd.rs:116`); the cache bits and the
  direct-to-LDS loads are not yet in the description (issue #64).

**Conformance:** mandatory from **R1**.

**Source:** `specs/number-formats/amd-cdna3-isa.pdf`, *"AMD Instinct MI300"
Instruction Set Architecture: Reference Guide*, 5-August-2025, §7.2 "BF8 and
FP8 Formats and Conversions" (Tables 30 and 31 and the FP16_OVFL table),
and for the capability values §3.1 (Table 2, p. 8), §9.1.10.2 (Table 48,
pp. 73 to 74) and §12.15 (pp. 499 to 500),
<https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/instruction-set-architectures/amd-instinct-mi300-cdna3-instruction-set-architecture.pdf>.
Executable definition: LLVM APFloat `Float8E4M3FNUZ` at `llvmorg-23.1.0`
(`specs/number-formats/llvm-23.1.0-APFloat.h` and `.cpp`). Both downloaded
2026-11-13.

| | |
|---|---|
| Pages | [requirements](std-amd-fnuz-requirements.html) · [audit](std-amd-fnuz-audit.html) · [tracker](std-amd-fnuz-tracker.html) |
| Conformance | mandatory R1 (RI-MIR-003, RI-CLI-002, RI-KC-003, RI-KVC-008; RI-KC-015 for the gfx942 capability values) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3` and its tests against the ISA guide and LLVM; re-audited at `b99720a` after PRs #48 and #52, on 2026-11-14 at `81fbcba` after PR #44, and on 2026-11-15 at `b057ef5` for the capability sections SRS v0.4.11 added |
| Result | the encoding conforms and is tested in the CPU reference, the Kernel IR and the fp8 KV CPU reference; the gfx942 FNUZ MFMA is merged (PR #44) but gfx942 is not yet run on hardware (#61, which no longer gates R1, SRS v0.4.12); the GPU KV kernels are #38; of the capability values the 64 kB LDS is right, the cache bits and direct-to-LDS loads are #64 |
| Open gaps | 2 (FNUZ-2, FNUZ-3) |
