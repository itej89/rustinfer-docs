---
title: Design
section: Design
order: 1
summary: The three representations, the fourteen crates and the direction their dependencies may point, the targets, and the four foundations every crate shares; the error contract, the log line, settings and constants.
---

# Design

Read from ADR-001, ADR-003, ADR-005, SRS §2, `docs/uml/component-diagram.md`,
`Cargo.toml`, `crates/rustinfer-core/`, `crates/rustinfer-mir/`,
`crates/rustinfer-target/`, `crates/rustinfer-planner/` and
`crates/rustinfer-cli/src/targets.rs` at commit `f039b4d`. The system as a whole is drawn on the [architecture diagram](architecture-diagram.html), in the C4 model from its context down to its code, with the layer stack, the standards, the build-then-run sequence and the deployment; the tree's own UML diagrams are on [design diagrams](design-diagrams.html).

## Three representations

ADR-005 fixes three representations and says there is no other interface
between a model file and machine code.

| representation | what it is | who produces it | who consumes it | carried in the artifact as |
|---|---|---|---|---|
| **Model IR** | a typed SSA graph: each node applies one operator to named input tensors and defines named outputs; shapes mix static integers with the four named dynamic dimensions `batch`, `num_tokens`, `seq_len`, `beam`, bounded by a profile; every tensor has a placement slot and every node a device slot. In the code as `rustinfer-mir` since Codeberg PR #19 (below) | the frontend | the graph compiler, the planner, every target | canonical JSON (sorted keys, compact, exact integers), versioned on its own (RI-MIR-007, -008) |
| **Kernel IR** | a tile-level MLIR dialect with explicit layouts: tiles, memory spaces (global, shared, register), barriers, a matrix-multiply op, masked loads and stores, reductions, structured control flow; thread identity does not appear | Rust generator functions, through a builder | the kernel compiler's lowerings | not carried; the lowered binaries are, in the `kernels` section |
| **Plan** | the static schedule: an ordered list of launches with kernel id, argument bindings, shape expressions over the dynamic dimensions, and sub-plans for prefill, decode and a mixed iteration. The launch itself, `Launch` in `rustinfer-target` (kernel id, operator, operand ranges with dtype and shape, a host-sync mark), is in the code since GitHub PR #21; the schedule is the graph compiler's, #10 | the graph compiler | the executor, verbatim | the `plan` section |

The SRS's §2.1 names the model: Core ML's MIL as the one graph contract, MLX's
fixed catalog of kernels plus a small fuser, Metal's AIR as portable IR
finalised on the device, Core ML's scheduler as the planner across units. The
rationale for a tile IR rather than a thread IR is RI-KC-002's: a tile IR
retargets to SIMT, vector and mesh devices; a thread IR does not.

## The Model IR in the code

Read from `crates/rustinfer-mir/src/` and `docs/api/model-ir.md` at
`f039b4d`, with the #27 changes of 2026-11-13 (PRs #30 and #32) read at
`04a2a26`. Codeberg PR #19 merged into `main` as 2d75c5d on 2026-11-12 and
closed issue #3; the
crate is the first component crate with behaviour, and its public API is
the `pub use` list of `lib.rs`: `Document`, `Function`, `KvGroup`, `Node`,
`Op` with its attribute structs, `OpKind` and the registry types, `Tensor`,
`DType`, `Shape`, `Dim`, `DynamicDim`, `Profile`, `Encoding`,
`PlacementSlot`, `Location`, `ShardSpec`, `MemoryTier`, `DeviceSlot`, `Limits` and `Error`.

**The document.** `Document` holds `ir_version`, one weight set, the
functions by name and the KV groups by name. A weight is a `Tensor`
descriptor and nothing more: name, dtype, shape, an `encoding` present
exactly when the dtype is fp8 (RI-MIR-011), and a `PlacementSlot` whose
`location` is empty until the planner fills it with a device index, a
memory-tier index the device can use and an optional shard spec (RI-MIR-005,
ADR-009; PR #32, 2026-11-13; before it the slot was a tier kind, `hbm`,
`dram`, `cxl` or `nvme`). The document never holds a weight byte; the bytes are the
weight manifest's and Sluice's business ([artifact](artifact.html),
[Sluice](sluice.html)).

