---
title: Open issues and risks
navtitle: Open issues (OI)
section: Trackers
order: 2
summary: The open issues of SRS §4 with their status, impact and recorded resolution; what is undecided, what waits for hardware, and which requirements each one holds up.
---

# Open issues and risks

Read from SRS §4 at commit `082df51`; OI-013 updated from SRS v0.3 at commit `04a2a26`; OI-014 to OI-016 read from SRS v0.4.8 at commit `8c7d47e`. An open issue is a decision the SRS
could not make when it was written; each names the requirements it affects
and the resolution it expects. **Open** means a decision is due before the
release its requirements name; **Deferred** means it waits on hardware. The
table is a tracker the [progress](progress.html) page counts; a row closes
when the ADR or decision it asks for lands.

| id | issue | status | impact | resolution recorded |
|---|---|---|---|---|
| OI-001 | Generated kernels against hand-tuned ones. Triton and FlyDSL show a tile-level IR with explicit layouts reaches a large fraction of hand-written GEMM and attention performance on gfx950; the remainder is what AITER's assembly holds. | Open | RI-NFR-003, RI-NFR-006, RI-KC-009 | measure after the R1 generator set; decide on the assembly generator path |
| OI-002 | Shape buckets and cost interpolation | Open | RI-GC-005, RI-KC-006 | start with padded-M buckets as AITER's tables use; revisit with data |
| OI-003 | RISC-V bench hardware. No RISC-V accelerator is on the bench; the lowering paths are chosen from documentation. | Deferred | RI-RV-001 to -004, RI-KC-004 | acquire a Tenstorrent p150 and a SpacemiT K3 board before R3 |
| OI-004 | Safetensors parsing: crate or in-tree | Open in the SRS; in-tree in the code | RI-FE-002, RI-SEC-003 | an ADR through the new-dep process; the frontend (PR #24) and Sluice (PR #23) parsed the headers in Rust, in-tree; since PR #30 (2026-11-13) one shared reader, `rustinfer_artifact::safetensors`, serves both |
| OI-005 | Multi-rank artifact layout | Open | RI-ART-007, RI-DIST-001 | an ADR before R2; one file per rank provisionally |
| OI-006 | Grammar backend for guided decoding | Open | RI-SMP-006 | an ADR before R3; a Rust-native backend preferred over an FFI |
| OI-007 | Tokenizer | Open | RI-SRV-003, RI-CLI-006 | new-dep evaluation of the `tokenizers` crate before R2 |
| OI-008 | Reference hardware. Autotuning and the baselines need a gfx950 host with vLLM and AITER. | Open; only the owner can rent the node | RI-KC-006, RI-NFR-003, RI-NFR-004, RI-NFR-006 | rent an MI355X node for R1 autotuning and the R2 acceptance run |
| OI-009 | MLIR and LLVM build and link. `melior` needs a pinned MLIR and LLVM; building in CI is slow. | Decided 2026-11-12 by ADR-007 | RI-KC-003, RI-NFR-012, RI-NFR-016 | LLVM 23.1 packages from `apt.llvm.org`, `melior` 0.29.1, static link, installed in CI by `scripts/ci/install_llvm.sh` ([kernel compiler](kernel-compiler.html)) |
| OI-010 | DPU agent ISA and deployment | Deferred | RI-PLN-006 | after a DPU is on the bench |
| OI-011 | Tensix mesh lowering: whether the mesh path targets TT-MLIR's dialects or emits its own kernels for the Tensix cores | Deferred | RI-KC-004, RI-RV-001 | decide with a Blackhole card in hand |
| OI-013 | Implicit launch operands: the paged KV operators take the KV cache pools as operands that are not in the Model IR node; the CPU launcher appended them at launch | Done 2026-11-12 (resolved in the SRS by PR #30, merged 2026-11-13) | RI-MIR-004, RI-TGT-002, RI-TGT-003, RI-GC-006, RI-KVC-001 | `OperatorSpec::implicit_operands` (`ImplicitOperands`, `ImplicitOperand::{KeyCache, ValueCache}`) is a column of the operator registry; the CPU launcher's operand counts are the node arity plus that column, with no operator-specific override left (PR #30, #27). The requirement is deferred to the SRS version that adds a second target launcher |
| OI-014 | Quark MXFP4 nibble order: the low-nibble-first packing of RI-MIR-003 was confirmed for gpt-oss, vLLM and compressed-tensors but only inferred for AMD Quark's `pack_method: "reorder"` export | Done 2026-11-14 (resolved in SRS v0.4.8 by GitHub PR #49, 8c7d47e, #35) | RI-FE-006, RI-MIR-003 | low nibble first: Quark's `Pack_fp4.pack` and `Pack_fp4.unpack` (`quark/torch/utils/pack.py` at 313cb0b) fix the order and `reorder` is ignored for fp4; the frontend's Quark fixtures are decoded through a port of the unpacker and the CPU reference. Quark was not run and no real Quark checkpoint decoded |
| OI-015 | gfx950 MXFP4 activation operand: the scaled MFMA takes only 8-, 6- and 4-bit float operands, so native MXFP4 GEMMs need in-kernel activation quantization | Decided 2026-11-13 by the owner, following vLLM (SRS v0.4, GitHub PR #41) | RI-KC-003, RI-KC-005, RI-KC-007, RI-GC-004, RI-CLI-002, RI-CLI-003, RI-MIR-011, RI-FE-006 | bf16 activations by default on every target; `build --activations mxfp8\|mxfp4` opts in on gfx950; precision never changes with batch size (ADR-010) |
| OI-016 | Minimum Vulkan and SPIR-V version for spirv-vulkan (R2): the BXM-4-64 of the SpacemiT K3 is Vulkan 1.2 in Mesa, which accepts SPIR-V up to 1.5 | Open; the owner has not decided (SRS v0.4.3, GitHub PR #50) | RI-KC-004, RI-RV-001; the VULKAN and SPIR-V rows of §1.4 | (a) Vulkan 1.2 with SPIR-V 1.5, (b) Vulkan 1.3 with SPIR-V 1.6; until decided the rows record no minimum |

## Which ones gate Release 1

OI-009 gated issue #7 and everything on the kernel-compiler path until
ADR-007 resolved it on 2026-11-12. OI-008 gates #9's autotuning and #12's hardware
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
