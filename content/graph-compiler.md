---
title: Graph compiler
section: Compiler
order: 1
summary: The pass pipeline from Model IR to Plan: shape inference under a profile, fusion against the catalog, precision, kernel selection with no fallback, layouts, arena planning and deterministic emission.
---

# Graph compiler

Read from SRS §3.2.4 (`RI-GC`), `docs/uml/activity-diagram.md` and ADR-005
at commit `082df51`. The `rustinfer-compiler` crate is an error type; issue
#10 implements this page, after the Model IR (#3, done), the target
abstraction with the `Catalog` it selects from (#5, done 2026-11-12) and
the generators (#9) it needs.

## The pipeline

An ordered pass pipeline, each pass logging its name, node count before and
after, and duration at `info` (RI-GC-001: "an attributable pipeline"). The
activity diagram gives the order; the passes are:

| pass | does | fails on |
|---|---|---|
| validate | the Model IR's own checks: no cycle, no undefined input, no use before definition, no double definition, no arity or dtype-rule breach, no unknown KV group (RI-MIR-006); in the code as `Document::validate` since PR #19 | names the function, the node and the field |
| shape inference | resolves every tensor under the profile (RI-GC-002) | an unresolved dimension; a profile with min > opt or opt > max; a `max_num_tokens` not a multiple of the KV block size |
| precision | assigns each matmul and attention a weight and activation format from the build options or the imported quantization, and inserts the quantize and scale nodes the chosen kernel requires (RI-GC-004) | bf16 and fp8 in R1; int8, MXFP4 and fp8 KV in R2; int4 weight-only in R3 |
| fusion | replaces matched sequences with fused nodes: rmsnorm→matmul, matmul→silu_and_mul, residual_add→rmsnorm, rope→kv_cache_write, quantize→matmul, elementwise chains (RI-GC-003) | only when the catalog lists a kernel for the fused node or the elementwise fuser (RI-KC-010, R2) can produce one |
| kernel selection | one catalog kernel per node by (operator, dtypes, layout, shape rules at `opt`) ordered by tuned cost; records the kernel id in the Plan (RI-GC-005) | no kernel and no device present: fails naming the node. With a device present it requests the missing bucket from the kernel compiler (RI-KC-006) |
| layout | records, per weight, the layout the selected kernel declares and the transform from the source layout, as entries of the weight manifest and as load-phase launches of the Plan; the transform runs at load on the device by [Sluice](sluice.html), never at build and never to disk (RI-GC-008) | the rationale: matrix-core tiled weights; a wrong layout is silent corruption; the checkpoint is never copied (RI-ART-012) |
| memory planning | one activation arena sized at the profile's `max`, offsets reusing non-overlapping lifetimes; records the arena size, KV block geometry and per-sequence state sizes (RI-GC-006) | |
| Plan emission | the ordered launches with bindings and shape expressions, sub-plans for prefill and decode (R1) and a mixed iteration (R2) (RI-GC-007) | |
| matrix check | refuses a build whose feature combination is not marked supported in `docs/feature-matrix.md`, naming the pair (RI-GC-014) | |

Compilation is single-threaded per build in R1; a parallel pass must first
pass a concurrency review and update the concurrency diagram (RI-CON-001).

## No fallback, no run-time selection

The design rule behind the selection pass is in RI-GC-005's rationale and
goal 6 of the SRS: every refusal is typed and before device work, and there
is no silent fallback, ever. The contrast is with the incumbents, whose
public functions select a kernel per shape at the moment of the call; here
the kernel id is in the Plan and the executor performs no selection, shape
inference or allocation per iteration (RI-RT-002).

## Determinism

Identical inputs and options give byte-identical `plan`, `catalog` and
`kernels` sections (RI-GC-009), which is what lets `build` and the
first-load path be interchangeable (ADR-006) and what `inspect` can be
checked against in CI. Shape buckets and how cost is interpolated between
them is open issue OI-002, to start with padded-M buckets as AITER's tables
use.

## Parallelism in later releases

`--tp N` shards attention heads and MLP columns across N ranks, inserts
collective nodes and emits one Plan per rank (RI-GC-010, R2). `--ep N`
places experts and inserts dispatch and combine nodes (RI-GC-011, R3). LoRA
application points are reserved on every matmul marked adaptable with
`max_lora_rank` fixed in the Plan (RI-GC-012, R3), and a verification
sub-plan for speculative decoding is emitted on request, bounded by
`max_draft_tokens` (RI-GC-013, R3).
