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
| CT-1 | compressed-tensors MXFP4 checkpoints are not imported on main | CT-R1 to CT-R10; RI-FE-006 | **In PR #49** | Issue #35. |
| CT-2 | `ignore` entries are matched with Quark's rules: glob characters make a glob, and class names are not matched | CT-R6 (`utils/match.py:353-469`) | **Open** | Also open in PR #49 as of `de19390`. The way: give `Patterns::parse` the source, so compressed-tensors entries are exact or `re:` only, and refuse (or map, for `Linear`) an entry that names a module class, naming it. Raise on #35. |
