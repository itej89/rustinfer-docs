---
title: The artifact
navtitle: Artifact format (.rie)
section: Design
order: 3
summary: The .rie engine file from ADR-002 and the artifact requirements; header, sections, hash, the verifying reader and the atomic writer, and the two places where the ADR and the SRS disagree.
---

# The artifact

Read from ADR-002, SRS §3.2.7 (`RI-ART`), RI-SEC-002, RI-PLN-005 and
`constants.rs` at commit `082df51`. No artifact has been written yet: the
`rustinfer-artifact` crate is an error type, and issue #4 implements this
page. The API changelog records that format version 1 and the magic are
reserved.

## Why a single file

ADR-002's context: a TensorRT engine is one file holding everything the
runtime needs so that inference performs no compilation, selection or
planning. rustinfer wants the same property plus four more: inspectable
without the GPU, integrity-checked before use, never left half-written, and
weights memory-mappable. The alternatives it rejected were a tar or zip
container (no page alignment, hash semantics unclear), FlatBuffers or Cap'n
Proto (a dependency for a format with a handful of sections) and safetensors
for the whole file (no section typing, no kernel binaries).

## The header

From ADR-002, little-endian throughout:

| offset | size | field |
|---|---|---|
| 0 | 4 | magic `RIE\0` (`ARTIFACT_MAGIC` in constants) |
| 4 | 2 | `format_version`, `1` at first release (`ARTIFACT_FORMAT_VERSION`) |
| 6 | 2 | `header_length` |
| 8 | 32 | target id, NUL-padded ASCII, for example `gfx950` |
| 40 | 32 | producer version, NUL-padded ASCII, for example `rustinfer 0.1.0` |
| 72 | 32 | SHA-256 of every byte after the header |
| 104 | 8 | `section_count` |
| 112 | … | section table: `name[16]` NUL-padded, `offset u64`, `length u64`, `alignment u32`, pad `u32` |

## The sections

| section | holds | notes |
|---|---|---|
| `model_ir` | the Model IR as canonical JSON | sorted keys, exact numerics (RI-MIR-007) |
| `plan` | the Plan as canonical JSON | deterministic key order (RI-GC-009) |
| `profile` | `min`, `opt`, `max` per dynamic dimension | |
| `metadata` | build options, producer, `rustc` and LLVM versions, catalog version, input hashes, origin (`build` or first load), timestamp | RI-ART-008, RI-SEC-004 |
| `catalog` | the kernel entries the Plan references | |
| `kernels` | concatenated code objects with an index JSON at the start | |
| `weights` | raw bytes, 4096-byte aligned, with an index of (weight id, dtype, shape, layout, offset, length) | `ARTIFACT_WEIGHT_ALIGNMENT`; RI-ART-005 |
| `topology`, `placement` | empty at build unless pinned | reserved from R1 for format stability (RI-PLN-005) |
| `lora_slots` | adapter application points | from R3 (RI-ART-002) |

ADR-002 and RI-ART-002 agree on this list: the ADR was corrected on
2026-11-11 to name the nine Release 1 sections and the Release 3
`lora_slots`, citing the RI-ART, RI-GC and RI-PLN ids, after the first
reading for this site found it still carrying its pre-SRS six-section list
([decisions](decisions.html), resolved table).

## The reader

Order of checks, each named in the error when it fails (RI-ART-003): magic,
version in the accepted set, header length, every section inside the file and
non-overlapping (RI-SEC-002 requires every length to be bounded by the file
size before any read), then the hash, and only then are sections exposed.
`inspect` reads the header, the table and the JSON sections and never
initialises a device (RI-CLI-005); the SRS budgets it at under one second for
any artifact (RI-NFR-002). The accepted format versions are listed in code,
and a bump must be recorded in `docs/api/CHANGELOG.md` with a migration note
(RI-ART-006).

## The writer

The writer streams to `<out>.tmp-<pid>` in the destination directory, writes
the hash last, calls `fsync`, and renames; an interrupted build leaves no
file at the destination (RI-ART-004, RI-NFR-007). The same protocol serves
`build` and the first-load path into the cache directory, which is why
ADR-006 can require the two paths to produce identical artifacts.

## Costs the ADR records

The hash covers the weights, so hashing a 140 GB artifact costs a full read
at write and at first load; the ADR says a later version may add per-section
hashes. JSON for the small sections is larger than a binary encoding but
readable in any tool, and the ADR estimates the plan of a 70B model at a few
megabytes.

## Multi-rank

A tensor-parallel build produces one artifact per rank carrying `rank`,
`world_size` and the parallel layout, and ranks from different builds are
refused together (RI-ART-007, R2). Whether that stays one file per rank is
open issue OI-005, provisionally yes.
