---
title: "compressed-tensors 0.13.0 audit"
navtitle: Audit
section: Standards
group: "Model formats / compressed-tensors 0.13.0"
order: 52
summary: The 2026-11-13 audit of rustinfer's compressed-tensors MXFP4 import, on main and in PR #49, against compressed-tensors 0.13.0.
---

# compressed-tensors 0.13.0 audit

**Audit of 2026-11-13**, against the [requirements](std-ct-requirements.html),
on origin/main `ccf02b3` and PR #49 (`feat/35-mxfp4-checkpoints`, head
`de19390`).

**Method.** Read the compressed-tensors 0.13.0 source listed on the
[overview](std-ct.html); read `crates/rustinfer-frontend/src/quant/{mod,ct,pattern}.rs`
and `src/mapping.rs` on the PR branch and its tests `tests/mxfp4.rs`;
checked main for any reading of `quantization_config` (none). The PR's
fixture configs copy the shape of `nm-testing/Meta-Llama-3-8B-Instruct-MXFP4`.
No real checkpoint was decoded and compressed-tensors was not run. Paths are
under `crates/rustinfer-frontend/` on the PR branch unless marked main.

On main every item is **missing**: `quantization_config` is never read (main
`src/config.rs:101-112`) and the `U8` tensors are refused as a dtype outside
the policy (main `tests/mapping.rs:125`).

| id | result | evidence (PR #49) |
|---|---|---|
| CT-R1 | **pending PR #49** | `quant_method` `compressed-tensors` dispatches to `ct::parse` (`src/quant/mod.rs:187-199`); `format`, `quantization_status`, `config_groups`, `ignore` and `kv_cache_scheme` are read (`src/quant/ct.rs:36-59`). |
| CT-R2 | **pending PR #49** | `mxfp4-pack-quantized` accepted, an absent `format` taken as it; FP8 and int8 formats refused as R2, int4 as R3, `nvfp4-pack-quantized` as unscheduled, others naming the field (`ct.rs:62-82`). A group with its own other `format` is refused (`ct.rs:95-100`). `test_compressed_tensors_fields_outside_mxfp4_are_refused_naming_the_field` (`tests/mxfp4.rs:524`). Taking an absent `format` as MXFP4 is looser than compressed-tensors, whose default is `fakequant` (`quantization/quant_config.py:101`); the group checks (CT-R5) still require MXFP4 weights. |
| CT-R3 | **pending PR #49** | `quantization_status` must be `compressed` (`ct.rs:39-40`). |
| CT-R4 | **pending PR #49** | `targets` must be exactly `["Linear"]` (`ct.rs:114-121`); `output_activations` refused (`ct.rs:103-106`); `symmetric`, `actorder`, `zp_dtype` and `block_structure` are not read, which is right for MXFP4 (symmetric, no zero point); `test_more_compressed_tensors_fields_are_refused` (`tests/mxfp4.rs:755`). |
| CT-R5 | **pending PR #49** | Weights `num_bits` 4, `type` float, `strategy` group, `group_size` 32 (else unscheduled), `scale_dtype` `torch.uint8` when given, not dynamic (`ct.rs:124-153`); activations absent (W4A16), 4-bit float (MXFP4) or 8-bit float (MXFP4xFP8), built as bf16 and reported (`ct.rs:156-167`). `test_compressed_tensors_fixture_of_each_family_lowers_to_mx_weights` (`tests/mxfp4.rs:125`), `test_w4a4_fixtures_build_and_record_the_deviation` (`:320`). |
| CT-R6 | **partial in PR #49** (CT-2) | Exact names and `re:` entries match as compressed-tensors matches them, `re:` anchored at the start only (`src/quant/pattern.rs:7-9, 89-92`). Two differences: an entry holding `*`, `?` or `[` is treated as a glob (`pattern.rs:10-12, 93-95`), where compressed-tensors compares it as an exact name; and an entry naming a module class (for example `Embedding`, or `Linear`) is not matched against classes. `test_exclusions_keep_weights_bf16` (`tests/mxfp4.rs:259`) covers names and patterns only. |
| CT-R7 | **pending PR #49** | A `kv_cache_scheme` is detected; its `k_scale` and `v_scale` tensors are tolerated and ignored with an `info` line (`ct.rs:54-59`). `test_kv_scales_are_ignored_only_under_a_kv_quantization` (`tests/mxfp4.rs:679`). Feeding them to `--kv-dtype fp8` is not done (see the Quark tracker, QK-3). |
| CT-R8 | **pending PR #49** | `<module>.weight_packed` `U8 [out, in/2]` and `<module>.weight_scale` `U8 [out, in/32]` map to an `fp4x2 [out, in]` weight and a `ue8m0` scale (`src/quant/mod.rs:41-43`; `src/mapping.rs:268-320`). `test_manifest_names_data_and_scale_of_every_mx_weight` (`tests/mxfp4.rs:184`), `test_bad_mx_tensors_are_refused_naming_the_tensor` (`:587`). |
| CT-R9 | **pending PR #49** | Low nibble first, the order of the CPU reference and of the fixture bytes (`tests/common/mxfp4.rs`); the fixture test of CT-R5 checks dequantized values equal values written into the fixture. |
| CT-R10 | **pending PR #49** | The scale byte is read as `ue8m0`, `2^(e-127)`, the same bias as compressed-tensors' `scale - 127`. |

## Result

Nothing conforms on main. State: **gap**. With PR #49 merged, every item
but CT-R6 would conform; CT-R6 would be partial. Gaps on the
[tracker](std-ct-tracker.html).
