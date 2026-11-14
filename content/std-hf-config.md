---
title: "Transformers config v5.23.0"
navtitle: Overview
section: Standards
group: "Model formats / Transformers config v5.23.0"
order: 20
summary: Hugging Face Transformers model configuration (config.json) at v5.23.0: model_type, the LLaMA-family architecture fields and quantization_config, as rustinfer's frontend reads them.
---

# Transformers config v5.23.0

**Scope** (SRS §1.4, HF-CONFIG): `model_type`, the architecture fields of
RI-FE-001 and `quantization_config`. `generation_config.json` is named in the
reference title but no R1 requirement reads it.
**Conformance:** mandatory from **R1**. Cited by RI-FE-001, RI-FE-003,
RI-FE-004, RI-ART-008 and RI-SEC-003.

**Implementation:** `crates/rustinfer-frontend` on origin/main `ccf02b3`.
`ModelConfig::from_json_with_limits` bounds the text, parses it as a JSON
object and looks `model_type` up in the architecture registry
(`src/config.rs:83-112`; registry `src/arch/mod.rs:121`). The LLaMA family
(`llama`, `mistral`, `qwen2`, `qwen3`) reads its fields in
`src/arch/llama/config.rs`: geometry (139-182), `rms_norm_eps` and
`rope_theta` with Hugging Face defaults (18-23, 279-294), `rope_scaling`
(405-477), biases (212-233), sliding window (391-403) and `hidden_act`
(378-387). Keys a family does not use are ignored. `quantization_config` is
not read on main; PR #49 (branch `feat/35-mxfp4-checkpoints`, head
`de19390`) adds it.

**Source:** Hugging Face Transformers **v5.23.0**: the configuration page
https://huggingface.co/docs/transformers/v5.23.0/en/main_classes/configuration
(its body is generated from `PreTrainedConfig`), and the source at tag
v5.23.0: `configuration_utils.py`, `modeling_rope_utils.py`,
`models/{llama,mistral,qwen2,qwen3}/configuration_*.py` and
`utils/quantization_config.py`. Local copies in `specs/model-formats/`
(`transformers-v5.23.0-*`).

| | |
|---|---|
| Pages | [requirements](std-hf-config-requirements.html) · [audit](std-hf-config-audit.html) · [tracker](std-hf-config-tracker.html) |
| Audited | 2026-11-13, by reading the frontend and its tests on origin/main and PR #49 against the v5.23.0 source |
| `model_type`, geometry, norm, biases | conform |
| RoPE | reads the v4 layout (`rope_theta`, `rope_scaling`) only; a v5 `rope_parameters` config is lowered with the default theta, silently |
| `quantization_config` | ignored on main; pending PR #49 |
