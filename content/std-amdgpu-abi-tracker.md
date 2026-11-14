---
title: "AMDGPU code object V5 tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / AMDGPU code object V5"
order: 33
summary: Gaps between rustinfer's AMD code objects and code object V5: emission in PR #44, untested metadata and descriptor, no hardware load yet, and no metadata reader.
---

# AMDGPU code object V5 tracker

Gaps found by the [audit](std-amdgpu-abi-audit.html). Issues from
`gh issue list -R itej89/rustinfer --state all`, 2026-11-13.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| ABI-1 | No code object on `main`: no ELF header, `e_flags`, `ET_DYN` link or V5 version (AB-R1, AB-R3 to AB-R8, AB-R15) | *Header*, *AMDGPU ELF Header `e_flags` for Code Object V4 and V5*, *Sections*, *Module Flags* | **In PR #44** | Issue [#8](https://github.com/itej89/rustinfer/issues/8). CI passes on `10b8b1b`; the PR stays unmerged until #45 reports |
| ABI-2 | No test checks `EI_OSABI`, `e_entry`, the `NT_AMDGPU_METADATA` note, the V5 metadata map (`amdhsa.version` `[1, 2]`, `amdhsa.target`, the required kernel keys), the `.kd` and entry symbols, or the kernel descriptor (AB-R2, AB-R5, AB-R8 to AB-R14) | *Header*; *Code Object V3 and Above Note Records*; *Symbols*; *Code Object V5 Metadata*; *Code Object V3 Kernel Descriptor* | **Open** | No issue covers it. These are written by LLVM and `lld`, so they are likely right, but a back-end default change would pass unnoticed. A host test could read the note through LLVM's object reader and decode the MessagePack map, and check `<name>.kd` is a 64-byte, 64-byte-aligned `STT_OBJECT` in `.rodata` |
| ABI-3 | No code object has been loaded by the HIP module loader (AB-R4, AB-R10) | *Header* ("The AMD HSA runtime loader requires a `ET_DYN` code object"); *Symbols* | **Open** | GPU test request [#45](https://github.com/itej89/rustinfer/issues/45) on MI300X (gfx942) and MI355X (gfx950), not run. `hipModuleLoadData` and `hipModuleGetFunction` in `crates/rustinfer-target-rocm/src/ffi/hip.rs` (PR #44) would prove the loader accepts the header, note and symbols |
| ABI-4 | No metadata reader: the LDS and register needs of each kernel are not read, so RI-ROC-004's check before the first launch cannot be made (AB-R13) | *Code Object V3 Metadata*, kernel table (`.group_segment_fixed_size`, `.sgpr_count`, `.vgpr_count`, `.agpr_count`) | **Open** | Issue [#12](https://github.com/itej89/rustinfer/issues/12) (ROCm target; acceptance: "A kernel requesting more LDS than the device has is refused before launch"). RI-KC-012's resource report could come from the same reader |
