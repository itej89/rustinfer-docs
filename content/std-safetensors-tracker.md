---
title: "safetensors v0.8.0 tracker"
navtitle: Tracker
section: Standards
group: "Model formats / safetensors v0.8.0"
order: 13
summary: Gaps between rustinfer's safetensors header reader and the v0.8.0 format; ST-2 closed by PR #52, ST-3 and ST-4 by PR #57; ST-1 open.
---

# safetensors v0.8.0 tracker

Gaps found by the [audit](std-safetensors-audit.html) of 2026-11-13,
re-audited against `origin/main` `8c7d47e` on 2026-11-14 after PRs #55, #53
and #49 merged, then against `99c1ec7` on the same day after PR #57 (issue #51).
ST-2 was fixed by PR #52 (merge `b99720a`), ST-3 and ST-4 by PR #57 (merge
`99c1ec7`), all under issue #51; no GitHub issue covers ST-1 yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| ST-1 | The first header byte is not checked to be `{`; leading whitespace is accepted | README 78 ("MUST begin with a `{`") | **Open** | One byte check in `parse_object` (`crates/rustinfer-artifact/src/safetensors.rs:621-635`). The reference reader is as lenient, so real files are unaffected; the check matters only for refusing files no conforming writer makes. |
| ST-2 | Duplicate keys in the header were accepted; the last entry won | README 87 ("Duplicate keys are disallowed") | Fixed 2026-11-13 b99720a | PR #52 (issue #51). The header is parsed through a visitor that refuses a repeated key at any level, naming it (`crates/rustinfer-artifact/src/unique_json.rs:24-26, 83-90`; `parse_unique`, `crates/rustinfer-artifact/src/safetensors.rs:577-585`). Tests: `crates/rustinfer-artifact/tests/safetensors_duplicates.rs:37` (a tensor named twice), `:47` (nested keys), `Verifies RI-SEC-003`. The test at `:71`, named for keys compared after unescaping, writes no escape (see the audit, ST-R8); the behaviour holds by construction. |
| ST-3 | `U8` was read as Model IR `ue8m0`, not as an unsigned byte | `tensor.rs` `enum Dtype` (`U8`: "Unsigned byte") | Fixed 2026-11-14 99c1ec7 | Issue #51, PR #57. The reader types `U8` as `StoredDtype::U8`, raw bytes with no Model IR dtype (`crates/rustinfer-artifact/src/safetensors.rs:71-81`, `parse_dtype` `:511-530`, `U8` at `:516-518`); `F8_E8M0` still reads as `ue8m0`. The frontend gives it a type only by role: packed data as `U8` with the innermost axis halved or `F4`, any other dtype, `F8_E8M0` included, refused naming the tensor and `dtype` (`check_packed`, `crates/rustinfer-frontend/src/mapping.rs:319-334`); a scale as `U8` or `F8_E8M0` (`check_scale`, `:337-348`); anywhere else `model_dtype` refuses it as `InvalidTensor` naming the tensor and `dtype` (`:256-269`). Sluice accepts a `U8` header only under a `ue8m0` or packed `fp4x2` entry (`header_shape`, `crates/rustinfer-sluice/src/plan.rs:323-341`). Tests: `test_u8_reads_as_raw_bytes_without_a_model_ir_dtype` (`crates/rustinfer-artifact/tests/safetensors.rs:153`, `Verifies RI-SEC-003`); `test_u8_tensor_where_bf16_is_expected_is_refused_naming_tensor_and_field` (`crates/rustinfer-frontend/tests/mapping.rs:146`, `Verifies RI-FE-002`); `test_u8_kv_scale_is_refused_naming_tensor_and_field` (`crates/rustinfer-frontend/tests/mxfp4_audit.rs:234`), `test_e8m0_tensor_in_a_packed_data_slot_is_refused` (`:258`); `test_u8_header_under_a_bf16_entry_is_refused` (`crates/rustinfer-sluice/tests/mxfp4.rs:727`), `test_e8m0_header_under_a_packed_fp4x2_entry_is_refused` (`:756`). |
| ST-4 | No test of an empty tensor (a zero dimension); a 0-rank tensor was exercised only through the frontend | README 94-98 | Fixed 2026-11-14 99c1ec7 | Issue #51, PR #57. Code unchanged in substance: the element count folds the shape from 1 with `checked_mul`, so `[]` is one element and a zero dimension zero, beside a huge one too (`tensor_bytes`, `crates/rustinfer-artifact/src/safetensors.rs:612-617`). Tests in `crates/rustinfer-artifact/tests/safetensors.rs`, all `Verifies RI-SEC-003`: `test_empty_tensor_with_a_zero_dimension_and_zero_bytes_is_accepted` (`:192`: alone in a shard with no data, between two tensors, two zero-length tensors at one offset, `[0, u64::MAX]`); `test_zero_rank_tensor_is_one_element` (`:226`); `test_empty_tensor_where_the_format_refuses_it_is_refused` (`:249`: a non-empty range for zero elements, a zero-byte range inside another tensor or past the data region). Sluice refuses a weight over an empty tensor naming the `shape` field: `test_weight_over_an_empty_tensor_is_refused_at_open` (`crates/rustinfer-sluice/tests/refusal.rs:508`, `Groundwork for RI-WST-005`). |
