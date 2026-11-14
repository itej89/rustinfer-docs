---
title: "HIP runtime API ROCm 7.2 requirements"
navtitle: Requirements
section: Standards
group: "Runtime / HIP runtime API ROCm 7.2"
order: 11
summary: The HIP calls and contracts in rustinfer's scope (memory, streams, events, modules, launches, graphs, error codes), quoted from the ROCm 7.2.4 reference.
---

# HIP runtime API ROCm 7.2 requirements

Source: `specs/runtime/hip-7.2.4-*.html` (AMD, *HIP Runtime API Reference*, HIP
7.2.53211 documentation for ROCm 7.2.4, 2026-05-29). The reference is an API
reference, not a numbered specification: items are cited by module page and
function, as the reference names them. Scope from SRS §1.4: memory, streams,
events, modules, launches, graphs and error codes. The release is the one of the
SRS requirement that needs the item.

| id | item (module page, function) | what the reference says | needed by | release |
|---|---|---|---|---|
| H1 | Device management: `hipGetDeviceCount`, `hipSetDevice`, `hipGetDeviceProperties` | `hipGetDeviceCount` "will return hipErrorNoDevice" when there is no compute-capable device. Valid ids for `hipSetDevice` are "0… (hipGetDeviceCount() -1)"; memory, streams and events created afterwards from that thread belong to that device. `hipDeviceProp_t::gcnArchName[256]` is the "AMD GCN Arch Name. HIP Only." | RI-ROC-001, RI-ROC-003 | R1 |
| H2 | Memory management: `hipMalloc`, `hipFree`, `hipMemcpy`, `hipMemcpyAsync` | "If size is 0, no memory is allocated, *ptr returns nullptr, and hipSuccess is returned." `hipFree` "performs an implicit hipDeviceSynchronize() call". `hipMemcpyAsync`: "The copy is always performed by the device associated with the specified stream." | RI-ROC-001 | R1 |
| H3 | Stream management: `hipStreamCreate`, `hipStreamSynchronize`, `hipStreamDestroy` | A stream "will remain allocated even if the handle goes out-of-scope. To release the memory used by the stream, the application must call hipStreamDestroy." `hipStreamSynchronize` blocks "until all operations on the specified stream ... are completed". | RI-ROC-001 | R1 |
| H4 | Event management: `hipEventCreate`, `hipEventRecord`, `hipEventSynchronize` | "hipEventQuery() or hipEventSynchronize() must be used to determine when the event transitions from recording ... to recorded." Recording an event that is being recorded: "results are undefined". | RI-ROC-001 | R1 |
| H5 | Module management: `hipModuleLoadData`, `hipModuleGetFunction`, `hipModuleUnload` | `hipModuleLoadData` "builds module from code object data which resides in host memory"; the image "can be either a single code object or a fat binary". `hipModuleUnload`: "the code objects associated with it are destroyed." | RI-ROC-001, RI-ROC-004 | R1 |
| H6 | Execution control: `hipModuleLaunchKernel` | Launches `f` "with launch parameters and shared memory on stream". "HIP does not support kernel launch with total work items defined in dimension with size gridDim x blockDim >= 2^32." Arguments passed through `extra` "must be in the memory layout and alignment expected by the kernel". | RI-ROC-001 | R1 |
| H7 | Execution control: `hipFuncGetAttribute`; device properties `sharedMemPerBlock`, `regsPerBlock` | `hipFuncGetAttribute` finds "a specific attribute for a given function". `hipGetDeviceProperties` lists a known bug: "HIP-Clang always returns 0 for regsPerBlock", so the register limit cannot come from that field. | RI-ROC-004 | R1 |
| H8 | Error handling: `hipError_t`, `hipGetErrorString`, `hipGetErrorName` | Every call returns a `hipError_t`; `hipGetErrorString` returns a "NULL-terminated error string" for an error code, `hipGetErrorName` its name. `hipGetLastError` returns and resets the last error of the calling host thread. | RI-ROC-002 | R1 |
| H9 | Initialization and version: `hipRuntimeGetVersion`, `hipDriverGetVersion` | The driver version is "HIP_VERSION_MAJOR * 10000000 + HIP_VERSION_MINOR * 100000 + HIP_VERSION_PATCH"; `hipRuntimeGetVersion` "Returns the approximate HIP Runtime version". | RI-NFR-017 (same HIP runtime major version) | R1 |
| H10 | Graph management: `hipStreamBeginCapture`, `hipStreamEndCapture`, `hipGraphInstantiate`, `hipGraphLaunch` | Capture begins on a stream with a capture mode and ends "returning the captured graph"; `hipGraphInstantiate` "Creates an executable graph from a graph"; `hipGraphLaunch` "Launches an executable graph in the specified stream." | RI-ROC-001 (binding of graph capture) | R1 |
| H11 | The same graph calls, used per bucket | Capture of every sub-plan into graph segments per bucket and replay. | RI-ROC-007 | R2 |
| H12 | Peer to peer: `hipDeviceCanAccessPeer` | Returns 1 if the device can access memory on the peer, 0 if not, and "0 if deviceId == peerDeviceId"; `hipErrorInvalidDevice` for an invalid id. | RI-PLN-002 | R2 |

Not in scope: textures, surfaces, virtual and unified memory, OpenGL and external
resource interop, runtime compilation (HIPRTC: rustinfer builds its own code objects,
RI-KC-008), cooperative groups. Which shared libraries may be loaded (RI-SEC-001) is
an SRS rule, not a HIP one; the audit notes it where a HIP call loads code.
