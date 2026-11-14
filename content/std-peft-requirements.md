---
title: "PEFT v0.21.3 requirements"
navtitle: Requirements
section: Standards
group: "Model formats / PEFT v0.21.3"
order: 61
summary: What a PEFT LoRA adapter directory holds and means, from the v0.21.3 checkpoint format guide and LoRA config.
---

# PEFT v0.21.3 requirements

Source: `docs/source/developer_guides/checkpoint.md` at v0.21.3 (local copy
`specs/model-formats/peft-v0.21.3-checkpoint.md`) and
`src/peft/tuners/lora/config.py` (`specs/model-formats/peft-v0.21.3-lora-config.py`).
The guide has no numbered clauses; items cite line numbers. All items are R3.

## Files

| id | requirement | source |
|---|---|---|
| PEFT-R1 | An adapter is `adapter_model.safetensors` (or `adapter_model.bin`) holding only the adapter's parameters, plus `adapter_config.json`; loading needs both. | `checkpoint.md:25-35, 76` |
| PEFT-R2 | An adapter saved under a name other than `default` is stored in a sub-directory of that name. | `checkpoint.md:139-140` |

## `adapter_config.json`

| id | requirement | source |
|---|---|---|
| PEFT-R3 | At the minimum it holds `target_modules` and `peft_type` (`LORA` for LoRA); parameters such as `r` are in it "unless the default value is used". | `checkpoint.md:113, 189-198` |
| PEFT-R4 | LoRA fields that change the loaded weights: `r`; `lora_alpha`; `use_rslora` (scaling `lora_alpha/math.sqrt(r)` instead of `lora_alpha/r`); `rank_pattern` and `alpha_pattern` (per-layer `r` and `lora_alpha` by name or regex); `fan_in_fan_out`; `bias`; `modules_to_save`; `use_dora`; `target_modules` (a string is a regex match; a list matches exactly or by name suffix). | `lora/config.py:458-490, 524-530, 557`; `checkpoint.md:154-185` |

## LoRA tensors

| id | requirement | source |
|---|---|---|
| PEFT-R5 | Keys start with `base_model.model.`, then the module path, then `lora_A.weight` or `lora_B.weight` (`lora_embedding_A`, `lora_embedding_B` for embeddings); the adapter name (`.default`) is stripped on save. | `checkpoint.md:113-137` |
| PEFT-R6 | A DoRA adapter is a LoRA checkpoint with an extra `lora_magnitude_vector` per layer. | `checkpoint.md:142-148` |
