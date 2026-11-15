---
title: "HIP memory management 7.2.4 requirements"
navtitle: Requirements
section: Standards
group: "Runtime / HIP memory management 7.2.4"
order: 15
summary: What HIP 7.2.4's memory-management how-to says about pinned host memory, the hipHostMalloc flags, coarse- and fine-grained coherence, event visibility, hipHostRegister and virtual-memory peer access, the part in rustinfer's scope.
---

# HIP memory management requirements

Sources, all HIP 7.2.4 in `specs/runtime/`: *Host memory*
(`hip-7.2.4-host_memory.txt`, **[HOST]**), *Coherence control*
(`hip-7.2.4-coherence_control.txt`, **[COH]**), *Virtual memory management*
(`hip-7.2.4-virtual_memory.txt`, **[VMM]**), cited by line; and the API
reference's memory-management page (`hip-7.2.4-memory_management.txt`,
**[API]**) for `hipHostRegister`. The requirements on rustinfer are
RI-ROC-008 and RI-WST-006 (R1), RI-WST-007 and RI-ROC-013 (R2); each row
names which.

## Pinned host memory and its flags (R1, RI-ROC-008)

| id | requirement | source |
|---|---|---|
| HMEM-R1 | Pinned (page-locked) host memory is what makes host-to-device transfers fast: "For transfer operations, such as `hipMemcpy()` or `hipMemcpyAsync()`, using pinned memory instead of pageable memory on the host can lead to a three times improvement in bandwidth"; its cost is "reduced availability of RAM for other processes". Pageable memory is what `malloc` or `new` return. RI-ROC-008 therefore stages uploads in pinned memory | [HOST] lines 152 to 160, 229 to 243 |
| HMEM-R2 | `hipHostMalloc` flags: `hipHostMallocPortable`, `hipHostMallocMapped`, `hipHostMallocNumaUser`, `hipHostMallocWriteCombined`, `hipHostMallocCoherent` (fine-grained), `hipHostMallocNonCoherent` (coarse-grained); "All allocation flags are independent and can be set in any combination", except that `Coherent` with `NonCoherent` "leads to an illegal state". RI-ROC-008 names `hipHostMallocNonCoherent` | [HOST] lines 306 to 347 |
| HMEM-R3 | Coherence of `hipHostMalloc`: `hipHostMallocNonCoherent` is coarse-grained; with none of `Coherent`, `NonCoherent`, `Mapped`, the `HIP_HOST_COHERENT` variable decides, and "If neither these flags nor the `HIP_HOST_COHERENT` environment variable is set, or set as 0, the host memory allocation is coarse-grained"; with `hipHostMallocMapped` "the allocated host memory is fine-grained and the `hipHostMallocNonCoherent` flag is ignored". So a staging buffer is coarse-grained only if it is not mapped | [COH] lines 195 to 293 |
| HMEM-R4 | Coarse-grained memory is "Recommended for bulk data transfers and large memory regions. Utilizes the full L2 cache"; fine-grained "Typically bypasses the L2 cache ... resulting in lower bandwidth" and is for flags and signals | [COH] lines 294 to 330 |
| HMEM-R5 | Visibility at a synchronisation point: `hipStreamSynchronize` and `hipDeviceSynchronize` make coarse-grained host memory visible; `hipEventSynchronize` "Depends on the used event"; `hipStreamWaitEvent` does not. An event created with `hipEventReleaseToSystem` makes coarse-grained host memory visible to other agents. This page's reading, not the document's words: a staging buffer the device only reads (an upload) may be reused once the copy's event has completed, which is RI-ROC-008's rule; a buffer the device writes (a readback) is visible to the host after an event wait only with that flag | [COH] lines 332 to 440 |

## Registered host memory (R2, RI-WST-007)

| id | requirement | source |
|---|---|---|
| HMEM-R6 | `hipHostRegister(hostPtr, sizeBytes, flags)` registers existing host memory: `hipHostRegisterDefault` ("Mapped and Portable"), `hipHostRegisterPortable`, `hipHostRegisterMapped`, `hipExtHostRegisterUncached`; "On some systems, registered memory is pinned. On some systems, registered memory may not be actually be pinned"; blocks "aligned to the host cache-line size" are "strongly encouraged". The page lists no coarse-grained registration flag, while RI-WST-007 asks for a coarse-grained registration and [COH] makes mapped memory fine-grained | [API] lines 346 to 366; [COH] lines 287 to 288 |

## Peer access by virtual memory (R2, RI-ROC-013)

| id | requirement | source |
|---|---|---|
| HMEM-R7 | With `hipMalloc` memory, `hipDeviceEnablePeerAccess` "enables access between two devices, but it means that every call to `hipMalloc()` takes more time to perform the checks and the mapping between the devices"; with virtual memory management, `hipMemSetAccess(ptr, size, &accessDesc, 1)` maps a chosen range for a chosen device, which "has no performance impact on memory allocation". RI-ROC-013 maps shared buffers this way | [VMM] lines 238 to 263 |

## Related, outside the scope

- The asynchrony of `hipMemcpyAsync` itself and the `Device` contract's
  events are the [HIP runtime API](std-hip.html)'s scope (SRS v0.5 extended it
  to host staging memory and stream priorities); this page covers the memory.
- RI-ROC-008's alignment of device allocations to the large-page fragment
  cites the Linux driver (LINUX-AMDGPU, `gmc_v9_0.c`, informative) and the
  device description of RI-ROC-011 (#92), not HIP-MEM.
