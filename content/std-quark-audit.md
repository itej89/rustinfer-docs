---
title: "AMD Quark MXFP4 export (surveyed 313cb0b) audit"
navtitle: Audit
section: Standards
group: "Model formats / AMD Quark MXFP4 export (surveyed 313cb0b)"
order: 42
summary: The 2026-11-14 audit of rustinfer's Quark MXFP4 import on origin/main 8c7d47e, after PR #49 merged, against Quark's source.
---

# AMD Quark MXFP4 export audit

**Audit of 2026-11-14 on origin/main `8c7d47e`** (PR #49 merged, issue #35;
PRs #53 `8d58ad6` and #55 `6a18042` before it), against the
[requirements](std-quark-requirements.html).

History: the audit of 2026-11-13 read main `ccf02b3` and `b99720a`, where no
`quantization_config` was read and every item was missing, and PR #49 at
`de19390`, where `algo_config` was not checked. This audit replaces it.

**Method.** Read Quark's config, export and packing source at `313cb0b`;
read on main `crates/rustinfer-frontend/src/quant/{mod,quark,quark_algo,pattern,section}.rs`,
`src/mapping.rs`, `src/kv_scales.rs`, `src/lowering.rs` and
`src/arch/llama/graph.rs`, and the tests `tests/mxfp4.rs`,
`tests/mxfp4_audit.rs`, `tests/mxfp4_review.rs`, `tests/mxfp4_kv_fp8.rs`,
`tests/mxfp4_logging.rs` and `tests/common/mxfp4.rs`. Quark was not run and
no real Quark checkpoint was decoded (the fixtures copy the `config.json`
shape of `amd/Llama-3.1-8B-Instruct-MXFP4-W4A4-MLCAL-C1000-GPTQ`). No tests
were run here. Paths are under `crates/rustinfer-frontend/` unless marked.

| id | result | evidence (origin/main `8c7d47e`) |
|---|---|---|
| QK-R1 | **conforms** | `quant_method` `quark` dispatches to `quark::parse` (`src/quant/mod.rs:197-211`); `global_quant_config`, `export`, `algo_config`, `softmax_quant_spec`, `online_config`, the three per-layer maps, `exclude` and `kv_cache_post_rope` are read (`src/quant/quark.rs:44-64`). `quant_mode` and `version` are calibration detail and ignored by the declared unknown-field policy (`src/quant/mod.rs:12-21`). |
| QK-R2 | **conforms** | `dtype` `fp4`, other dtypes refused naming their release (`quark.rs:161-179`); `qscheme` `per_group` (`:110-117`); `group_size` 32, `ch_axis` -1, `scale_format` `e8m0` (`:120-139`); `is_dynamic` not true, legacy `mx_element_dtype` refused (`:142-158`); a list of weight specs refused (`:101-107`). `test_quark_scheme_fields_outside_mxfp4_are_refused_naming_the_field` (`tests/mxfp4.rs:443`), `test_more_quark_fields_are_refused` (`:802`). |
| QK-R3 | **not applicable** | Not read, correctly: decoding a stored E8M0 byte does not depend on the mode that chose it. |
| QK-R4 | **conforms** | `export.pack_method` must be `reorder` and `export.weight_format` `real_quantized` (`quark.rs:190-198`); an absent `export` takes Quark's defaults, which are those values. |
| QK-R5 | **conforms** (stricter) | Every entry of `kv_cache_quant_config`, `layer_quant_config` and `layer_type_quant_config` must repeat the global weight spec, else refused naming the entry (`quark.rs:232-272`). Quark allows other schemes per layer; RI-FE-006 asks for the refusal. |
| QK-R6 | **conforms** | `input_tensors` null is W4A16; `fp4` dynamic is W4A4, built with bf16 activations, logged at `warn` and recorded in `metadata` (`quark.rs:214-228`, `src/lowering.rs:145-173`). A global `output_tensors` or `bias` is refused (`quark.rs:202-210`); a per-layer `output_tensors` is accepted only as fp8 E4M3 per tensor, the KV quantization (`:266-284`). `test_w4a4_fixtures_build_and_record_the_deviation` (`tests/mxfp4.rs:320`), `test_w4a4_deviation_is_logged_once_at_warn` (`tests/mxfp4_logging.rs:55`), `test_kv_schemes_other_than_fp8_per_tensor_are_refused` (`tests/mxfp4_review.rs:218`). `--activations` (RI-CLI-002) is not on main. |
| QK-R7 | **conforms** (superset) | An entry holding `*`, `?` or `[` is a glob translated as `fnmatch.translate` does, anchored, `*` crossing dots; any other entry is the exact module name, never expanded to descendants (`src/quant/pattern.rs:142-157, 172-233`); Quark matches no class names (`:88-98`). `re:` entries are also accepted, which Quark does not define; harmless for Quark exports. `test_exclusions_keep_weights_bf16` (`tests/mxfp4.rs:259`), `test_compressed_tensors_has_no_globs_and_quark_no_classes` (`tests/mxfp4_audit.rs:247`), `test_exact_entry_matches_only_the_name` (`src/quant/pattern.rs:263`). |
| QK-R8 | **conforms** | `quark_algo::check` (`src/quant/quark_algo.rs:58-114`) accepts the offline weight-changing algorithms (`smooth`, `autosmoothquant`, `awq`, `gptq`, `gptaq`, `qronos`) and `rotation` only with `r3` and `r4` present and false and `online_r1_rotation` not true; `quarot`, `svdquant` and any other name are refused naming the field, with the Quark source lines for each decision in the module header (`:1-31`). `softmax_quant_spec`, non-empty `online_config.online_rotation_layers` (`quark.rs:68-86`) and `kv_cache_post_rope` true (`:90-98`) are refused. `test_quark_offline_algorithms_are_accepted` (`tests/mxfp4_audit.rs:282`), `test_quark_runtime_algorithms_are_refused_naming_the_field` (`:309`), `test_malformed_quark_algo_config_is_refused_naming_the_field` (`:360`), `test_quark_inference_time_fields_are_refused` (`tests/mxfp4_review.rs:104`). |
| QK-R9 | **conforms** | Packed data is `U8 [out, in/2]` (read as `ue8m0` by the shared reader), checked against the halved shape and given its `fp4x2 [out, in]` meaning by role (`src/mapping.rs:76-83, 270-309`); low nibble first, as `Pack_fp4.pack`. `test_quark_fixture_of_each_family_lowers_to_mx_weights` (`tests/mxfp4.rs:111`) decodes the fixture bytes through a line-for-line port of `Pack_fp4.unpack` (`tests/common/mxfp4.rs:14-15`) and the CPU reference; `test_packed_u8_shape_mismatch_is_refused_naming_the_tensor` (`tests/mxfp4_review.rs:162`). SRS v0.4.8 closes OI-014 on this evidence. |
| QK-R10 | **conforms** | `<module>.weight_scale` `U8 [out, in/32]` must be `ue8m0` of the block shape (`src/mapping.rs:312-321`); the data's manifest entry names it (`:281-291`); each projection reads a `dequantize` of data and scales (`src/arch/llama/graph.rs:337-350`). `test_manifest_names_data_and_scale_of_every_mx_weight` (`tests/mxfp4.rs:184`), `test_bad_mx_tensors_are_refused_naming_the_tensor` (`:587`), `test_each_mx_projection_reads_a_dequantize_of_its_weight` (`:140`). |

## KV scales (RI-FE-006, RI-KVC-008)

A Quark KV quantization (`output_tensors` fp8 E4M3 per tensor on the
`k_proj` and `v_proj` entries) makes each layer's `<k_proj>.output_scale` and
`<v_proj>.output_scale` expected tensors (`src/quant/mod.rs:172-183`,
`src/mapping.rs:96-102`). Lowering locates them as float scalars, shape `[]`
or `[1]` in bf16, fp16 or fp32 (`src/kv_scales.rs:135-179`), and
`apply_kv_scales` reads them and fills the fp8 KV group's per-layer
`KvScales` (`:102-121`), refusing a value that is not positive and finite
(`:182-195`) or a layer count other than the group's. Since PR #53 their
bytes are used ranges of the checkpoint identity (`src/lowering.rs:354-359`).
Tests: `test_quark_kv_scales_are_recorded_per_layer_and_read`
(`tests/mxfp4_audit.rs:69`), `test_bad_kv_scale_tensors_are_refused_naming_them`
(`:149`), `test_non_positive_kv_scale_is_refused_on_read` (`:186`),
`test_checkpoint_kv_scales_fill_the_fp8_geometry` (`tests/mxfp4_kv_fp8.rs:85`),
`test_kv_scale_ranges_are_recorded_in_the_identity` (`:140`).

`apply_kv_scales` is library API: no command calls it, because `rustinfer
build` returns `NotImplemented` on main (`crates/rustinfer-cli/src/commands.rs:69-79`,
RI-CLI-002). That is the build's open work, not a format gap.

Two module headers are stale: `src/quant/quark.rs:11-13` and
`src/quant/ct.rs:12-13` still say the KV scale tensors are "ignored by this
build", which `src/kv_scales.rs` no longer makes true. A documentation
defect in the code, noted here, not a conformance gap.

## Result

Every in-scope item conforms on main `8c7d47e`; QK-R3 is not applicable.
State: **works**. QK-1 to QK-3 are fixed by PR #49; no gap is open. Gaps
on the [tracker](std-quark-tracker.html).
