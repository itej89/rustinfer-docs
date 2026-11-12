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
SRS specifies it as RI-WST-001 to RI-WST-005 and issue #18 implements it as
the crate `rustinfer-sluice`.

## What it takes and what it gives

| in | out |
|---|---|
| the weight manifest from the artifact's `weights` section: per weight id the source shard, tensor name, dtype, shape, source layout, byte range, target layout, transform, and the ranks that need it (RI-ART-005) | every weight this rank needs, as a device buffer in its target layout (RI-WST-001) |
| a checkpoint root, from the artifact's directory or `--weights <dir>` | load time, bytes and throughput per stage in `iteration_stats()` (RI-WST-004, R2) |
| a rank | an error naming the first tensor whose header disagrees with the manifest (RI-WST-005) |

Sluice never sees the Model IR or the Plan. The manifest is its whole
description of the model, which is what makes it a component rather than a
corner of the executor: the frontend writes the manifest at build from
`config.json` and the shard headers alone (RI-FE-004), the graph compiler adds
the target layout and transform per weight (RI-GC-008), and Sluice reads the
result at load.

## How it moves the bytes

1. **Range reads.** Each tensor is read by the byte range the manifest
   records, from the shard that holds it. A rank reads nothing another rank
   needs; the test accounts for every byte (RI-WST-001).
2. **Bounded staging.** Host memory is capped by `RUSTINFER_STAGING_BYTES`
   (default 1 GiB) regardless of model size; a tensor larger than the budget
   streams in slices (RI-WST-002).
3. **Device-side transforms.** The staging buffer holds source layout only.
   The transform into the kernel's tiled or pre-shuffled layout runs on the
   device as the load-phase launches the graph compiler recorded; the CPU
   reference target runs the same transforms on the host (RI-WST-003).
4. **Overlap.** Shard reads, host-to-device copies and transforms run on
   separate queues, so load throughput is bounded by the slowest of storage,
   interconnect and transform, not their sum (RI-WST-004).
5. **Verification.** Dtype, shape and byte range are checked against the
   shard header before any byte is read; `--verify-weights` adds the
   per-tensor hash from the manifest (RI-WST-005).

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
2026-11-12, and is being implemented since then; it blocks #13 (the
executor). The acceptance criteria are on the [tracker](issues.html).
