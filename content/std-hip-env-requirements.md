---
title: "HIP and ROCm environment variables 7.2.4 requirements"
navtitle: Requirements
section: Standards
group: "Runtime / HIP and ROCm environment variables 7.2.4"
order: 19
summary: The meaning and default of each of the 13 HIP and HSA variables RI-ROC-015 records, from the HIP and ROCm 7.2.4 references and, for the three they omit, the rocm-7.2.4 source; and what recording them set or unset requires.
---

# HIP and ROCm environment variables requirements

Sources: the HIP reference, `specs/runtime/hip-7.2.4-env_variables.txt`, cited
as **[HIPENV]** with its section and line; the ROCm reference,
`specs/runtime/rocm-7.2.4-env-variables.txt`, as **[ROCMENV]**; the HIP
runtime's flag table, `projects/clr/rocclr/utils/flags.hpp` at `rocm-7.2.4`
(`specs/runtime/rocm-7.2.4-clr-flags.hpp`), as **[CLR]**; ROCr's flag reader,
`projects/rocr-runtime/runtime/hsa-runtime/core/util/flag.h`
(`specs/runtime/rocm-7.2.4-rocr-flag.h`), as **[ROCR]**, and its blit choice
in `core/runtime/amd_gpu_agent.cpp` (`rocm-7.2.4-rocr-amd_gpu_agent.cpp`). The
source files are ROCM-SRC, an informative reference of SRS §1.4; they are
cited where the documents are silent or say less.

## The 13 variables

| id | variable | meaning | default | source |
|---|---|---|---|---|
| HENV-R1 | `HSA_ENABLE_SDMA` | "Enables the use of direct memory access (DMA) engines in all copy directions (Host-to-Device, Device-to-Host, Device-to-Device)" for `hsa_memory_copy`, `hsa_amd_memory_fill`, `hsa_amd_memory_async_copy` and `..._on_engine`; `0` disable, `1` enable | documented `1`; in ROCr, `0` and `1` are read and anything else, unset included, is `SDMA_DEFAULT` | [ROCMENV] *ROCR-Runtime environment variables*, line 914; [ROCR] lines 90 to 91 |
| HENV-R2 | `HSA_ENABLE_PEER_SDMA` | DMA engines for device-to-device copies; "ignored if `HSA_ENABLE_SDMA` is set to 0" | documented `1`; tri-state as HENV-R1 | [ROCMENV] line 937; [ROCR] lines 93 to 94 |
| HENV-R3 | `HSA_FORCE_SDMA_SIZE` | Not documented. A copy inside one device's memory smaller than this many bytes goes to the (potentially SDMA) device-to-host blit, "If the copy is very small then cache flush overheads can dominate"; a larger one to the device-to-device blit kernel | 1048576 (`1024 * 1024`) when unset | [ROCR] lines 206 to 207; `amd_gpu_agent.cpp` lines 2427 to 2436 |
| HENV-R4 | `HSA_XNACK` | "Enables XNACK"; ROCr reads `0` and `1`, "Any other value will be interpreted as not defining the env variable" | documented "None"; unset is `XNACK_UNCHANGED` | [ROCMENV] line 888; [ROCR] lines 210 to 215 |
| HENV-R5 | `HSA_CU_MASK` | "Sets the mask on a lower level of queue creation in the driver, this mask will also be set for queues being profiled" (example `1:0-8`) | documented "None" | [HIPENV] *Profiling variables*, line 208; [ROCMENV] line 900; [ROCR] line 312 |
| HENV-R6 | `ROC_GLOBAL_CU_MASK` | "Sets the mask on queues created by the HIP or the OpenCL runtimes, this mask will also be set for queues being profiled" (example `0xf`, "enables only 4 CUs") | no default in the document; `""` in the flag table | [HIPENV] *Profiling variables*, line 217; [CLR] line 211 |
| HENV-R7 | `GPU_MAX_HW_QUEUES` | "The maximum number of hardware queues allocated per device"; streams past it reuse the queues "in a round-robin manner"; CU-masked and cooperative queues are not counted | `4` | [HIPENV] *Debug variables*, line 439; [CLR] line 150 |
| HENV-R8 | `HIP_FORCE_DEV_KERNARG` | "Forces kernel arguments to be stored in device memory to reduce latency. Can improve performance by 2-3 µs for some kernels." | `1` | [HIPENV] *Debug variables*, line 342; [CLR] line 238 (`true`) |
| HENV-R9 | `HIP_HOST_COHERENT` | "Specifies if the memory is coherent between the host and GPU in `hipHostMalloc`"; `0` not coherent; overridden per allocation by `hipHostMallocCoherent` and `hipHostMallocNonCoherent` (see [HIP memory management](std-hip-mem-requirements.html), HMEM-R3) | `0` | [HIPENV] *Memory management related variables*, line 491; [CLR] line 176 |
| HENV-R10 | `GPU_FORCE_BLIT_COPY_SIZE` | Not documented. "Use Blit until this size(in KB) for copies" | `16` (KiB) | [CLR] line 187 |
| HENV-R11 | `ROC_P2P_SDMA_SIZE` | Not documented. "The minimum size in KB for P2P transfer with SDMA" | `1024` (KiB) | [CLR] line 220 |
| HENV-R12 | `AMD_SERIALIZE_KERNEL` | "Serialize kernel enqueue": `1` wait for completion before enqueue, `2` after, `3` both | `0` | [HIPENV] *Debug variables*, line 401; [CLR] line 165 |
| HENV-R13 | `AMD_SERIALIZE_COPY` | "Serialize copies", the same values | `0` | [HIPENV] *Debug variables*, line 420; [CLR] line 168 |

