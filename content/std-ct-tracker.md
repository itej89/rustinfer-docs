---
title: "compressed-tensors 0.13.0 tracker"
navtitle: Tracker
section: Standards
group: "Model formats / compressed-tensors 0.13.0"
order: 53
summary: Gaps between rustinfer and the compressed-tensors mxfp4-pack-quantized format.
---

# compressed-tensors 0.13.0 tracker

Gaps found by the [audit](std-ct-audit.html) of 2026-11-13. KV scales from
a `kv_cache_scheme` are tracked once, as QK-3 on the
[Quark tracker](std-quark-tracker.html).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| CT-1 | compressed-tensors MXFP4 checkpoints are not imported on main | CT-R1 to CT-R10; RI-FE-006 | **In PR #49** | Issue #35; PR head `fd03bc1`. Still unread on main `b99720a`; the `U8` tensors are handled by the safetensors reader and Sluice (PR #47, `ccf02b3`). |
| CT-2 | `ignore` entries are matched with Quark's rules: glob characters make a glob, and class names are not matched | CT-R6 (`utils/match.py:353-469`) | **In PR #49** | Open in PR #49 as of `de19390`. Head `fd03bc1` claims it: `re:` by `re.match`, any other entry an exact module name or the class of the module or a base, no globs, with LLaMA projections and `lm_head` declared `Linear` and the embedding `Embedding` (`ExpectedTensor::module_class`), per the PR description. To be audited when it merges. |
