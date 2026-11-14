---
title: "compressed-tensors 0.13.0"
navtitle: Overview
section: Standards
group: "Model formats / compressed-tensors 0.13.0"
order: 50
summary: The compressed-tensors mxfp4-pack-quantized checkpoint format (llm-compressor), as rustinfer imports it under RI-FE-006, measured against compressed-tensors 0.13.0.
---

# compressed-tensors 0.13.0

**Scope** (SRS §1.4, CT): the `mxfp4-pack-quantized` format, read by
RI-FE-006. The SRS pins "0.13.0 or later" (0.13.0 tagged 2025-12-16).
**Conformance:** mandatory from **R1** (RI-FE-006, ADR-010).

**Implementation:** none on origin/main `ccf02b3`: `quantization_config` is
not read and a compressed-tensors checkpoint is refused through its tensor
dtypes. The safetensors reader and Sluice on main already handle its `U8`
tensors (PR #47, merged). The import is in **PR #49**
(`feat/35-mxfp4-checkpoints`, head `de19390`, issue #35):
`crates/rustinfer-frontend/src/quant/ct.rs` and `quant/pattern.rs`.

**Source:** compressed-tensors, https://github.com/vllm-project/compressed-tensors
at tag `0.13.0` (commit 797d3019ef68): `config/base.py`, `config/format.py`,
`quantization/quant_config.py`, `quantization/quant_args.py`,
`quantization/quant_scheme.py`, `quantization/utils/mxfp4_utils.py`,
`compressors/quantized_compressors/fp4_quantized.py` and `utils/match.py`
(all under `src/compressed_tensors/`). The `MXFP4xFP8` preset RI-FE-006 names
is not in 0.13.0; it appears later (commit 70e7167, `quant_scheme.py:244`),
which "or later" admits. Transformers' wrapper `CompressedTensorsConfig`
(v5.23.0, `utils/quantization_config.py:1095-1170`) documents the same
fields. Local copies: `specs/model-formats/ct-0.13.0-*`.

| | |
|---|---|
| Pages | [requirements](std-ct-requirements.html) · [audit](std-ct-audit.html) · [tracker](std-ct-tracker.html) |
| Audited | 2026-11-13, by reading the compressed-tensors source, origin/main and PR #49 |
| On main | nothing imported; every requirement is missing or pending PR #49 |
| PR #49 | format, presets, tensors, nibble order and scale bias read as compressed-tensors writes them |
| `ignore` | PR #49 matches globs and skips class names, where compressed-tensors matches exact names, `re:` and class names |
