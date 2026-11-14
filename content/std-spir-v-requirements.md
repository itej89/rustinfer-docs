---
title: "SPIR-V 1.6 rev 8 requirements"
navtitle: Requirements
section: Standards
group: "Compiler and code generation / SPIR-V 1.6 rev 8"
order: 41
summary: What the SPIR-V specification requires of a module's binary form, logical layout and validity, for the compute modules spirv-vulkan will emit.
---

# SPIR-V 1.6 rev 8 requirements

Source: `specs/compiler/SPIRV-unified1.pdf` (*SPIR-V Specification*,
version 1.6, Revision 8, Unified). Sections are those of that document.
Only what a module emitter must produce is listed; what the consuming
environment adds comes from the client API (§1.2: "The full set of rules
needed to consume SPIR-V in a particular environment comes from the
combination of SPIR-V and that environment's client API specification"),
here Vulkan. In MLIR most of these are produced by the `spirv` dialect's
serializer; rustinfer's part is a valid `spirv.module` with the right
version, capabilities and entry points.

## Physical layout (§2.3, §3.1)

| id | requirement | section |
|---|---|---|
| SV-R1 | Word 0 is the magic number 0x07230203 | §2.3 Table 1; §3.1 |
| SV-R2 | Word 1 is the version, its bytes, high-order to low-order, are 0, Major, Minor, 0 ("version 1.3 is the value 0x00010300"); "Major and Minor (but not Revision) are declared within a SPIR-V module" | §2.3 Table 1; §1.3.1 |
| SV-R3 | Word 2 is the generator's magic number ("allowed to be 0"); word 3 the bound, "where all <id>s in this module are guaranteed to satisfy 0 < id < Bound"; word 4 is 0 (reserved for the instruction schema) | §2.3 Table 1 |
| SV-R4 | Each instruction: "The 16 high-order bits are the WordCount of the instruction. The 16 low-order bits are the opcode enumerant", then optional type and result `<id>`s and operands | §2.3 Table 2 |
| SV-R5 | "A module is defined as a stream of words, not a stream of bytes"; stored as bytes, the magic number tells the reader the byte order | §3.1 (Endianness) |

## Logical layout (§2.4)

| id | requirement | section |
|---|---|---|
| SV-R6 | Instructions "must be in the following order": `OpCapability`; `OpExtension`; `OpExtInstImport`; "The single required `OpMemoryModel` instruction"; `OpEntryPoint`; `OpExecutionMode` or `OpExecutionModeId`; debug instructions; annotations; types, constants and global variables; function declarations; function definitions | §2.4 items 1 to 11 |
| SV-R7 | Within a function, a block starts with `OpLabel` and ends with a termination instruction; every `OpVariable` has storage class Function and is in the first block; forward references only where §2.4 lists them | §2.4 |
| SV-R8 | A module "can contain multiple entry points, but only one set of capabilities"; "A single entry point is limited to a single execution model" | §2.2.4 |

## Validity (§2.16)

| id | requirement | section |
|---|---|---|
| SV-R9 | Every universal validation rule, among them the logical-pointer rules that apply when neither `VariablePointers` nor `VariablePointersStorageBuffer` is declared (pointers only as operands and results of the listed instructions) | §2.16.1 |
| SV-R10 | With the Shader capability (as Vulkan requires), "Loops must be structured" (`OpLoopMerge` on the back-edge target) and "Selections must be structured" (`OpSelectionMerge`); "Each entry point in a module, along with its corresponding static call tree within that module, forms a complete pipeline stage" | §2.16.2 |

## Version emitted

| id | requirement | section |
|---|---|---|
| SV-R11 | The module declares one version (SV-R2). Enumerated tokens marked "Missing before" or "Missing after" a version "are invalid SPIR-V for the missing versions"; tokens with no such mark "are valid in all versions of SPIR-V". Which version, 1.5 or 1.6, is the open decision OI-016 | §1.3.1; §2.22 *Unified Specification*; SRS OI-016 |
