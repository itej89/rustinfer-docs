---
title: "AMDGPU DMA Operations (LLVM 23.1) requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / AMDGPU DMA Operations (LLVM 23.1)"
order: 39
summary: What LLVM 23.1's AMDGPU DMA Operations defines for the per-lane global-to-LDS loads of gfx942 and gfx950 and the gfx1250 tensor load and store, the part in rustinfer's scope.
---

# AMDGPU DMA Operations requirements

Source: `specs/compiler/llvm-23.1.0-AMDGPUDMAOperations.md` (the Markdown
source of the LLVM 23.1.0 page), cited as **[DMA]** with its lines; and
`specs/compiler/llvm-23.1.0-AMDGPUAsyncOperations.rst`, cited as
**[ASYNC]**. The document describes LLVM intrinsics; rustinfer reaches them
through the pinned MLIR's ROCDL and AMDGPU dialects
(`rocdl.load.to.lds`, `rocdl.load.async.to.lds`, `rocdl.global.load.lds`,
`amdgpu.gather_to_lds`, `rocdl.tensor.load.to.lds`,
`rocdl.tensor.store.from.lds`), cited as **[MLIR]**. The requirement on
rustinfer is RI-KC-015's: the description reports these movers with these
widths, and the lowering maps the Kernel IR's asynchronous tile copy onto
one of them, or onto loads and stores when none fits.

## GFX9 DMA: gfx942 and gfx950 (*GFX9 DMA*, [DMA] lines 20 to 89)

| id | requirement | source |
|---|---|---|
| DMA-R1 | The per-lane data size of a global-to-LDS load is an immediate of 1, 2 or 4 bytes; gfx950 also allows 12 or 16: "The data size can be 1, 2, or 4 bytes (gfx950 also allows 12 or 16 bytes)". The gfx942 description reports {1, 2, 4}, the gfx950 description {1, 2, 4, 12, 16} | [DMA] lines 36, 41 to 42, 58, 72 |
| DMA-R2 | The LDS address "is implicitly offset by `4 * lane_id` bytes for sizes up to 4 bytes, and by `16 * lane_id` bytes for larger sizes"; "The `%lds_base` pointer must be wave-uniform"; the size, the offset (applied to both addresses) and the cache policy are immediates. A tile copy lowered to it must have that shared layout, one slot per lane | [DMA] lines 33 to 46, 54 to 63, 82 |
| DMA-R3 | The source is flat (0), global (1) or a buffer fat pointer (7); the buffer forms take a resource descriptor whose `%voffset` and `%offset` are "included in bounds checking" | [DMA] lines 48 to 52, 65 to 89 |
| DMA-R4 | Completion: DMA operations "are usually asynchronous, and require the user to explicitly track completion using asyncmarks"; each has a synchronous counterpart for which "the compiler automatically ensures completion before their side-effects are used". An asyncmark is produced by `@llvm.amdgcn.asyncmark()` and waited on by `@llvm.amdgcn.wait.asyncmark(i16 %N)`, which leaves at most N outstanding | [DMA] lines 11 to 15, 22 to 25; [ASYNC] lines 13 to 15, 29 to 38 |
| DMA-R5 | "All DMA operations support the same cache modifiers as ordinary load/store operations from registers. They cannot be performed atomically." On GFX9, volatile is `aux/cpol` bit 31 and nontemporal is metadata, "as if they were loads from the global address space" | [DMA] lines 17 to 18, 27 to 28 |

## GFX1250 tensor load and store (*GFX1250*, [DMA] lines 91 to 146)

| id | requirement | source |
|---|---|---|
| DMA-R6 | `@llvm.amdgcn.tensor.load.to.lds` and `@llvm.amdgcn.tensor.store.from.lds` take a tensor descriptor (D#) in five groups, `%desc0` to `%desc4`, and a cache policy: "GFX1250 supports up to 4 descriptor groups; `%desc4` is reserved for future targets and must be zero-initialized"; groups 2 and 3 are "zero-init for D# up to 2D". The operations are asynchronous "despite the absence of `.async` in their names", and "All arguments must be wave-uniform". "Tensor DMA instructions do not support volatile or nontemporal" | [DMA] lines 93 to 95, 126 to 146 |
| DMA-R7 | For R1, what RI-KC-015 (i) needs of DMA-R6: a description can report a descriptor-based tensor mover with its maximum tile rank, and generators emit the same Kernel IR under capability sets that differ only in the mover (none, per-lane loads, a tensor mover of rank 5). The gfx1250 values and lowering are due with the gfx1250 target | SRS RI-KC-015 (i), Acceptance and Release; [MLIR] `AMDGPUOps.td:1967` ("tensors of up to five dimensions") |

## Related, outside the Scope phrase

- GFX1250 also has per-lane asynchronous loads and stores,
  `@llvm.amdgcn.{global|cluster}.load.async.to.lds.b<N>` and
  `global.store.async.from.lds.b<N>`, whose LDS pointer is per lane and whose
  "bit-size encoded in the name can be 8, 32, 64 or 128" ([DMA] lines 97 to
  124). They would be gfx1250's per-lane mover; the scope names only its
  tensor mover.
- The CDNA4 ISA guide names the gfx950 instructions behind the 12- and
  16-byte sizes, `GLOBAL_LOAD_LDS_DWORDX3` and `_DWORDX4`; see
  [AMD CDNA4 ISA](std-amd-cdna4-isa-requirements.html), C4-R5.
