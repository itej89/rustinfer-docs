---
title: "AMD Quark MXFP4 export (surveyed 313cb0b) tracker"
navtitle: Tracker
section: Standards
group: "Model formats / AMD Quark MXFP4 export (surveyed 313cb0b)"
order: 43
summary: Gaps between rustinfer and the Quark MXFP4 export.
---

# AMD Quark MXFP4 export tracker

Gaps found by the [audit](std-quark-audit.html) of 2026-11-13 and closed by
PR #49 (issue #35, merge `8c7d47e`), as re-audited on `origin/main` `8c7d47e`
on 2026-11-14. Paths are under `crates/rustinfer-frontend/` unless marked.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| QK-1 | Quark MXFP4 checkpoints were not imported on main: `quantization_config` was not read | QK-R1, R2, R4 to R7, R9, R10; RI-FE-006 | Fixed 2026-11-14 8c7d47e | PR #49 (issue #35). `quant_method` `quark` dispatches to `quark::parse` (`src/quant/mod.rs:197-211`), which checks the global weight spec (`src/quant/quark.rs:44-64, 101-179`), `export` (`:190-198`), the per-layer maps (`:232-272`) and `exclude` (`:55-56`, `src/quant/pattern.rs:142-157`); packed `U8 [out, in/2]` data becomes `fp4x2` and `weight_scale` a `ue8m0` scale (`src/mapping.rs:270-321`), each projection reading a `dequantize` (`src/arch/llama/graph.rs:337-350`). Tests: `test_quark_fixture_of_each_family_lowers_to_mx_weights` (`tests/mxfp4.rs:111`, through a port of Quark's `Pack_fp4.unpack`), `test_quark_scheme_fields_outside_mxfp4_are_refused_naming_the_field` (`:443`), `test_more_quark_fields_are_refused` (`:802`), `test_manifest_names_data_and_scale_of_every_mx_weight` (`:184`), `test_exclusions_keep_weights_bf16` (`:259`). |
| QK-2 | `algo_config` (rotation among others), `softmax_quant_spec` and `kv_cache_post_rope` were not checked | QK-R8 (`quantization/config/config.py:156, 229-262, 383-392`) | Fixed 2026-11-14 8c7d47e | PR #49. `quark_algo::check` (`src/quant/quark_algo.rs:58-114`) accepts `smooth`, `autosmoothquant`, `awq`, `gptq`, `gptaq`, `qronos` and a `rotation` whose `r3` and `r4` are present and false and `online_r1_rotation` absent or false; `quarot`, `svdquant` and every other name are refused naming the field. `softmax_quant_spec` and a non-empty `online_config.online_rotation_layers` are refused (`src/quant/quark.rs:68-86`), `kv_cache_post_rope` true is refused (`:90-98`). Tests: `test_quark_offline_algorithms_are_accepted` (`tests/mxfp4_audit.rs:282`), `test_quark_runtime_algorithms_are_refused_naming_the_field` (`:309`), `test_malformed_quark_algo_config_is_refused_naming_the_field` (`:360`), `test_quark_inference_time_fields_are_refused` (`tests/mxfp4_review.rs:104`). |
| QK-3 | Checkpoint KV scales were not fed to `--kv-dtype fp8` | RI-FE-006, RI-KVC-008 | Fixed 2026-11-14 8c7d47e | PR #49. A Quark `output_tensors` entry (fp8 E4M3 per tensor only, `src/quant/quark.rs:266-284`) makes every layer's `<k_proj>.output_scale` and `<v_proj>.output_scale` expected (`src/quant/mod.rs:172-183`); lowering locates them as float scalars (`src/kv_scales.rs:135-179`), and `apply_kv_scales` reads them and fills the fp8 KV group's per-layer `KvScales` of PR #48 (`:102-121`), refusing a non-positive or non-finite value (`:182-195`) or a layer count other than the group's. PR #53's identity binds their bytes (`src/lowering.rs:354-359`). Tests: `test_quark_kv_scales_are_recorded_per_layer_and_read` (`tests/mxfp4_audit.rs:69`), `test_checkpoint_kv_scales_fill_the_fp8_geometry` (`tests/mxfp4_kv_fp8.rs:85`), `test_layer_count_mismatch_is_refused_naming_the_group` (`:120`), `test_kv_schemes_other_than_fp8_per_tensor_are_refused` (`tests/mxfp4_review.rs:218`). No command calls `apply_kv_scales` yet because `rustinfer build` itself is not implemented on main (`crates/rustinfer-cli/src/commands.rs:69-79`, RI-CLI-002); that wiring belongs to the build, not to this format. |
