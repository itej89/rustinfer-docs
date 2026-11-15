---
title: "HIP and ROCm environment variables 7.2.4"
navtitle: Overview
section: Standards
group: "Runtime / HIP and ROCm environment variables 7.2.4"
order: 18
summary: The HIP and ROCm 7.2.4 environment-variable references, for the 13 HIP and HSA settings RI-ROC-015 records in the version manifest; none is recorded on main yet (#95), and rustinfer sets none of them.
---

# HIP and ROCm environment variables 7.2.4

**Scope (SRS §1.4, HIP-ENV):** "the variables RI-ROC-015 records, their
meaning and defaults". Added by SRS v0.5 (PR #80). RI-ROC-015 (R1): "The
version manifest (RI-CLI-010) SHALL record the HIP and HSA environment
settings that change copy, queue, memory or launch behaviour, set or unset:
`HSA_ENABLE_SDMA`, `HSA_ENABLE_PEER_SDMA`, `HSA_FORCE_SDMA_SIZE`,
`HSA_XNACK`, `HSA_CU_MASK`, `ROC_GLOBAL_CU_MASK`, `GPU_MAX_HW_QUEUES`,
`HIP_FORCE_DEV_KERNARG`, `HIP_HOST_COHERENT`, `GPU_FORCE_BLIT_COPY_SIZE`,
`ROC_P2P_SDMA_SIZE`, `AMD_SERIALIZE_KERNEL`, `AMD_SERIALIZE_COPY`. A value
that differs from the runtime default SHALL be logged at `warn`. rustinfer
SHALL NOT set any of them itself." RI-OBS-005 copies the same environment into
every `tune` and GPU test record (see [AMD SMI](std-amd-smi.html)).

**Implementation on `main` (`5a6db49`):** none of the 13 is read, recorded or
logged; the version manifest holds the software, toolchain, host and
dependency lines, the HIP library path and, at device open, the HIP runtime
version (`crates/rustinfer-core/src/manifest.rs:36-136`;
`crates/rustinfer-target-rocm/src/lib.rs:150`). rustinfer sets none of them:
the only `std::env::set_var` calls in the tree are in a test of the HIP
library override (`crates/rustinfer-target-rocm/tests/hip_override.rs:94-125`).
Planned in issue [#95](https://github.com/itej89/rustinfer/issues/95) (open,
R1) for the ROCm target, and #14 for the print on every subcommand.

**Three of the 13 are not in the documents.** `HSA_FORCE_SDMA_SIZE`,
`GPU_FORCE_BLIT_COPY_SIZE` and `ROC_P2P_SDMA_SIZE` appear in neither the HIP
nor the ROCm reference of 7.2.4; their meaning and defaults are read from the
ROCm source at tag `rocm-7.2.4` (ROCM-SRC, informative), see the
[requirements](std-hip-env-requirements.html).

**Conformance:** mandatory from **R1** (RI-ROC-015).

**Source:** *HIP environment variables*,
<https://rocm.docs.amd.com/projects/HIP/en/docs-7.2.4/reference/env_variables.html>,
and *ROCm environment variables*,
<https://rocm.docs.amd.com/en/docs-7.2.4/reference/env-variables.html>, both
downloaded 2026-11-15 into `specs/runtime/` as
`hip-7.2.4-env_variables.html` and `rocm-7.2.4-env-variables.html` with text
copies (`.txt`, cited by section and line). For the three undocumented
variables and the runtime's own defaults: `projects/clr/rocclr/utils/flags.hpp`
and `projects/rocr-runtime/runtime/hsa-runtime/core/util/flag.h` of
`ROCm/rocm-systems` at tag `rocm-7.2.4`, as `specs/runtime/rocm-7.2.4-clr-flags.hpp`
and `rocm-7.2.4-rocr-flag.h`.

| | |
|---|---|
| Pages | [requirements](std-hip-env-requirements.html) · [audit](std-hip-env-audit.html) · [tracker](std-hip-env-tracker.html) |
| Conformance | mandatory R1 (RI-ROC-015; read by RI-OBS-005) |
| Audited | 2026-11-15, by reading `main` `5a6db49` and the documents; no test run |
| Result | missing: no variable is recorded or compared with its default; the "never set" rule already holds |
| Open gaps | 2 of 2 (HENV-1 record set or unset, HENV-2 warn on a non-default value), both planned in #95 |
