---
title: "safetensors v0.8.0"
navtitle: Overview
section: Standards
group: "Model formats / safetensors v0.8.0"
order: 10
summary: The safetensors shard format: rustinfer's own header reader, shared by the frontend and Sluice, measured against the format section of the v0.8.0 README.
---

# safetensors v0.8.0

**Scope** (SRS §1.4, SAFETENSORS): the header layout (8-byte little-endian
length, JSON header, `data_offsets`) and the dtype names.
**Conformance:** mandatory from **R1**. Cited by RI-FE-004, RI-ART-005,
RI-ART-008, RI-SEC-003, RI-SEC-004 and RI-WST-005.

**Implementation:** one header reader, `rustinfer_artifact::safetensors`
(`crates/rustinfer-artifact/src/safetensors.rs`, origin/main `b99720a`). It
bounds the length prefix before allocating (`header_end`, lines 303-323),
parses the header as a JSON object that repeats no key, refusing a
duplicate by name (`parse_object`, 557-573, through `unique_json`, PR #52), whose `__metadata__` must be a map of
strings, types every entry and refuses unknown keys
(`parse_entry`, 410-427), checks each `data_offsets` against the data region
and the shape times the element size (`parse_offsets`, 507-527), and requires
the ranges to tile the data region with no gap or overlap
(`check_contiguous`, 369-389; `check_region_end`, 392-408). The dtype names it
reads are the table `DTYPES` (56-67). The frontend
(`crates/rustinfer-frontend/src/safetensors.rs`) and Sluice
(`crates/rustinfer-sluice/src/safetensors.rs`) call it and map its refusals
into their own error types. No byte after the header is read at build.

**Source:** *safetensors* README, section "Format", at tag v0.8.0 (commit
a406ca3e7a90, 2026-06-09),
https://github.com/huggingface/safetensors/blob/v0.8.0/README.md, and the
`Dtype` enum and `Metadata::validate` of `safetensors/src/tensor.rs` at the
same tag. Local copies: `specs/model-formats/safetensors-v0.8.0-README.md`,
`specs/model-formats/safetensors-v0.8.0-tensor.rs`.

The index file `model.safetensors.index.json` is a Transformers convention,
not part of this format; the frontend reads its `weight_map`
(`crates/rustinfer-frontend/src/lowering.rs:130-138`) and it is outside this
standard's scope.

| | |
|---|---|
| Pages | [requirements](std-safetensors-requirements.html) · [audit](std-safetensors-audit.html) · [tracker](std-safetensors-tracker.html) |
| Audited | 2026-11-13, by reading the reader and its tests on origin/main (`b99720a`) against the README and `tensor.rs`, and one probe of `serde_json` 1.0.154 (the locked version) |
| Header layout | length prefix, bounds, offsets, tiling, unique keys (since `b99720a`) and `__metadata__` conform |
| Gaps | the first header byte is not checked to be `{`; `U8` read as `ue8m0`; no empty or 0-rank tensor test (duplicate keys fixed in `b99720a`) |
| Dtype names | 10 of the 22 names read, spelled as the format spells them; the rest refused by name |
