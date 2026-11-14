---
title: "AMD Quark MXFP4 export (surveyed 313cb0b) tracker"
navtitle: Tracker
section: Standards
group: "Model formats / AMD Quark MXFP4 export (surveyed 313cb0b)"
order: 43
summary: Gaps between rustinfer and the Quark MXFP4 export.
---

# AMD Quark MXFP4 export tracker

Gaps found by the [audit](std-quark-audit.html) of 2026-11-13.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| QK-1 | Quark MXFP4 checkpoints are not imported on main: `quantization_config` is not read | QK-R1, R2, R4 to R7, R9, R10; RI-FE-006 | **In PR #49** | Issue #35; PR head `fd03bc1`. Sluice and the safetensors reader on main already handle the `U8` tensors (PR #47, `ccf02b3`). Still unread on main `b99720a`. |
| QK-2 | `algo_config` (rotation among others), `softmax_quant_spec` and `kv_cache_post_rope` are not checked | QK-R8 (`quantization/config/config.py:156, 229-262, 383-392`) | **In PR #49** | Open on main `b99720a`, and in PR #49 as of `de19390`. Head `fd03bc1` claims it: `src/quant/quark_algo.rs` accepts only algorithms whose weights load as plain MXFP4 and refuses online rotations, `quarot` and `svdquant` naming the field; `softmax_quant_spec` and `kv_cache_post_rope` true are refused (`src/quant/quark.rs:49, 92`, tests `tests/mxfp4_audit.rs:309, 359`, per the PR's precision table). To be audited when it merges. |
| QK-3 | Checkpoint KV scales are not fed to `--kv-dtype fp8` | RI-FE-006, RI-KVC-008 | **In PR #49** | Ownership settled: PR #48 (merged `e218b8a`) added the per-layer `KvScales` of the plan's KV geometry, unit until a frontend replaces them (`crates/rustinfer-artifact/src/plan.rs:79-125`, `tests/kv_geometry.rs:133`); PR #49 at `fd03bc1` reads the Quark `output_scale` and compressed-tensors `k_scale`/`v_scale` tensors into them (`src/kv_scales.rs`, `src/mapping.rs:99`, tests `tests/mxfp4_audit.rs:69, 149`, per its precision table). Still unit scales on main. |
