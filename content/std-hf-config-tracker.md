---
title: "Transformers config v5.23.0 tracker"
navtitle: Tracker
section: Standards
group: "Model formats / Transformers config v5.23.0"
order: 23
summary: Gaps between the frontend's config.json reading and Transformers v5.23.0.
---

# Transformers config v5.23.0 tracker

Gaps found by the [audit](std-hf-config-audit.html) of 2026-11-13.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| HFC-1 | `rope_parameters` (the v5 layout) is not read; a v5 config lowers with theta 10000 and no scaling, with no error | `modeling_rope_utils.py:679-760`; RI-FE-001 | **Open** | The most serious finding: silent wrong output for any checkpoint re-saved with Transformers 5. The way: read `rope_parameters` first (flat form; refuse the per-layer nested form by name), fall back to `rope_theta` and `rope_scaling`, refuse a config that has both and disagrees, and refuse `partial_rotary_factor` other than 1 naming it. Add a v5 fixture per family. No issue yet. |
| HFC-2 | Defaults for absent keys follow Llama for every family: `num_key_value_heads` (Mistral 8, Qwen 32), Qwen3 `head_dim` 128, Mistral `sliding_window` 4096, `max_position_embeddings` | `configuration_mistral.py:68-80`; `configuration_qwen2.py:66-75`; `configuration_qwen3.py:67-78` | **Open** | Real exports write these keys, so the risk is hand-made or trimmed configs. The way: per-family defaults in `src/arch/llama/config.rs`, or refuse the absent key naming it. No issue yet. |
| HFC-3 | `quantization_config` is not read on main | `utils/quantization_config.py:43-69`; RI-FE-006 | **In PR #49** | PR #49 parses it, imports Quark and compressed-tensors MXFP4 and refuses other methods naming their release. Issue #35. |
| HFC-4 | `rope_type` `llama3`, `yarn` and `dynamic` are refused | `modeling_rope_utils.py:666-676`; RI-FE-001 | **Later release R2** | The R1 gap RI-FE-001 names: Model IR v1 carries linear scaling only. Issue #31 (static frequency-table attribute on `rope`). |
