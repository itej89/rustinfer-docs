---
title: "AMD Quark MXFP4 export (surveyed 313cb0b) audit"
navtitle: Audit
section: Standards
group: "Model formats / AMD Quark MXFP4 export (surveyed 313cb0b)"
order: 42
summary: The 2026-11-13 audit of rustinfer's Quark MXFP4 import, on main and in PR #49, against Quark's source.
---

# AMD Quark MXFP4 export audit

**Audit of 2026-11-13**, against the [requirements](std-quark-requirements.html),
on origin/main `ccf02b3` (re-read on `b99720a`) and PR #49 (`feat/35-mxfp4-checkpoints`, head
`de19390`).

**Re-read on origin/main `b99720a`** (after PRs #47, #48, #50 and #52):
main still has no `quantization_config` reader, so every result below
stands. PR #48 (`e218b8a`) added the place checkpoint KV scales go: the plan's
KV geometry records per-layer fp8 `KvScales`, unit scales that "a frontend
replaces with the checkpoint's" (`crates/rustinfer-artifact/src/plan.rs:79-125`;
`test_fp8_geometry_records_unit_scales_per_layer`,
`crates/rustinfer-artifact/tests/kv_geometry.rs:133`). PR #49 has moved to
head `fd03bc1`; its description now claims the `algo_config` check (`src/quant/quark_algo.rs`: only offline algorithms accepted; online rotations, `quarot` and `svdquant` refused), refusal of `softmax_quant_spec` and of `kv_cache_post_rope` true, and checkpoint KV scales filling the fp8 KV group's `KvScales` (`src/kv_scales.rs`). Those commits were not
re-audited here: the PR evidence below is as read at `de19390`, and the PR is
re-audited when it merges.

**Method.** Read Quark's config, export and packing source at `313cb0b`;
read `crates/rustinfer-frontend/src/quant/{mod,quark,pattern,section}.rs`,
`src/mapping.rs` and `src/arch/llama/graph.rs` on the PR branch, and its tests
`tests/mxfp4.rs` and `tests/common/mxfp4.rs`; checked main for any reading of
`quantization_config` (none). Quark was not run and no real Quark checkpoint
was decoded, here or in the PR (its description says so). The PR's fixtures
copy the shape of the `config.json` of
`amd/Llama-3.1-8B-Instruct-MXFP4-W4A4-MLCAL-C1000-GPTQ`. Paths below are
under `crates/rustinfer-frontend/` on the PR branch unless marked main.

On main every item is **missing**: the frontend never reads
`quantization_config` (main `src/config.rs:101-112`), and a Quark
checkpoint's `U8` weights are refused as a dtype outside the policy (main
`tests/mapping.rs:125`). The table gives what PR #49 does; none of it counts
as conforming until it merges.

