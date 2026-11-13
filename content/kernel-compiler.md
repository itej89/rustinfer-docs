---
title: Kernel compiler
section: Compiler
order: 3
summary: The route from a Rust generator to a device binary; the tile-level Kernel IR, the AMD, SPIR-V and RISC-V lowerings, the fixed catalog plus one fuser, the autotuner, and the CPU reference as the oracle.
---

# Kernel compiler

Read from ADR-005, ADR-007, SRS §3.2.5 (`RI-KC`), §3.2.10 (`RI-RV`), §2.6
and §4, `docs/api/kernel-ir.md` and `crates/rustinfer-kc/src/` at commit
`7913427`. GitHub PR #25 merged into `main` as ad51bce on 2026-11-12 and
closed issue #7: the `kir` dialect, the typed builder and, behind a Cargo
feature, the in-process link to a pinned MLIR and LLVM 23 that verifies a
kernel, lowers it for the host and translates it to LLVM IR. No generator,
no device lowering, no code object, catalog entry or autotuner exists yet;
those are #8 and #9. Nothing here has been run on a GPU.

## The route

```text
Rust generator (parameter struct) ──builder──▶ Kernel IR (MLIR dialect, tile level)
                                                     │
          ┌──────────────────────────────────────────┼──────────────────────────────┐
          ▼                                          ▼                              ▼
  MLIR gpu → rocdl → LLVM AMDGPU            MLIR spirv dialect           rustinfer's own lowering
  code object for gfx942 / gfx950           Vulkan-class devices         RVV (+ matrix ext.) via LLVM RISC-V
  MFMA, LDS, bounds-checked loads           (R2, compile-tested)         Tensix-class mesh via its open MLIR dialect
  (R1)                                                                   (R3 vector, R4 mesh)
```

