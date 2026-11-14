---
title: "safetensors v0.8.0 audit"
navtitle: Audit
section: Standards
group: "Model formats / safetensors v0.8.0"
order: 12
summary: The 2026-11-13 audit of rustinfer's safetensors header reader against the v0.8.0 format.
---

# safetensors v0.8.0 audit

**Audit of 2026-11-13**, against the [requirements](std-safetensors-requirements.html),
on origin/main `ccf02b3`.

**Method.** Read `crates/rustinfer-artifact/src/safetensors.rs` and its
callers in the frontend and Sluice, and the tests that exercise the reader:
`crates/rustinfer-artifact/tests/safetensors.rs`,
`crates/rustinfer-artifact/tests/mx_manifest.rs`,
`crates/rustinfer-frontend/tests/safetensors.rs` and
`crates/rustinfer-sluice/tests/refusal.rs`. Compared each check with the
README and with the reference reader's `read_metadata` and
`Metadata::validate`. One probe was run: a scratch program against
`serde_json` 1.0.154, the version in the workspace `Cargo.lock`, to see how
the reader's JSON step treats a duplicate key and leading whitespace. The
rustinfer test suite was not run; results are as the tests are written.

## Header layout

| id | result | evidence |
|---|---|---|
| ST-R1 | **conforms** | `header_end` reads the 8-byte prefix as `u64::from_le_bytes` (`safetensors.rs:301-306`). A short file is malformed: `test_short_prefix_is_malformed` (`crates/rustinfer-frontend/tests/safetensors.rs:142`), `test_bounds_and_malformed_headers` (`crates/rustinfer-artifact/tests/safetensors.rs:151`). |
| ST-R2 | **conforms** | Exactly `N` bytes are read (`read_prefix`, 224-240) and decoded as UTF-8 then JSON (`parse_object`, 555-562). `test_header_must_be_a_json_object` (`frontend/tests/safetensors.rs:199`). |
| ST-R3 | **missing** (ST-1) | `serde_json::from_str` accepts leading whitespace; the probe parsed `"  {}  "` as an empty object. No check that the first header byte is `{`. The reference reader does not check it either. |
| ST-R4 | **conforms** | Trailing whitespace is accepted by `serde_json`; a header whose length is not a multiple of eight passes: `test_unpadded_header_is_accepted_and_a_truncated_prefix_is_refused` (`crates/rustinfer-sluice/tests/refusal.rs:358`). The reader also accepts tab, CR and LF as padding, which is more than the README's 0x20. |
| ST-R5 | **conforms** | Each entry must be an object with exactly `dtype`, `shape`, `data_offsets`; a missing, mistyped or extra key is a schema fault naming the tensor and field (`parse_entry`, 408-425). `test_schema_faults_name_the_tensor_and_field` (`artifact/tests/safetensors.rs:63`), `test_malformed_entries_name_the_tensor_and_field` (`frontend/tests/safetensors.rs:218`). Refusing an extra key is stricter than the reference reader. |
| ST-R6 | **conforms** | Offsets are relative to the data region and turned into absolute byte ranges (`parse_offsets`, 505-525). `test_header_parses_into_typed_entries_and_identity` (`artifact/tests/safetensors.rs:36`), `test_offsets_are_checked_against_the_data_region_and_shape` (`frontend/tests/safetensors.rs:267`). |
| ST-R7 | **conforms** | `__metadata__` must be an object of strings (`parse_object`, 563-571). `test_metadata_key_is_accepted_only_as_a_string_map` (`frontend/tests/safetensors.rs:377`). |
| ST-R8 | **missing** (ST-2) | The header is parsed into a `serde_json::Map`, which keeps the last of two equal keys without error; the probe parsed `{"t":{"a":1},"t":{"a":2}}` as `{"t":{"a":2}}`. A shard naming one tensor twice is read as if it named it once, with the second entry's offsets. The tiling check (ST-R10) then usually fails, because the first entry's bytes are left unindexed, but not when both entries give the same range. |
| ST-R9 | **conforms, untested** (ST-4) | The element count is the product of the shape, 1 for `[]` and 0 for a zero dimension (`tensor_bytes`, 546-551); a zero-length range tiles. No test builds an empty or 0-rank tensor. |
| ST-R10 | **conforms** | Sorted by start, each range begins where the last ends, the first at 0 and the last at the end of the data region (`check_contiguous`, 367-387; `check_region_end`, 390-406). `test_overlapping_ranges_are_refused_naming_both_tensors` (`frontend/tests/safetensors.rs:437`), `test_gaps_in_the_data_region_are_refused` (`:464`), `test_contiguous_ranges_pass_in_any_header_order` (`:494`), `test_gap_in_the_data_region_is_refused` (`sluice/tests/refusal.rs:463`). |
| ST-R11 | **conforms** | `END - BEGIN` must equal `storage_bytes(product(shape))` (`parse_offsets`, 514-520); overflow is refused (`test_shape_product_overflow_is_refused`, `frontend/tests/safetensors.rs:308`). For `F4` the reader requires an even innermost axis (`tensor_bytes`, 429-437), where the reference requires only an even element count: a `F4 [2, 3]` tensor valid in the format is refused. That is a narrower reading, consistent with `fp4x2` packing pairs along the innermost axis (RI-MIR-003), not a misreading. `test_safetensors_reader_types_f4_and_e8m0_with_packed_sizes` (`crates/rustinfer-artifact/tests/mx_manifest.rs:407`). |
| ST-R12 | **conforms** | Sluice reads multi-byte values with `from_le_bytes` (`crates/rustinfer-sluice/src/convert.rs:484-496`) and slices tensors row-major. |
| ST-R13 | **conforms** | `SAFETENSORS_MAX_HEADER_BYTES` is 100,000,000, the reference value (`crates/rustinfer-core/src/config/constants.rs:347`), checked before the header is allocated (`check_header_bound`, 325-334); a length past the file is `HeaderPastFile` (309-318). `test_header_over_the_bound_is_refused_before_reading` (`frontend/tests/safetensors.rs:155`), `test_header_length_is_bounded_by_the_file_size` (`:174`), `test_header_length_past_the_bound_or_the_file_is_refused` (`sluice/tests/refusal.rs:230`). |

