---
title: "safetensors v0.8.0 tracker"
navtitle: Tracker
section: Standards
group: "Model formats / safetensors v0.8.0"
order: 13
summary: Gaps between rustinfer's safetensors header reader and the v0.8.0 format.
---

# safetensors v0.8.0 tracker

Gaps found by the [audit](std-safetensors-audit.html) of 2026-11-13. ST-2
was fixed by PR #52 (issue #51, merge `b99720a`); no GitHub issue covers the
others yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| ST-1 | The first header byte is not checked to be `{`; leading whitespace is accepted | README 78 ("MUST begin with a `{`") | **Open** | One byte check in `parse_object` (`crates/rustinfer-artifact/src/safetensors.rs:557`). The reference reader is as lenient, so real files are unaffected; the check matters only for refusing files no conforming writer makes. |
| ST-2 | Duplicate keys in the header were accepted; the last entry won | README 87 ("Duplicate keys are disallowed") | Fixed 2026-11-13 b99720a | PR #52 (issue #51). The header is parsed through a visitor that refuses a repeated key at any level, naming it (`crates/rustinfer-artifact/src/unique_json.rs:24-26, 83-90`; `parse_unique`, `crates/rustinfer-artifact/src/safetensors.rs:577-585`). Tests: `crates/rustinfer-artifact/tests/safetensors_duplicates.rs:37` (a tensor named twice), `:47` (nested keys), `Verifies RI-SEC-003`. The test at `:71`, named for keys compared after unescaping, writes no escape (see the audit, ST-R8); the behaviour holds by construction. |
| ST-3 | `U8` is read as Model IR `ue8m0`, not as an unsigned byte | `tensor.rs` `enum Dtype` (`U8`: "Unsigned byte") | **Open** | Deliberate for the MXFP4 exports (RI-FE-006). Today no wrong value results, because the frontend refuses a `U8` tensor outside an MXFP4 import. Closing it needs a Model IR unsigned-byte dtype, or a reader type for `U8` that the frontend reinterprets as `fp4x2` or `ue8m0` by role. |
| ST-4 | No test of an empty tensor (a zero dimension) or a 0-rank tensor | README 94-98 | **Open** | The code handles both (`tensor_bytes`, `safetensors.rs:548-553`); a test in `crates/rustinfer-artifact/tests/safetensors.rs` would prove it, including two zero-length tensors at one offset. |
