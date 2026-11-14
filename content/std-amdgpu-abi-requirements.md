---
title: "AMDGPU code object V5 requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / AMDGPU code object V5"
order: 31
summary: What AMDGPUUsage at LLVM 23.1 requires of an AMDHSA code object V5: ELF header and e_flags, sections, note records, metadata, symbols and the kernel descriptor.
---

# AMDGPU code object V5 requirements

Source: `specs/compiler/llvm-23.1.0-AMDGPUUsage.rst` (*User Guide for AMDGPU
Backend* at `llvmorg-23.1.0`). Each item names its section or table and the
line of that copy. Only code object V5 for the `amdhsa` OS on gfx942 and
gfx950 is in scope. Most of these fields are written by the LLVM back end
and `lld`; rustinfer's part is to configure them (triple, processor,
code-object version, features, link mode) and to read what the loader
check of RI-ROC-004 needs.

## ELF header (*Header*, line 2929; table *AMDGPU ELF Header*)

| id | requirement | source |
|---|---|---|
| AB-R1 | `e_ident[EI_CLASS]` is `ELFCLASS64` ("for `amdgcn` architecture which only supports 64-bit process address space applications"); `e_ident[EI_DATA]` is `ELFDATA2LSB` | lines 2940 to 2941, 2985 to 2994 |
| AB-R2 | `e_ident[EI_OSABI]` is `ELFOSABI_AMDGPU_HSA` (64) "for `amdhsa` OS" | lines 2942 to 2943, 2973, 2996 to 3002 |
| AB-R3 | `e_ident[EI_ABIVERSION]` is `ELFABIVERSION_AMDGPU_HSA_V5` (3), "the version of AMD HSA runtime ABI for code object V5 ... This is the default code object version if not specified" | lines 2946 to 2949, 2979, 3008 to 3025 |
| AB-R4 | `e_type` is `ET_DYN`: "`ET_REL` The type produced by the AMDGPU backend compiler as it is relocatable code object. `ET_DYN` The type produced by the linker as it is a shared code object. The AMD HSA runtime loader requires a `ET_DYN` code object" | lines 2953 to 2954, 3037 to 3048 |
| AB-R5 | `e_machine` is `EM_AMDGPU` (224); `e_entry` is 0, "as the entry points for individual kernels must be selected in order to invoke them through AQL packets" | lines 2955 to 2956, 2971, 3050 to 3064 |

## `e_flags` (table *AMDGPU ELF Header `e_flags` for Code Object V4 and V5*, line 3130)

| id | requirement | source |
|---|---|---|
| AB-R6 | `EF_AMDGPU_MACH` (mask 0x0ff) names the processor: `EF_AMDGPU_MACH_AMDGCN_GFX942` 0x04c, `EF_AMDGPU_MACH_AMDGCN_GFX950` 0x04f | lines 3136 to 3140; table *AMDGPU `EF_AMDGPU_MACH` Values*, lines 3259 and 3262 |
| AB-R7 | `EF_AMDGPU_FEATURE_XNACK_V4` (mask 0x300) and `EF_AMDGPU_FEATURE_SRAMECC_V4` (mask 0xc00) hold one of unsupported, any, off, on (`ANY` is 0x100 and 0x400: the feature "can have any value") | lines 3141 to 3155; *Target ID* (line 1025) |

## Sections, notes and symbols

| id | requirement | source |
|---|---|---|
| AB-R8 | Standard ELF sections with their standard meanings; `.text` holds "The executable machine code for the kernels ... Generated as position independent code"; `.note` is `SHT_NOTE`; `.rodata` is `SHT_PROGBITS` + `SHF_ALLOC`; the dynamic sections (`.dynamic`, `.dynstr`, `.dynsym`, `.hash`) are "used by a dynamic loader" | *Sections* (line 3286), table *AMDGPU ELF Sections* |
| AB-R9 | For code object V3 and above the `.note` section holds an `NT_AMDGPU_METADATA` (32) record with vendor "AMDGPU", "Metadata in Message Pack binary format" | *Code Object V3 and Above Note Records* (line 3599) |
| AB-R10 | Each kernel has a `<link-name>.kd` `STT_OBJECT` symbol in `.rodata` (the kernel descriptor; "It is the address of the kernel descriptor that is used in the AQL dispatch packet") and a `<link-name>` `STT_FUNC` symbol in `.text` (the entry point) | *Symbols* (line 3646), table *AMDGPU ELF Symbols* |

## Metadata (*Code Object Metadata*, line 4718)

| id | requirement | source |
|---|---|---|
| AB-R11 | Metadata "is required when the target triple OS is `amdhsa`" and "must contain the minimum information necessary to support the HSA compatible runtime kernel queries. For example, the segment sizes needed in a dispatch packet" | lines 4729 to 4734 |
| AB-R12 | V5 map: `amdhsa.version` is `[1, 2]`; `amdhsa.target` is `<target-triple> [ "-" <target-id> ]` with "A canonical target ID"; `amdhsa.kernels` is required | *Code Object V5 Metadata* (line 5655), *V4 Metadata* (line 5621), *V3 Metadata* table (line 5190) |
| AB-R13 | Each kernel map carries the required keys `.name`, `.symbol`, `.kernarg_segment_size`, `.group_segment_fixed_size`, `.private_segment_fixed_size`, `.kernarg_segment_align`, `.wavefront_size`, `.sgpr_count`, `.vgpr_count`, `.agpr_count`, `.max_flat_workgroup_size`; each argument map `.size`, `.offset`, `.value_kind`, with the V5 hidden argument kinds (`hidden_block_count_x` to `hidden_grid_dims` and others) | V3 kernel table (line 5235), argument table (line 5419), V5 argument additions (line 5712) |

## Kernel descriptor (*Code Object V3 Kernel Descriptor*, line 6019)

| id | requirement | source |
|---|---|---|
| AB-R14 | "CP microcode requires the Kernel descriptor to be allocated on 64-byte alignment"; it is 64 bytes ("Total size 64 bytes"); `GROUP_SEGMENT_FIXED_SIZE`, `PRIVATE_SEGMENT_FIXED_SIZE`, `KERNARG_SIZE`, then `KERNEL_CODE_ENTRY_BYTE_OFFSET` to the entry point, "which must be 256 byte aligned"; reserved fields "must be 0"; `COMPUTE_PGM_RSRC1` to `RSRC3` per processor | lines 6022 to 6023, 6028 to 6110, 6194 |

## Back-end behaviour the code objects rely on

| id | requirement | source |
|---|---|---|
| AB-R15 | Untyped buffer accesses keep per-element out-of-bounds guarantees unless `amdgpu.buffer.oob.mode` is 1 (relaxed); absent means "any", whose "Code generation is identical to strict" | *Module Flags* (line 973), lines 990 to 1002 |
