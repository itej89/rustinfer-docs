---
title: Supported models
section: Overview
order: 4
summary: Which model families each release lowers and serves, from the SRS frontend requirements and the use cases; on 2026-11-10 no model runs, because only the scaffold exists.
---

# Supported models

Read from SRS §3.2.2 (`RI-FE`), §2.4, the feature inventory and the use cases
at commit `082df51`.

**No model runs today.** The tree is the Release 1 scaffold: the frontend
crate has an error type and nothing else (issue #6 adds the LLaMA lowering),
and there is no Model IR, artifact, target or executor for it to feed. The
table below is the plan the SRS commits to, with the release each row names
and the status on 2026-11-10.

## Input format

The only input is a Hugging Face model directory: `config.json`,
`*.safetensors` with an optional index, `generation_config.json` and the
tokenizer files (SRS §3.1.3). There is no intermediate checkpoint format, by
decision: the feature inventory marks TensorRT-LLM's `convert_checkpoint` step
as adopted without the intermediate. From R2 a model may also be given as a
Model IR JSON document (RI-FE-008). Safetensors are parsed in Rust; whether
with a crate or in-tree is open issue OI-004.

## Families by release

| family | `model_type` | what the frontend reads | release | status |
|---|---|---|---|---|
| LLaMA | `llama` | layers, hidden size, attention and KV heads, intermediate size, vocabulary, RoPE parameters and scaling, norm epsilon, tied embeddings (RI-FE-001) | R1 | <span class="state-no">not started</span> — issue #6 |
| Mistral, Qwen2, Qwen3 | `mistral`, `qwen2`, `qwen3` | the same lowering; the SRS lists them under RI-FE-001 with release R2 | R2 | <span class="state-no">not started</span> |
| MoE families: DeepSeek-V3 with MLA, Qwen MoE, GPT-OSS | | router, experts, shared experts, MLA latent projections (RI-FE-005) | R3 | <span class="state-no">not started</span> |
| Pre-quantized checkpoints: FP8 per-tensor and block-scale | | imported with their scales; refused when the target has no catalog kernel for the scheme (RI-FE-006) | R2 | <span class="state-no">not started</span> |
| Pre-quantized checkpoints: AWQ, GPTQ, MXFP4 | | as above | R3 | <span class="state-no">not started</span> |
| LoRA adapters, PEFT layout | | `adapter_config.json` plus safetensors, keyed by target module, rank checked against `max_lora_rank` (RI-FE-007) | R3 | <span class="state-no">not started</span> |
| Model IR JSON as input | | accepted in place of an HF directory (RI-FE-008) | R2 | <span class="state-no">not started</span> |
| Multimodal, encoder-decoder, Mamba and hybrid | | the feature inventory marks these *later*, after R4; no requirement exists | after R4 | <span class="state-no">not started</span> |
| Diffusion and visual generation | | out of scope: the SRS says rustinfer does not generate images or video | never | — |

## What a model needs from the rest of the engine

A family is supported when every operator its lowering emits has a catalog
kernel on the target. The R1 operator set (RI-MIR-004) is the LLaMA subset:
embedding, matmul, rmsnorm, rope, attention prefill, paged attention decode,
KV cache write, `silu_and_mul`, residual add, quantize, logits head and
sample. `collective` arrives in R2 and `moe_route`, `moe_experts` and
`lora_apply` in R3, which is why the MoE and LoRA rows above cannot come
earlier.

Refusals are typed and happen before any device work (goal 6 of the SRS): an
unsupported `model_type` is rejected naming it and the supported list
(RI-FE-003); a checkpoint with a missing or unexpected parameter fails naming
the first one (RI-FE-002), because the SRS's rationale is that a silent weight
mismatch is wrong output, not an error.

## Precision per release

The formats follow the AMD matrix cores (RI-MIR-003, RI-GC-004): bf16, fp16,
fp32 and fp8 (OCP e4m3 on gfx950, FNUZ e4m3 on gfx942) in R1; int8, fp4x2
and e8m0 scales plus an FP8 KV cache in R2; int4 weight-only in R3.
