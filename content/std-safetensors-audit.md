---
title: "safetensors v0.8.0 audit"
navtitle: Audit
section: Standards
group: "Model formats / safetensors v0.8.0"
order: 12
summary: The audit of rustinfer's safetensors header reader against the v0.8.0 format, re-audited 2026-11-14 at 8c7d47e: used ranges read by header range, U8 consumed by role in the MXFP4 import.
---

# safetensors v0.8.0 audit

**Re-audit of 2026-11-14**, against the [requirements](std-safetensors-requirements.html),
on origin/main `8c7d47e`, after PRs #55, #53 (`8d58ad6`, SRS v0.4.7: the
build may read weight bytes and binds the artifact to the ranges it used) and
#49 (`8c7d47e`, Quark and compressed-tensors MXFP4 import, the first `U8`
consumer) merged. The reader itself (`safetensors.rs`) is unchanged since
`b99720a`. History: first audit 2026-11-13 on `ccf02b3`; re-audited on
`b99720a` after PR #52 (duplicate keys).

**Method.** Read `crates/rustinfer-artifact/src/safetensors.rs` and its
callers in the frontend and Sluice, and the tests that exercise the reader:
`crates/rustinfer-artifact/tests/safetensors.rs`,
`crates/rustinfer-artifact/tests/mx_manifest.rs`,
`crates/rustinfer-artifact/tests/safetensors_duplicates.rs` (PR #52),
`crates/rustinfer-frontend/tests/safetensors.rs` and
`crates/rustinfer-sluice/tests/refusal.rs`; for the 2026-11-14 re-audit also
the build's reads of weight bytes by header range
(`crates/rustinfer-frontend/src/kv_scales.rs`, `src/mapping.rs`), Sluice's
used-range check (`crates/rustinfer-sluice/src/checkpoint.rs`) and the tests
`crates/rustinfer-frontend/tests/mxfp4.rs`, `mxfp4_audit.rs`,
`mxfp4_kv_fp8.rs` and `crates/rustinfer-sluice/tests/used_ranges.rs`. Compared each check with the
README and with the reference reader's `read_metadata` and
`Metadata::validate`. One probe was run: a scratch program against
`serde_json` 1.0.154, the version in the workspace `Cargo.lock`, to see how
the reader's JSON step treats a duplicate key and leading whitespace. The
rustinfer test suite was not run; results are as the tests are written.

## Header layout

| id | result | evidence |
|---|---|---|
| ST-R1 | **conforms** | `header_end` reads the 8-byte prefix as `u64::from_le_bytes` (`safetensors.rs:303-308`). A short file is malformed: `test_short_prefix_is_malformed` (`crates/rustinfer-frontend/tests/safetensors.rs:142`), `test_bounds_and_malformed_headers` (`crates/rustinfer-artifact/tests/safetensors.rs:169`). |
| ST-R2 | **conforms** | Exactly `N` bytes are read (`read_prefix`, 226-242) and decoded as UTF-8 then JSON with unique keys (`parse_object`, 557-562; `parse_unique`, 577-585). `test_header_must_be_a_json_object` (`frontend/tests/safetensors.rs:199`). |
| ST-R3 | **missing** (ST-1) | `serde_json::from_str` accepts leading whitespace; the probe parsed `"  {}  "` as an empty object. No check that the first header byte is `{`. The reference reader does not check it either. |
| ST-R4 | **conforms** | Trailing whitespace is accepted by `serde_json`; a header whose length is not a multiple of eight passes: `test_unpadded_header_is_accepted_and_a_truncated_prefix_is_refused` (`crates/rustinfer-sluice/tests/refusal.rs:358`). The reader also accepts tab, CR and LF as padding, which is more than the README's 0x20. |
| ST-R5 | **conforms** | Each entry must be an object with exactly `dtype`, `shape`, `data_offsets`; a missing, mistyped or extra key is a schema fault naming the tensor and field (`parse_entry`, 410-427). `test_schema_faults_name_the_tensor_and_field` (`artifact/tests/safetensors.rs:63`), `test_malformed_entries_name_the_tensor_and_field` (`frontend/tests/safetensors.rs:218`). Refusing an extra key is stricter than the reference reader. |
| ST-R6 | **conforms** | Offsets are relative to the data region and turned into absolute byte ranges (`parse_offsets`, 507-527). `test_header_parses_into_typed_entries_and_identity` (`artifact/tests/safetensors.rs:36`), `test_offsets_are_checked_against_the_data_region_and_shape` (`frontend/tests/safetensors.rs:267`). Since `8c7d47e` the build reads bytes by these ranges: each checkpoint KV scale tensor is read at its header `byte_range` (`read_range`, `crates/rustinfer-frontend/src/kv_scales.rs:197-214`) and recorded as a used range, which Sluice re-reads and re-hashes at load (`observe_range`, `crates/rustinfer-sluice/src/checkpoint.rs:79-99`); `test_kv_scale_ranges_are_recorded_in_the_identity` (`crates/rustinfer-frontend/tests/mxfp4_kv_fp8.rs:140`) checks the recorded range is the header's and its digest that of exactly those file bytes. |
| ST-R7 | **conforms** | `__metadata__` must be an object of strings (`parse_object`, 563-571). `test_metadata_key_is_accepted_only_as_a_string_map` (`frontend/tests/safetensors.rs:377`). |
| ST-R8 | **conforms** (ST-2 fixed in `b99720a`) | The header is parsed by `unique_json::parse`, a `serde_json` visitor that refuses any object repeating a name with `duplicate key "<name>"`, at every nesting level and in the same single pass as the parse (`crates/rustinfer-artifact/src/unique_json.rs:24-26, 83-90`); the reader reports it as a malformed header naming the key (`parse_unique`, `safetensors.rs:577-585`, called from `parse_object` `:560`). Keys are compared as the decoded strings `serde_json` hands the visitor, so an escaped spelling of a name collides with the plain one by construction. `test_duplicate_tensor_name_is_refused_naming_the_key` (`crates/rustinfer-artifact/tests/safetensors_duplicates.rs:37`), `test_duplicate_nested_keys_are_refused_naming_the_key` (`:47`), each `Verifies RI-SEC-003`. Note: `test_duplicates_are_compared_after_unescaping` (`:71`) writes the same literal key `"a"` twice and no escape (its doc comment shows `"a"` and `"a"`), so the escaped case its name promises is not exercised; a one-line fix to the fixture (`"\u0061"`). |
| ST-R9 | **conforms**; empty tensor untested (ST-4) | The element count is the product of the shape, 1 for `[]` and 0 for a zero dimension (`tensor_bytes`, 548-553); a zero-length range tiles. Since `8c7d47e` a 0-rank tensor passes through the reader in the frontend's KV scale fixtures (`scalar_stored`, shape `[]`, `crates/rustinfer-frontend/tests/common/mxfp4.rs:435-451`), and `test_quark_kv_scales_are_recorded_per_layer_and_read` (`tests/mxfp4_audit.rs:69`) reads their F32 and BF16 values back bit for bit. No test builds an empty tensor (a zero dimension), nor two zero-length tensors at one offset. |
| ST-R10 | **conforms** | Sorted by start, each range begins where the last ends, the first at 0 and the last at the end of the data region (`check_contiguous`, 369-389; `check_region_end`, 392-408). `test_overlapping_ranges_are_refused_naming_both_tensors` (`frontend/tests/safetensors.rs:437`), `test_gaps_in_the_data_region_are_refused` (`:464`), `test_contiguous_ranges_pass_in_any_header_order` (`:494`), `test_gap_in_the_data_region_is_refused` (`sluice/tests/refusal.rs:463`). |
| ST-R11 | **conforms** | `END - BEGIN` must equal `storage_bytes(product(shape))` (`parse_offsets`, 516-522); overflow is refused (`test_shape_product_overflow_is_refused`, `frontend/tests/safetensors.rs:308`). For `F4` the reader requires an even innermost axis (`tensor_bytes`, 431-439), where the reference requires only an even element count: a `F4 [2, 3]` tensor valid in the format is refused. That is a narrower reading, consistent with `fp4x2` packing pairs along the innermost axis (RI-MIR-003), not a misreading. `test_safetensors_reader_types_f4_and_e8m0_with_packed_sizes` (`crates/rustinfer-artifact/tests/mx_manifest.rs:407`). |
| ST-R12 | **conforms** | Sluice reads multi-byte values with `from_le_bytes` (`crates/rustinfer-sluice/src/convert.rs:484-496`) and slices tensors row-major. |
| ST-R13 | **conforms** | `SAFETENSORS_MAX_HEADER_BYTES` is 100,000,000, the reference value (`crates/rustinfer-core/src/config/constants.rs:347`), checked before the header is allocated (`check_header_bound`, 327-336); a length past the file is `HeaderPastFile` (311-320). `test_header_over_the_bound_is_refused_before_reading` (`frontend/tests/safetensors.rs:155`), `test_header_length_is_bounded_by_the_file_size` (`:174`), `test_header_length_past_the_bound_or_the_file_is_refused` (`sluice/tests/refusal.rs:230`). |

## Dtype names

| id | result | evidence |
|---|---|---|
| ST-R14 | **conforms** for the names read | `DTYPES` (`safetensors.rs:56-67`) reads `BF16`, `F16`, `F32`, `F8_E4M3`, `F4`, `F8_E8M0`, `U8`, `I32`, `I64`, `BOOL`, spelled as `enum Dtype` spells them, with the format's bit sizes. The other twelve (`F6_E2M3`, `F6_E3M2`, `I8`, `F8_E5M2`, `F8_E4M3FNUZ`, `F8_E5M2FNUZ`, `I16`, `U16`, `U32`, `C64`, `F64`, `U64`) are refused naming the tensor and the name: `test_dtype_names_map_and_others_are_refused` (`frontend/tests/safetensors.rs:111`), `test_unknown_dtype_is_refused` (`artifact/tests/safetensors.rs:135`), `test_dtype_this_release_does_not_read_is_refused` (`sluice/tests/refusal.rs:480`). Reading a subset is allowed: the format defines names, it does not require a reader to support each. |
| ST-R15 | **partial** (ST-3) | `U8` is typed as Model IR `ue8m0`, the same as `F8_E8M0` (`safetensors.rs:51-63`), because Quark and compressed-tensors store both MXFP4 scales and packed E2M1 pairs as `U8`; `test_u8_reads_as_one_byte_ue8m0` (`crates/rustinfer-artifact/tests/safetensors.rs:151`, `Groundwork for RI-FE-006`, new in `8c7d47e`) pins that typing. Since `8c7d47e` the frontend consumes it by role: a packed-data slot accepts `ue8m0` with the innermost axis halved and gives it `fp4x2` (`check_packed`, `crates/rustinfer-frontend/src/mapping.rs:297-309`; `map_mx`, `:270-295`), a scale slot requires `ue8m0` (`check_scale`, `:311-322`). The format's `U8` is an unsigned byte with no exponent meaning, and the reader keeps no trace of which name the file used: an `F8_E8M0` tensor in a packed-data slot with the halved shape is accepted as E2M1 pairs exactly like `U8`. No real export writes that, and a `U8` tensor outside an MXFP4 slot is still refused (`test_mixed_dtype_is_refused`, `crates/rustinfer-frontend/tests/mapping.rs:125`; KV scales accept only bf16, fp16, fp32, `kv_scales.rs:28, 164-170`), so no value is misread; the reader still has no plain unsigned-byte type. |

## Result

Thirteen of fifteen requirements conform (ST-R8 since `b99720a`; ST-R9 now
for its 0-rank case, with no empty-tensor test), ST-R15 is partial and ST-R3
is missing. Nothing in the reader changed since `b99720a`; what `8c7d47e`
adds is the first consumer of `U8` (MXFP4 import, by role) and reads of
weight bytes by header range for the used-range identity, both resting on
ST-R6 and ST-R11. State: **partial**. Gaps on the
[tracker](std-safetensors-tracker.html).
