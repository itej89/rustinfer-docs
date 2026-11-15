---
title: "OCP OFP8 Revision 1.1 tracker"
navtitle: Tracker
section: Standards
group: "Number formats / OCP OFP8 Revision 1.1"
order: 23
summary: Gaps between rustinfer's E4M3 and E5M2 handling and OFP8 Revision 1.1 in its saturating-only scope; the test gap is fixed, the non-saturating mode is out of scope, the gfx950 fp8 MFMA is merged and verified exact on hardware (#45), the GPU KV and mxfp8 kernels remain (#38).
---

# OCP OFP8 Revision 1.1 tracker

Gaps found by the [audit](std-ocp-ofp8-audit.html) of 2026-11-13, re-audited
against `origin/main` `b99720a` the same day after PRs #48, #50 and #52 merged,
on 2026-11-14 against `8c7d47e` after PR #55 (merge `6a18042`) added E5M2, and
the same day against `81fbcba` after PR #44 (issue #8, merge `38f2f60`) added
the gfx950 OCP fp8 MFMA. The E5M2 rows (OFP8-R12 to R18) conform and raise no
gap. OFP8-1 is out of the narrowed scope and counts in no total.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| OFP8-1 | No non-saturating conversion mode: overflow and ±Inf always give ±448, never NaN | §5.2.1 ("requires implementation of saturating and non-saturating modes"), Table 3 | Out of scope (owner decision 2026-11-13, PR #50) | The second way out was taken: SRS v0.4.3 (merge `48c2820`) scopes OCP-OFP8 to "saturating conversion (roundTiesToEven) only; the non-saturating mode of Revision 1.1 section 5.2.1 is out of scope" (`docs/SRS-RI-v0.1.md:160` on `8c7d47e`). `f32_to_fp8` stays saturating for E4M3 and, since PR #55, E5M2 (`crates/rustinfer-target/src/numeric.rs:327-331`, every fp8 row `saturating: true`, `:66`, `:75`, `:86`). Reopen only if a requirement needs NaN on overflow |
| OFP8-2 | Two correct behaviours have no test: ±Inf to ±448 (saturating), and the Kernel IR `max` identity 0xFE | Table 3 (±Inf row); Table 2 (max normal) | Fixed 2026-11-13 b99720a | PR #52 (issue #51). ±Inf: `test_fp8_e4m3_infinity_saturates_to_448` (`crates/rustinfer-target/tests/numeric.rs:186`) asserts 0x7E and 0xFE and −448 back, for the encoder `numeric.rs:327-331` (overflow `:185-192`, lines of `8c7d47e`). Identity: `test_max_identity_of_ocp_e4m3_is_minus_448` (`crates/rustinfer-kc/src/mlir/lower.rs:441`) checks the constant 0xFE (`lower.rs:23`) decodes to −448 by an independent bit-field decoder and is the most negative of all 256 patterns |
| OFP8-3 | The R1 GPU users of E4M3 not yet written: the fp8 KV write and `mxfp8` activation quantization kernels | §5.2.1 for each conversion; SRS RI-KVC-008, RI-MIR-012 | **Open** ([#38](https://github.com/itej89/rustinfer/issues/38), GPU KV and `mxfp8`); gfx950 fp8 MFMA merged 2026-11-14 38f2f60 and verified on hardware (#45); KV CPU reference merged 2026-11-13 e218b8a | The gfx950 fp8 MFMA (RI-KC-003) is no longer part of the gap: PR #44 maps OCP E4M3 and E5M2 on gfx950 to `v_mfma_f32_32x32x64_f8f6f4` and `v_mfma_f32_16x16x128_f8f6f4` with operand format codes 0 and 1 (`crates/rustinfer-kc/src/amd.rs:160-170`; `test_mfma_table_records_the_fp8_operand_format_on_gfx950`, `crates/rustinfer-kc/tests/amd_target.rs:72`; disassembly tests `crates/rustinfer-kc/tests/amd_lowering.rs:244-262`, Groundwork for RI-KC-003), and GPU test [#45](https://github.com/itej89/rustinfer/issues/45) on an MI350X (gfx950) under ROCm 10.1 (10.1.0-3) gave `max_abs_err=0` on all 12 fp8 `mma` lines, `F8E4M3Fn` and `F8E5M2` at 16x16x128, 32x32x128 and 48x16x256 with 64 and 256 work items (results in [#54](https://github.com/itej89/rustinfer/issues/54); `test_matrix_op_matches_the_cpu_on_the_gpu`, `crates/rustinfer-target-rocm/tests/gpu_code_objects.rs:257`). The inputs are multiples of 0.5 in [−2, 2], so this proves the hardware reads those codes as the CPU reference does, not every code. The run was at `821a57e`, before PR #44's rebase onto #58's ROCm target; #61 asks for a gfx950 re-run on `main`. Still to land: the GPU KV and `mxfp8` kernels (#38), each to match the CPU reference bit for bit. The fp8 KV CPU reference landed with PR #48 (issue #37, merge `e218b8a`): the cache write encodes `x / scale` with the saturating `f32_to_fp8` (`crates/rustinfer-target/src/reference/kv.rs:263-285`, `:277`), and `test_cached_k_and_v_equal_the_oracle_conversion_bit_exactly` (`crates/rustinfer-target/tests/kv.rs:212`, `Groundwork for RI-KVC-008`) checks it against the oracle for OCP E4M3 (`tests/kv.rs:51`) |
