---
title: "AMD Quark MXFP4 export (surveyed 313cb0b)"
navtitle: Overview
section: Standards
group: "Model formats / AMD Quark MXFP4 export (surveyed 313cb0b)"
order: 40
summary: The AMD Quark MXFP4 checkpoint export, as rustinfer imports it under RI-FE-006, measured against Quark's own source.
---

# AMD Quark MXFP4 export

**Scope** (SRS §1.4, QUARK): the MXFP4 export fields (`quant_method:
"quark"`, `dtype: "fp4"`, `scale_format: "e8m0"`,
`scale_calculation_mode: "even"`), read by RI-FE-006. The SRS pins no
version ("as surveyed"); this audit surveys Quark's source at commit
`313cb0b` (head of `release/0.13`, the repository's default branch on
2026-11-13).
**Conformance:** mandatory from **R1** (RI-FE-006, ADR-010).

**Implementation:** none on origin/main `ccf02b3`. The frontend does not read
`quantization_config`, so a Quark checkpoint is refused through its tensor
dtypes. The shared safetensors reader already types `U8` for MXFP4
(`crates/rustinfer-artifact/src/safetensors.rs:48-61`) and Sluice already
streams `U8`-packed data with its scales (PR #47, merged;
`crates/rustinfer-sluice/tests/mxfp4.rs:653`). The import itself is in
**PR #49** (`feat/35-mxfp4-checkpoints`, head `de19390`, issue #35):
`crates/rustinfer-frontend/src/quant/quark.rs` and `quant/pattern.rs`.

**Source:** AMD Quark, https://github.com/amd/Quark at `313cb0b78ef3`:
`quark/torch/quantization/config/config.py` (`QConfig.to_dict`,
`OCP_MXSpec`, `OCP_MXFP4Spec`, `QTensorConfig`), `quark/torch/export/config/config.py`
(`JsonExporterConfig`), `quark/torch/export/api.py`, `quark/torch/utils/pack.py`
(`Pack_fp4`), `quark/torch/quantization/model_transformation.py` and
`docs/source/pytorch/export/quark_export_hf.rst`. Quark publishes no format
specification of its `quantization_config`; the source is the reference.
Local copies: `specs/model-formats/quark-313cb0b-*`.

| | |
|---|---|
| Pages | [requirements](std-quark-requirements.html) · [audit](std-quark-audit.html) · [tracker](std-quark-tracker.html) |
| Audited | 2026-11-13, by reading Quark's source, origin/main and PR #49 |
| On main | nothing imported; every requirement is missing or pending PR #49 |
| PR #49 | reads every listed field, the packing order and `exclude` as Quark writes them; does not check `algo_config` |
| KV scales | Quark KV scales reach `--kv-dtype fp8` in neither PR #48 nor PR #49 |
