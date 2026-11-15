---
title: "AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025) requirements"
navtitle: Requirements
section: Standards
group: "Number formats / AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
order: 31
summary: What the CDNA3 ISA guide and LLVM APFloat define for the FP8 E4M3 FNUZ encoding, the part in rustinfer's scope.
---

# AMD FP8 FNUZ requirements

Sources: `specs/number-formats/amd-cdna3-isa.pdf` (*"AMD Instinct MI300"
Instruction Set Architecture: Reference Guide*, 5-August-2025), §7.2, cited
as **[ISA]**; and LLVM APFloat at `llvmorg-23.1.0`, cited as **[LLVM]**, which
the SRS names as the executable definition. The ISA guide states the format
as one row of a table; LLVM states the same format as code, and is used where
the table is terse.

Table 30, row FP8 [ISA]: "FP8, E4M3, bias 8, +/-: 0x00 (+0, −0), INF N/A,
NaN 0x80, max 240, min (norm) +/−2.0^(−7), min (denorm) +/−2.0^(−10)".

`semFloat8E4M3FNUZ = {7, -7, 4, 8, fltNonfiniteBehavior::NanOnly,
fltNanEncoding::NegativeZero}` [LLVM] (`APFloat.cpp:82-83`): maximum exponent
7, minimum exponent −7, precision 4 with the hidden bit, 8 bits. The comment
at `APFloat.h:219-224`: "8-bit floating point number mostly following IEEE-754
conventions and bit layout S1E4M3 ... with expanded range and with no infinity
or signed zero. NaN is represented as negative zero. (FN -> Finite, UZ ->
unsigned zero). This format's exponent bias is 8".

| item | requirement | source |
|---|---|---|
| FNUZ-R1 | Layout S1E4M3: 1 sign bit, 4 exponent bits, 3 mantissa bits; exponent bias 8. | [ISA] Table 30; [LLVM] `APFloat.h:219-224` |
| FNUZ-R2 | Values "mostly following IEEE-754 conventions": a normal value is (−1)^S × 2^(E−8) × (1 + M/8); E = 0 is subnormal, (−1)^S × 2^−7 × (M/8). Min normal ±2^−7, min subnormal ±2^−10. | [LLVM] the semantics (emin −7, precision 4); [ISA] Table 30 min (norm), min (denorm) |
| FNUZ-R3 | No infinity. | [ISA] Table 30 "INF N/A"; [LLVM] `NanOnly`: "There is no representation for Inf" (`APFloat.h:965-968`) |
| FNUZ-R4 | One zero, 0x00; no negative zero. | [ISA] Table 30 "+/-: 0x00"; [LLVM] "no ... signed zero", "unsigned zero" |
| FNUZ-R5 | One NaN, 0x80 (the negative-zero pattern). | [ISA] Table 30 "NaN 0x80"; [LLVM] `fltNanEncoding::NegativeZero` |
| FNUZ-R6 | Largest finite magnitude 240 (S.1111.111, emax 7, significand 1.875). | [ISA] Table 30 "max 240"; [LLVM] maximum exponent 7, precision 4 |

## The gfx942 capability values (SRS v0.4.11)

SRS v0.4.11 (PR #65) extends the scope with three more sections of the same
guide, the gfx942 values of RI-KC-015's capability query; the gfx950 values
are [AMD-CDNA4-ISA](std-amd-cdna4-isa-requirements.html)'s. Page numbers
are the guide's printed "n of 553".

| item | requirement | source |
|---|---|---|
| FNUZ-R7 | LDS, "Local Data Share", 64kB; "There are 64 kB memory per compute unit, segmented into 32 banks of 512 Dwords ... One work-group can request up to 64 kB memory". The gfx942 description's shared-memory bytes per work group are 64 × 1024 | [ISA] §3.1 Table 2 (p. 8); §11 (p. 84) |
| FNUZ-R8 | Vector memory instructions have "SC[1:0] System Cache level: 0=wave, 1=group, 2=device, 3=system" and "NT Non-Temporal: 0=expect temporal reuse; 1=do not expect temporal reuse"; Table 48 gives the CU cache, L2 and last-level behaviour per combination (NT = 1: "Miss Evict", "Hit Stream", "Hit Evict" at wave and group scope). RI-KC-015 (iii)'s abstract hints map onto them | [ISA] §9.1.10.2, Table 48 "Load Controls", Table 49 "Store Controls" (pp. 73 to 74) |
| FNUZ-R9 | The global loads into LDS are `GLOBAL_LOAD_LDS_UBYTE`, `_SBYTE`, `_USHORT`, `_SSHORT` and `_DWORD`: 1, 2 or 4 bytes per lane (no `DWORDX3` or `DWORDX4` on CDNA3); M0 gives the LDS offset ("Implied use of M0 for SCRATCH and GLOBAL only when LDS=1") and lane `i` writes at `ThreadID*4` | [ISA] §12.15 (pp. 499 to 500); §10.1 Table 54 (p. 79); §10.2 (p. 81) |

## Related, outside the Scope phrase

The Scope phrase is the encoding only. The ISA guide also defines the
hardware conversions, which bear on RI-KVC-008's bit-exact acceptance once
gfx942 kernels write FNUZ:

- Table 31: `CVT_PK_FP8_F32` (f32 to FP8) rounds to nearest even ("RNE");
  `CVT_SR_FP8_F32` rounds stochastically.
- The FP16_OVFL table: with FP16_OVFL = 1, ±Inf and values above the FP8
  maximum give ±max; with FP16_OVFL = 0 they give NaN. NaN gives NaN.
- "The register SH_MEM_CONFIG, bit[8] must be set to 1 to produce the
  correct results for BF8 and FP8 operations."

LLVM's own conversion to `Float8E4M3FNUZ` gives NaN on overflow under
round-to-nearest (`handleOverflow`, `APFloat.cpp:1490`) and turns −0 into +0
(`IEEEFloat::convert`). The audit records how the CPU reference compares.
