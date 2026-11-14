---
title: "Transformers config v5.23.0 requirements"
navtitle: Requirements
section: Standards
group: "Model formats / Transformers config v5.23.0"
order: 21
summary: What a Transformers v5.23.0 config.json means for the LLaMA family, in rustinfer's scope: model_type, the RI-FE-001 fields and quantization_config.
---

# Transformers config v5.23.0 requirements

Source: Transformers v5.23.0 source, local copies in
`specs/model-formats/transformers-v5.23.0-*`. The configuration is defined by
code, not by a numbered specification; items cite file and line at the tag.
"Defaults" are the dataclass defaults a value takes when `config.json` omits
the key.

## `model_type` (RI-FE-003)

| id | requirement | source |
|---|---|---|
| HFC-R1 | `model_type` names the configuration class: `llama`, `mistral`, `qwen2`, `qwen3` for the R1 families. An unknown value is "Unrecognized model type" in Transformers; rustinfer refuses it naming it and the supported list. | `configuration_llama.py:46`, `configuration_qwen3.py:41`; `configuration_utils.py:217-225` |

## Architecture fields of RI-FE-001

| id | field | meaning and default per family | source |
|---|---|---|---|
| HFC-R2 | `num_hidden_layers`, `hidden_size`, `intermediate_size`, `vocab_size`, `num_attention_heads` | sizes; each family has a default (Llama 32, 4096, 11008, 32000, 32) | `configuration_llama.py:64-68` and the same fields in the other three |
| HFC-R3 | `num_key_value_heads` | KV heads. Default: Llama `None`, then `num_attention_heads`; Mistral **8**; Qwen2 and Qwen3 **32** | `configuration_llama.py:69, 89-90`; `configuration_mistral.py:68`; `configuration_qwen2.py:66`; `configuration_qwen3.py:67` |
| HFC-R4 | `head_dim` | Llama and Mistral: `None`, then `hidden_size // num_attention_heads`; Qwen3: **128**; Qwen2 has no field (the model uses `hidden_size // num_attention_heads`) | `configuration_llama.py:84-88`; `configuration_mistral.py:69, 84`; `configuration_qwen3.py:68` |
| HFC-R5 | `rms_norm_eps` | default 1e-6 in all four | `configuration_llama.py:73` and others |
| HFC-R6 | `tie_word_embeddings` | default false in all four | `configuration_llama.py:79` and others |
| HFC-R7 | `hidden_act` | default `silu` | `configuration_llama.py:70` |
| HFC-R8 | `attention_bias`, `mlp_bias` | Llama: both, default false; Qwen3: `attention_bias`; Mistral none; Qwen2 has fixed q, k, v biases | `configuration_llama.py:81-83`; `configuration_qwen3.py:76` |
| HFC-R9 | `sliding_window`, `use_sliding_window`, `max_window_layers`, `layer_types` | Mistral `sliding_window` default **4096**; Qwen2 and Qwen3 apply `sliding_window` only under `use_sliding_window`, and then only to layers from `max_window_layers` on | `configuration_mistral.py:80`; `configuration_qwen3.py:77-80, 86-97` |
| HFC-R10 | `max_position_embeddings` | Llama 2048, Mistral 131072, Qwen 32768 | `configuration_llama.py:71`; `configuration_mistral.py:71`; `configuration_qwen3.py:70` |

## Rotary parameters (RI-FE-001: "RoPE parameters and scaling")

| id | requirement | source |
|---|---|---|
| HFC-R11 | In v5 the rotary parameters live in **`rope_parameters`**, a dict with `rope_type` (default `default`), `rope_theta` (default `default_theta`, 10000.0), optional `partial_rotary_factor`, and the scaling keys (`factor`, `original_max_position_embeddings`, `low_freq_factor`, `high_freq_factor`, `beta_fast`, `beta_slow`, `attention_factor`, ...). Every family declares `rope_parameters` and no `rope_theta` field. | `modeling_rope_utils.py:679-753, 760`; `configuration_llama.py:80` |
| HFC-R12 | The v4 layout is read for backward compatibility: a top-level `rope_scaling` becomes `rope_parameters`, a top-level `rope_theta` and `partial_rotary_factor` move into it, and a legacy `type` key gives `rope_type`. | `modeling_rope_utils.py:775-804, 806-843` (line 825); `configuration_utils.py:472-479, 720-733` |
| HFC-R13 | `rope_type` is one of `default`, `linear`, `dynamic`, `yarn`, `longrope`, `llama3`, `proportional` (and `axial`); `factor` is at least 1. For `llama3`, `yarn` and `longrope`, a missing `original_max_position_embeddings` defaults to `max_position_embeddings`. | `modeling_rope_utils.py:666-676, 686-687, 835-843, 1059` |
| HFC-R14 | A v5 `save_pretrained` writes `config.json` with `to_json_string(use_diff=True)`: keys equal to the base `PreTrainedConfig` default may be dropped, while model-specific keys are kept. A reader takes an absent key at the class default. | `configuration_utils.py:785, 1199-1242, 1311-1330` |

## `quantization_config`

| id | requirement | source |
|---|---|---|
| HFC-R15 | A quantized checkpoint's `config.json` carries `quantization_config`, an object whose `quant_method` selects the method; the v5.23.0 values include `quark`, `compressed-tensors`, `mxfp4`, `fp8`, `gptq`, `awq`, `gguf`, `bitsandbytes`. A config with no `quant_method` (and no `load_in_*bit`) is an error in Transformers. A reader that ignores `quantization_config` reads quantized bytes as if they were plain. | `utils/quantization_config.py:43-69`; `quantizers/auto.py:161-179` |
