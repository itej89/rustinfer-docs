---
title: "AMD CDNA4 ISA (5 August 2025) audit"
navtitle: Audit
section: Standards
group: "Compiler and code generation / AMD CDNA4 ISA (5 August 2025)"
order: 36
summary: The 2026-11-15 audit at main b057ef5 of rustinfer's gfx950 capability values against the CDNA4 ISA guide; the 160 kB LDS conforms and is verified on an MI350X, the cache bits and the direct-to-LDS loads are not yet described or emitted (#64).
---

# AMD CDNA4 ISA audit

**Audit of 2026-11-15**, against the [requirements](std-amd-cdna4-isa-requirements.html),
on `main` `b057ef5` (SRS v0.4.12; the standard was added to SRS §1.4 by
v0.4.11, PR #65). First audit.

**Method.** Read §3.1, §9.1.10.2, §10.1, §10.2, §11 and, for the related
items, §7.1 to §7.3 of the guide (`pdftotext -layout` of
`specs/number-formats/amd-cdna4-isa.pdf`). Read on `b057ef5`:
`crates/rustinfer-kc/src/capabilities.rs`, `amd.rs`, `dialect/ops.rs`,
`mlir/rocdl/mod.rs`, `mlir/rocdl/wrap.rs`, `mlir/rocdl/helpers.rs`,
`crates/rustinfer-core/src/config/constants.rs`, the ROCm target's
`src/resources.rs`; the tests `crates/rustinfer-kc/tests/amd_lowering.rs`,
`amd_target.rs`, `generators.rs`, `generator_sources.rs` and
`crates/rustinfer-target-rocm/tests/resources.rs`; searched every crate for
`load.to.lds`, `global.load.lds`, `gather_to_lds`, cache-policy, `sc0`,
`sc1`, `nt` and non-temporal spellings (none found). Read the gfx950 results
of GPU tests #45 and #59 in #54 (MI350X, ROCm 10.1, 10.1.0-3, 2026-11-15) and
the plan of #64. No tests were run. Test tags follow `docs/testing.md`.

| id | requirement | result | evidence |
|---|---|---|---|
| C4-R1 | LDS 160 kB per work group | **conforms**; no per-field test (CDNA4-1) | `KC_GFX950_LDS_BYTES` = `160 * 1024`, doc comment citing "the §3.1 table: 160 KiB per CU" (`crates/rustinfer-core/src/config/constants.rs:721-723`), returned as `shared_memory_bytes` of the gfx950 description (`crates/rustinfer-kc/src/amd.rs:115-118`). The back end refuses a kernel needing 163844 bytes and compiles one at 163840 with `.group_segment_fixed_size` 163840 (`test_kernel_over_the_lds_limit_is_refused_by_the_back_end`, `crates/rustinfer-kc/tests/amd_lowering.rs:437`, Groundwork for RI-KC-003). The ROCm target checks a kernel's LDS against the device's `sharedMemPerBlock` before loading (`crates/rustinfer-target-rocm/src/resources.rs:65`; `tests/resources.rs:106`, `:125`, Verifies RI-ROC-004). Hardware, #59 on an MI350X: the device reported `lds_bytes=163840`, a kernel at 163840 launched with no mismatch, one needing 163844 was refused. No test reads `AmdArch::Gfx950.capabilities().shared_memory_bytes`, and no generator reads the field yet |
| C4-R2 | SC[1:0] scope and NT bits exist on vector memory | **missing** (CDNA4-2) | The description has no cache-policy hint field (`crates/rustinfer-kc/src/capabilities.rs:47-64`). The lowering emits `amdgpu.raw_buffer_load {boundsCheck = true}` and plain `vector.load`, `vector.store`, `memref.load` with no cache-policy attribute (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:321-330`, `:78`, `:154`), so every access takes SC = 0, NT = 0: wave scope, "expect temporal reuse". Correct for the kernels of `b057ef5`, which do not need coherence beyond the work group; but no hint can be asked for |
| C4-R3 | Table 49 and 50 behaviour per bit combination | **missing** (CDNA4-2) | Nothing chooses between the rows; the only row used is wave scope, NT = 0 ("Hit LRU" at every level) |
| C4-R4 | Abstract hints mapped to SC and NT on gfx950 | **missing** (CDNA4-2) | No hint type and no mapping; #64 plans the `cache-hints` pass (RI-KC-016 (h), R1) and its lowering to SC1, SC0 and NT through the ROCDL `gfx942_cache_policy` attribute |
| C4-R5 | `GLOBAL_LOAD_LDS_*` at 1, 2, 4, 12 and 16 bytes per lane | **missing** (CDNA4-3) | No tile-mover field in the description (`capabilities.rs:47-64`) and no asynchronous tile copy in the Kernel IR: the operation table is `tile_load`, `tile_store`, `make_mask`, `mma`, `reduce`, `barrier` (`crates/rustinfer-kc/src/dialect/ops.rs:8-21`). Shared tiles are staged through registers: the ROCDL preparation turns shared buffers into `gpu.func` workgroup attributions (`crates/rustinfer-kc/src/mlir/rocdl/wrap.rs:106-143`) and copies with a load and a store; no `rocdl.load.to.lds`, `rocdl.global.load.lds` or `amdgpu.gather_to_lds` is emitted. The pinned MLIR has those operations (`ROCDLOps.td`, `ROCDL_LoadToLDSOp`, `ROCDL_GlobalLoadLDSOp`; `AMDGPUOps.td`, `AMDGPU_GatherToLDSOp`) |
| C4-R6 | The M0 LDS offset and the per-lane slot (4 or 16 bytes per lane) | **not applicable yet** (CDNA4-3) | No direct-to-LDS load is emitted, so no shared layout depends on the per-lane slot. When #64 lowers the tile copy, the shared tile's layout must place lane `i`'s data at `4 * i` or `16 * i`, or the lowering must fall back to a load and a store (#64: "plain loads and stores when the width or the layout does not fit") |
| C4-R7 | SC and NT on the direct-to-LDS loads | **missing** (CDNA4-2, CDNA4-3) | Follows from C4-R2 and C4-R5 |

**Values not yet tested per field.** RI-KC-015's Acceptance requires the
gfx950 description to "return the values of [its] documents (tested per
field, each value cited in #64)". On `b057ef5` the description holds
`shared_memory_bytes` (160 KiB, C4-R1), `lane_width` 64
(`KC_AMD_WAVE_LANES`, `constants.rs:726`), `vector_bytes` 16 (`dwordx4`,
`constants.rs:728-729`), `native_fp8` OCP E4M3 (`amd.rs:117`) and the MFMA
shapes (`amd.rs:189-210`); the tests read the shapes and the fp8 encoding
through the generators (`test_gemm_target_rules_follow_the_capabilities`,
`crates/rustinfer-kc/tests/generators.rs:329`;
`test_one_generator_serves_two_capability_sets`, `:360`, both Groundwork for
RI-KC-015) but no test compares a field with its cited value. CDNA4-1.

**Generators never name a mover or a bit.** RI-KC-015 requires that "no
generator or pass SHALL name a mover, an instruction or a cache-policy bit".
The deny-list over the generator sources already refuses the spellings
(`crates/rustinfer-kc/tests/generator_sources.rs:17-43`: `rocdl`, `amdgpu`,
`llvm.`; `:55-66`: the prefixes `global_load`, `buffer_load`, `ds_`, `flat_`),
so the future mover and hints can reach a generator only through the
capability query.

## Related, outside the Scope phrase

Recorded, not judged:

- **MFMA shapes.** The gfx950 rows of the MFMA table,
  `v_mfma_f32_32x32x16_bf16`, `_16x16x32_bf16`, `v_mfma_f32_32x32x64_f8f6f4`
  and `_16x16x128_f8f6f4` (`crates/rustinfer-kc/src/amd.rs:196-209`), are
  Table 28's CDNA4 shapes.
- **Operand format codes.** E4M3 0 and E5M2 1 (`amd.rs:40-42`, `:199-209`)
  are the `CBSZ` and `BLGP` codes 000 and 001 of §7.1.5; asserted by
  `test_mfma_table_records_the_fp8_operand_format_on_gfx950`
  (`crates/rustinfer-kc/tests/amd_target.rs:72`).
- **8-bit operand layout.** `Mfma::k_of` (`amd.rs:161-166`) places a lane's
  `chunk = lane_k / 2` values in two runs `k / 2` apart: for 16x16x128,
  `k` 0 to 15 and 64 to 79 in lanes 0 to 15; for 32x32x64, 0 to 15 and 32 to
  47. That is §7.1.5.1's FP8 table. On gfx950 hardware, #45 ran every R1
  fp8 shape with `max_abs_err=0` against the CPU reference (results in #54).
- **Scaled MFMA.** No `V_MFMA_SCALE_F32_*_F8F6F4` is emitted on `b057ef5`;
  it is the `--activations mxfp8` and `mxfp4` path of RI-KC-003, issue #38,
  tracked as [MLIR-3](std-mlir-tracker.html) and [MX-3](std-ocp-mx-tracker.html).
- **FP8 formats.** gfx950's native fp8 is `F8E4M3Fn` (`amd.rs:117`), Table
  30's E4M3 with bias 7, max 448 and NaN 0x7F and 0xFF; the encoding is
  audited under [OCP OFP8](std-ocp-ofp8-audit.html). The CPU reference
  saturates, which is the FP16_OVFL = 1 column; a gfx950 conversion kernel
  (#38) must run with FP16_OVFL = 1 or clamp, as the OCP OFP8 tracker notes.
- **Registers per lane.** Table 2's 256 VGPRs and 256 AccVGPRs are not in
  the description; RI-KC-015 lists registers per lane and #64 adds the field
  (the ROCm target already checks a kernel's register counts against the
  architecture, `crates/rustinfer-target-rocm/tests/resources.rs:155`).

## Result

One of the three in-scope facts holds: gfx950's 160 kB of LDS is the
guide's, it bounds every kernel at compile time and at load, and an MI350X
confirmed it (#59). The other two, the SC1, SC0 and NT bits and the
`GLOBAL_LOAD_LDS_*` movers up to `DWORDX4`, are not in the capability
description and nothing emits them; and no field of the description is
tested against its cited value. All three gaps are R1 work planned in #64.
**Partial.** Gaps are on the [tracker](std-amd-cdna4-isa-tracker.html).
