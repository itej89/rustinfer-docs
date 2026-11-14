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

**Implementation:** `crates/rustinfer-frontend` on origin/main `8c7d47e`.
`ModelConfig::from_json_with_limits` bounds the text, parses it as a JSON
object and looks `model_type` up in the architecture registry
(`src/config.rs:112-145`; registry `src/arch/mod.rs:135, 162`). The LLaMA family
(`llama`, `mistral`, `qwen2`, `qwen3`) reads its fields in
`src/arch/llama/config.rs`: geometry (149-192), `rms_norm_eps` with its Hugging Face default (18-19,
294), the rotary parameters from the v5 `rope_parameters` or the v4
`rope_theta` and `rope_scaling`, refusing a config whose two forms disagree
(465-604, PR #52) and a `partial_rotary_factor` other than 1 (611-645, PR #55),
biases (222-244), sliding window (417-432) and `hidden_act` (406-415). Keys a family does not use are ignored. `quantization_config` is
read before `model_type` (`src/config.rs:130-145`, `src/quant/mod.rs:197-235`,
PR #49): Quark and compressed-tensors MXFP4 are imported, every other method
refused naming its release.

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
| Audited | 2026-11-13 on `ccf02b3` and `b99720a`; re-audited 2026-11-14 on origin/main `8c7d47e` (PRs #55, #53, #49), by reading the frontend and its tests against the v5.23.0 source |
| `model_type`, geometry, norm, biases | conform |
| RoPE | reads the v5 `rope_parameters` and the v4 `rope_theta`, `rope_scaling`, refusing disagreeing forms (fixed in `b99720a`); a `partial_rotary_factor` other than 1 is refused (HFC-5, fixed in `6a18042`); `llama3`, `yarn`, `dynamic` are R2 (HFC-4) |
| `quantization_config` | read and dispatched by `quant_method` (HFC-3, fixed in `8c7d47e`) |
