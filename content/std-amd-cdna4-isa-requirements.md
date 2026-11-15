---
title: "AMD CDNA4 ISA (5 August 2025) requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / AMD CDNA4 ISA (5 August 2025)"
order: 35
summary: What the CDNA4 ISA guide states for the three gfx950 facts of the capability query: LDS size, the vector-memory cache bits and the direct-to-LDS global loads.
---

# AMD CDNA4 ISA requirements

Source: `specs/number-formats/amd-cdna4-isa.pdf` (*AMD Instinct CDNA4
Instruction Set Architecture Reference Guide*, 5-August-2025), read as
`pdftotext -layout` text; each item names the section, the table and the
printed page. The guide states facts about the hardware, not obligations
on a compiler; the requirement is RI-KC-015's: the gfx950 description
"SHALL return the values of [its] documents", and its lowering SHALL map the
asynchronous tile copy to a mover and each abstract hint to "the ISA's
cache-policy bits".

## Section 3.1, State Overview (Table 2, p. 8)

| id | requirement | source |
|---|---|---|
| C4-R1 | LDS, "Local Data Share", 160kB: "a scratch RAM ... shared between threads in a workgroup". Chapter 11: "There are 160 kB memory per compute unit, segmented into 64 banks of 640 Dwords ... One work-group can request up to 160 kB memory". The gfx950 description's shared-memory bytes per work group are 160 × 1024 | §3.1 Table 2 (p. 8); §11 (p. 95) |

## Section 9.1.10.2, Vector Memory (Tables 49 and 50, pp. 84 to 85)

| id | requirement | source |
|---|---|---|
| C4-R2 | "Vector Memory instructions (Flat, Global, Scratch, and Buffer) have 3 bits to control scope and cacheability": "SC[1:0] System Cache level: 0=wave, 1=group, 2=device, 3=system" and "NT Non-Temporal: 0=expect temporal reuse; 1=do not expect temporal reuse" | §9.1.10.2 (pp. 84 to 85) |
| C4-R3 | Loads, Table 49: per scope (SC1, SC0) and NT, the CU cache, L2 and last-level cache behaviour. NT = 1 turns the CU cache to "Miss Evict", the L2 to "Hit Stream" ("Coherent Cache Bypass" at system scope, and at device scope with more than one L2) and the last level to "Hit Evict"; device and system scope miss the CU cache. Stores, Table 50, the same columns | Table 49 "Load Controls", Table 50 "Store Controls" (p. 85) |
| C4-R4 | The hints the description reports (RI-KC-015 (iii): non-temporal or streaming, expected reuse, coherence scope) map onto these bits on gfx950: non-temporal or streaming to NT = 1, expected reuse to NT = 0, a coherence scope to SC1, SC0 | RI-KC-015 (iii) read against §9.1.10.2 |

## Section 10.1, Flat Memory Instruction (Tables 54 and 55, pp. 90 to 91)

| id | requirement | source |
|---|---|---|
| C4-R5 | The global opcodes that load into LDS are `GLOBAL_LOAD_LDS_UBYTE`, `_SBYTE`, `_USHORT`, `_SSHORT`, `_DWORD`, `_DWORDX3` and `_DWORDX4`: per lane 1, 2, 4, 12 or 16 bytes. `DWORDX3` and `DWORDX4` are new in CDNA4: the CDNA3 guide lists `GLOBAL_LOAD_LDS_UBYTE` to `_DWORD` only | Table 55 "Flat, Global and Scratch Opcodes" (p. 91); CDNA3 guide §12.15 (pp. 499 to 500) |
| C4-R6 | The LDS destination comes from M0: "Implied use of M0 for SCRATCH and GLOBAL only when LDS=1. Provides the LDS address-offset"; the address is `LDSbase + M0[17:2] * 4 + INST.OFFSET + ThreadID*4` up to a dword and `+ ThreadID*16` for `DWORDX4`, so each lane writes its own consecutive slot | Table 54 (p. 90); §10.2 (p. 93) |
| C4-R7 | The direct-to-LDS loads take the same SC and NT bits as other vector-memory instructions (Table 54 has `SC` 2 bits and `NT` 1 bit for every flat, global and scratch instruction) | Table 54 (p. 90); §9.1.10.2 |

## Related, outside the Scope phrase

The Scope phrase is the three capability sections. The same guide is the
source for the gfx950 matrix instructions rustinfer emits (RI-KC-003, whose
formats cite OCP-OFP8 and OCP-MX); the audit records how the MFMA table
compares, without a gap:

- Table 28 (p. 43): the CDNA4 bf16 MFMAs `V_MFMA_F32_{*}_BF16` at 16x16x32
  and 32x32x16, and `V_MFMA_F32_16x16x128_F8F6F4` and `_32x32x64_F8F6F4`.
- §7.1.5 (p. 50): in the `F8F6F4` instructions `CBSZ[2:0]` and `BLGP[2:0]`
  select the A and B format, 000 E4M3 (FP8), 001 E5M2 (BF8), 100 E2M1
  (FP4); round mode forced to RNE.
- §7.1.5.1 (pp. 51 to 52): the 8-bit layouts; for 16x16x128 FP8 lanes 0 to
  15 hold `k` 0 to 15 and 64 to 79, so each lane's operand is two runs
  `k / 2` apart.
- §7.2 and §7.2.1 (pp. 55 to 56): block scaling with one E8M0 scale (bias
  127, 0xFF NaN) per 32 `k` values, through `V_MFMA_SCALE_F32_16X16X128_F8F6F4`
  and `_32X32X64_F8F6F4`.
- §7.3 Table 30 (p. 57): FP8 E4M3, bias 7, max 448, NaN 0x7F and 0xFF, no
  infinity (the OCP E4M3 of OCP-OFP8, not FNUZ); BF8 E5M2, bias 15, with
  infinities. The FP16_OVFL table (pp. 58 to 59): with FP16_OVFL = 1, ±Inf
  and values above the maximum convert to ±max; with 0, to NaN for FP8.
- §3.1 Table 2 (p. 8): 256 VGPRs and 256 AccVGPRs per lane (V0 to V255,
  AV0 to AV255), which bear on RI-KC-015's registers per lane.
