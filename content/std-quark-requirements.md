---
title: "AMD Quark MXFP4 export (surveyed 313cb0b) requirements"
navtitle: Requirements
section: Standards
group: "Model formats / AMD Quark MXFP4 export (surveyed 313cb0b)"
order: 41
summary: What a Quark MXFP4 export holds and means, from Quark's source at 313cb0b, in the scope RI-FE-006 reads.
---

# AMD Quark MXFP4 export requirements

Source: AMD Quark at commit `313cb0b` (local copies
`specs/model-formats/quark-313cb0b-*`). Quark has no numbered format
specification; items cite file and line. Paths are under `quark/torch/`.
The element and scale encodings themselves are OCP MX v1.1 (see the OCP-MX
standard); this page covers how Quark stores and describes them.

## `quantization_config`

| id | requirement | source |
|---|---|---|
| QK-R1 | `QConfig.to_dict` writes `quant_method: "quark"`, `global_quant_config`, `exclude`, `algo_config`, `softmax_quant_spec`, `layer_type_quant_config`, `layer_quant_config`, `kv_cache_quant_config`, `kv_cache_post_rope`, `quant_mode` and `version`; the exporter adds `export` and the result is `config.json`'s `quantization_config`. | `quantization/config/config.py:229-262`; `export/api.py:326-336`; `quark_export_hf.rst` (table: "quantization configuration added in a `quantization_config` key") |
| QK-R2 | An MXFP4 weight spec (`OCP_MXFP4Spec`) is `dtype` `fp4`, `qscheme` `per_group`, `group_size` 32, `scale_format` `e8m0`, `round_method` `half_even`, `scale_type` `float`, `ch_axis` as given (-1 in the documented form: blocks along the last axis), `scale_calculation_mode` default `even`; weights are static (`is_dynamic` false in the documented form). | `quantization/config/config.py:1466-1475` (`OCP_MXSpec`), `1583-1606` (`OCP_MXFP4Spec`); `QTensorConfig` 1724-1733 ("`group_size`: ... also the block size for MX datatypes") |
| QK-R3 | `scale_calculation_mode` selects how the shared exponent was chosen at quantization; the stored scale is an E8M0 power of two whatever the mode. | `quantization/config/config.py:1597`; the E8M0 scale of OCP MX v1.1 |
| QK-R4 | `export.weight_format` defaults to `real_quantized` (packed weights) and `export.pack_method` to `reorder`. | `export/config/config.py:30-46` |
| QK-R5 | `layer_quant_config` (by layer name) and `layer_type_quant_config` (by module type) override `global_quant_config` for the layers they name; `kv_cache_quant_config` gives KV cache quantization by layer name. | `quantization/config/config.py:146-149, 183-189` |
| QK-R6 | `input_tensors` `None` in `global_quant_config` means activations are not quantized; a spec there means they were (W4A4 for an fp4 spec). `output_tensors` likewise for outputs. | `quantization/config/config.py:416-417` |
| QK-R7 | `exclude` lists module names matched "verbatim with `fnmatch.fnmatch` against the full module name", never expanded to descendants; an excluded module keeps its source dtype. | `quantization/config/config.py:151-155`; `quantization/model_transformation.py:290-360` |
| QK-R8 | `algo_config` records algorithms applied before export (GPTQ, AWQ, Qronos, rotation); after it "the datatype/fake_datatype of weights will be changed". A `rotation` with `r3` relates to KV cache quantization (an online rotation). | `quantization/config/config.py:156, 383-392` |

## Tensors

| id | requirement | source |
|---|---|---|
| QK-R9 | `Pack_fp4.pack` maps each value to its 4-bit E2M1 code, pairs codes along the last axis and stores `(code[2i+1] << 4) + code[2i]`: the **low nibble is the even element**. A packed weight `<module>.weight` is `uint8` of shape `[out, in/2]`. `pack_method` `reorder` does not change this order: `Pack_fp4` ignores its `reorder` argument. | `utils/pack.py:598-636`; `export/nn/modules/realquantizer.py:94-98, 266` |
| QK-R10 | The block scale is exported as `<module>.weight_scale`, one E8M0 byte (`uint8`) per block of 32 along the last axis: shape `[out, in/32]`. | `export/api.py:981-982` (`.weight_scale`); `export/nn/modules/realquantizer.py:548-565` (`_quantized_block_scale`); `scale_format` `e8m0` (QK-R2) |
