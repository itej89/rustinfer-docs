---
title: "HIP runtime API ROCm 7.2 tracker"
navtitle: Tracker
section: Standards
group: "Runtime / HIP runtime API ROCm 7.2"
order: 13
summary: Gaps between rustinfer's ROCm target and the HIP runtime calls it must use; most are issue #12.
---

# HIP runtime API ROCm 7.2 tracker

Gaps found by the [audit](std-hip-audit.html) of 2026-11-13. The binding is issue
[#12](https://github.com/itej89/rustinfer/issues/12) (open); the harness is PR
[#44](https://github.com/itej89/rustinfer/pull/44), whose GPU run is
[#45](https://github.com/itej89/rustinfer/issues/45).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| HIP-1 | No device enumeration, selection or properties; the architecture is not read from `gcnArchName` | Device management: `hipGetDeviceCount`, `hipSetDevice`, `hipGetDeviceProperties` | Open | #12 (RI-ROC-001, RI-ROC-003). The binding must also fix where `libamdhip64` is loaded from (RI-SEC-001); PR #44 loads it by bare name |
| HIP-2 | No device memory in the target | Memory management: `hipMalloc`, `hipFree`, `hipMemcpyAsync` | In PR #44 | Harness only, synchronous `hipMemcpy`; the target's version is #12. Zero-size `hipMalloc` returns a null pointer with success: to be handled and tested |
| HIP-3 | No streams | Stream management | Open | #12. One stream per iteration (RI-RT-008) |
| HIP-4 | No events | Event management | Open | #12 |
| HIP-5 | No module loading in the target | Module management: `hipModuleLoadData`, `hipModuleGetFunction`, `hipModuleUnload` | In PR #44 | Harness only. RI-ROC-004 also requires loading only after the artifact check |
| HIP-6 | No kernel launch in the target | Execution control: `hipModuleLaunchKernel` | In PR #44 | Harness only, one-dimensional grid, default stream; the per-dimension limit (grid times block below 2^32) is unchecked |
| HIP-7 | HIP errors not mapped to a typed error in the target | Error handling: `hipError_t`, `hipGetErrorString` | In PR #44 | `Error::Hip { call, detail }` in the harness; #12 asks for `operation`, `code` and `message` as fields (RI-ROC-002) |
| HIP-8 | No check of a kernel's LDS and register needs before its first launch | Execution control: `hipFuncGetAttribute`; `hipDeviceProp_t` | Open | #12 (RI-ROC-004). `regsPerBlock` is always 0 per the reference's bug note, so the limit needs another source |
| HIP-9 | HIP runtime version not recorded or compared | Initialization and version: `hipRuntimeGetVersion`, `hipDriverGetVersion` | Open | RI-NFR-017; no issue covers it (#12 lists RI-ROC-001 to 005 only). Natural places: the startup manifest and the artifact's target check |
| HIP-10 | No graph capture binding | Graph management: `hipStreamBeginCapture`, `hipStreamEndCapture`, `hipGraphInstantiate`, `hipGraphLaunch` | Open | #12 (RI-ROC-001 binds graph capture in R1) |
| HIP-11 | No graph replay per bucket | Graph management | Later release R2 | RI-ROC-007 |
| HIP-12 | No peer access discovery | Peer to peer: `hipDeviceCanAccessPeer` | Later release R2 | RI-PLN-002 |
