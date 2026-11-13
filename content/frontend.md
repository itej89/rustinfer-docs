---
title: Frontend
section: Compiler
order: 1
summary: How a Hugging Face checkpoint of the LLaMA family becomes a Model IR document, a weight manifest and a checkpoint identity; the Architecture seam and how to add an architecture; the R1 gaps refused by name.
---

# Frontend

Read from `crates/rustinfer-frontend/src/`, SRS §3.2.2 (`RI-FE`) at v0.3,
`docs/api/CHANGELOG.md` and issue #6 at commit `7913427`. GitHub PR #24
merged into `main` as 84449e7 on 2026-11-12 and closed issue #6: the crate
`rustinfer-frontend` lowers the LLaMA family from a checkpoint directory
into Model IR. No subcommand calls it yet; `build` wires it to the graph
compiler and the artifact writer in #11.

## What it takes and what it gives

`rustinfer_frontend::lower(dir)` (or `lower_with_limits`) reads a Hugging
Face directory and returns a `Lowered` value with four parts:

| part | what it is |
|---|---|
| `document` | the validated Model IR `Document`: one weight set, the functions `prefill` and `decode`, one paged KV group named `main` (RI-FE-001, RI-MIR-009, RI-MIR-010) |
| `manifest` | the weight manifest: every Model IR weight mapped to its shard, tensor name, dtype, shape and byte range, with `root "."`, `source_layout` and `target_layout` `row_major`, `transform` `identity` and `ranks [0]` (RI-FE-002, RI-ART-005); the graph compiler later sets the target layout and transform per weight (#10) |
| `identity` | the checkpoint identity a load must match: the SHA-256 of `config.json` and each shard's size and header hash (RI-ART-008, RI-ART-012) |
| `config` | the typed `ModelConfig` the document was built from |

Only `config.json`, `model.safetensors.index.json` when present and the
safetensors headers are read, never a weight byte (RI-FE-004). All three are
untrusted input, bounded by size before they are read and parsed into typed
structures, and every refusal names the field or tensor (RI-SEC-003). With
an index, only the shards its `weight_map` names are read, so a
consolidated copy beside the shards is ignored; without one, every
`.safetensors` file in the directory, in name order. Safetensors are parsed
in Rust inside the crate, with no Python (OI-004).

## What lowers

The `llama` architecture serves four `model_type` values, the families
RI-FE-001 lists for R1 since SRS v0.3: `llama` (LLaMA 1, 2 and 3),
`mistral`, `qwen2` (QKV bias, often tied embeddings) and `qwen3` (QK norm).
Per layer the graph is `rmsnorm` → q, k and v `matmul` (with bias when the
family has one) → `rope` → `kv_cache_write` → `attention_prefill` or
`attention_decode_paged` → o `matmul` → `residual_add` → `rmsnorm` → gate
and up `matmul` → `silu_and_mul` → down `matmul` → `residual_add`; then the
final `rmsnorm`, `logits_head` (reading the embedding table when the
embeddings are tied) and `sample`. Logits are `fp32`.

Every architecture shares one calling convention so the executor binds the
same names whatever the model: inputs `token_ids`, `positions`,
`slot_mapping` and, for `decode`, `block_table` and `seq_lens`; outputs
`logits` and `tokens`. Model IR weights are named after the checkpoint
tensors (`model.layers.N.self_attn.q_proj.weight`).

Refusals, each naming what it refuses: a `model_type` outside the registry,
with the supported list (RI-FE-003); the first missing or unexpected tensor,
and a shape or dtype mismatch (RI-FE-002); a non-contiguous safetensors
data range; an unknown RoPE scaling type.

| family | `model_type` | state |
|---|---|---|
| LLaMA | `llama` | <span class="state-ok">lowers</span> — golden graph `tests/golden/llama.json` |
| Mistral | `mistral` | <span class="state-ok">lowers</span> without an active sliding window — golden graph `mistral.json` |
| Qwen2, Qwen2.5 | `qwen2` | <span class="state-ok">lowers</span> — golden graph `qwen2.json` |
| Qwen3 | `qwen3` | <span class="state-part">parsed, refused at lowering</span> — QK norm, until #26 |

## The Architecture seam

Everything outside `src/arch/` is architecture-neutral: `lowering.rs` walks
the directory, `config.rs` bounds and parses `config.json` and looks up the
`model_type`, `safetensors.rs` reads the headers, and `mapping.rs` matches
the expected tensors against them and builds the manifest. An architecture
supplies the three things that differ, as the crate-internal trait
`Architecture`:

| method | what it does |
|---|---|
| `parse_config(model_type, fields)` | reads the architecture's configuration from the fields of `config.json` into a type implementing `ArchConfig` |
| `expected_tensors(config)` | the tensors a checkpoint of that configuration holds, in weight order; fallible, so a configuration of another architecture's type is reported as a registry bug instead of answered with an empty table |
| `build_graph(config, dtype)` | the validated `prefill` and `decode` document over those tensors |

`REGISTRY` in `arch/mod.rs` maps each `model_type` to its architecture, one
line per type, and `SUPPORTED_MODEL_TYPES`, the list the refusal reports, is
derived from it. `ModelConfig::downcast::<LlamaConfig>()` exposes the
architecture-specific configuration. A minimal architecture compiled only
for the crate's unit tests (`arch/test_arch.rs`) lowers through the same
generic path, which shows that path needs nothing from the LLaMA family.

**Adding an architecture**, as `arch/mod.rs` sets out:

1. Create `src/arch/<name>/` with a unit struct implementing
   `Architecture` and a configuration type implementing `ArchConfig`, plus
   its tensor names and graph builder. Read `config.json` through `Fields`
   so every refusal names the field, use the function inputs and outputs of
   `arch/signature.rs`, and validate the document before returning it.
2. Add one line per `model_type` to `REGISTRY`.
3. Add a fixture `config.json` and a golden graph under `tests/`.

The first real second architecture is RI-FE-005 (MoE and MLA, R3).

## R1 gaps

What the Model IR cannot yet express is refused by name at lowering, never
approximated (RI-FE-001 v0.3, issue #6):

| gap | refusal | lifted by |
|---|---|---|
| Qwen3 QK norm (`q_norm`, `k_norm`, a per-head `rmsnorm`) | refused as R2: the R1 `rmsnorm` normalises over the whole last dimension, so lowering it would be silently wrong | #26, a per-head attribute on `rmsnorm`; the `qwen3` fixture then gets a golden graph |
| `llama3`, `yarn` and `dynamic` RoPE scaling | parsed, then refused: `rope_scaling type … (Model IR v1 carries linear scaling only)`; this rejects Llama 3.1 and later | a static frequency-table attribute on `rope`, follow-up of #27 |
| An active sliding window (Mistral's `sliding_window`, Qwen's under `use_sliding_window`) | refused as R2 (RI-MIR-010 window groups) | R2 |
| One dtype per checkpoint | the embedding table's dtype is taken and any other is refused as `mixed_dtype`, which blocks mixed fp8 and bf16 checkpoints such as DeepSeek-V3 | a dtype per `ExpectedTensor` (RI-FE-006) |

Supported families by release are on [supported models](supported-models.html);
the Model IR the frontend lowers to is on [design](design.html).
