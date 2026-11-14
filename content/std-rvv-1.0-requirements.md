---
title: "RISC-V V 1.0 requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / RISC-V V 1.0"
order: 51
summary: What the RISC-V V extension 1.0 requires of code that must run unchanged on any VLEN: implementation parameters, vtype and vl, stripmining, masking and the instruction set V guarantees.
---

# RISC-V V 1.0 requirements

Source: `specs/compiler/riscv-v-spec-1.0.pdf` (*RISC-V "V" Vector
Extension, Version 1.0*). Sections are those of that document. The
specification constrains hardware; the items below are the ones that
constrain code which must run on every V implementation, which is what a
vector-length-agnostic lowering needs.

## What every V core guarantees (§2, §18.3)

| id | requirement | section |
|---|---|---|
| RV-R1 | ELEN and VLEN are per-hart parameters: "ELEN ≥ 8", "VLEN ≥ ELEN", both powers of 2, VLEN "no greater than 2^16"; code "will execute portably on harts with different values for the VLEN parameter, provided the harts support the required element types and instructions" | §2 |
| RV-R2 | "The V vector extension requires Zvl128b" (VLEN ≥ 128); it "supports EEW of 8, 16, and 32, and 64", all configuration instructions, all loads and stores, all integer, fixed-point, mask and permutation instructions, and floating point "for floating-point operands with EEW=32 or EEW=64"; the scalar core implements F and D | §18.3, §18.1 |

## Configuration (§3.4, §3.5, §6)

| id | requirement | section |
|---|---|---|
| RV-R3 | `vtype` holds `vsew` (selected element width), `vlmul` (register grouping), `vta`, `vma` and `vill`; an unsupported setting sets `vill` | §3.4, §3.4.1 to §3.4.4 |
| RV-R4 | `vset{i}vl{i}` take the application vector length (AVL) and "write the new value of vl into rd"; the hardware answers with "the (frequently smaller) number of elements that the hardware will handle per iteration" | §6 |
| RV-R5 | `vl` obeys: "vl = AVL if AVL ≤ VLMAX", "ceil(AVL / 2) ≤ vl ≤ VLMAX if AVL < (2 * VLMAX)", "vl = VLMAX if AVL ≥ (2 * VLMAX)", deterministic for the same AVL and VLMAX. So code must use the returned `vl`, not compute it | §6.3 |
| RV-R6 | Stripmining: loop on the returned `vl` until the remaining count is zero | §6, §6.4 |

## Element policies and masking (§3.4.3, §5.3, §5.4)

| id | requirement | section |
|---|---|---|
| RV-R7 | With an agnostic policy, tail or inactive destination elements "can either retain the value they previously held, or are overwritten with 1s", not necessarily deterministically. Code must not read them | §3.4.3 |
| RV-R8 | "The mask value used to control execution of a masked vector instruction is always supplied by vector register v0"; masked-off elements "never generate exceptions"; the destination of a masked instruction cannot overlap `v0` except where §5.3 allows | §5.3 |

## Memory and arithmetic

| id | requirement | section |
|---|---|---|
| RV-R9 | A misaligned element is either transferred "or an address misaligned exception is raised on that element"; support is "independent of an implementation's support for misaligned scalar memory accesses". Code must keep elements naturally aligned | §8 |
| RV-R10 | `vfredosum` "must sum the floating-point values in element order"; `vfredusum` may use any "reduction tree", so its result can differ between implementations and VLENs | §14.3.1, §14.3.2 |