**Functions.** `prefill` and `decode` in R1 (RI-MIR-009); `draft` and
`adapter` are refused as R3 and any other name as unknown. A `Function` is
its input tensors, its output names and its nodes in definition-before-use
order: a node reads only weights, function inputs and the outputs of earlier
nodes, a cycle is refused naming the first node on it, and an acyclic but
mis-ordered list is refused as `use_before_definition`. Every node carries
an `Op` and a `DeviceSlot`, empty until the planner fills it.

**KV groups.** A `KvGroup` is `kind` (`paged` in R1), `dtype`,
`num_kv_heads` and `head_dim`, one per document in R1 (RI-MIR-010). Every
`attention_prefill`, `attention_decode_paged` and `kv_cache_write` node names
its group in `attrs.kv_group`; a missing or unknown name is refused naming
the node.

**Operators.** The twenty operators of RI-MIR-004 are one static registry in
`registry.rs`, an `OperatorSpec` of release, arity and dtype rules per
operator, kept in `OpKind::ALL` order by a unit test. Since PR #30 one
`operators!` list generates `Op`, `OpKind`, `COUNT` and `ALL`, the two enums
are no longer `#[non_exhaustive]` so a new operator fails to compile until
every match handles it, and the registry has an `implicit_operands` column
naming the operands a launcher adds beyond the node's arity (the KV cache
pools of the paged operators), which resolved OI-013;
`docs/api/model-ir.md` "Adding an operator" lists every place. Sixteen are accepted in R1, `fused` among them as the composition
of its parts; `collective` (R2) and `moe_route`, `moe_experts` and
`lora_apply` (R3) exist as variants and are refused with
`error=unsupported` naming the node, the operator and the release.