## Dtype names

| id | result | evidence |
|---|---|---|
| ST-R14 | **conforms** for the names read | `DTYPES` (`safetensors.rs:54-65`) reads `BF16`, `F16`, `F32`, `F8_E4M3`, `F4`, `F8_E8M0`, `U8`, `I32`, `I64`, `BOOL`, spelled as `enum Dtype` spells them, with the format's bit sizes. The other twelve (`F6_E2M3`, `F6_E3M2`, `I8`, `F8_E5M2`, `F8_E4M3FNUZ`, `F8_E5M2FNUZ`, `I16`, `U16`, `U32`, `C64`, `F64`, `U64`) are refused naming the tensor and the name: `test_dtype_names_map_and_others_are_refused` (`frontend/tests/safetensors.rs:111`), `test_unknown_dtype_is_refused` (`artifact/tests/safetensors.rs:135`), `test_dtype_this_release_does_not_read_is_refused` (`sluice/tests/refusal.rs:480`). Reading a subset is allowed: the format defines names, it does not require a reader to support each. |
| ST-R15 | **partial** (ST-3) | `U8` is typed as Model IR `ue8m0`, the same as `F8_E8M0` (`safetensors.rs:48-61`), because Quark and compressed-tensors store both MXFP4 scales and packed E2M1 pairs as `U8`. The format's `U8` is an unsigned byte with no exponent meaning. A `U8` tensor that is neither is not misread into a result: the frontend refuses it as a dtype outside the architecture's policy (`test_mixed_dtype_is_refused`, `crates/rustinfer-frontend/tests/mapping.rs:125`), but the reader itself has no plain unsigned-byte type. |

## Result

Eleven of fifteen requirements conform, ST-R9 conforms without a test, ST-R15
is partial, and ST-R3 and ST-R8 are missing. State: **partial**. Gaps on the
[tracker](std-safetensors-tracker.html).
