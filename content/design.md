---
title: Design
section: Design
order: 1
summary: The three representations, the fourteen crates and the direction their dependencies may point, the targets, and the four foundations every crate shares; the error contract, the log line, settings and constants.
---

# Design

Read from ADR-001, ADR-003, ADR-005, SRS §2, `docs/uml/component-diagram.md`,
`Cargo.toml` and `crates/rustinfer-core/` at commit `082df51`. The diagrams
themselves are on [design diagrams](design-diagrams.html).

## Three representations

ADR-005 fixes three representations and says there is no other interface
between a model file and machine code.

| representation | what it is | who produces it | who consumes it | carried in the artifact as |
|---|---|---|---|---|
| **Model IR** | a typed SSA graph: each node applies one operator to named input tensors and defines named outputs; shapes mix static integers with the four named dynamic dimensions `batch`, `num_tokens`, `seq_len`, `beam`, bounded by a profile; every tensor has a placement slot and every node a device slot | the frontend | the graph compiler, the planner, every target | canonical JSON (sorted keys, exact numerics), versioned on its own (RI-MIR-007, -008) |
| **Kernel IR** | a tile-level MLIR dialect with explicit layouts: tiles, memory spaces (global, shared, register), barriers, a matrix-multiply op, masked loads and stores, reductions, structured control flow; thread identity does not appear | Rust generator functions, through a builder | the kernel compiler's lowerings | not carried; the lowered binaries are, in the `kernels` section |
| **Plan** | the static schedule: an ordered list of launches with kernel id, argument bindings, shape expressions over the dynamic dimensions, and sub-plans for prefill, decode and a mixed iteration | the graph compiler | the executor, verbatim | the `plan` section |

The SRS's §2.1 names the model: Core ML's MIL as the one graph contract, MLX's
fixed catalog of kernels plus a small fuser, Metal's AIR as portable IR
finalised on the device, Core ML's scheduler as the planner across units. The
rationale for a tile IR rather than a thread IR is RI-KC-002's: a tile IR
retargets to SIMT, vector and mesh devices; a thread IR does not.

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
| targets | `rustinfer-target` (trait, CPU reference); `rustinfer-target-rocm`, `-riscv-vector`, `-riscv-mesh`, `-spirv-vulkan` | target, core |
| model IR | `rustinfer-mir` | core |
| foundation | `rustinfer-core` | nothing in the workspace |

On the scaffold branch only `rustinfer-core` and `rustinfer-cli` carry
behaviour; every other crate has its `COMPONENT` name, its error enum and its
`pub use` list, so the dependency graph is fixed from the first commit (the
component diagram cites heuristic G22, logical dependencies made physical).
Note that the diagram shows the compilers and runtime depending on `mir`,
`target` and `artifact`, while the Cargo manifests at `082df51` list only
`core`; the edges are added when the issues that need them land.

The public API of a crate is the `pub use` list in its `lib.rs`; everything
else is crate-private. `missing_docs = deny` makes every public item a
documented decision.

## Targets

ADR-003: one trait, `Target`, composed of three capabilities. `Catalog` is
device-free, the list of generated kernels for an architecture with
constraints, tuned parameters, cost and validation records; the graph compiler
queries it, so `build` runs on any host. `Device` is enumeration, properties,
buffers, streams, events, copies and graph capture. `Launcher` executes one
Plan entry against bound buffers. A backend crate implements all three,
registers its architecture strings, and provides one Kernel IR lowering;
adding a target touches a new crate, one registry entry and one lowering, and
nothing in the compilers, planner or runtime (RI-TGT-004). Targets are
resolved from the architecture string only; product names are never
interpreted (RI-TGT-001). The runtime holds `Box<dyn Target>`, which ADR-003
prices at one indirect call per launch.

Registered strings: `cpu`, `gfx942`, `gfx950`, `riscv-vector`, `riscv-mesh`,
`spirv-vulkan`. The CPU reference implements every R1 operator in Rust with
fp32 accumulation and is the correctness oracle for every other target
(RI-TGT-003). The three RISC-V and SPIR-V crates are stubs until hardware is
on the bench; a build for one fails at kernel selection with `catalog empty`,
which RI-RV-002 keeps as the proof that the abstraction holds end to end.

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
