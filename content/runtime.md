---
title: Runtime and serving
section: Runtime
order: 1
summary: The executor, scheduler, KV cache and sampler as the SRS specifies them, the high-concurrency serving workload they are tuned for, and the line between Release 1's static batch and the serving features of Release 2 and 3.
---

# Runtime and serving

Read from SRS §3.2.11 to §3.2.19 and §3.2.21, `docs/observability.md`, and
the state, sequence and concurrency diagrams at commit `082df51`. The
`rustinfer-runtime` crate is an error type; issue #13 implements the R1
executor and #14 wires `run` through it. No request has been served.

## The first-class workload

SRS §2.5: the first-class workload is high-concurrency API serving, and
defaults and the first benchmark follow it. Concretely, from R2 the default
scheduler policy is `max_utilization` with chunked prefill on (RI-SCH-003),
prefix reuse is on by default (RI-KVC-005), the overlap scheduler is on by
default (RI-SCH-005), and the acceptance benchmark is Llama-3-8B in FP8 at
batch 64 with 1k input and 1k output tokens on gfx950 against vLLM with the
AITER backend (RI-NFR-003).

## The executor

The executor loads an artifact, verifies the target, runs the planner,
allocates the arena, the KV pool and the per-sequence state once, and has
[Sluice](sluice.html) stream every weight the rank needs into device memory in
its target layout, all before the first request; no device allocation happens on the
request path (RI-RT-001). Each iteration executes the Plan's launches in
order with no kernel selection, shape inference or allocation (RI-RT-002).
RI-NFR-001 makes that testable: zero heap allocations on the decode path
after warm-up, verified by an allocation-counting test on the CPU target.

| API verb | release |
|---|---|
| `enqueue(Request) -> RequestId`, `await_responses(timeout)` | R1 |
| `cancel(RequestId)`, `iteration_stats()`, `request_stats()`, streaming responses | R2 |

A `Request` carries prompt tokens, `SamplingConfig`, `max_new_tokens` in R1;
`OutputConfig` (logprobs, logits, streaming), stop and bad words in R2; LoRA
id, guided-decoding spec, priority and deadline in R3 (RI-RT-004). A launch
failure aborts its batch naming the Plan entry and kernel id, marks those
requests failed, frees their KV blocks, and leaves the executor serving the
next iteration (RI-RT-006). One iteration runs per device stream and an
activation arena is never shared between concurrent iterations (RI-RT-008).

The concurrency rules are RI-CON-002 and the concurrency diagram: one device
context per rank, submissions from many threads through one bounded queue,
device buffers touched only by the executor thread. R1 is single-threaded;
the diagram records the R2 design so the R1 types are shaped for it.

## The scheduler

R1 has one policy, `static_batch`. R2 brings in-flight batching with
prefill requests first in a padding-free iteration (RI-SCH-001), decode
tokens scheduled before prefill tokens within `max_batch_size` and
`max_num_tokens` (RI-SCH-002), chunked prefill in KV-block-aligned chunks
(RI-SCH-004), the overlap scheduler running the host work of iteration *n*
during the device work of *n+1* (RI-SCH-005), pause and resume of the
lowest-priority most-recent decode request under KV pressure (RI-SCH-006),
iteration statistics (RI-SCH-009), and one uniform token-level state for
every phase rather than queues per phase (RI-SCH-010, vLLM V1's lesson). R3
adds priorities and deadlines (RI-SCH-007) and LoRA batching (RI-SCH-008).

The request lifecycle the state diagram draws: Queued → Prefill (chunk by
chunk) → Decode ⇄ Paused → Finished, with Cancelled reachable from the first
three and Failed from Prefill and Decode.

## The KV cache

A pool of fixed-size token blocks, power of two, default 32 and recorded in
the Plan, with a block table per sequence (RI-KVC-001). Allocation and
release are O(1) from one pre-allocated pool with an LRU free list and no
per-block heap allocation at run time (RI-KVC-002). A sequence longer than
the profile's `max_seq_len` is refused at admission (RI-KVC-004). Those
three are R1. R2 sizes the pool as the smaller of `free_gpu_memory_fraction`
(default 0.9) and an explicit `max_tokens` after weights and arena
(RI-KVC-003), indexes filled blocks in a radix tree by prefix with reuse on
by default and hits and misses counted (RI-KVC-005), stores FP8 and INT8
with per-block scales where the attention kernels read them (RI-KVC-008), and
supports per-layer windows with a circular buffer, refusing beam search with
them (RI-KVC-009). R3 adds prioritised LRU eviction with priority 0 to 100,
default 35, and retention windows, where only unreferenced leaf blocks are
evictable (RI-KVC-006), and offload of evicted blocks to DRAM and NVMe under
the planner's policy (RI-KVC-007); CXL and remote tiers are R4.

## The sampler

Greedy, temperature, top-k and top-p run per request on device for the whole
batch in one launch in R1; min-p, top-p decay and seeds follow in R2
(RI-SMP-001). R2 also brings repetition, presence and frequency penalties,
`no_repeat_ngram_size`, embedding bias, min and max tokens, stop and bad
words (RI-SMP-002), logprobs from the same logits the sample was drawn from
(RI-SMP-003), a caller-supplied host post-processor (RI-SMP-004) and
reproducibility for the same seed, request, artifact and target
(RI-SMP-007). Beam search (RI-SMP-005) and guided decoding from a JSON
schema, regex or grammar with masks applied on device each step (RI-SMP-006)
are R3; the grammar backend is open issue OI-006.

## Speculation, LoRA, distribution, the server

All R3 or later and all Not started. Draft/target speculation with rejection
sampling and MTP for DeepSeek and Qwen MoE families, with acceptance metrics
and the matrix refusals (RI-SPD-001 to -004); EAGLE-3 in R4. Run-time LoRA
adapters with host and device caches, `max_loras` in flight, a request that
waits for its adapter or fails and never runs without it (RI-LORA-001 to
-003). Tensor parallelism on one node with one process per rank and a shared
build id check in R2 (RI-DIST-001, -004); expert and attention data
parallelism in R3; pipeline, context, multi-node over Ultra Ethernet, Helios
scale-up and disaggregated prefill and decode designed for and implemented
in R4 (RI-DIST-005). The server (RI-SRV-001 to -006) implements the OpenAI
chat-completions and completions shapes with SSE, `/v1/models`, `/health`
answering 200 only when a request can be admitted, `/version`, `/metrics`,
`/prometheus/metrics`, chat templates, a UUID v4 request id at every
boundary, size limits, 400 on malformed JSON, 429 or 503 under overload, no
stack traces, and profiling toggles.

## Observability

`docs/observability.md` holds the tier assessment SWG-001 §15.1 asks for and
a signal inventory. Structured logging is R1 and done on the scaffold branch.
Metrics are R2 (RI-OBS-001): `rustinfer_requests_total{status}`,
`rustinfer_iteration_duration_seconds`, `rustinfer_ttft_seconds`,
`rustinfer_tpot_seconds`, `rustinfer_tokens_total{phase}`,
`rustinfer_kv_blocks{state}`, `rustinfer_kv_reuse_total{result}`,
`rustinfer_errors_total{error_type}`, with no high-cardinality labels and
never a prompt. Health checks and `request_id` propagation are R3; OTLP
export is not before multi-node. Every request is logged at admission and
completion with id, lengths, finish reason and latency, never with text
(RI-OBS-002).