## What recording them requires (RI-ROC-015)

| id | requirement | source |
|---|---|---|
| HENV-R14 | Each of HENV-R1 to HENV-R13 is a manifest line, its value as set or the word that it is unset; "the default environment records every variable as unset" | SRS RI-ROC-015 and its Acceptance |
| HENV-R15 | A set value that differs from the runtime's default is logged at `warn`. The default is the runtime's, which for the tri-state ROCr flags (HENV-R1, HENV-R2, HENV-R4) is "unset", not the documented `1`: `HSA_ENABLE_SDMA=1` selects `SDMA_ENABLE`, which ROCr keeps apart from `SDMA_DEFAULT` | SRS RI-ROC-015 ("running with `GPU_MAX_HW_QUEUES=2` logs it at `warn`"); [ROCR] lines 90 to 94, 210 to 215 |
| HENV-R16 | rustinfer sets none of them, in any process it starts | SRS RI-ROC-015 ("rustinfer SHALL NOT set any of them itself") |

## Related, outside the list

- `HIP_LAUNCH_BLOCKING` serialises kernel enqueue, "behaves the same as
  `AMD_SERIALIZE_KERNEL`" ([HIPENV] *Debug variables*, line 370; [CLR]: "same
  as `AMD_SERIALIZE_KERNEL=2`"), so a run with it set serialises launches
  without any of the 13 being set.
- AMD's acceptance guide lists `HSA_OVERRIDE_CPU_AFFINITY_DEBUG=0` with
  `HIP_FORCE_DEV_KERNARG=1` as "Critical ROCm/HIP Environment Variables"
  (`specs/observability/amd-acc-os-tuning.txt`, *Environment Variables*); see
  [AMD Instinct system acceptance](std-amd-acc.html).
- `HSA_ENABLE_SDMA_GANG`, `HSA_ENABLE_SDMA_COPY_SIZE_OVERRIDE` and
  `HSA_ENABLE_SDMA_RECOMMENDED_ENG` also change which engine copies ([ROCR]
  lines 96 to 106). None of these is in RI-ROC-015's list; the audit records
  them as observations, not gaps.
