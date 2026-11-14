---
title: "Transformers config v5.23.0 audit"
navtitle: Audit
section: Standards
group: "Model formats / Transformers config v5.23.0"
order: 22
summary: The 2026-11-13 audit of the frontend's config.json reading against Transformers v5.23.0, re-read at b99720a after the v5 rope_parameters fix.
---

# Transformers config v5.23.0 audit

**Audit of 2026-11-13**, against the [requirements](std-hf-config-requirements.html),
on origin/main `b99720a` (re-audited after PR #52, which reads the v5
`rope_parameters`; first audit on `ccf02b3`), with PR #49
(`feat/35-mxfp4-checkpoints`, head `fd03bc1`) read for HFC-R15.

**Method.** Read `crates/rustinfer-frontend/src/config.rs`,
`src/fields.rs`, `src/arch/llama/config.rs` and `src/arch/llama/graph.rs`,
and the tests `tests/config.rs`, `tests/lower.rs`, `tests/mapping.rs`,
`tests/rope_parameters.rs` (PR #52) and the
four fixtures `tests/fixtures/*/config.json`; compared each field with the
v5.23.0 class definitions and RoPE standardization. The fixtures are
Transformers 4.51 exports (`"transformers_version": "4.51.0"`, top-level
`rope_theta` and `rope_scaling`); the v5 layout is covered by the configs
`tests/rope_parameters.rs` writes. Tests were not
run. Paths below are under `crates/rustinfer-frontend/` unless given in full.

## `model_type`

| id | result | evidence |
|---|---|---|
| HFC-R1 | **conforms** | `model_type` is read first and looked up in the registry; an unknown one is `UnsupportedModelType` naming it and `SUPPORTED_MODEL_TYPES` (`src/config.rs:101-112`, `src/arch/mod.rs:121`). `test_gpt2_is_refused_with_the_supported_list` (`tests/config.rs:113`), `test_missing_model_type_is_named` (`:138`), `test_family_names_round_trip` (`:526`). |

## Architecture fields

| id | result | evidence |
|---|---|---|
| HFC-R2 | **conforms** | Each size is required, a positive integer under its bound (`src/arch/llama/config.rs:145-177`). Requiring them where Transformers has defaults is stricter, and harmless: they are model-specific keys, always written by `save_pretrained` (HFC-R14). `test_each_required_field_is_named_when_missing` (`tests/config.rs:151`), `test_out_of_range_dimension_is_named` (`:201`), `test_dimension_limit_is_inclusive` (`:217`), `test_layers_over_the_limit_are_refused` (`:235`), `test_head_geometry_must_divide` (`:253`). |
| HFC-R3 | **partial** (HFC-2) | An absent `num_key_value_heads` defaults to `num_attention_heads` for every family (`config.rs:148`). Right for Llama; Transformers gives Mistral 8 and Qwen2 and Qwen3 32. `test_kv_heads_and_head_dim_default_when_absent` (`tests/config.rs:100`) covers Llama only. |
| HFC-R4 | **partial** (HFC-2) | An absent `head_dim` is `hidden_size / num_attention_heads` (`config.rs:178-188`). Right for Llama, Mistral and Qwen2; Qwen3's default is 128. |
| HFC-R5 | **conforms** | Default 1e-6 (`config.rs:19, 290`); non-finite or non-positive refused. `test_llama_config_parses_every_field` (`tests/config.rs:52`), `test_reals_must_be_positive_and_finite` (`:273`). |
| HFC-R6 | **conforms** | Default false (`config.rs:292`); a tied checkpoint expects no `lm_head.weight`. `test_family_defaults_are_applied` (`tests/config.rs:80`), `test_tied_embeddings_decide_whether_lm_head_is_expected` (`tests/mapping.rs:82`). |
| HFC-R7 | **conforms** | Absent or `silu` accepted; anything else refused naming it (`config.rs:381-390`). `test_gelu_activation_is_refused` (`tests/config.rs:292`). |
| HFC-R8 | **conforms** | Per family as Transformers defines them (`config.rs:218-240`). `test_llama_biases_are_expected_when_configured` (`tests/config.rs:500`), `test_qwen2_biases_reach_the_projections` (`tests/lower.rs:220`). |
| HFC-R9 | **partial** (HFC-2) | Qwen's window applies only under `use_sliding_window`, as in Transformers, and any active window is refused as R2 (`config.rs:392-407`, `src/arch/llama/graph.rs:78-84`; `test_sliding_window_is_recorded_when_active`, `tests/config.rs:433`). But a Mistral config without `sliding_window` is read as no window, where Transformers applies 4096. A refusal of "every layer slides from `max_window_layers` on" is not needed in R1, since every active window is refused. |
| HFC-R10 | **partial** (HFC-2) | Default 2048 for every family (`config.rs:23, 164-165`); Mistral's is 131072 and Qwen's 32768. RI-FE-001 does not list this field, so the effect is limited to what reads it later. |

## Rotary parameters

| id | result | evidence |
|---|---|---|
| HFC-R11 | **partial** (HFC-5; HFC-1 fixed in `b99720a`) | `rope_parameters` is read first: theta from `rope_parameters.rope_theta`, else the top-level `rope_theta`, else 10000, and the scaling from the same object with `rope_type` defaulting to `default`, as `standardize_rope_params` does (`config.rs:440-477`, `V5_PARAMETERS` `:428-435`). A per-layer-type nested object is refused naming it, not read as the default (`:461-467`); a config carrying both forms is read only when they agree, else refused naming both fields (`check_forms_agree`, `:480-502`). `test_v5_rope_parameters_give_theta_and_scaling` (`tests/rope_parameters.rs:66`), `test_v5_defaults_follow_transformers` (`:84`), `test_disagreeing_theta_is_refused_naming_both_fields` (`:123`), `test_disagreeing_scaling_is_refused_naming_both_fields` (`:142`), `test_v5_refusals_name_the_rope_parameters_field` (`:186`), each `Verifies RI-FE-001`. Still missing: `partial_rotary_factor`, which Transformers reads from `rope_parameters` (`modeling_rope_utils.py:179-181`), is ignored in either layout (HFC-5). |
| HFC-R12 | **conforms** | Without `rope_parameters`, the top-level `rope_theta` and `rope_scaling` are read, with `rope_type` or the legacy `type` (`config.rs:440-445`, `parse_rope_scaling` `:504-510`, `rope_kind` `:514-523`). `test_rope_scaling_kinds_parse` (`tests/config.rs:306`), `test_legacy_rope_theta_and_scaling_still_read` (`tests/rope_parameters.rs:99`), `test_both_forms_that_agree_are_accepted` (`:110`). |
| HFC-R13 | **partial** | `default` and `linear` lower (`config.rs:96-108`), in either layout; `dynamic`, `yarn` and `llama3` parse and are refused as R2, the R1 gap RI-FE-001 names (HFC-4, #31): `test_only_linear_scaling_lowers_in_r1` (`tests/config.rs:400`), and in `rope_parameters` `test_v5_later_release_kinds_are_still_refused` (`tests/rope_parameters.rs:157`). `longrope` and `proportional` are refused as unknown, naming the value: `test_unknown_rope_scaling_is_refused` (`:350`). `factor` below 1 is refused (`config.rs:570-577`). For `yarn` and `llama3` an absent `original_max_position_embeddings` is an error where Transformers defaults it; moot while both are refused. |
| HFC-R14 | **partial** (HFC-2) | Keys absent from a v5 diff export take a default; rustinfer's defaults match the class defaults except those in HFC-R3, R4, R9 and R10. |

## `quantization_config`

| id | result | evidence |
|---|---|---|
| HFC-R15 | **missing on main; pending PR #49** (HFC-3) | Main never reads `quantization_config`. A quantized checkpoint is refused only through its tensor dtypes: `test_quantized_weights_are_a_later_release` (`tests/mapping.rs:157`), `test_one_fp8_tensor_in_a_llama_checkpoint_is_refused` (`:144`). PR #49 (head `fd03bc1`) parses it before `model_type` (`src/config.rs:121` on the branch), imports `quark` and `compressed-tensors` MXFP4 and refuses every other `quant_method` naming the field and its release (`src/quant/mod.rs:187-223`); `test_other_quant_methods_are_refused_naming_their_release` (`tests/mxfp4.rs:641`). |

## Result

HFC-R1, R2, R5 to R8 and R12 conform; R3, R4, R9, R10, R11, R13 and R14 are
partial; R15 is pending PR #49. The v5 `rope_parameters` layout (HFC-1, the
silent wrong-output finding) is read on main since `b99720a`; R11 stays
partial only for `partial_rotary_factor` (HFC-5). State: **partial**. Gaps on
the [tracker](std-hf-config-tracker.html).
