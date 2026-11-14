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
| HFC-1 | `rope_parameters` (the v5 layout) was not read; a v5 config lowered with theta 10000 and no scaling, with no error | `modeling_rope_utils.py:679-760`; RI-FE-001 | Fixed 2026-11-13 b99720a | PR #52 (issue #51). `parse_rope` reads `rope_parameters` first, else the v4 `rope_theta`/`rope_scaling` (`crates/rustinfer-frontend/src/arch/llama/config.rs:440-455`); theta from `rope_parameters.rope_theta`, else the top-level key, and a per-layer-type nested object refused naming it (`parse_rope_parameters`, `:461-477`); a config whose two forms disagree is refused naming both fields (`check_forms_agree`, `:480-502`). Tests: `crates/rustinfer-frontend/tests/rope_parameters.rs:66` (theta and scaling from v5), `:84` (v5 defaults), `:99` (v4 still read), `:110`, `:123`, `:142` (agreeing and disagreeing forms), `:157` (R2 kinds still refused), `:186` (refusals name the field, nested form refused), all `Verifies RI-FE-001`. `partial_rotary_factor` is still not read: HFC-5. |
| HFC-2 | Defaults for absent keys follow Llama for every family: `num_key_value_heads` (Mistral 8, Qwen 32), Qwen3 `head_dim` 128, Mistral `sliding_window` 4096, `max_position_embeddings` | `configuration_mistral.py:68-80`; `configuration_qwen2.py:66-75`; `configuration_qwen3.py:67-78` | **Open** | Real exports write these keys, so the risk is hand-made or trimmed configs. The way: per-family defaults in `src/arch/llama/config.rs`, or refuse the absent key naming it. No issue yet. |
| HFC-3 | `quantization_config` is not read on main | `utils/quantization_config.py:43-69`; RI-FE-006 | **In PR #49** | PR #49 (head `fd03bc1`) parses it, imports Quark and compressed-tensors MXFP4 and refuses other methods naming their release. Issue #35. |
| HFC-4 | `rope_type` `llama3`, `yarn` and `dynamic` are refused | `modeling_rope_utils.py:666-676`; RI-FE-001 | **Later release R2** | The R1 gap RI-FE-001 names: Model IR v1 carries linear scaling only. Issue #31 (static frequency-table attribute on `rope`). |
| HFC-5 | `partial_rotary_factor` is not read in either layout; a config with a value below 1 would rotate the whole head, with no error | `modeling_rope_utils.py:179-181` (`dim = int(head_dim * partial_rotary_factor)`, read from `rope_parameters`); RI-FE-001 | Open | Found by the re-audit of `b99720a`: no code on main names the key (`grep partial_rotary` over `crates/` finds nothing). LLaMA-family exports do not write it, so real checkpoints are unaffected; the way is to refuse a value other than 1, in `rope_parameters` or at top level, naming it. No issue yet. |