No external process at any step: MLIR and LLVM are linked as libraries
through the `melior` crate at one pinned version, LLVM 23 (ADR-007), and
`lld` is to be linked for code objects (RI-KC-008, #8). Of the route, the
Kernel IR and its host lowering to LLVM IR are in the code; the three device
lowerings are not. The target's own module loader takes the result.
The SRS's §3.1.3 names the dialects linked: `gpu`, `amdgpu`, `rocdl`,
`spirv`, `vector`, `llvm`, with the AMDGPU, RISC-V and SPIR-V back ends.

## Generators, not kernels

A kernel exists only as a Rust generator: a function taking a parameter
struct (dtypes, tiles, layouts, pipeline depth, fused epilogue) and emitting
Kernel IR through a builder. No kernel may exist as MLIR text, HIP, OpenCL or
assembly source (RI-KC-001). The exception is RI-KC-009, R4: a generator may
emit target assembly for one hot kernel on one architecture, registered
through the same catalog interface and validated the same way, if measurement
after the R1 set shows it is needed (OI-001).

The R1 generator set (RI-KC-005) is the catalog of a transformer, "as MLX
keeps one": GEMM in bf16 and fp8 with bias, scale and activation epilogues;
attention prefill; paged attention decode; rmsnorm; rope with cache write;
`silu_and_mul`; embedding; residual add; quantize; logits head; sampling. R3
adds MoE routing and expert GEMMs, MLA attention, LoRA application and
speculative verification. One fusion generator composes chains of
elementwise and reduction ops into a single kernel, and the SRS forbids a
general-purpose fusion compiler (RI-KC-010, R2).

## The Kernel IR (in the code since PR #25)

An MLIR dialect named `kir` at tile level with explicit layouts. Thread
identity does not appear (RI-KC-002): no operation produces or takes a
thread, lane, wave or block id, and how a tile is spread over threads is the
lowering's decision. The reason recorded is retargetability: a tile IR
lowers to SIMT (AMD), vector (RVV) and mesh (Tensix) devices; a thread IR
does not. A kernel is one `func.func` in a `module`; its arguments are
buffers, its values tiles and indices, its control flow `scf.for`.

| concept | MLIR form |
|---|---|
| tile | `vector<RxT>` or `vector<RxCxT>`, rank 1 or 2 |
| buffer | `memref<…, 1>` global or `memref<…, 3>` shared, static shapes |
| mask | `vector<…xi1>` of the tile's shape |
| element types | `bf16`, `f16`, `f32`, `f8E4M3FN`, `f8E5M2`, `f8E4M3FNUZ`, `i32`, `i8` |

The six operations are `kir.tile_load` and `kir.tile_store` (with a layout,
`row_major` or `col_major`, and an optional mask; masked lanes read as zero
and are not written), `kir.make_mask`, `kir.mma` (`c + a × b`, the
accumulator type is the result type), `kir.reduce` (`sum` or `max` along one
axis) and `kir.barrier`. Elementwise arithmetic is `arith` on vectors. The
text form is MLIR's canonical generic form; `docs/api/kernel-ir.md` in the
tree is the reference for the text kept beside each binary in an artifact
(RI-ART-013).

**The operation table is the single source of truth.** The operations are a
Rust table in `crates/rustinfer-kc/src/dialect/`; the dialect MLIR loads is
IRDL text generated from it at context creation (`irdl_definition`), so no
C++ TableGen is built in the repository (ADR-007 point 6), and the verifier
MLIR runs on every kernel is the one derived from that table.

**The builder.** `KernelBuilder` is the one way a generator emits Kernel IR
(RI-KC-001): `new(name, argument buffer types)`, then `index`, `tile_load`,
`tile_store`, `make_mask`, `mma`, `reduce`, `add`, `barrier` and
`for_loop`, then `finish`, which returns a `KernelModule` whose `to_mlir`
is the canonical text. It checks what IRDL cannot (shapes and element types
agree, indices match the buffer rank, a mask matches its tile, a value is
used only in its scope) and needs no MLIR, so it works in every build.

**The MLIR link.** With the feature on, `KernelContext` (one per thread,
`!Send + !Sync`, MLIR's own thread pool disabled) offers `verify` (parse
with unregistered dialects disallowed, verify, print the canonical text
back), `lower_to_llvm_dialect` and `translate_to_llvm_ir`. Lowering rewrites
each `kir` operation into the standard `vector` and `arith` dialects and
then runs a flavour's pass pipeline; the one flavour today is `Host`, whose
barrier is erased and whose pipeline is `convert-scf-to-cf`,
`convert-vector-to-llvm`, `finalize-memref-to-llvm`, `convert-func-to-llvm`,
`convert-arith-to-llvm`, `convert-cf-to-llvm`, `reconcile-unrealized-casts`.
The flavour's two methods, the barrier lowering and the pipeline, are the
seam the AMD lowering (#8) fills with a `gpu.barrier` or `rocdl.barrier`
and the `rocdl` passes. Every output is byte-identical for the same text,
flavour and LLVM version, across contexts and threads (RI-KC-011). Text
entering the context is bounded by `KIR_MAX_TEXT_BYTES`; a refusal is
`error=invalid component=kc` naming the stage (`dialect`, `parse`, `lower`,
`translate`) with at most `KIR_MAX_DIAGNOSTICS` captured diagnostics. The
context re-checks the LLVM major against `LLVMGetVersion` when it is
created.

**The feature flag.** The link sits behind the Cargo feature `mlir` of
`rustinfer-kc`, re-exported by `rustinfer-cli` as `kc`, both off by
default, so the workspace builds and every non-MLIR test passes on a host
without LLVM (RI-NFR-016). Without it `require_link` and the CLI answer
`not_implemented`: `tune` fails with `error=not_implemented component=kc`
naming the `kc` feature. `unsafe` is allowed in one more module,
`crates/rustinfer-kc/src/mlir/`, and the CI budget moved from 0 to 5 blocks
(ADR-007 point 7). The feature's build dependencies need rustc 1.89, so the
workspace MSRV is 1.89 and an `msrv` CI job checks `--all-features` on that
toolchain.

## Installing LLVM 23 locally

ADR-007 pins LLVM **major 23, release line 23.1**, from `apt.llvm.org`
(suite `llvm-toolchain-<codename>-23`; `noble` on Ubuntu 24.04), bound
through `melior` 0.29.1 and `mlir-sys` 230.0.2 and linked statically, so the
binary loads no LLVM shared object. The Ubuntu archive's MLIR is LLVM 18,
which predates gfx950, and the LLVM release tarballs ship no MLIR, so
neither will do.

**With sudo**, run the script CI runs. It verifies the `apt.llvm.org` key
fingerprint, adds the suite for the host's codename and installs
`llvm-23-dev`, `libmlir-23-dev`, `mlir-23-tools`, `libpolly-23-dev` and
`libclang-23-dev` at the exact version pinned per codename:

```sh
scripts/ci/install_llvm.sh
cargo test --workspace --all-features
```

`.cargo/config.toml` points `MLIR_SYS_230_PREFIX` and `TABLEGEN_230_PREFIX`
at `/usr/lib/llvm-23`, where the packages install.

**Without sudo**, download the same packages (`apt-get download` or `curl`
from the pool) and extract each with `dpkg-deb -x <package>.deb <dir>`, then
point the two variables at the extracted prefix; the environment wins over
`.cargo/config.toml`, and `llvm-config` is relocatable:

```sh
export MLIR_SYS_230_PREFIX=<dir>/usr/lib/llvm-23
export TABLEGEN_230_PREFIX=<dir>/usr/lib/llvm-23
cargo test -p rustinfer-kc --features mlir
```

`apt.llvm.org` keeps only the latest build per suite, so the pinned version
strings go stale when it rebuilds; a bump changes `VERSIONS` in the script
and ADR-007 in one PR. Statically linked test binaries are about 240 MB each.

## The AMD lowering

Through the MLIR `gpu` pipeline to `rocdl` and the LLVM AMDGPU back end
(RI-KC-003): MFMA for the matrix op in each architecture's formats (bf16 on
both; fp8 FNUZ on gfx942; OCP fp8, fp4 and fp6 with e8m0 scales on gfx950),
LDS for shared tiles, and bounds-checked buffer loads. Kernel compilation is
deterministic for the same generator, parameters, target and LLVM version,
and the artifact records the LLVM version (RI-KC-011).

The SRS's own assumption (§2.6): that a tile-level IR lowered this way
reaches a large fraction of hand-written GEMM and attention performance on
gfx942 and gfx950, with Triton and FlyDSL as the published evidence. If
false, the assembly generator path closes the rest. The targets that make
this measurable are RI-NFR-006 (80 percent of the best AITER GEMM per
catalog bucket on gfx950 by the end of R2) and RI-NFR-003 (70 percent, then
100 percent, of vLLM-with-AITER throughput).

## The RISC-V and SPIR-V lowerings

RI-KC-004 says the RISC-V lowering is rustinfer's own: Kernel IR to a vector
form, RVV 1.0 with a vector-length-agnostic tile mapping and a core's matrix
extension where the catalog entry records it (RI-RV-004), through the LLVM
RISC-V back end; and to a mesh form for Tensix-class devices through their
open MLIR dialect. Whether the mesh path targets TT-MLIR's dialects or emits
its own kernels for the Tensix cores is open issue OI-011, to be decided
with a Blackhole card in hand. The SPIR-V path uses MLIR's `spirv` dialect.
The release order is spirv-vulkan compile-tested in R2, riscv-vector in R3,
riscv-mesh in R4, and RI-RV-003 fixes the bring-up order on hardware:
lowering compile-tested, CPU-reference parity for every R1 generator,
autotuned catalog committed with validation records, op tests.

## The catalog and the autotuner

The catalog is the committed, per-target list of generated kernels with
tuned parameters, constraints, cost and validation records; the graph
compiler selects from it without a device. `rustinfer tune --target <arch>
[--generator <name>] [--shapes <file>]` (RI-CLI-007) runs a generator over
its declared parameter space on the device, checks each variant against the
CPU reference, keeps the fastest correct variant per shape bucket, and
writes the entry with parameters, cost, binary hash and resource report;
catalogs are committed per target and merged with no duplicate keys
(RI-KC-006). Three rules guard it:

- No kernel enters the catalog or an artifact without validation against the
  CPU reference at its catalogued shapes within a per-dtype tolerance
  (RI-KC-007: "correctness before speed").
- An entry records the hardware it was validated on (architecture, driver
  version, date) and is never used on an architecture it was not validated
  on (RI-KC-013: "gfx950 and the CDNA successor share nothing but a CU
  count").
- The autotuner runs variants sequentially on one device and may distribute
  generators across devices by process (RI-CON-005).

From R2 every entry carries a resource report (registers, LDS, occupancy)
that `inspect` prints (RI-KC-012).

## What is unresolved

OI-009, how the pinned MLIR and LLVM are obtained, is resolved by ADR-007
(above). Still open after it: code-object emission (the `llc` equivalent
through the LLVM C API and `lld` as a library, with a byte-identical
rebuild), moved from #7 to #8 by the PR #25 review, which adds
`liblld-23-dev` to the install script; a hash-pinned mirror of the LLVM 23
packages if `apt.llvm.org` ever becomes a problem; an LLVM 23 build for
RISC-V hosts (R3). OI-008: autotuning needs a gfx950 host. OI-003: no
RISC-V accelerator is on the bench. See [open issues](open-issues.html) and
[decisions](decisions.html).