| id | result | evidence (PR #49) |
|---|---|---|
| QK-R1 | **pending PR #49** | `quant_method` `quark` dispatches to `quark::parse` (`src/quant/mod.rs:187-199`); `global_quant_config`, `export`, `exclude`, `layer_quant_config`, `layer_type_quant_config`, `kv_cache_quant_config` are read (`src/quant/quark.rs:44-60, 194-232`). `algo_config`, `softmax_quant_spec` and `kv_cache_post_rope` are not read (QK-2). |
| QK-R2 | **pending PR #49** | `dtype` `fp4` (other dtypes refused naming their release, `quark.rs:123-141`), `qscheme` `per_group` (72-79), `group_size` 32, `ch_axis` -1 and `scale_format` `e8m0` (82-101), `is_dynamic` not true (104-111), legacy `mx_element_dtype` refused (112-119); a list of weight specs refused (63-69). `test_quark_scheme_fields_outside_mxfp4_are_refused_naming_the_field` (`tests/mxfp4.rs:443`), `test_more_quark_fields_are_refused` (`:802`). |
| QK-R3 | **not applicable** | Not read, correctly: decoding a stored E8M0 byte does not depend on the mode that chose it. |
| QK-R4 | **pending PR #49** | `export.pack_method` must be `reorder` and `export.weight_format` `real_quantized` (`quark.rs:152-160`); an absent `export` is accepted. |
| QK-R5 | **pending PR #49** | Every entry of the three per-layer maps must repeat the global weight spec, else refused naming the entry (`quark.rs:194-232`). Stricter than Quark, which allows other schemes per layer; RI-FE-006 asks for that refusal. |
| QK-R6 | **pending PR #49** | `input_tensors` null is W4A16; `fp4` dynamic is W4A4, built with bf16 activations, logged at `warn` and recorded in `metadata` (`quark.rs:176-190`, `src/lowering.rs:108`). `test_w4a4_fixtures_build_and_record_the_deviation` (`tests/mxfp4.rs:320`). A global `output_tensors` or `bias` spec is refused (`quark.rs:164-172`). `--activations` (RI-CLI-002) is not part of the PR. |
| QK-R7 | **pending PR #49** | Exact names, and `fnmatch` globs translated to anchored regexes with `*` crossing dots, as Quark matches them (`src/quant/pattern.rs:1-13, 81-97`); entries also accept `re:` patterns, which Quark does not define (a superset, harmless for Quark exports). `test_exclusions_keep_weights_bf16` (`tests/mxfp4.rs:259`) and the unit tests in `pattern.rs` (197-245). |
| QK-R8 | **missing**, in main and PR #49 (QK-2) | `algo_config` is ignored as calibration detail (`src/quant/mod.rs:12-19`). Weight-changing algorithms such as GPTQ leave weights in the same format and are harmless to import; a rotation whose part is applied online at inference is not, and is neither detected nor refused. Whether Quark's MXFP4 exports with `rotation` carry an online part was not established from the source read. |
| QK-R9 | **pending PR #49** | Packed data is `U8 [out, in/2]`, viewed as `fp4x2 [out, in]` (`src/mapping.rs:75-84, 297-308`); the CPU reference and the fixtures take the low nibble as the even element. `test_quark_fixture_of_each_family_lowers_to_mx_weights` (`tests/mxfp4.rs:111`) decodes fixture bytes through a line-for-line port of `Pack_fp4.unpack` and the CPU reference. |
| QK-R10 | **pending PR #49** | `<module>.weight_scale` `U8 [out, in/32]` becomes a `ue8m0` scale weight, its shape checked against the data (`src/mapping.rs:310-320`); the manifest data entry names it (`:268-296`); each projection reads a `dequantize` of data and scales (`src/arch/llama/graph.rs:333-345`). `test_manifest_names_data_and_scale_of_every_mx_weight` (`tests/mxfp4.rs:184`), `test_bad_mx_tensors_are_refused_naming_the_tensor` (`:587`), `test_each_mx_projection_reads_a_dequantize_of_its_weight` (`:140`). |

## KV scales (RI-FE-006, RI-KVC-008)

Beyond the listed fields, RI-FE-006 requires a Quark KV quantization
(`kv_cache_quant_config`, or `output_tensors` on `k_proj` and `v_proj`) to
supply the fp8 KV scales when `--kv-dtype fp8` is selected. PR #49 detects
it and ignores the scale tensors with an `info` line, leaving the feed to
issue #37 (`src/quant/quark.rs:9-13`); PR #48 (#37) fills unit scales and
lists the checkpoint scales as "#35 frontend" work. Neither PR does it
(QK-3). On main the scale slot now exists (PR #48, `plan.rs:79-125`); the
feed from the checkpoint is claimed by PR #49 at `fd03bc1`.

## Result

Nothing conforms on main `b99720a`. State: **gap**. With PR #49 merged, QK-R1, R2, R4
to R7, R9 and R10 would conform, QK-R8 would stay missing. Gaps on the
[tracker](std-quark-tracker.html).
