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
| QK-1 | Quark MXFP4 checkpoints are not imported on main: `quantization_config` is not read | QK-R1, R2, R4 to R7, R9, R10; RI-FE-006 | **In PR #49** | Issue #35. Sluice and the safetensors reader on main already handle the `U8` tensors (PR #47). |
| QK-2 | `algo_config` (rotation among others), `softmax_quant_spec` and `kv_cache_post_rope` are not checked | QK-R8 (`quantization/config/config.py:156, 229-262, 383-392`) | **Open** | Also open in PR #49 as of `de19390`. The way: refuse a non-null `softmax_quant_spec` and any `algo_config` entry whose `name` is not on a list known to leave nothing to do at inference (for example `gptq`, `awq`, `qronos`), naming it; settle what a Quark `rotation` leaves online. No issue yet. |
| QK-3 | Checkpoint KV scales are not fed to `--kv-dtype fp8` | RI-FE-006, RI-KVC-008 | **Open** | PR #49 leaves it to #37; PR #48 (#37) leaves it to #35. One of them has to own it; raise on #35 and #37. |
