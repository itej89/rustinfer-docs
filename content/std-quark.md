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

**Implementation:** on origin/main since PR #49 (issue #35, merge
`8c7d47e`): `crates/rustinfer-frontend/src/quant/quark.rs` (the
`quantization_config` fields), `quant/quark_algo.rs` (`algo_config`),
`quant/pattern.rs` (`exclude`), `src/mapping.rs` (packed `U8` data as
`fp4x2`, `weight_scale` as `ue8m0`) and `src/kv_scales.rs` (checkpoint KV
scales into the fp8 KV group's `KvScales`). The shared safetensors reader
types `U8` for MXFP4 (`crates/rustinfer-artifact/src/safetensors.rs:51-63`)
and Sluice streams the packed data with its scales (PR #47).

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
| Audited | 2026-11-14, by reading Quark's source and origin/main `8c7d47e` (after PR #49); first audited 2026-11-13 on `b99720a` and PR #49 at `de19390` |
| Result | every in-scope item conforms (QK-R3 not applicable); state **works** |
| KV scales | Quark `output_scale` KV tensors fill the fp8 KV group's per-layer `KvScales` (`src/kv_scales.rs`); no command calls it until `rustinfer build` lands (RI-CLI-002) |
| Open gaps | 0 |
