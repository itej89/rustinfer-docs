---
title: "LLVM 23.1 requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / LLVM 23.1"
order: 11
summary: What the LLVM 23.1 documentation requires of a client that links the AMDGPU back end and lld, and the R2 and R3 back ends that come later.
---

# LLVM 23.1 requirements

Source: `specs/compiler/` at tag `llvmorg-23.1.0`: *LLVM 23.1.0 Release
Notes* (`llvm-23.1.0-ReleaseNotes.md`), *LLVM Language Reference Manual*
(`llvm-23.1.0-LangRef.md`), *User Guide for AMDGPU Backend*
(`llvm-23.1.0-AMDGPUUsage.rst`). The documents are not numbered; each item
names its section and the line of that copy. Only items in the scope of the
SRS row LLVM are listed: the AMDGPU back end and `lld` (R1), the SPIR-V back
end (R2), the RISC-V back end (R3), and the IR features the lowering uses.
The code-object format itself is on the [AMDGPU-ABI](std-amdgpu-abi-requirements.html) page.

## Release line (R1)

| id | requirement | source |
|---|---|---|
| LL-R1 | Link one build of the 23.1 release line, and only that major. The release notes describe "LLVM 23.1.0"; the SRS pins 23.1.x and ADR-007 records the exact build in each artifact | Release Notes, *Introduction* (line 19); SRS §1.4 LLVM; ADR-007 point 1 |
| LL-R2 | The C API changed in 23: "Replaced opcode `LLVMBr` with `LLVMUncondBr` and `LLVMCondBr`", and "The operand order of `CondBr` instructions was adjusted to match the successor order". A client of the C API must not rely on the old forms | Release Notes, *Changes to the C API* (lines 420 to 426) |

## IR the lowering emits (R1)

| id | requirement | source |
|---|---|---|
| LL-R3 | A module "may specify a target triple string", with the canonical form `ARCHITECTURE-VENDOR-OPERATING_SYSTEM[-ENVIRONMENT]`. For AMD code objects the OS is `amdhsa`. LLVM 23 "Changed triple naming system from "amdgcn" to "amdgpu" plus a subarch suffix"; the note says the legacy spelling "is accepted" for compatibility | LangRef *Target Triple* (line 3674); Release Notes *Changes to the AMDGPU Backend* (line 225); AMDGPUUsage *Target Triples* (lines 49 to 60) |
| LL-R4 | A module "may specify a target-specific data layout string"; code generated for a target must use that target's layout | LangRef *Data Layout* (line 3447) |
| LL-R5 | `llvm.module.flags` holds behaviour, unique ID and value triplets; "Each module may only have one flag entry for each unique ID" | LangRef *Module Flags Metadata* (line 9132) |
| LL-R6 | `llvm.masked.load`: "masked-off lanes in the result vector are taken from the corresponding lanes of the `passthru` argument"; "Only the masked-on lanes of the vector need to be inbounds of an allocation". `llvm.masked.store`: "the masked-off lanes are not accessed" | LangRef *`llvm.masked.load.*` Intrinsics* (line 25922), *`llvm.masked.store.*` Intrinsics* (line 25964) |

## AMDGPU back end (R1)

| id | requirement | source |
|---|---|---|
| LL-R7 | AMDGPU address spaces: Global is LLVM IR address space 1, Local (LDS, the HSA `group` segment) is 3 | AMDGPUUsage *Address Spaces*, table *AMDGPU Address Spaces* (line 1086) |
| LL-R8 | "The AMDGPU backend generates a standard ELF relocatable code object", for one processor (`gfx942`, `gfx950`); `.text` is "Generated as position independent code" | AMDGPUUsage *ELF Code Object* (line 2920), *Sections* (line 3286) |
| LL-R9 | Buffer out-of-bounds semantics: LLVM 23 replaced the `relaxed-buffer-oob-mode` feature by the module flag `amdgpu.buffer.oob.mode`; "An absent flag is treated as strict by the backend". "0 (or absent): any ... Code generation is identical to strict"; "1: relaxed" may merge misaligned accesses "even if that changes OOB behaviour" | Release Notes (lines 218 to 223); AMDGPUUsage *Module Flags* (lines 973 to 1002), *Buffer Fat Pointer out of bounds (OOB) handling* (line 1485) |

## lld (R1)

| id | requirement | source |
|---|---|---|
| LL-R10 | The relocatable code object "can be linked by `lld` to produce a standard ELF shared code object which can be loaded and executed on an AMDGPU target" | AMDGPUUsage *ELF Code Object* (lines 2922 to 2925) |

## Later back ends

| id | requirement | source | release |
|---|---|---|---|
| LL-R11 | The SPIR-V back end of the pinned LLVM, if the SPIR-V path uses it (RI-KC-004 names MLIR's `spirv` dialect instead) | SRS §1.4 LLVM scope | R2 |
| LL-R12 | The RISC-V back end of the pinned LLVM with the V extension (see [RVV 1.0](std-rvv-1.0-requirements.html)); the 23.1 notes add `-mcpu=spacemit-x100` and `-mcpu=spacemit-a100` and assembler support for SpacemiT's `XSMTVDotII` matrix extension | Release Notes *Changes to the RISC-V Backend* (line 303) | R3 |
