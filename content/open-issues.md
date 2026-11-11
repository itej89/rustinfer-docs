---
title: Open issues and risks
navtitle: Open issues (OI)
section: Trackers
order: 2
summary: The eleven open issues of SRS §4 with their status, impact and recorded resolution; what is undecided, what waits for hardware, and which requirements each one holds up.
---

# Open issues and risks

Read from SRS §4 at commit `082df51`. An open issue is a decision the SRS
could not make when it was written; each names the requirements it affects
and the resolution it expects. **Open** means a decision is due before the
release its requirements name; **Deferred** means it waits on hardware.

| id | issue | status | impact | resolution recorded |
|---|---|---|---|---|
| OI-001 | Generated kernels against hand-tuned ones. Triton and FlyDSL show a tile-level IR with explicit layouts reaches a large fraction of hand-written GEMM and attention performance on gfx950; the remainder is what AITER's assembly holds. | Open | RI-NFR-003, RI-NFR-006, RI-KC-009 | measure after the R1 generator set; decide on the assembly generator path |
| OI-002 | Shape buckets and cost interpolation | Open | RI-GC-005, RI-KC-006 | start with padded-M buckets as AITER's tables use; revisit with data |
| OI-003 | RISC-V bench hardware. No RISC-V accelerator is on the bench; the lowering paths are chosen from documentation. | Deferred | RI-RV-001 to -004, RI-KC-004 | acquire a Tenstorrent p150 and a SpacemiT K3 board before R3 |
| OI-004 | Safetensors parsing: crate or in-tree | Open | RI-FE-002, RI-SEC-003 | an ADR through the new-dep process |
| OI-005 | Multi-rank artifact layout | Open | RI-ART-007, RI-DIST-001 | an ADR before R2; one file per rank provisionally |
| OI-006 | Grammar backend for guided decoding | Open | RI-SMP-006 | an ADR before R3; a Rust-native backend preferred over an FFI |
| OI-007 | Tokenizer | Open | RI-SRV-003, RI-CLI-006 | new-dep evaluation of the `tokenizers` crate before R2 |
| OI-008 | Reference hardware. Autotuning and the baselines need a gfx950 host with vLLM and AITER. | Open | RI-KC-006, RI-NFR-003, RI-NFR-004, RI-NFR-006 | rent an MI355X node for R1 autotuning and the R2 acceptance run |
| OI-009 | MLIR and LLVM build and link. `melior` needs a pinned MLIR and LLVM; building in CI is slow. | Open | RI-KC-003, RI-NFR-012, RI-NFR-016 | ADR-005 names the version; a vendored prebuilt with a recorded hash. The draft of issue #7 assigns this to an ADR-007 |
| OI-010 | DPU agent ISA and deployment | Deferred | RI-PLN-006 | after a DPU is on the bench |
| OI-011 | Tensix mesh lowering: whether the mesh path targets TT-MLIR's dialects or emits its own kernels for the Tensix cores | Deferred | RI-KC-004, RI-RV-001 | decide with a Blackhole card in hand |

## Which ones gate Release 1

OI-009 gates issue #7 and everything on the kernel-compiler path (#8, #9,
#10, #11, #13, #14). OI-008 gates #9's autotuning and #12's hardware
validation, and with them the Epic's acceptance criteria. OI-002 is decided
provisionally and does not block. The rest are R2 or later, or deferred.

## Assumptions the SRS makes

§2.6 lists five assumptions and what happens if each is false. They are
risks in the same sense as the open issues and are kept here with them.

| assumption | if false |
|---|---|
| A tile-level Kernel IR lowered through MLIR to ROCDL reaches a large fraction of hand-written GEMM and attention performance on gfx942 and gfx950 | an assembly generator path closes the rest (RI-KC-009) |
| RCCL is usable from Rust over its C API | own collectives arrive in R2 instead of R3 |
| HF `config.json` plus safetensors is enough to lower the supported families | per-family adapters in the frontend |
| A RISC-V accelerator with a public driver exists when its backend is scheduled | the RISC-V backends stay compile-tested until one does |
| A pinned MLIR and LLVM can be built or fetched reproducibly in CI | ADR-005 names a vendored prebuilt with a recorded hash |