**The validator.** `Document::validate` refuses the first fault it meets,
and the error names the function, the node and the field: a cycle, an
undefined input, use before definition, a duplicate definition, an arity or
dtype-rule breach, a non-finite attribute, a missing or unknown KV group, an
encoding fault, or a later-release operator or feature (RI-MIR-006). Every
`Error` maps to the code `invalid` or `unsupported` under `component=mir`,
following the [error contract](#the-error-contract).

**Canonical JSON.** `to_json` validates first, then writes sorted keys,
compact, exact integers, shortest round-trip reals, and empty slots and
absent encodings as explicit `null`. `from_json(to_json(d)) == d` and
`to_json(from_json(text)) == text` for any text the writer produced, under
`ir_version` 2 since PR #32; the reader also accepts a version 1 document
whose slots are all empty, reads it as version 2, and refuses a filled
version 1 slot as `FilledLegacySlot` because it must be re-planned
(RI-MIR-007, -008). The
schema is `docs/api/model-ir.md` in the tree and the format has its own
changelog line in `docs/api/CHANGELOG.md`.

**The bounded reader.** `from_json` caps the text length, parses, and then
reads in three phases: an untyped scan of the version, the counts and every
name (operator, dtype, dimension, encoding, KV group) that refuses naming
the node or tensor; typed construction that refuses a missing, unknown or
mistyped field as `malformed`; then validation. The bounds are the
`MODEL_IR_MAX_*` constants in `rustinfer-core` ([constants](ref-constants.html)),
and every refusal is logged once at `error` as
`stage=read boundary=model_ir_json reason=...` (RI-SEC-003).

**What is not in it.** The `Profile` is a type of the crate but not part of
the document: the artifact carries it as its own section (ADR-002) and the
graph compiler resolves dimensions against it (RI-GC-002). The R2 dtypes
`int8`, `fp4x2` and `e8m0`, the R3 `int4x2`, the `lookup_table` and
`sparse` encodings and per-block granularity are specified in the SRS and
refused by this release naming the tensor.

## The crates and the direction of dependencies

One crate per box of the component diagram; the source tree mirrors the
diagram (SWG-001 §5.9.3) and Cargo refuses a cycle, so the direction is
enforced by the build, not by review. The full table with sizes and tests is
generated on the [crates](ref-crates.html) page.

| layer | crates | depends on |
|---|---|---|
| command | `rustinfer-cli` | everything below |
| runtime | `rustinfer-runtime` | artifact, target, planner, sluice, core |
| sluice | `rustinfer-sluice` (the weight streamer, #18) | artifact, target, core |
| compilers | `rustinfer-compiler` (graph), `rustinfer-kc` (kernel) | mir, target, artifact, core |
| planner | `rustinfer-planner` | mir, core |
| frontend | `rustinfer-frontend` | mir, core |
| artifact | `rustinfer-artifact` | mir, core |
| targets | `rustinfer-target` (traits, registry, CPU reference); `rustinfer-target-rocm`, `-riscv-vector`, `-riscv-mesh`, `-spirv-vulkan` | `rustinfer-target`: mir, core; each backend: target, core |
| model IR | `rustinfer-mir` | core |
| foundation | `rustinfer-core` | nothing in the workspace |

At `f039b4d` `rustinfer-core`, `rustinfer-cli`, `rustinfer-mir`,
`rustinfer-artifact`, `rustinfer-planner` and `rustinfer-target` carry
behaviour and the four backend crates implement `Target` as stubs; the
compilers, the frontend and the runtime have their `COMPONENT` name, their
error enum and their `pub use` list, so the dependency graph is fixed from
the first commit (the component diagram cites heuristic G22, logical
dependencies made physical). The Cargo manifests carry the edges `mir` →
`core`; `artifact`, `planner` and `target` → `mir`, `core`; each backend →
`target`, `core`; the command → every crate. The compilers and the runtime
still list only `core`, and the diagram's edges from them to `mir`, `target`
and `artifact` are added when the issues that need them land.
`rustinfer-mir` adds `serde` and `serde_json`, pinned, for the canonical
JSON; `rustinfer-planner` the same two and `tracing`; `rustinfer-target`
`tracing`.

The public API of a crate is the `pub use` list in its `lib.rs`; everything
else is crate-private. `missing_docs = deny` makes every public item a
documented decision.

## Targets in the code

Read from `crates/rustinfer-target/src/`, the four backend crates and
`crates/rustinfer-cli/src/targets.rs` at `f039b4d`. GitHub PR #21 merged
into `main` on 2026-11-12 and closed issue #5. ADR-003's one trait composed
of three capabilities is the `pub use` list of `lib.rs`:

| trait | methods in the code | notes |
|---|---|---|
| `Target` | `architecture`, `catalog`, `devices`, `device(index)`, `launcher(index)` | `NoDevice` for an index the host does not have (RI-NFR-016) |
| `Catalog` | `architecture`, `entries`, `select(node, query)` | device-free; `select` returns the cheapest entry matching operator, every operand's dtype and the encoding (`KernelQuery.dtypes`, `encoding`, PR #30), layout and bucket among those whose `Validation` names this architecture (RI-GC-005, RI-KC-013); `CatalogEmpty` naming the target when there are no entries (RI-RV-002), `NoKernel` naming the query when nothing matches |
| `Device` | `properties`, `alloc`, `free`, `create_stream`, `create_event`, `record`, `wait`, `copy_to_device`, `copy_to_host`, `copy_on_device`, `synchronize`, `synchronize_event`, `capture`, `replay`, `sync_counters`, `reset_sync_counters` | every method takes `&self`, a backend serialises its own state; `wait` makes a stream wait on the device without the host; the three host synchronisations are counted (`SyncCounters`) so a test can prove a path performs none (RI-RT-010); `capture` splits a sub-plan into graph segments at the host-synchronising launches, keyed by a batch bucket (RI-TGT-005, RI-GC-015) |
| `Launcher` | `load(binary)`, `launch(launch, stream)` | executes one resolved `Launch` against bound buffers; refuses an unknown kernel, a mismatched operand, an unsupported dtype or a range outside a live buffer before any byte is read |

All four are object-safe and `Send + Sync`, so the runtime will hold
`Box<dyn Target>` (one indirect call per launch, ADR-003's price) and the
compiler `&dyn Catalog`, which is why `build` will run on any host. A
`KernelEntry` is a kernel id, the operator, its dtypes, a layout, shape rules,
a `KernelCost` (measured, or `Untuned`), an optional `Validation` record
(architecture, driver version, date) and tuned parameters; a `KernelBinary`
carries the bytes, their `BinaryFormat` (in `rustinfer-core` since PR #30) and the
Kernel IR beside them, required and refused when empty since PR #29 (RI-ART-013).
A `Launch` is the kernel id, the operator, input and output `Operand`s (a
buffer range with dtype and shape) and a `HostSync` mark; `segments` splits a
launch list at the marks.

A backend exposes one `TargetEntry` (its architecture strings and a
constructor) and the `Registry` resolves a target from an architecture string
only, validated at the boundary (non-empty, at most 64 bytes, `[A-Za-z0-9_-]`)
and never mapped from a product name (RI-TGT-001); the refusal is logged once
as `stage=resolve boundary=architecture_string`. The composition root is
`rustinfer-cli/src/targets.rs`, one line per backend crate, and a unit test
there asserts the registry lists exactly `cpu`, `gfx942`, `gfx950`,
`riscv-vector`, `riscv-mesh` and `spirv-vulkan`; adding a target is a new
crate and one line there, nothing in the compilers, planner or runtime
(RI-TGT-004). `build` and `tune` resolve `--target` before any component
runs. The one Kernel IR lowering a backend is to provide does not exist yet
(#7, #8).

The CPU reference target `CpuTarget` registers `cpu`: a `reference` module
of plain functions over `f32` slices with `f32` accumulation, the
correctness oracle of every other target (RI-TGT-003, RI-KC-007), covering
`embedding`, `matmul`, `logits_head`, `rmsnorm`, `layernorm`, `rope` in the
rotate-half convention, `silu_and_mul`, `gelu_and_mul` (tanh approximation),
`residual_add`, `attention_prefill`, `attention_decode_paged`,
`kv_cache_write`, `quantize`, `dequantize` and `sample`, a pure function of
a caller-supplied uniform draw; each checks its operand lengths and index
operands and refuses a mismatch naming the operator and the operand. The
`numeric` module converts `bf16`, `fp16` and the fp8 `e4m3` and `e4m3fnuz`
formats, round to nearest even and saturating. The catalog lists one
`Untuned` native kernel `cpu.<operator>` per compute operator, validated on
`cpu`, and no fused kernel, so the compiler never fuses for `cpu`; the one
device has a memory budget (16 GiB by default, `OutOfMemory` past it), and
its launcher checks buffers out of one mutex around the compute so no lock
is held across a launch. The four backend crates (`RocmTarget` under
`gfx942` and `gfx950`, `RiscvVectorTarget`, `RiscvMeshTarget`,
`SpirvVulkanTarget`) implement `Target` with an `EmptyCatalog` and no device,
so a build for one fails at kernel selection with `catalog empty` naming the
target, which RI-RV-002 keeps as the proof that the abstraction holds end to
end; the `unsafe` budget is still `0`, the HIP binding is #12.

## The error contract

Every crate defines one error enum with `thiserror` and implements the
`StructuredError` trait from `rustinfer-core::error`: `component()` returns
the crate's name and `code()` one of ten `ErrorCode` values whose `snake_case`
string is the wire value. The entry point prints any failure as one line,

```text
error=<code> component=<name> detail="<text>"
```

with the detail quoted and `"`, `\` and newlines escaped so the line stays
one line and parses. The codes are `config`, `usage`, `not_found`, `io`,
`invalid`, `unsupported`, `not_implemented`, `artifact`, `device` and
`internal`; the enum is `#[non_exhaustive]` and the source says a class may be
added but never renamed. The CLI's own enum wraps every component's enum and
delegates component and code to it, so `inspect` on an existing file reports
`component=artifact`, not `cli`. The generated list is on
[error codes](ref-error-codes.html).

What the lints forbid is as much a part of the contract: `unwrap_used`,
`expect_used`, `panic`, `todo`, `unimplemented` and `dbg_macro` are denied
workspace-wide, with `clippy.toml` allowing `unwrap` and `expect` in tests
only. Every error path in production code is a typed value.

## The log line

`rustinfer-core::logging` installs one `tracing` subscriber with a custom
event formatter. Every line is `key=value` text on stderr (RI-CLI-011):

```text
ts=<ISO-8601, millisecond, Z> level=<level> component=<target> [msg="<quoted>"] <field>=<value>...
```

The timestamp is produced without a date crate, by Howard Hinnant's
`civil_from_days` in `logging.rs`. `configure(level)` is idempotent through a
`OnceLock`, and the order at start is fixed by `main.rs`: parse arguments,
read settings, configure logging, emit the version manifest, dispatch. The
manifest (RI-CLI-010) is one `info` line per entry under `component=manifest`
with `startup="version_manifest"`: the software, the `rustc` that built it,
the host OS and architecture, and each direct dependency. Dependency versions
are read from `Cargo.lock` by `build.rs` at compile time and baked in, so the
list cannot drift from the lock file. stdout carries only results.

The observability document in the tree records that structured logging is the
only tier done in R1; metrics are R2 and health and tracing are R3
([runtime](runtime.html)).

## Settings and constants

Two files under `rustinfer-core::config` divide configuration the way SWG-001
§13.6 asks.

**`constants.rs`** is the single definition of every domain string and
threshold: environment variable names, the default log level and cache
directory name, the artifact magic `RIE\0`, extension, format version and
weight alignment, the KV block size, memory fraction and block priority
defaults, the two exit codes, and the three field names of the error line.
The file's header says a literal that encodes a concept appears there and
nowhere else. The generated table is on [constants](ref-constants.html).

**`settings.rs`** reads the environment once, at the process boundary, into a
typed `Settings { log_level: LogLevel, cache_dir: PathBuf }`.
`Settings::from_env` is the only reader of the environment in the workspace;
`from_lookup` takes a closure so tests inject values. An invalid
`RUSTINFER_LOG` is `SettingsError::InvalidLogLevel` and a host with neither
`XDG_CACHE_HOME` nor `HOME` is `NoCacheDir`, both reported as `error=config
component=core` before any work starts. Downstream code receives typed values
and never a raw string.

## Rules the compiler enforces

ADR-001 maps every SWG-001 rule to Rust tooling; `CONTRIBUTING.md` lists each
rule beside what enforces it. The ones enforced by the build rather than by
review: `missing_docs`, `unsafe_code` and `unused_must_use` denied;
`rust_2018_idioms` denied; clippy `pedantic` as warnings promoted to errors by
`-D warnings` in CI; `print_stdout` and `print_stderr` denied, with one
`#[allow]` on the entry point's error path; `missing_errors_doc` and
`missing_panics_doc` denied. `unsafe` is allowed only in a backend's `ffi`
module and the MLIR binding layer, each block with a `// SAFETY:` comment,
and `scripts/ci/check_unsafe_budget.sh` fails CI if the count grows past
`scripts/ci/unsafe_budget.txt`, which holds `0`. The rest of the rules, and
how to contribute, are on [engineering rules](engineering-rules.html).
