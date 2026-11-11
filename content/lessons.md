---
title: Lessons from vLLM, SGLang and TensorRT-LLM
navtitle: Lessons from the incumbents
section: Design
order: 4
summary: What the planning documents and the SRS rationales take from the three incumbent engines, feature by feature, and the one thing TensorRT-LLM does not have that rustinfer needs.
---

# Lessons from vLLM, SGLang and TensorRT-LLM

Read from `docs/planning/trt-llm-feature-inventory.md`, the rationale lines
of the SRS, and the context sections of ADR-005 and ADR-006 at commit
`e91e002`. The inventory was read from NVIDIA's documentation on 2026-11-10;
rows it could not source from documentation are marked in the file as coming
from the executor API headers as known to the author. The vLLM and SGLang
lessons are the ones the SRS states as rationale; this page does not add
others.

## The lesson that shaped the whole engine

TensorRT-LLM has two runtimes. The classic engine flow (`convert_checkpoint`
→ `trtllm-build` → `rank{N}.engine` → the C++ executor) fixes every kernel,
fusion, precision choice and memory plan at build time under optimization
profiles. NVIDIA now marks it legacy and recommends the PyTorch backend, where
the graph is Python, kernels are selected at run time and CUDA graphs capture
the decode step. The inventory's reading of why: a rebuilt engine per
profile, per GPU and per TensorRT version was too rigid for the pace of model
releases.

rustinfer keeps the ahead-of-time engine, which was the owner's requirement,
and takes the lesson in two ways:

- The artifact is **semi-static**. Batch size, token count and sequence
  lengths are profile-bounded run-time values; graph, fusion, precision,
  kernel choice, layouts, arena plan and KV geometry are fixed at build. A
  rebuild is needed for a new model, target, precision or profile range,
  never for a new batch shape.
- The artifact is a **cache** (ADR-006). TensorRT-LLM removed its mandatory
  build step in version 1.2; vLLM and SGLang compile and capture on first
  load and cache the result. What is worth keeping is the artifact's
  properties, not the obligation to run a command first; so `run` and
  `serve` build on first load, and `--require-prebuilt` restores the
  obligation for fleets that want it.

## Feature by feature

What the inventory marks **adopt**, **adapt** or **later**, with the release
the SRS assigns.

| from TensorRT-LLM | taken as | release |
|---|---|---|
| Optimization profiles (`max_batch_size`, `max_num_tokens`, `opt_num_tokens`, `max_beam_width`, …) | a `profile` section with min, opt, max per dynamic dimension | R1 |
| Plugins (`gpt_attention_plugin`, `gemm_plugin`, `paged_kv_cache`, …) versus native layers | the catalog: every operator is a generated, tuned kernel with constraints; no plugin versus native distinction | R1 |
| Engine `config.json` beside the engine | the `metadata` section | R1 |
| Executor API: `enqueueRequest`, `awaitResponses`, `cancelRequest`, streaming, iteration and request stats | a Rust `Executor` with the same verbs | R1 core, R2 full |
| In-flight batching, context requests first, no padding | adopted | R2 |
| Scheduler policies `MAX_UTILIZATION`, `GUARANTEED_NO_EVICT`, `STATIC_BATCH` | the three policies; static batch is the R1 mode; `max_utilization` the default from R2 | R1, R2 |
| Chunked prefill aligned to the KV block | adopted, on by default with the R2 scheduler | R2 |
| Overlap scheduler, one step of added latency, on by default | adopted, disable-able per executor | R2 |
| CUDA graphs for the decode step | HIP graphs per batch-size bucket; the static Plan makes capture natural | R2 |
| Paged KV, `free_gpu_memory_fraction` 0.9, power-of-two block size, per-layer windows | adopted; the block size and fraction are constants in `rustinfer-core` | R1, R2 |
| Block reuse by prefix | adopted, on by default | R2 |
| Prioritised LRU eviction with priority 0 to 100 and retention windows; host offload | adopted | R3 |
| Quantized KV: FP8 | adopted; FP4 later | R2 |
| Sampling, penalties, stop and bad words, logprobs, logits post-processor | adopted | R1 core, R2 rest |
| Beam search, guided decoding (XGrammar, LLGuidance backends) | adopted; the grammar backend is open issue OI-006 | R3 |
| Speculative decoding: draft/target, EAGLE-3, MTP, tree modes; not with pipeline parallel; tree not with sliding window or MLA | draft/target and MTP first, EAGLE-3 next; the refusals in the feature matrix | R3, R4 |
| TP, PP, DP, EP with hybrid ETP, context parallel, attention DP, Helix, Wide-EP with EPLB | TP on one node over RCCL, then EP and attention DP, then the rest | R2, R3, R4 |
| Disaggregated serving with KV transfer over NIXL | the executor API is designed so a KV transceiver can be added | R4 |
| Multi-LoRA with host and device caches, `max_loras`, `max_lora_rank` | adopted | R3 |
| `trtllm-serve` endpoints, YAML config with `--set`, `/health`, `/metrics`, profiling toggles | `rustinfer serve` with the same endpoints, one process, async frontend | R3 |
| `trtllm-bench throughput`, `latency`; real and synthetic datasets | `rustinfer bench` with TTFT, TPOT, ITL, tokens/s, requests/s | R2 |
| Feature combination matrix | `docs/feature-matrix.md` from the first release; untested combinations are refused, not attempted | R1 |
| Prompt tuning, multimodal, encoder-decoder, diffusion, Triton Inference Server and Dynamo deployment | later, or out of scope (diffusion) | — |

## What the SRS takes from vLLM and SGLang

Each of these appears as the rationale of a requirement.

| lesson | requirement | the SRS's words |
|---|---|---|
| vLLM V1's block pool | RI-KVC-002: O(1) allocation and release from one pre-allocated pool with an LRU free list | "prefix reuse must cost nothing at a 0 percent hit rate" |
| vLLM V1's uniform scheduler | RI-SCH-010: one token-level model for prefill, chunked prefill, decode, reuse and speculation | "features compose when the scheduler is uniform" |
| vLLM V1 and SGLang on host overhead | RI-NFR-004: under 500 µs host time per iteration at batch 64 with the overlap scheduler off | "host overhead is the bottleneck as GPUs get faster" |
| SGLang's RadixAttention | RI-KVC-005: filled blocks indexed by token prefix in a radix tree, reuse on by default | "agent traffic served well by default" |
| Both engines' first-load compilation | ADR-006 | the artifact is a cache |
| Python on the serving path | ADR-005's context | it "would reintroduce the host overhead vLLM V1 and SGLang spent a year removing" |

## What the incumbents do not have

The inventory's last section: a target other than NVIDIA, and its own
kernels. TensorRT-LLM's kernels are NVIDIA's; vLLM and SGLang on AMD run on
AITER's. rustinfer generates every kernel from its Kernel IR and keeps its
own catalog per target, which is the premise of ADR-005 and the reason
[the kernel compiler](kernel-compiler.html) exists. AITER remains the
benchmark baseline (RI-NFR-003, RI-NFR-006) and the SRS lists the AITER
documentation site in its references for that purpose.
