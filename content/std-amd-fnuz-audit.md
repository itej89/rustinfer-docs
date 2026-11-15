---
title: "AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025) audit"
navtitle: Audit
section: Standards
group: "Number formats / AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
order: 32
summary: The audit of rustinfer's FP8 E4M3 FNUZ encoding against the CDNA3 ISA guide and LLVM APFloat (main 81fbcba) and of the gfx942 capability values (main b057ef5); the encoding conforms, the cache bits and direct-to-LDS loads are #64.
---

# AMD FP8 FNUZ audit

**Audit of 2026-11-14**, against the [requirements](std-amd-fnuz-requirements.html),
on `origin/main` `81fbcba`, after PR #44 (issue #8, merge `38f2f60`: the AMD
lowering with the gfx942 FNUZ MFMA). First audited 2026-11-13 on `ccf02b3`,
re-audited the same day on `b99720a` after PRs #48 (KV dtypes) and #52
(issue #51 fixes). PR #44 and the other merges since (#58, #60, #62) change
no line of `numeric.rs`, `dtype.rs`, `kv.rs` or `lower.rs`, so the encoding
results and their line numbers below stand.

**Method.** Read §7.2 of the ISA guide (`pdftotext -layout` of
`specs/number-formats/amd-cdna3-isa.pdf`, pages 50 and 51) and LLVM APFloat
at `llvmorg-23.1.0` (`semFloat8E4M3FNUZ`, `fltNonfiniteBehavior`,
`fltNanEncoding`, `handleOverflow`, `convert`). Read `origin/main` at
`b99720a`: `crates/rustinfer-target/src/numeric.rs`,
`crates/rustinfer-mir/src/dtype.rs`, `crates/rustinfer-kc/src/dialect/types.rs`,
`crates/rustinfer-kc/src/mlir/lower.rs`, and the tests in
`crates/rustinfer-target/tests/numeric.rs`, and the fp8 KV path of PR #48
(`crates/rustinfer-mir/src/kv.rs`, `crates/rustinfer-target/src/reference/kv.rs`,
their tests). On `81fbcba`, also read the MFMA table `crates/rustinfer-kc/src/amd.rs`, the
gfx942 tests of `crates/rustinfer-kc/tests/amd_lowering.rs` and the hardware
test `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs`, and the GPU
results of #45 in #54 and the open request #61. No tests were run.

**Test tags.** `tests/numeric.rs` tags `Verifies RI-MIR-003` and `Verifies
RI-TGT-003`.

**The exhaustive check.** `test_every_fp8_pattern_round_trips`
(`tests/numeric.rs:141`) decodes all 256 FNUZ patterns and requires each
non-NaN one to encode back to itself. Since the encoder gives 0x80 only for a
NaN, and 0x00 for every zero (`numeric.rs:141-146`), the test proves that 0x80
is the only pattern decoding to NaN, and that 0x00 to 0x7F and 0x81 to 0xFF
decode to 255 distinct values the encoder maps back to them. Together with
the explicit assertion that 0x7F is 240, no pattern is an infinity.

| item | requirement | result | evidence |
|---|---|---|---|
| FNUZ-R1 | S1E4M3, bias 8 | conforms | `MiniFloat::E4M3FNUZ` 4 exponent bits, 3 mantissa bits, bias 8 (`numeric.rs:57-64`). Asserted: 1.0 is 0x40 (`tests/numeric.rs:123-124`) |
| FNUZ-R2 | IEEE-like values; min normal 2^−7, min subnormal 2^−10 | conforms | the shared decode, `min_exponent` 1 − 8 = −7 (`numeric.rs:79-81`, `:103-108`). Asserted: 2^−10 round-trips, −3.5 round-trips (`tests/numeric.rs:131-135`). Min normal 2^−7 is not asserted by value; it follows from the formula and the exhaustive round trip |
| FNUZ-R3 | no infinity | conforms | `special` returns a value only for the NaN pattern when `fnuz` (`numeric.rs:113-115`); exponent 15 decodes as a normal binade |
| FNUZ-R4 | one zero, no negative zero | conforms | a zero result is 0x00 whatever the sign (`numeric.rs:141-146`). Asserted: −0.0 encodes to 0 (`tests/numeric.rs:130`). A negative value that rounds to zero takes the same branch |
| FNUZ-R5 | one NaN, 0x80 | conforms | decode: only `bits == 0x80` is NaN (`numeric.rs:113-114`); encode: a NaN gives 0x80 (`:21`, `:132-133`). Asserted (`tests/numeric.rs:128-129`) and by the exhaustive round trip |
| FNUZ-R6 | max 240 | conforms | `max` uses all-ones exponent and mantissa when `fnuz` (`numeric.rs:87-88`). Asserted: 240 is 0x7F and decodes to 240 (`tests/numeric.rs:122`, `:125-126`), `test_format_maxima` (`numeric.rs:336`) |

## Other users of FNUZ on `origin/main`

- The Kernel IR's `max` identity for `f8E4M3FNUZ` is 0xFF, S.1111.111 =
  −240, the most negative FNUZ value (`crates/rustinfer-kc/src/mlir/lower.rs:25`).
  Correct by FNUZ-R6, and asserted since PR #52 by
  `test_max_identity_of_fnuz_e4m3_is_minus_240` (`lower.rs:454`), which decodes
  the byte with its own bit-field decoder and checks it is the most negative
  of all 256 patterns (FNUZ-1 fixed).
- fp8 KV (PR #48, `e218b8a`): `kv_fp8_dtype` gives `fp8_e4m3fnuz` on gfx942
  (`crates/rustinfer-mir/src/kv.rs:15-25`; `crates/rustinfer-mir/tests/kv_dtypes.rs:88`),
  and the CPU reference cache write encodes with the same saturating
  `f32_to_fp8` (`crates/rustinfer-target/src/reference/kv.rs:277`);
  `test_cached_k_and_v_equal_the_oracle_conversion_bit_exactly`
  (`crates/rustinfer-target/tests/kv.rs:212`) covers FNUZ storage (`tests/kv.rs:57`).

## The gfx942 capability values, audit of 2026-11-15

Against FNUZ-R7 to FNUZ-R9, added to the scope by SRS v0.4.11 (PR #65), on
`main` `b057ef5`. Read §3.1, §9.1.10.2, §10.1, §10.2, §11 and §12.15 of the
guide; on `b057ef5` read `crates/rustinfer-kc/src/capabilities.rs`,
`amd.rs`, `dialect/ops.rs`, `mlir/rocdl/`, the constants and the tests named
below, and searched every crate for direct-to-LDS and cache-policy
spellings (none). No tests were run. gfx942 hardware runs no longer gate R1
(SRS v0.4.12 §2.4); the checks below are all offline.

| item | requirement | result | evidence |
|---|---|---|---|
| FNUZ-R7 | LDS 64 kB per work group | conforms; no per-field test (FNUZ-3) | `KC_GFX942_LDS_BYTES` = `64 * 1024`, citing "the §3.1 table: 64 KiB per CU" (`crates/rustinfer-core/src/config/constants.rs:717-719`), the gfx942 description's `shared_memory_bytes` (`crates/rustinfer-kc/src/amd.rs:116`). The back end refuses 65540 bytes and compiles 65536 for gfx942 (`test_kernel_over_the_lds_limit_is_refused_by_the_back_end`, `crates/rustinfer-kc/tests/amd_lowering.rs:437`); the ROCm target checks against the device before loading (`crates/rustinfer-target-rocm/src/resources.rs:65`). No test reads the capability field |
| FNUZ-R8 | SC1, SC0, NT and Table 48 | missing (FNUZ-3) | No hint field in `Capabilities` (`capabilities.rs:47-64`); the lowered accesses carry no cache-policy attribute (`crates/rustinfer-kc/src/mlir/rocdl/helpers.rs:78`, `:154`, `:321-330`), so all are wave scope, NT = 0 |
| FNUZ-R9 | `GLOBAL_LOAD_LDS_*` at 1, 2, 4 bytes | missing (FNUZ-3) | No mover field and no asynchronous tile copy (`crates/rustinfer-kc/src/dialect/ops.rs:8-21`); no `rocdl.load.to.lds`, `global.load.lds` or `amdgpu.gather_to_lds` emitted. LLVM's widths for gfx942 are [DMA-1](std-llvm-amdgpu-dma-tracker.html) |

## Conversion behaviour, outside the scope

Recorded for the gfx942 work, not judged:

- The CPU reference rounds to nearest even and **saturates**: overflow and
  ±Inf give ±240 (`numeric.rs:137-139`, `:161-168`; asserted for 1e9,
  `tests/numeric.rs:127`, and for ±Inf since PR #52,
  `tests/numeric.rs:199`). This is the ISA's FP16_OVFL = 1 column, not the
  FP16_OVFL = 0 column (NaN), and not LLVM APFloat's conversion, which gives
  NaN on overflow under round-to-nearest (`APFloat.cpp:1490-1503`).
- RI-KVC-008 requires the cached K and V to equal the CPU reference
  bit-exactly. A gfx942 cache-write kernel therefore has to saturate the same
  way: run its `V_CVT_PK_FP8_F32` with FP16_OVFL = 1, or clamp to ±240 before
  converting, and not rely on MLIR constant folding (APFloat semantics) for
  out-of-range values. This belongs to issue #37 and #38.

## Requirements of the SRS not yet met on `origin/main`

| SRS requirement | what needs FNUZ | where it is |
|---|---|---|
| RI-KC-003 | fp8 FNUZ MFMA operands on gfx942 | merged with PR #44 (`38f2f60`): `crates/rustinfer-kc/src/amd.rs:154-156`, host disassembly tests `crates/rustinfer-kc/tests/amd_lowering.rs:220`, `:226`; not yet run on gfx942 hardware (#61) |
| RI-KVC-008 | `--kv-dtype fp8` on gfx942: FNUZ KV written by the cache-write kernel, read by attention | configuration and CPU reference merged (PR #48, `e218b8a`); GPU kernels issue #38 |

Recorded as FNUZ-2.

## The gfx942 FNUZ MFMA (PR #44)

The MFMA table maps `F8E4M3Fnuz` on gfx942 to `v_mfma_f32_32x32x16_fp8_fp8`
and `v_mfma_f32_16x16x32_fp8_fp8` (`crates/rustinfer-kc/src/amd.rs:154-156`),
the CDNA3 instructions that read FNUZ operands; OCP E4M3 on gfx942 and FNUZ on
gfx950 are refused (`test_mfma_table_refuses_every_pair_outside_the_r1_set_naming_both`,
`crates/rustinfer-kc/tests/amd_target.rs:90`). On the host this is checked by
disassembly only (`crates/rustinfer-kc/tests/amd_lowering.rs:220`, `:226`,
Groundwork for RI-KC-003). Whether the hardware reads the FNUZ codes as
Table 30 defines is shown only by the gfx942 run of
`test_matrix_op_matches_the_cpu_on_the_gpu`
(`crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:257`), whose inputs
are encoded with `f32_to_fp8(x, Fp8Format::E4m3Fnuz)` (`:149`). That run is
#61, not yet made; the gfx950 run of #45 (#54) has no FNUZ case.

## Result

Every in-scope item of the encoding conforms on `origin/main` and is tested;
the identity constant is asserted since PR #52 (FNUZ-1 fixed), and the fp8 KV
CPU reference of PR #48 writes FNUZ on gfx942. The gfx942 FNUZ MFMA is merged
(PR #44) but not yet run on gfx942 hardware (#61), and the GPU cache-write
kernel (#38) is not written (FNUZ-2). Of the gfx942 capability values the
scope gained on 2026-11-15, the 64 kB LDS is right but its capability field
is untested, and the cache bits and the direct-to-LDS loads are not yet in
the description (FNUZ-3, #64). **Partial**, for the R1 coverage, not for
any wrong encoding.
