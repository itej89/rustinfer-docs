---
title: "compressed-tensors 0.13.0 tracker"
navtitle: Tracker
section: Standards
group: "Model formats / compressed-tensors 0.13.0"
order: 53
summary: Gaps between rustinfer and the compressed-tensors mxfp4-pack-quantized format.
---

# compressed-tensors 0.13.0 tracker

Gaps found by the [audit](std-ct-audit.html) of 2026-11-13 and closed by
PR #49 (issue #35, merge `8c7d47e`), as re-audited on `origin/main` `8c7d47e`
on 2026-11-14. KV scales from a `kv_cache_scheme` are tracked once, as QK-3
on the [Quark tracker](std-quark-tracker.html). Paths are under
`crates/rustinfer-frontend/`.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| CT-1 | compressed-tensors MXFP4 checkpoints were not imported on main | CT-R1 to CT-R10; RI-FE-006 | Fixed 2026-11-14 8c7d47e | PR #49 (issue #35). `quant_method` `compressed-tensors` dispatches to `ct::parse` (`src/quant/mod.rs:197-211`), which checks `format`, `quantization_status`, `transform_config`, every config group and `kv_cache_scheme` (`src/quant/ct.rs:36-203`); `<module>.weight_packed` `U8 [out, in/2]` becomes `fp4x2` and `<module>.weight_scale` a `ue8m0` scale (`src/quant/mod.rs:157-168`, `src/mapping.rs:270-321`). Tests: `test_compressed_tensors_fixture_of_each_family_lowers_to_mx_weights` (`tests/mxfp4.rs:125`), `test_compressed_tensors_fields_outside_mxfp4_are_refused_naming_the_field` (`:524`), `test_more_compressed_tensors_fields_are_refused` (`:755`), `test_compressed_tensors_transform_config_is_refused` (`tests/mxfp4_review.rs:148`). |
| CT-2 | `ignore` entries were matched with Quark's rules: glob characters made a glob, and class names were not matched | CT-R6 (`utils/match.py:353-469`) | Fixed 2026-11-14 8c7d47e | PR #49. Under `Dialect::CompressedTensors` an entry is `re:` (`re.match`, anchored at the start only) or a plain name matched against the module name or the module class the architecture declares; `*` is literal (`src/quant/pattern.rs:81-98, 137-157`). LLaMA projections and `lm_head` are declared `Linear`, the embedding `Embedding` (`src/arch/llama/config.rs:312, 322, 400`; `src/arch/llama/names.rs:59-61`). Tests: `test_compressed_tensors_ignore_matches_module_classes` (`tests/mxfp4_audit.rs:221`), `test_compressed_tensors_has_no_globs_and_quark_no_classes` (`:247`), `test_compressed_tensors_entries_match_names_and_classes` (`src/quant/pattern.rs:249`). |
