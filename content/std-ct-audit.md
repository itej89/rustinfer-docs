---
title: "compressed-tensors 0.13.0 audit"
navtitle: Audit
section: Standards
group: "Model formats / compressed-tensors 0.13.0"
order: 52
summary: The 2026-11-14 audit of rustinfer's compressed-tensors MXFP4 import on origin/main 8c7d47e, after PR #49 merged, against compressed-tensors 0.13.0.
---

# compressed-tensors 0.13.0 audit

**Audit of 2026-11-14 on origin/main `8c7d47e`** (PR #49 merged, issue #35;
PRs #53 `8d58ad6` and #55 `6a18042` before it), against the
[requirements](std-ct-requirements.html).

History: the audit of 2026-11-13 read main `ccf02b3` and `b99720a`, where no
`quantization_config` was read and every item was missing, and PR #49 at
`de19390`, where `ignore` followed Quark's rules (CT-R6 partial). This audit
replaces it.

**Method.** Read the compressed-tensors 0.13.0 source listed on the
[overview](std-ct.html); read on main
`crates/rustinfer-frontend/src/quant/{mod,ct,pattern}.rs`, `src/mapping.rs`,
`src/kv_scales.rs` and the architecture's module classes
(`src/arch/llama/config.rs`, `names.rs`), and the tests `tests/mxfp4.rs`,
`tests/mxfp4_audit.rs`, `tests/mxfp4_review.rs` and `tests/mxfp4_kv_fp8.rs`.
The fixture configs copy the shape of `nm-testing/Meta-Llama-3-8B-Instruct-MXFP4`.
No real checkpoint was decoded, compressed-tensors was not run, and no tests
were run here. Paths are under `crates/rustinfer-frontend/`.

| id | result | evidence (origin/main `8c7d47e`) |
|---|---|---|
| CT-R1 | **conforms** | `quant_method` `compressed-tensors` dispatches to `ct::parse` (`src/quant/mod.rs:197-211`); `format`, `quantization_status`, `config_groups`, `ignore` and `kv_cache_scheme` are read (`src/quant/ct.rs:36-57`); `global_compression_ratio` is informational and ignored by the declared unknown-field policy (`src/quant/mod.rs:12-21`). |
| CT-R2 | **conforms** | `mxfp4-pack-quantized` accepted; FP8 and int8 formats refused as R2, int4 as R3, `nvfp4-pack-quantized` as unscheduled, others naming the field (`ct.rs:98-118`); a group with its own other `format` is refused (`:131-136`). An absent `format` is taken as MXFP4 (`:37`), looser than compressed-tensors' `fakequant` default (`quantization/quant_config.py:101`); the group checks (CT-R5) still require packed MXFP4 weights, so no other format loads that way. `test_compressed_tensors_fields_outside_mxfp4_are_refused_naming_the_field` (`tests/mxfp4.rs:524`). |
| CT-R3 | **conforms** | `quantization_status` must be `compressed` (`ct.rs:39-40`). |
| CT-R4 | **conforms** | `targets` must be exactly `["Linear"]` (`ct.rs:150-157`); `output_activations` refused (`:139-142`); a non-empty `transform_config` (online Hadamard or rotation) refused (`:61-75`); `symmetric`, `actorder`, `zp_dtype` and `block_structure` are not read, right for MXFP4 (symmetric, no zero point). `test_more_compressed_tensors_fields_are_refused` (`tests/mxfp4.rs:755`), `test_compressed_tensors_transform_config_is_refused` (`tests/mxfp4_review.rs:148`). |
| CT-R5 | **conforms** | Weights `num_bits` 4, `type` float, `strategy` group, `group_size` 32 (else unscheduled), `scale_dtype` `torch.uint8` when given, not dynamic (`ct.rs:160-189`); activations absent (MXFP4A16), 4-bit float (MXFP4) or 8-bit float (MXFP4XFP8), built as bf16 and reported (`:192-203`). `test_compressed_tensors_fixture_of_each_family_lowers_to_mx_weights` (`tests/mxfp4.rs:125`), `test_w4a4_fixtures_build_and_record_the_deviation` (`:320`). |
| CT-R6 | **conforms** | Under `Dialect::CompressedTensors` a `re:<p>` entry compiles to `^(?:p)`, anchored at the start only, as `re.match` (`src/quant/pattern.rs:150-153`); any other entry matches the module name exactly or the module class the architecture declares, and `*` is a literal character (`:88-98, 154-157`). Projections and `lm_head` are declared `Linear`, the embedding `Embedding` (`src/arch/llama/config.rs:312, 322, 400`). `test_compressed_tensors_ignore_matches_module_classes` (`tests/mxfp4_audit.rs:221`), `test_compressed_tensors_has_no_globs_and_quark_no_classes` (`:247`), `test_compressed_tensors_entries_match_names_and_classes` (`src/quant/pattern.rs:249`), `test_case_insensitive_patterns_match` (`tests/mxfp4_review.rs:182`). One narrow difference: `_match_class` walks the whole MRO (`utils/match.py:447-465`), so an entry `Module` would ignore every module; rustinfer matches the declared class only. Such a checkpoint keeps bf16 weights where rustinfer expects `weight_packed`, and is refused naming the missing tensor, so no wrong value results. |
| CT-R7 | **conforms** | A `kv_cache_scheme` must be 8-bit float per tensor with static scales (`ct.rs:80-95`); its `<attention>.k_scale` and `<attention>.v_scale` per layer become expected tensors (`src/quant/mod.rs:178-181`), located as float scalars and read into the fp8 KV group's `KvScales` by `apply_kv_scales` (`src/kv_scales.rs:102-179`), see QK-3. `test_compressed_tensors_kv_scales_are_recorded_per_layer` (`tests/mxfp4_audit.rs:104`), `test_kv_scales_are_expected_only_under_a_kv_quantization` (`tests/mxfp4.rs:679`), `test_checkpoint_kv_scales_fill_the_fp8_geometry` (`tests/mxfp4_kv_fp8.rs:85`), `test_kv_schemes_other_than_fp8_per_tensor_are_refused` (`tests/mxfp4_review.rs:218`). |
| CT-R8 | **conforms** | `<module>.weight_packed` `U8 [out, in/2]` and `<module>.weight_scale` `U8 [out, in/32]` map to an `fp4x2 [out, in]` weight and a `ue8m0` scale (`src/quant/mod.rs:157-168`; `src/mapping.rs:270-321`). `test_manifest_names_data_and_scale_of_every_mx_weight` (`tests/mxfp4.rs:184`), `test_bad_mx_tensors_are_refused_naming_the_tensor` (`:587`), `test_packed_u8_shape_mismatch_is_refused_naming_the_tensor` (`tests/mxfp4_review.rs:162`). |
| CT-R9 | **conforms** | Low nibble first, the order of the CPU reference and of the fixture bytes (`tests/common/mxfp4.rs:7-15, 375-377`); the CT-R5 fixture test checks dequantized values equal the values written. |
| CT-R10 | **conforms** | The scale byte is read as `ue8m0`, `2^(e-127)`, the same bias as compressed-tensors' `scale - 127` (fixture decoder `tests/common/mxfp4.rs:346-347`). |

A stale module header: `src/quant/ct.rs:12-13` still says the `k_scale` and
`v_scale` tensors are "ignored by this build"; `src/kv_scales.rs` reads them.
A documentation defect in the code, noted, not a conformance gap.

## Result

Every item conforms on main `8c7d47e`. State: **works**. CT-1 and CT-2 are
fixed by PR #49; no gap is open. Gaps on the [tracker](std-ct-tracker.html).
