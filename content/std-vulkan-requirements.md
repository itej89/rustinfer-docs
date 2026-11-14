---
title: "Vulkan 1.4.368 requirements"
navtitle: Requirements
section: Standards
group: "Runtime / Vulkan 1.4.368"
order: 31
summary: What the Vulkan specification requires of an application that creates SPIR-V shader modules and dispatches compute work.
---

# Vulkan 1.4.368 requirements

Source: `specs/runtime/vkspec-1.4.368.html` (Khronos, *Vulkan 1.4.368 - A
Specification*, accessed 2026-11-13). Scope from SRS §1.4: compute dispatch of
SPIR-V modules. These are obligations on rustinfer as a Vulkan *application* (valid
usage), not on the driver. Every item is needed from R2. Valid usage IDs (VUIDs) are
quoted as the specification gives them.

## Version (Appendix A, *Vulkan Environment for SPIR-V*, and OI-016)

| id | requirement |
|---|---|
| V1 | Appendix A, *Versions and Formats*: "A Vulkan 1.4 implementation must support the 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, and 1.6 versions of SPIR-V." The SPIR-V version rustinfer emits must be one the chosen core version accepts. The 1.4.368 text states only the 1.4 rule; OI-016 records that core 1.2 accepts SPIR-V up to 1.5 and SPIR-V 1.6 needs 1.3. **The minimum is open (OI-016).** |

## Shader modules (§9.2 *Shader Modules*, `VkShaderModuleCreateInfo`)

| id | requirement |
|---|---|
| V2 | VUID-VkShaderModuleCreateInfo-codeSize-01085: "codeSize must be greater than 0"; -codeSize-08735: "codeSize must be a multiple of 4". |
| V3 | -pCode-08736: "pCode must point to valid SPIR-V code, formatted and packed as described by the Khronos SPIR-V Specification"; -pCode-08737: it must adhere to the validation rules of the SPIR-V Environment appendix. Appendix A adds that the first words "must be a magic number and a SPIR-V version number". |
| V4 | -pCode-08738: "pCode must declare the Shader capability"; -pCode-08739 and -08741: it must not declare a capability or a SPIR-V extension the API does not support; -08740 and -08742: a listed capability or extension needs its feature or extension enabled. |

## Compute pipelines and dispatch (§10.3 *Compute Pipelines*, §37 *Dispatching Commands*)

| id | requirement |
|---|---|
| V5 | VUID-VkComputePipelineCreateInfo-stage-00701: "The stage member of stage must be VK_SHADER_STAGE_COMPUTE_BIT"; -layout-07987 and -07988: push constant ranges and descriptor sets in the layout must match what the shader declares. |
| V6 | VUID-vkCmdDispatch-commandBuffer-cmdpool: "The VkCommandPool that commandBuffer was allocated from must support VK_QUEUE_COMPUTE_BIT operations." |
| V7 | VUID-vkCmdDispatch-groupCountX-00386, -groupCountY-00387, -groupCountZ-00388: each group count "must be less than or equal to VkPhysicalDeviceLimits::maxComputeWorkGroupCount" in that dimension. |
| V8 | Appendix A, runtime SPIR-V validation: VUID-RuntimeSpirv-x-06429 (and the y and z rules after it): each `LocalSize` or `LocalSizeId` size "must be less than or equal to" `maxComputeWorkGroupSize` in that dimension; -x-06432: their product must not exceed `maxComputeWorkGroupInvocations`; -Workgroup-06530: Workgroup storage "must be less than or equal to maxComputeSharedMemorySize". |

The values to check against are the device's. What the device may report is bounded
by §57.1 *Limit Requirements*: for Vulkan Core, at least (65535, 65535, 65535) work
groups, a work-group size of (128, 128, 64), 128 invocations and 16384 bytes of shared
memory; the Roadmap 2022 and 1.4 columns raise the size to (256, 256, 64) and the
invocations to 256. Which column applies depends on OI-016. Graphics, presentation,
images and every extension are out of scope.
