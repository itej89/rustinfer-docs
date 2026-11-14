---
title: "Vulkan 1.4.368 tracker"
navtitle: Tracker
section: Standards
group: "Runtime / Vulkan 1.4.368"
order: 33
summary: The open decision on the minimum Vulkan version (OI-016) and the R2 work for compute dispatch of SPIR-V modules.
---

# Vulkan 1.4.368 tracker

From the [audit](std-vulkan-audit.html) of 2026-11-13. No GitHub issue covers the
Vulkan work yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| VULK-1 | No minimum core Vulkan version, so no SPIR-V version to emit | Appendix A, *Versions and Formats* | Open | OI-016 (owner decision): (a) Vulkan 1.2 with SPIR-V 1.5, runs on the K3's BXM-4-64 today; (b) Vulkan 1.3 with SPIR-V 1.6. Blocks VULK-2 to VULK-5 |
| VULK-2 | No shader module creation or SPIR-V validation before it | §9.2, VUID-VkShaderModuleCreateInfo-codeSize-01085, -08735, -pCode-08736 to -08742 | Later release R2 | RI-KC-004, RI-RV-001. A standalone validation of the emitted module (Appendix A, *Standalone SPIR-V Validation*) would catch V3 and V4 on a host without a GPU |
| VULK-3 | No compute pipeline or dispatch | §10.3, VUID-VkComputePipelineCreateInfo-stage-00701; §37, VUID-vkCmdDispatch-commandBuffer-cmdpool | Later release R2 | RI-RV-001 |
| VULK-4 | Group counts, work-group size and shared memory not checked against the device | §37, VUID-vkCmdDispatch-groupCount*-0038x; Appendix A, VUID-RuntimeSpirv-x-06429, -06432, -Workgroup-06530 | Later release R2 | The same check RI-ROC-004 asks of the ROCm target |
| VULK-5 | No device or compute queue family selection | VUID-vkCmdDispatch-commandBuffer-cmdpool | Later release R2 | Discovery must leave out a device it cannot probe (RI-PLN-002 rule) |
