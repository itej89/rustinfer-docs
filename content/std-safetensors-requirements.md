---
title: "safetensors v0.8.0 requirements"
navtitle: Requirements
section: Standards
group: "Model formats / safetensors v0.8.0"
order: 11
summary: What the safetensors format requires of a file and its header, in rustinfer's scope: the header layout and the dtype names.
---

# safetensors v0.8.0 requirements

Source: the "Format" section and its notes in the safetensors README at
v0.8.0 (`specs/model-formats/safetensors-v0.8.0-README.md`, lines 74-104),
and `safetensors/src/tensor.rs` at the same tag
(`specs/model-formats/safetensors-v0.8.0-tensor.rs`), which is the reference
reader. The README has no numbered clauses; items are cited by README line
and by function in `tensor.rs`.

Scope (SRS §1.4): the header layout and the dtype names. Tensor values are
out of scope; the format itself does not check them (README line 92).

## Header layout (README "Format")

| id | requirement | source |
|---|---|---|
| ST-R1 | The file starts with 8 bytes `N`, "an unsigned little-endian 64-bit integer, containing the size of the header". | README 76 |
| ST-R2 | The next `N` bytes are "a JSON UTF-8 string representing the header". | README 77 |
| ST-R3 | "The header data MUST begin with a `{` character (0x7B)." | README 78 |
| ST-R4 | "The header data MAY be trailing padded with whitespace (0x20)." A reader accepts such padding. | README 79 |
| ST-R5 | The header is a dict of tensor name to `{"dtype", "shape", "data_offsets": [BEGIN, END]}`. | README 80 |
| ST-R6 | `data_offsets` are relative to the start of the byte buffer after the header, `BEGIN` inclusive and `END` one past, "so total tensor byte size = `END - BEGIN`". | README 81-82 |
| ST-R7 | The special key `__metadata__` holds a "free form string-to-string map. Arbitrary JSON is not allowed, all values must be strings." | README 83 |
| ST-R8 | "Duplicate keys are disallowed." | README 87 |
| ST-R9 | Empty tensors (a dimension of 0) are allowed and store no data; 0-rank tensors (shape `[]`) are allowed and are a scalar. | README 94-98 |
| ST-R10 | "The byte buffer needs to be entirely indexed, and cannot contain holes." The reference reader requires each tensor to begin where the previous ends and the last to end at the end of the file (`Metadata::validate`, `read_metadata`: `MetadataIncompleteBuffer`). | README 99-100; `tensor.rs` 390-424, 627-663 |
| ST-R11 | Each tensor's `END - BEGIN` equals the element count times the dtype's bit size over 8; a sub-byte tensor whose bit count is not a multiple of 8 is invalid (`MisalignedSlice`). | `tensor.rs` 640-661 |
| ST-R12 | Data is little-endian and in row-major ('C') order. | README 101-103 |
| ST-R13 | The reference reader bounds `N` at 100,000,000 bytes (`MAX_HEADER_SIZE`) and requires `N` to fit inside the file (`InvalidHeaderLength`). A reader of untrusted files bounds it likewise (RI-SEC-003). | `tensor.rs` 10, 402-414 |

## Dtype names (`tensor.rs`, `enum Dtype`)

| id | requirement | source |
|---|---|---|
| ST-R14 | The `dtype` string is one of the 22 names of `enum Dtype`: `BOOL`, `F4`, `F6_E2M3`, `F6_E3M2`, `U8`, `I8`, `F8_E5M2`, `F8_E4M3`, `F8_E8M0`, `F8_E4M3FNUZ`, `F8_E5M2FNUZ`, `I16`, `U16`, `F16`, `BF16`, `I32`, `U32`, `F32`, `C64`, `F64`, `I64`, `U64`, each with the bit size of `Dtype::bitsize` (`F4` 4, `F6_*` 6, the 8-bit names 8, and so on). | `tensor.rs` 811-892 |
| ST-R15 | A reader that reads a name gives it the meaning the format gives it (for example `U8` "Unsigned byte", `F8_E8M0` the OCP MX scale, `F4` the MX FP4 element). | `tensor.rs` 811-863 |
