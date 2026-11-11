---
title: Decisions and retracted conclusions
navtitle: Decisions
section: Trackers
order: 3
summary: The six ADRs and the owner's decisions the SRS and ADRs record, each with its reason and date; the conclusions this site reached while reading and then had to retract.
---

# Decisions and retracted conclusions

A decision is recorded here when the tree states it: in an ADR, in the SRS
changelog or constraints, or in a planning document. The reason column is the
tree's, paraphrased. Every decision below is dated 2026-11-10, the day the
project was specified; the column is kept so later rows can differ.

## Architecture decision records

| ADR | decision | reason | status |
|---|---|---|---|
| ADR-001 | Rust, stable, edition 2021, one workspace; SWG-001's Python and C++ rules mapped to `tracing`, `thiserror`, workspace lints, `cargo llvm-cov`, `cargo deny` and `cargo audit`; `unsafe` only in `ffi` modules with `// SAFETY:` and a CI count | memory safety at the FFI boundary with GPU runtimes, zero-cost abstractions on the inference path, one static binary | Accepted |
| ADR-002 | One `.rie` file: fixed header with magic, version, target, producer, SHA-256 and a section table; small sections as canonical JSON; 4096-aligned weights; a reader that validates everything before exposing a byte; a writer that streams to a temp file, hashes last, `fsync`s and renames | the TensorRT engine's property of no inference-time decisions, plus inspectable without a GPU, integrity-checked, never half-written, memory-mappable, versioned | Accepted |
| ADR-003 | One `Target` trait composed of `Catalog` (device-free), `Device` and `Launcher`; a backend is one crate, one registry entry, one lowering | the compiler must select kernels without a device, the runtime must launch them, and a RISC-V backend must be addable without touching compiler, planner or runtime | Accepted; revised the same day to remove kernel providers after ADR-005 |
| ADR-004 | Codeberg hosting with the standard's GitHub rules mapped to Forgejo; `.github/` paths kept; root `CODEOWNERS` symlink; `cargo audit` and `cargo outdated` in place of Renovate | Forgejo has the same concepts with different file locations and no enforced CODEOWNERS on the free tier | Accepted |
| ADR-005 | Three representations (Model IR, Kernel IR, Plan) and no other interface; kernels as Rust generators lowered through MLIR to ROCDL and SPIR-V and through an own lowering to RISC-V; a fixed catalog plus one fuser; no kernel library, vendor BLAS or Python | a vendor library ties the engine to one vendor's cadence and leaves RISC-V without a path; Python reintroduces the host overhead the incumbents removed; Apple's stack shows the shape that scales across heterogeneous hardware | Accepted |
| ADR-006 | The artifact is a cache: `build` writes it, `run` and `serve` build it on first load, `--require-prebuilt` forbids building; placement cached and pinnable the same way | TensorRT-LLM dropped its mandatory build in 1.2 and vLLM and SGLang compile on first load; keep the artifact's properties, not the obligation | Accepted |

## Decisions the owner made

Recorded in the SRS changelog, §1.2 and §2.5, and in the ADR contexts, from
the discussion that preceded the SRS.

| decision | where recorded | reason given |
|---|---|---|
| The mission is the industry-standard engine for AMD Instinct and RISC-V; NVIDIA is out of scope | SRS §1.2 | the goal is to own the whole path from model file to machine code on those two families |
| No kernel library, no vendor BLAS, no Python, anywhere | SRS §1.2, §2.5; ADR-005 | the vendor's engine is not an industry standard; Python costs host time |
| An own IR for RISC-V is acceptable | RI-KC-004 | no vendor kernel exists on RISC-V; the IR must be ours end to end |
| Follow Apple's three-level model: Model IR as the single contract, a fixed kernel catalog plus a small fuser, portable IR finalised on the device, a planner across units | SRS §2.1; ADR-005 | it is the shape that scales across heterogeneous hardware |
| MLIR is the route for the kernel compiler; MLIR and LLVM are linked, never shelled out to | ADR-005; RI-KC-008 | no toolchain dependency at build or load |
| Keep the ahead-of-time engine but make the artifact a cache with a strict mode | ADR-006 | the lesson of TensorRT-LLM 1.2 |
| Topology planner interfaces in Release 1, implementation in Release 2 | SRS changelog; RI-PLN | the R1 types must be shaped by the R2 job; the artifact format must not change for it |
| High-concurrency API serving is the first-class workload; prefix reuse on by default | SRS §2.5, RI-SCH-003, RI-KVC-005 | defaults and the first benchmark follow the workload operators run |
| The SRS is written with clean requirements before any component; SWG-001 applies in full | SRS §1.1, §2.5 | the standard's Step 0 |
| Targets by architecture string, never by product name | RI-TGT-001 | product names are many-to-one |
| Feature combinations not marked supported are refused, never attempted | RI-SEC-005, `docs/feature-matrix.md` | an untested pair is a wrong answer waiting |

## Reversals

None yet. The only revision is ADR-003's, on 2026-11-10, when ADR-005
removed the idea of pluggable kernel providers in favour of generators.

## Resolved since this site was first written

Discrepancies the first reading of 2026-11-10 found and the tree has since
closed; kept for one cycle so the next reader knows they were real.

| found | resolved |
|---|---|
| ADR-002 listed six sections (`plan`, `graph`, `profile`, `metadata`, `kernels`, `weights`) under older `RI-ENG` and `RI-CMP` ids while RI-ART-002 lists nine plus `lora_slots` | 2026-11-11: ADR-002 corrected on `docs/1-srs-rustinfer` to the nine R1 sections plus `lora_slots`, citing RI-ART, RI-GC and RI-PLN ids |
| No `LICENSE` file although the manifest and README said MIT | 2026-11-11: `LICENSE` (MIT) added at `082df51` |
| CI actions referenced by tag, no `timeout-minutes`, no `permissions` | 2026-11-11: full-SHA pins, `permissions: contents: read`, `timeout-minutes: 10`, Codeberg runner labels; recorded in ADR-004 |

## Retracted conclusions

Conclusions this site reached while reading and then disproved by reading
further. Kept so that the next reader does not reach them again.

| believed | disproved by |
|---|---|
| The scaffold branch is at `42e6c2d` | a post-coding refactor commit `e91e002` landed on the branch while this site was being written; the footer and the generators read the commit from git so this cannot recur |
| `--require-prebuilt` on a directory reports a dedicated error code | the CLI reports it under `invalid`; the `PrebuiltRequired` variant exists but maps to that code |
| The version manifest names the software `rustinfer` | it names the crate, `rustinfer-cli`, since the name comes from `CARGO_PKG_NAME` |
| The component diagram's edges are the Cargo dependencies today | every non-core crate depends only on `rustinfer-core` at `082df51`; the diagram's edges from the compilers, runtime and artifact to `mir`, `target` and `artifact` are added by the issues that need them |
