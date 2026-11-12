---
title: Features
section: Overview
order: 5
summary: Every feature of the engine by component with its release tag and its status on 2026-11-10, and the feature combination matrix the tree refuses unlisted pairs against.
---

# Features

Read from the SRS by component and from `docs/feature-matrix.md` at commit
`082df51`. A status of **Supported** means tested in the tree; **Planned
R*n*** means a requirement and, for R1, an issue exist; **Not started** is
used where the SRS names the release but no issue has been opened yet (every
R2 to R4 row). On 2026-11-12 the supported rows are the core, the Model IR, the
artifact, the planner interfaces and the targets, all on `main`.

## By component

| component | feature | requirement | release | status |
|---|---|---|---|---|
| CLI | six subcommands, exit codes, one structured error line | RI-CLI-001 | R1 | <span class="state-part">in progress</span> — contract tested, behaviour pending |
| CLI | path validation before any work | RI-CLI-012 | R1 | <span class="state-part">in progress</span> |
| CLI | version manifest at start; `key=value` logs with ISO-8601, level, component | RI-CLI-010, -011 | R1 | <span class="state-part">in progress</span> |
| CLI | `--require-prebuilt` refusal | RI-CLI-004 | R1 | <span class="state-part">in progress</span> — the refusal exists, the build it refuses does not |
| CLI | `build`, `inspect` | RI-CLI-002, -005 | R1 | Planned R1, #11 |
| CLI | `run` with token ids | RI-CLI-006 | R1 | Planned R1, #14 |
| CLI | `tune` | RI-CLI-007 | R1 | Planned R1, #9 |
| CLI | build on first load into the cache | RI-CLI-003 | R1 | Planned R1, #11 |
| CLI | `bench` with TTFT, TPOT, ITL percentiles | RI-CLI-008 | R2 | Not started |
| CLI | `serve` with YAML config and `--set` | RI-CLI-009 | R3 | Not started |
| Frontend | LLaMA from HF | RI-FE-001 to -003 | R1 | Planned R1, #6 |
| Frontend | weight streaming, Model IR JSON input, FP8 import | RI-FE-004, -006, -008 | R2 | Not started |
| Frontend | MoE and MLA families, AWQ, GPTQ, MXFP4, LoRA adapters | RI-FE-005 to -007 | R3 | Not started |
| Model IR | typed SSA graph, profile-bounded dims, R1 dtypes, operator set, slots, validation, canonical JSON, own version, named functions, KV groups, encodings | RI-MIR-001 to -011 | R1 | <span class="state-ok">done</span> — PR #19 merged 2026-11-12 |
| Graph compiler | logged pass pipeline, shape inference, fusion against the catalog, bf16 and fp8 precision, kernel selection, arena planning, Plan, layouts, determinism, matrix refusal | RI-GC-001 to -009, -014 | R1 | Planned R1, #10 |
| Graph compiler | tensor parallel sharding, mixed iteration sub-plan | RI-GC-010, -007 | R2 | Not started |
| Graph compiler | expert parallel, LoRA points, speculative verification sub-plan | RI-GC-011 to -013 | R3 | Not started |
| Kernel compiler | Rust generators, tile-level MLIR dialect, in-process LLVM and `lld`, determinism | RI-KC-001, -002, -008, -011 | R1 | Planned R1, #7 |
| Kernel compiler | AMD lowering with MFMA, LDS, bounds-checked loads | RI-KC-003 | R1 | Planned R1, #8 |
| Kernel compiler | R1 generator set, autotuner, CPU validation, validated-hardware records | RI-KC-005 to -007, -013 | R1 | Planned R1, #9 |
| Kernel compiler | SPIR-V lowering, elementwise fuser, resource reports | RI-KC-004, -010, -012 | R2 | Not started |
| Kernel compiler | RISC-V vector lowering; MoE, MLA, LoRA, verification generators | RI-KC-004, -005 | R3 | Not started |
| Kernel compiler | RISC-V mesh lowering; assembly generator for one hot kernel | RI-KC-004, -009 | R4 | Not started |
| Planner | topology model, reserved artifact sections | RI-PLN-001, -005 | R1 | <span class="state-ok">done</span> — GitHub PR #20 merged 2026-11-12 |
| Planner | discovery, placement over GPU, host, DRAM, NVMe, RDMA; cached and pinnable | RI-PLN-002 to -004 | R2 | Not started |
| Planner | CXL tier, expert placement | RI-PLN-003 | R3 | Not started |
| Planner | DPU-resident serving functions | RI-PLN-006 | R4 | Not started |
| Artifact | header, sections, verifying reader, atomic writer, alignment, versions, metadata | RI-ART-001 to -006, -008 | R1 | <span class="state-ok">done</span> — Codeberg PR #21 merged 2026-11-12 |
| Artifact | one artifact per rank | RI-ART-007 | R2 | Not started |
| Targets | architecture strings, the `Target` trait, CPU reference operators, one-crate backends, stub targets that fail with `catalog empty` | RI-TGT-001 to -004, RI-RV-001, -002 | R1 | <span class="state-ok">done</span> — GitHub PR #21 merged 2026-11-12 |
| Targets | device graph capture; CPU collectives | RI-TGT-005, -003 | R2 | <span class="state-part">in progress</span> — `capture` and `replay` exist, eager on the CPU; collectives not started |
| ROCm | HIP binding, typed errors, `gcnArchName` check, module loading with resource checks, `unsafe` confined to `ffi` | RI-ROC-001 to -005 | R1 | Planned R1, #12 |
| ROCm | RCCL collectives, HIP graphs per batch bucket | RI-ROC-006, -007 | R2 | Not started |
| ROCm | own IPC all-reduce for small messages | RI-ROC-006 | R3 | Not started |
| Executor | load once, static execution, `enqueue` and `await_responses`, core `Request`, failure isolation, one stream per iteration | RI-RT-001 to -004, -006, -008 | R1 | Planned R1, #13 |
| Executor | streaming, cancel, stats, one process per rank | RI-RT-003, -005, -007, -009 | R2 | Not started |
| Scheduler | static batch | RI-SCH-003 | R1 | Planned R1, #13 |
| Scheduler | in-flight batching, decode before prefill, `max_utilization` default, chunked prefill, overlap scheduler, pause and resume, iteration stats, uniform token-level state | RI-SCH-001 to -006, -009, -010 | R2 | Not started |
| Scheduler | priorities and deadlines, LoRA batching | RI-SCH-007, -008 | R3 | Not started |
| KV cache | fixed-size block pool, O(1) LRU free list, admission refusal above `max_seq_len` | RI-KVC-001, -002, -004 | R1 | Planned R1, #13 |
| KV cache | memory fraction, radix-tree prefix reuse on by default, FP8 and INT8 storage, sliding windows | RI-KVC-003, -005, -008, -009 | R2 | Not started |
| KV cache | prioritised eviction, offload to DRAM and NVMe | RI-KVC-006, -007 | R3 | Not started |
| KV cache | offload to CXL and remote tiers | RI-KVC-007 | R4 | Not started |
| Sampling | greedy, temperature, top-k, top-p on device in one launch | RI-SMP-001 | R1 | Planned R1, #13 |
| Sampling | min-p, top-p decay, seeds, penalties, stop and bad words, logprobs, host post-processor, reproducibility | RI-SMP-001 to -004, -007 | R2 | Not started |
| Sampling | beam search, guided decoding | RI-SMP-005, -006 | R3 | Not started |
| Speculative decoding | draft/target, MTP, acceptance metrics, matrix refusals | RI-SPD-001 to -004 | R3 | Not started |
| Speculative decoding | EAGLE-3 linear and dynamic tree | RI-SPD-005 | R4 | Not started |
| LoRA | run-time adapters with host and device caches, waits and refusals | RI-LORA-001 to -003 | R3 | Not started |
| Distributed | tensor parallel on one node, shared build id check | RI-DIST-001, -004 | R2 | Not started |
| Distributed | expert parallel, attention data parallel | RI-DIST-002, -003 | R3 | Not started |
| Distributed | pipeline and context parallel, multi-node, Helios scale-up, disaggregated prefill and decode | RI-DIST-005 | R4 | Not started |
| Server | OpenAI-compatible endpoints, health and metrics, chat templates, request ids, limits, profiling toggles | RI-SRV-001 to -006 | R3 | Not started |
| Observability | `docs/observability.md` tier assessment and signal inventory | RI-OBS-004 | R1 | <span class="state-part">in progress</span> — the file is on `main` |
| Observability | Prometheus metrics, request logs, bench datasets | RI-OBS-001 to -003 | R2 | Not started |
| Security | canonical paths, only HIP and RCCL loaded, bounded artifact reader, bounded file parsing, input hashes, matrix refusal | RI-SEC-001 to -005 | R1 | Planned R1 (#2 carries path canonicalisation; the rest with #4, #6, #10) |
| Security | time budgets for grammars and post-processors | RI-SEC-006 | R3 | Not started |
| Concurrency | single-threaded compiler, one device context per rank, sequential autotuner | RI-CON-001, -002, -005 | R1 | Planned R1 |
| Concurrency | overlap channel, async server with backpressure | RI-CON-003, -004 | R2, R3 | Not started |

## The feature combination matrix

`docs/feature-matrix.md` is kept from the first release (RI-NFR-015). Its
rule, from the file: a combination not marked **S** is refused at build or at
admission, never attempted (RI-SEC-005, RI-GC-014). **U** is unsupported by
design, **T** untested, and **–** not yet implemented in any release. A cell
moves from `–` to `S` only with a test that exercises the pair.

On 2026-11-10 one cell is **S**: static batch with itself. Every other pair
is `–`, except the decisions carried from the TensorRT-LLM inventory:

| pair | marking | reason recorded |
|---|---|---|
| in-flight batching, chunked prefill × static batch | U | the policies exclude each other |
| tree speculation × sliding window | U | carried from the inventory; also refused with MLA (RI-SPD-004) |
| beam search × sliding window | U | carried from the inventory (RI-KVC-009) |
| speculation × pipeline parallelism | U | not a column until R4 (RI-SPD-004) |
| LoRA × TP, LoRA × EP, speculation × LoRA | T | combinations to be tested, not assumed |

The columns are static batch, IFB, chunked prefill, prefix reuse, FP8 KV,
sliding window, TP, EP, LoRA, linear speculation, tree speculation, guided
decoding, beam search, overlap scheduler and HIP graph. The lower triangle is
authoritative; the graph compiler will read the file's state and refuse an
unlisted pair naming it (RI-GC-014).
