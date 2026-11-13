---
title: Sluice, the weight streamer
section: Runtime
order: 2
summary: The component that moves a checkpoint of any size into device memory in the kernels' layout from the artifact's weight manifest alone, through a bounded staging buffer, with reads, copies and transforms overlapped.
---

# Sluice, the weight streamer

A sluice moves an enormous volume of water through a gate of fixed width.
That is the job: a checkpoint that may be 5 TB, through a staging buffer of
a gigabyte, into the layout the kernels declare, without ever being written a
second time. Sluice is the component the owner asked for on 2026-11-11 when
the weights left the artifact ([artifact](artifact.html), RI-ART-012); the
SRS specifies it as RI-WST-001 to RI-WST-005.

Read from `crates/rustinfer-sluice/src/`, its tests, `docs/api/CHANGELOG.md`
and SRS v0.3 at commit `04a2a26`. GitHub PR #23 merged into `main` as
add4752 on 2026-11-12: the crate `rustinfer-sluice` with the API below,
tested on the CPU reference target's device; 57 crate tests and a workspace
of 587 in the PR's run. Issue #18 closed on 2026-11-13. The #27 pull
requests of 2026-11-13 changed it twice: PR #29 counted the zero block in
the staging budget, and PR #30 replaced its safetensors parser with the
shared reader and moved the digests into the manifest. No executor calls
Sluice yet (#13).

## What it takes and what it gives

| in | out |
|---|---|
| the weight manifest from the artifact's `weights` section: per weight id the source shard, tensor name, dtype, shape, source layout, byte range, target layout, transform, and the ranks that need it (RI-ART-005) | every weight this rank needs, as a device buffer in its target shape and layout: `LoadedWeights`, by name (RI-WST-001) |
| the artifact's checkpoint identity (RI-ART-008), a checkpoint root, a rank and a `SluiceConfig` (the staging budget) | a `LoadReport`: weights, slices, bytes read, copied and transformed, the budget and the peak staged, and each stage's busy time with `serial_sum` and `overlap_ratio` (RI-WST-004) |
| for `--verify-weights`, the expected SHA-256 per weight | an error naming the first tensor whose header disagrees with the manifest, or whose bytes differ (RI-WST-005) |

Sluice never sees the Model IR or the Plan. The manifest is its whole
description of the model, which is what makes it a component rather than a
corner of the executor: the [frontend](frontend.html) writes the manifest at
build from `config.json` and the shard headers alone (RI-FE-004), the graph
compiler adds the target layout and transform per weight (RI-GC-008, #10),
and Sluice reads the result at load.

## The API

`Sluice::open(manifest, identity, root, rank, config)` does every check
before any weight byte is read: the checkpoint identity first (a differing
`config.json` hash, shard size or header hash is refused with code
`artifact`, RI-ART-012); then the safetensors header of every shard the
rank needs, bounded and parsed as untrusted input (RI-SEC-001,
RI-SEC-003) by `rustinfer_artifact::safetensors`, the one header reader the
[frontend](frontend.html) also uses since PR #30 (Sluice's own copy was
deleted; it now also refuses a gap in a shard's data region and a dtype this
release does not read); then, per needed weight, dtype, shape and byte range against
that header, refused naming the tensor and the field (RI-WST-005); then the
transform and layout strings. Then:

| call | what it does |
|---|---|
| `rank`, `root`, `weights`, `needed_bytes` | what was opened: the needed weights in name order and the sum of their byte ranges |
| `load(device)` | streams every needed weight into `device` in its target layout; on any failure every buffer allocated so far is freed and the error names the stage (`alloc`, `copy`, `transform`, `sync`, `free`) |
| `digest_weights()` | the SHA-256 of every needed tensor's source bytes, by weight name: the full read `--verify-weights` performs |
| `verify_weights(expected)` | compares those digests with `expected` and refuses the first weight that differs, or that `expected` lacks |
| `LoadedWeights::release(device)` | frees every buffer |

The transform vocabulary accepted at load is `identity`, `transpose` (rank
2) and `pad:<rows>x<cols>` (rank 2, zero filled); `source_layout` must be
`row_major`. Anything else is refused at `open` naming the weight.

## How it moves the bytes

1. **Range reads.** Each tensor is read by the byte range the manifest
   records, from the shard that holds it, and nothing else: the report's
   bytes read equal the needed byte ranges, and the tests account for every
   byte (RI-WST-001).
2. **Bounded staging.** Host memory is capped by `RUSTINFER_STAGING_BYTES`
   (default 1 GiB, at least 64 KiB) regardless of model size. The budget is
   split into `SLUICE_STAGING_CHUNKS` (4) chunks, allocated as first needed
   and reused only after the copier returns them, so the bound holds by
   construction; a tensor larger than a chunk streams in slices
   (RI-WST-002). The tests load a checkpoint ten times the budget.
3. **Device-side transforms.** The staging buffer holds source layout only.
   A slice of an identity weight is copied straight into place; any other
   slice is copied to a scratch slot on the device and then moved to its
   target positions as contiguous runs on the device's transform stream,
   with a pad's padding zero-filled; the host computes only the runs.
   `Transform::apply_host` is the reference the tests compare against
   (RI-WST-003).
4. **Overlap.** A reader, a copier and a transformer run on three scoped
   threads joined by bounded channels; host order is the channels and device
   order the events between the copy and transform streams. Sluice holds no
   lock of its own. The overlap test injects a 6 ms delay into every device
   copy and transform and requires the sum of the stages' busy times to be
   at least 1.5 times the wall time (RI-WST-004).
5. **Verification.** Header checks at `open`, always; the per-tensor digest
   check under `--verify-weights` (RI-WST-005).

## The v0.3 digest, in part

SRS v0.3 (#27) puts the per-tensor digest into the weight manifest as an
optional SHA-256 field, recorded by `build --hash-weights` or by a
first-load build under `--verify-weights`, and makes a manifest without
digests a refusal under `--verify-weights` naming its first weight
(RI-ART-005, RI-WST-005). Since PR #30 (2026-11-13) `WeightEntry.sha256` is
an optional field, refused naming the weight when it is not 64 hex digits,
and `Sluice::verify_weights(None)` compares against the manifest's digests
and refuses the first needed weight without one; an external
`WeightDigests` map is used only when passed. No `build` records a digest
yet (#11), so both ids are tagged `Groundwork for` and count as partial on
the [requirements](ref-requirements.html) page. PR #29 fixed the
conformance defect #27 listed for RI-WST-002: the device zero block is
sized to the largest padding region and its host zeros are staged through
the pool, so they count in `staging_peak_bytes`.

## Why not the alternatives

| alternative | why not |
|---|---|
| weights inside the artifact (the first draft of ADR-002, and TensorRT's engine) | a second copy of a trillion-parameter checkpoint; a 5 TB hash; a rebuild per fine-tune; nothing publishable |
| a transformed weight pack on disk next to the artifact | still a second copy, so the same objection at the scale that matters |
| transform on the host at load | the host becomes the bottleneck for exactly the layouts (matrix-core tiles, pre-shuffles) that make the kernels fast; the device does the shuffle in a fraction of the copy time |
| kernels that read the source layout directly | gives up the tiled layouts that the fastest AMD kernels depend on; a wrong layout is silent corruption, so the transform is recorded per weight and tested against the reference |

## Where it sits

```
checkpoint shards ──► Sluice ──► device buffers in target layout ──► executor
        ▲                ▲
   byte ranges      weight manifest (artifact `weights` section)
```

Issue #18 was blocked by #4 (the manifest) and #5 (device buffers, copy
queues and the reference target's host transforms), both closed on
2026-11-12; PR #23 implemented it the same day, and it blocks #13 (the
executor). The acceptance criteria are on the [tracker](issues.html).
