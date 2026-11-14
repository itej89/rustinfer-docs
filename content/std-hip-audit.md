---
title: "HIP runtime API ROCm 7.2 audit"
navtitle: Audit
section: Standards
group: "Runtime / HIP runtime API ROCm 7.2"
order: 12
summary: The 2026-11-13 audit of rustinfer's HIP use against the ROCm 7.2.4 reference: the target is a stub, and PR #44's test harness covers memory, modules, one launch shape and error strings.
---

# HIP runtime API ROCm 7.2 audit

**Audit of 2026-11-13**, against the [requirements](std-hip-requirements.html).

**Method.** Read `crates/rustinfer-target-rocm` on origin/main (`ccf02b3`), its
tests and `rustinfer-core`'s version manifest; read the same crate on the head of
open PR #44 (`10b8b1b`, feature `rocm-test`); read issue #12; compared each with
the HIP 7.2.4 reference pages in `specs/runtime/`. Nothing was run: there is no GPU
on this host, and the harness tests are ignored without one. Test tags follow
`docs/testing.md`.

**State on origin/main.** `RocmTarget` registers `gfx942` and `gfx950`
(`crates/rustinfer-core/src/config/constants.rs:297`), reports no device and refuses
`device` and `launcher` (`crates/rustinfer-target-rocm/src/lib.rs:59-69`). The tests
say so: `tests/stub.rs:35` `test_rocm_entry_registers_gfx942_and_gfx950` and
`tests/stub.rs:67` `test_rocm_target_has_no_device_until_hip_is_bound` (a
`Groundwork for RI-NFR-016` tag). No HIP symbol is referenced anywhere on main.

**State on PR #44.** `src/ffi/hip.rs` resolves nine entry points
(`hip.rs:61-71`: `hipModuleLoadData`, `hipModuleGetFunction`,
`hipModuleLaunchKernel`, `hipModuleUnload`, `hipMalloc`, `hipFree`, `hipMemcpy`,
`hipDeviceSynchronize`, `hipGetErrorString`); `Hip::open` loads
`libamdhip64.so` (`hip.rs:121-139`); `Hip::check` turns a non-zero status into
`Error::Hip { call, detail }` with `hipGetErrorString`'s text and the status
(`hip.rs:204-217`, `src/error.rs:20-28`). The test is
`tests/gpu_code_objects.rs`, ignored without a GPU; its run is #45.

| id | result | evidence |
|---|---|---|
| H1 devices, `gcnArchName` | **missing** | no device call on main or in PR #44; the architecture is the registry string, never read from the device. Issue #12 |
| H2 memory | **pending PR #44** | `hipMalloc`, `hipMemcpy`, `hipFree` in the harness (`hip.rs:262-289`); no `hipMemcpyAsync` (no streams). The zero-size case of `hipMalloc` is not handled or tested |
| H3 streams | **missing** | the harness launches on the default stream (`hip.rs:175`) |
| H4 events | **missing** | not referenced |
| H5 modules | **pending PR #44** | `Module::load` calls `hipModuleLoadData` (`hip.rs:225-231`), unloads on drop (`hip.rs:248`) |
| H6 launch | **pending PR #44** | `hipModuleLaunchKernel` on a one-dimensional grid (`hip.rs:164-196`); the reference's limit (grid times block below 2^32 per dimension) is not checked: `Launch` holds two `u32` whose product can exceed it |
| H7 resource check | **missing** | no `hipFuncGetAttribute`; no comparison with the device. The reference warns that `regsPerBlock` is always 0, so the register check needs another source. Issue #12 acceptance "refused before launch" |
| H8 error codes | **pending PR #44** | every harness call goes through `Hip::check`; the code is `ErrorCode::Device`. Issue #12 asks for `Error::Hip { operation, code, message }`; the PR carries the status inside `detail`, not as a field |
| H9 runtime version | **missing** | the startup manifest has software, toolchain, host and dependencies, no HIP version (`crates/rustinfer-core/src/manifest.rs:42-61`); the artifact header records no HIP major version |
| H10 graph capture binding | **missing** | not referenced |
| H11 graph replay per bucket | **later release** (R2) | RI-ROC-007 |
| H12 peer access | **later release** (R2) | RI-PLN-002 |

**Note on RI-SEC-001.** The harness opens `libamdhip64.so` by bare name, so the
dynamic loader's search (including `LD_LIBRARY_PATH`) decides which file is loaded.
RI-SEC-001 allows only the HIP runtime "from the system library path". The harness is
test code, but the production binding of #12 must decide this; it is noted on
HIP-1 in the [tracker](std-hip-tracker.html).

**Result.** No R1 item conforms. Four are pending PR #44 and only as a test harness;
six are not started.
