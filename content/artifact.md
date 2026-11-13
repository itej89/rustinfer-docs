---
title: The artifact
navtitle: Artifact format (.rie)
section: Design
order: 3
summary: The .rie engine file from ADR-002 and the artifact requirements; header, sections, hash, the verifying reader and the atomic writer, and the two places where the ADR and the SRS disagree.
---

# The artifact

Read from ADR-002, ADR-009, SRS §3.2.7 (`RI-ART`) at v0.3, RI-SEC-002,
RI-SEC-004, RI-PLN-005, `constants.rs` and `crates/rustinfer-artifact/src/`
at commit `7913427`. The crate is in the code since Codeberg PR #21 merged
into `main` as 678b084 on 2026-11-12 (issue #4): the fixed header, the
section table with nine sections, the content hash, the verifying reader and
the atomic writer under format version 1, with the layout the code writes in
`docs/api/artifact.md` in the tree. Since then the [frontend](frontend.html)
produces the weight manifest and the checkpoint identity (PR #24) and
[Sluice](sluice.html) consumes them (PR #23); no `build` writes an artifact
yet (#11). SRS v0.3 (PR #28) changed four clauses of this contract, and the
code has not caught up with all of them: the
[v0.3 section](#the-v03-contract-changes) below says which part is where.

## Why a single file

ADR-002's context: a TensorRT engine is one file holding everything the
runtime needs so that inference performs no compilation, selection or
planning. rustinfer wants the same property plus four more: inspectable
without the GPU, integrity-checked before use, never left half-written, and
small, because it holds the engine and never the weights (the amendment of
2026-11-11, below). The alternatives it rejected were a tar or zip
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
| `model_ir` | the Model IR document as canonical JSON: the weight set as tensor descriptors (name, dtype, shape, encoding, placement slot), the named functions and the KV groups; never a weight byte | sorted keys, compact, exact integers (RI-MIR-007); the document and its writer and reader exist in `rustinfer-mir` since PR #19 ([design](design.html)), the section around them is #4 |
| `plan` | the Plan as canonical JSON | deterministic key order (RI-GC-009) |
| `profile` | `min`, `opt`, `max` per dynamic dimension | |
| `metadata` | build options, producer, `rustc` and LLVM versions, catalog version, the checkpoint identity (SHA-256 of `config.json`, each weight file's size and header hash), origin (`build` or first load), timestamp | RI-ART-008, RI-SEC-004 (v0.3) |
| `catalog` | the kernel entries the Plan references | |
| `kernels` | concatenated code objects with an index JSON at the start | |
| `weights` | the **weight manifest**, canonical JSON: the checkpoint's format and root, and per weight id the source shard, tensor name, dtype, shape, source layout, byte range, target layout, transform and the ranks that need it, and from SRS v0.3 an optional per-tensor SHA-256; never a weight byte | RI-ART-005, RI-ART-012; written by the [frontend](frontend.html), read by [Sluice](sluice.html) |
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

## Why the weights stay out

The first draft of ADR-002 bundled the weights, as a TensorRT engine does.
On 2026-11-11 the owner struck that: a 2.4T-parameter checkpoint is near
5 TB at bf16, sharded over dozens of ranks, and writing it a second time into
an engine file is not practical on disk, in build time or for distribution.
The artifact now references the checkpoint through the weight manifest and
never copies it (RI-ART-012). Three things follow:

- `build` reads only `config.json` and the safetensors headers, so its time
  and disk use do not depend on model size, and a published prebuilt artifact
  (RI-ART-011) is megabytes and carries no weight licence.
- The layout the kernels want is still produced, but at load, on the device,
  one shard at a time, by [Sluice](sluice.html), the weight streamer
  (RI-GC-008, RI-WST). A fine-tune of the same architecture reuses the
  artifact unchanged.
- `metadata` records the checkpoint's identity as hashes of `config.json`,
  the shard headers and the file sizes; `run` refuses a checkpoint that
  differs, and `--verify-weights` opts into a full per-tensor hash check.
  SRS v0.3 makes this the whole build-time input identity (RI-SEC-004): no
  build hashes a whole weight file, and weight content is hashed only per
  tensor, under `--hash-weights` or `--verify-weights`.

## The v0.3 contract changes

SRS v0.3 of 2026-11-12 (PR #28, change request #27, ADR-009) amended the
artifact's contract before the graph compiler and the executor start
reading it. Each change is marked by where it stands at `7913427`:
*specified in the SRS* means the clause is approved and the code still
follows v0.2; *in the code* means a test on `main` exercises it.

| change | requirement | state |
|---|---|---|
| The build-time input identity is the checkpoint identity: SHA-256 of `config.json`, each weight file's size and header hash; no whole-file hashing | RI-SEC-004, RI-ART-008 | <span class="state-ok">in the code</span> — `CheckpointIdentity` and `FileIdentity` in `metadata.rs`, produced by the frontend and verified by Sluice; the reworded clause matches what PR #24 already did |
| An optional per-tensor SHA-256 in each weight manifest entry, recorded by `build --hash-weights` or a first-load build under `--verify-weights`; a digest that is not 64 hex digits refused naming the weight; a build without the flag opens no weight byte range | RI-ART-005, RI-CLI-002, RI-WST-005 | <span class="state-no">specified in the SRS</span> — `WeightEntry` has no digest field; Sluice's `verify_weights` takes the digests as a separate map |
| Every JSON section carries its own top-level version (`ir_version` for `model_ir`, `<section>_version` otherwise), read against a listed set and refused naming the section and the version | RI-ART-014 (new) | <span class="state-part">partly in the code</span> — `model_ir` (`ir_version` 1), `topology` and `placement` (`topology_version`, `placement_version` 1) carry one; `plan`, `profile`, `metadata`, `catalog` and `weights` do not, and #27 notes the section set is fixed in five places |
| The `placement` section records each tensor's slot as a device index, a tier index and an optional shard spec, under `placement_version` 2 with Model IR `ir_version` 2; a pinned section is parsed and validated against the pinned topology at load | RI-PLN-005, RI-MIR-005, ADR-009 | <span class="state-no">specified in the SRS</span> — the code writes `placement_version` 1 with a tier kind per tensor, and pinned `topology` and `placement` bytes are never parsed (a #27 defect); see the [planner](planner.html) |

The code changes land in the later PRs of #27, which is open with four
pull requests coming.

## Costs the ADR records

First load pays the layout transform on the device, streamed per shard, so
load time scales with weight size as every engine's does. JSON for the small
sections is larger than a binary encoding but readable in any tool, and the
ADR estimates the plan of a 70B model at a few megabytes.

## Multi-rank

A tensor-parallel build produces one artifact per rank carrying `rank`,
`world_size` and the parallel layout, and ranks from different builds are
refused together (RI-ART-007, R2). Whether that stays one file per rank is
open issue OI-005, provisionally yes.
