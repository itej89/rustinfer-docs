---
title: "AMD CDNA4 ISA (5 August 2025)"
navtitle: Overview
section: Standards
group: "Compiler and code generation / AMD CDNA4 ISA (5 August 2025)"
order: 34
summary: The gfx950 values of the target capability query (RI-KC-015) as the CDNA4 ISA guide states them: 160 kB of LDS, the SC1, SC0 and NT cache bits, and the GLOBAL_LOAD_LDS direct-to-LDS loads up to DWORDX4.
---

# AMD CDNA4 ISA (5 August 2025)

**Scope (SRS §1.4, AMD-CDNA4-ISA):** "the gfx950 capability values of
RI-KC-015: section 3.1 (LDS 160 kB), section 9.1.10.2 (SC1, SC0, NT;
Table 49), section 10.1 (`GLOBAL_LOAD_LDS_*` including `DWORDX3` and
`DWORDX4`)". Added by SRS v0.4.11 (PR #65, ADR-011). The requirement that
cites it is RI-KC-015 (the target capability query, R1 for cpu, gfx942 and
gfx950); RI-KC-016 (h), cache-hint assignment, maps its hints to these bits.
The gfx942 counterpart of the same three sections is in the scope of
[AMD-FNUZ](std-amd-fnuz.html) (the CDNA3 guide).

**Implementation on `main` (`b057ef5`):**

- The LDS size: `KC_GFX950_LDS_BYTES` = 160 × 1024, citing "the §3.1 table"
  (`crates/rustinfer-core/src/config/constants.rs:721-723`), reported as
  `shared_memory_bytes` of the gfx950 description
  (`crates/rustinfer-kc/src/amd.rs:115-118`), refused past the limit by the
  back end at compile time and by the ROCm target before a load.
- The capability description (`crates/rustinfer-kc/src/capabilities.rs:47-64`,
  PR #63) has no tile-mover, cache-level or cache-hint field, and no Kernel
  IR operation copies a tile asynchronously
  (`crates/rustinfer-kc/src/dialect/ops.rs:8-21`); nothing emits a
  `GLOBAL_LOAD_LDS_*` or sets SC or NT.
- All of that is planned in issue
  [#64](https://github.com/itej89/rustinfer/issues/64) (open): the
  capability fields, the asynchronous tile copy lowered to the direct-to-LDS
  loads, and the `cache-hints` pass.

**Conformance:** mandatory from **R1** (RI-KC-015).

**Source:** `specs/number-formats/amd-cdna4-isa.pdf`, *AMD Instinct CDNA4
Instruction Set Architecture Reference Guide*, 5-August-2025, 600 pages:
§3.1 (Table 2, p. 8), §9.1.10.2 (Tables 49 and 50, pp. 84 to 85), §10.1
(Tables 54 and 55, pp. 90 to 91) and the LDS address of §10.2 (p. 93),
<https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/instruction-set-architectures/amd-instinct-cdna4-instruction-set-architecture.pdf>,
downloaded 2026-11-15. Page numbers are the guide's printed "n of 600".

| | |
|---|---|
| Pages | [requirements](std-amd-cdna4-isa-requirements.html) · [audit](std-amd-cdna4-isa-audit.html) · [tracker](std-amd-cdna4-isa-tracker.html) |
| Conformance | mandatory R1 (RI-KC-015; RI-KC-016 (h)) |
| Audited | 2026-11-15, by reading `main` `b057ef5`, its tests, the GPU results of #59 in #54 and the guide; no test run locally |
| Result | part: the 160 kB LDS is right, refused past the limit by the back end and by the ROCm target, and verified on gfx950 hardware (#59); the description's values have no per-field test; the cache bits and the direct-to-LDS loads are neither described nor emitted (#64) |
| Open gaps | 3 of 3 (CDNA4-1 field tests, CDNA4-2 cache bits, CDNA4-3 direct-to-LDS loads), all planned in #64 |
