---
title: "compressed-tensors 0.13.0 requirements"
navtitle: Requirements
section: Standards
group: "Model formats / compressed-tensors 0.13.0"
order: 51
summary: What a compressed-tensors mxfp4-pack-quantized checkpoint holds and means, from the 0.13.0 source.
---

# compressed-tensors 0.13.0 requirements

Source: compressed-tensors at tag 0.13.0 (local copies
`specs/model-formats/ct-0.13.0-*`; paths under `src/compressed_tensors/`).
The format is defined by code; items cite file and line.

## `quantization_config`

| id | requirement | source |
|---|---|---|
| CT-R1 | `QuantizationConfig` holds `config_groups`, `quant_method` (`compressed-tensors`), `kv_cache_scheme`, `format`, `quantization_status`, `global_compression_ratio` and `ignore`. | `quantization/quant_config.py:104-143` |
| CT-R2 | `format` `mxfp4-pack-quantized` is the format of 4-bit float weights in groups of 32; 4-bit float with another group size is `nvfp4-pack-quantized`. | `config/base.py:36-37`; `config/format.py:52-55` |
| CT-R3 | `quantization_status` `compressed`: "weights have been converted to their target type". Other states (`initialized`, `calibration`, `frozen`) hold weights in their original precision. | `quantization/quant_config.py:38-50` |
| CT-R4 | Each config group gives `targets`, `weights`, optional `input_activations` and `output_activations`, as `QuantizationArgs`: `num_bits`, `type`, `symmetric`, `group_size`, `strategy`, `block_structure`, `dynamic`, `actorder`, `scale_dtype`, `zp_dtype`. | `quantization/quant_args.py:178-187` |
| CT-R5 | Presets: **MXFP4A16**, weights `num_bits` 4, `type` float, `strategy` group, `group_size` 32, static, symmetric, `scale_dtype` uint8; **MXFP4**, the same weights plus dynamic group-32 4-bit float `input_activations`. (Later releases add **MXFP4xFP8**: 8-bit float activations.) | `quantization/quant_scheme.py:195-229, 383-384` |
| CT-R6 | `ignore` lists "layer names or types to not quantize, supports regex prefixed by 're:'": an entry matches a module when it equals the module name, when it is `re:<pattern>` and `re.match` finds the pattern at the start of the name, or when it equals the name of one of the module's classes (`Linear` also matching vLLM's `LinearBase`). | `utils/match.py:353-390, 421-469`; Transformers `utils/quantization_config.py:1110-1111` |
| CT-R7 | `kv_cache_scheme`, when set, quantizes the KV cache; `None` means it is not quantized. | `quantization/quant_config.py:136`; Transformers `utils/quantization_config.py:1106-1107` |

## Tensors

| id | requirement | source |
|---|---|---|
| CT-R8 | A quantized `Linear` stores `<module>.weight_packed`, `uint8` of shape `[out, in/2]`, and `<module>.weight_scale`. | `compressors/quantized_compressors/fp4_quantized.py:51-82, 110-118` |
| CT-R9 | `pack_fp4_to_uint8` maps each value to its 4-bit E2M1 index (sign in bit 3) and packs consecutive pairs as `index[0] | index[1] << 4`: the **low nibble is the even element**. | `fp4_quantized.py:160-201` |
| CT-R10 | The MXFP4 scale is stored as an unsigned 8-bit exponent with **bias 127** (`127 + floor(log2(scale)) - 2` at compression; `scale - 127` when read back), `scale_dtype` `uint8`: one byte per group of 32 along the input axis, shape `[out, in/32]`. | `fp4_quantized.py:143-150`; `quantization/utils/mxfp4_utils.py:37-50, 90-103` |
