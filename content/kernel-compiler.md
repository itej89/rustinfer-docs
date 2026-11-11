---
title: Kernel compiler
section: Compiler
order: 2
summary: The route from a Rust generator to a device binary; the tile-level Kernel IR, the AMD, SPIR-V and RISC-V lowerings, the fixed catalog plus one fuser, the autotuner, and the CPU reference as the oracle.
---

# Kernel compiler

Read from ADR-005, SRS §3.2.5 (`RI-KC`), §3.2.10 (`RI-RV`), §2.6 and §4 at
commit `082df51`. The `rustinfer-kc` crate is an error type; issues #7, #8
and #9 implement this page in that order. Nothing described here has been
compiled, lowered or measured.

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
through the `melior` crate at one pinned version and `lld` is linked for
code objects (RI-KC-008). The target's own module loader takes the result.
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

## The Kernel IR

An MLIR dialect at tile level with explicit layouts: tiles, memory spaces
(global, shared, register), barriers, a matrix-multiply op, masked loads and
stores, reductions and structured control flow. Thread identity does not
appear (RI-KC-002). The reason recorded is retargetability: a tile IR lowers
to SIMT (AMD), vector (RVV) and mesh (Tensix) devices; a thread IR does not.

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

OI-009: `melior` needs a pinned MLIR and LLVM and building them in CI is
slow; the SRS's §1.4 names LLVM 22, and the recorded resolution is a vendored
prebuilt with a recorded hash. The issue draft for #7 says an ADR-007 will
record it; no ADR-007 exists at `082df51`. OI-008: autotuning needs a gfx950
host. OI-003: no RISC-V accelerator is on the bench. See
[open issues](open-issues.html).
