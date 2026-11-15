---
title: "HIP runtime API ROCm 7.2 audit"
navtitle: Audit
section: Standards
group: "Runtime / HIP runtime API ROCm 7.2"
order: 12
summary: The 2026-11-14 re-audit of rustinfer's HIP use against the ROCm 7.2.4 reference on main 81fbcba: every R1 item conforms with host tests and is verified on gfx950 (#59); gfx942 is not yet run (#61).
---

# HIP runtime API ROCm 7.2 audit

**Audit of 2026-11-14**, against the [requirements](std-hip-requirements.html);
it replaces the audit of 2026-11-13, which read the stub on `ccf02b3` and PR #44's
test harness.

**Method.** Read `crates/rustinfer-target-rocm` on `main` at `81fbcba` (after the
merges of PR #58, `53dac5b`, issue #12; PR #60, `14ec27e`; PR #44, `38f2f60`; PR
#62, `81fbcba`): `src/lib.rs`, `src/runtime.rs`, `src/hip.rs`, `src/ffi/`,
`src/device/`, `src/resources.rs`, `src/code_object/` and every file in `tests/`;
`crates/rustinfer-core/src/config/hip_library.rs`, `constants.rs` and
`manifest.rs`; SRS v0.4.10 (§1.4 HIP row, RI-SEC-001, RI-NFR-017). Compared each
with the HIP 7.2.4 reference pages in `specs/runtime/`. Read the result comments
of GPU tests #45 and #59 on issue #54 and the open request #61. Nothing was run
here: there is no GPU on this host. The host tests run against `MockHip`
(`tests/common/mock.rs`), an implementation of the same function table
(`HipApi`, `src/hip.rs:125`) that the `rocm` feature implements over the real
library. Test tags follow `docs/testing.md`.

**Hardware evidence.** #59 ran the 11 hardware tests of `tests/gpu.rs` at
`bb0ce2f`, the head PR #58 merged, on an AMD Instinct MI350X (gfx950,
`gcnArchName` `gfx950:sramecc+:xnack-`) in `rocm/dev-ubuntu-24.04:latest` with
ROCm 10.1 (10.1.0-3), on 2026-11-15 (UTC): 11 passed, 0 failed, results in
#54. The binding refuses any HIP runtime whose major version is not 7, so that
install ships a HIP 7.x runtime; SRS v0.4.10 now states support by HIP runtime
major version 7 (`libamdhip64.so.7`) and records ROCm 10.1 (10.1.0-3) as
verified. No gfx942 device has run it: #61 asks for the MI300X run.

**State on main.** `RocmTarget` (`src/lib.rs:58-121`) opens the devices on first
use: it checks the runtime's major version, counts the devices, reads each one's
properties and `gcnArchName`, and serves each as a `RocmDevice` that implements
`Device` and `Launcher` (`src/lib.rs:204-227`). Every HIP call goes through
`Hip::call` (`src/runtime.rs:23-29`); raw handles exist only in `src/ffi/`
(RI-ROC-005). Without the `rocm` feature selecting a device reports
`unsupported` (`src/lib.rs:130-137`; `test_without_the_rocm_feature_the_target_reports_unsupported`,
`tests/unsupported.rs:26`, `Groundwork for RI-NFR-016`).

| id | result | evidence |
|---|---|---|
| H1 devices, `gcnArchName` | **conforms**; verified on gfx950 | `hipGetDeviceCount` (`hipErrorNoDevice` read as no device), `hipGetDevicePropertiesR0600`, `hipSetDevice` (`src/lib.rs:140-186`, `src/ffi/symbols.rs:69-71`); the processor is parsed from `gcnArchName` (`src/arch.rs:32`), never taken from the registry string. Tests in `tests/architecture.rs` (`Verifies RI-ROC-003`). #59: `gpu_device_reports_its_architecture` read `architecture=gfx950` |
| H2 memory | **conforms**; verified on gfx950 | `hipMalloc`, `hipFree`, `hipMemcpyWithStream`, `hipMemcpyAsync` (`src/ffi/symbols.rs:72-75`). Zero bytes is refused before `hipMalloc` (`src/device/mod.rs:243-253`; `test_zero_byte_allocation_is_refused_without_calling_hip`, `tests/device.rs:75`). `hipFree`'s implicit synchronisation covers only the current device, so `free` calls `hipSetDevice` and waits on per-resource last-use events first (`src/device/lifetime.rs:1-16`). #59: `memory_round_trip`, `free_while_in_use` |
| H3 streams | **conforms**; verified on gfx950 | `hipStreamCreateWithFlags`, `hipStreamSynchronize`, `hipStreamDestroy` (`src/ffi/symbols.rs:76-78`); every stream destroyed on drop after a synchronise (`src/device/mod.rs:436-456`; `test_drop_releases_every_hip_resource`, `tests/device.rs:463`) |
| H4 events | **conforms**; verified on gfx950 | create, record, synchronize, elapsed time, `hipStreamWaitEvent`, destroy (`src/ffi/symbols.rs:79-84`). An event is re-recorded only on the stream that owns the last use, in stream order (`src/device/lifetime.rs`). #59: `stream_event_ordering` proved ordering, not only completion |
| H5 modules | **conforms**; verified on gfx950 | `hipModuleLoadData`, `hipModuleGetFunction`, `hipModuleUnload`; the code object is parsed and checked (architecture, `xnack`/`sramecc`, one kernel, resources, arguments) before `hipModuleLoadData` (`src/device/kernels.rs:102-170`). The image is a single code object, not a fat binary. #59: `module_load_and_launch` |
| H6 launch | **conforms**; verified on gfx950 | `hipModuleLaunchKernel` with three-dimensional grid and block on a chosen stream (`src/device/mod.rs:150-158`); grid times block below 2^32 per dimension and every dimension at least 1 (`src/device/kernels.rs:316-331`; `test_explicit_dimensions_and_the_work_item_limit`, `tests/device.rs:326`). Arguments are packed from the metadata's argument list, and a kernel whose arguments the launcher cannot bind is refused at load (`check_arguments`, `src/device/kernels.rs:281`; `tests/device.rs:433`) |
| H7 resource check | **conforms**, by the code object's metadata instead of `hipFuncGetAttribute`; LDS verified on gfx950 | `hipFuncGetAttribute` is not bound. The kernel's LDS, registers, work-group and wavefront size are read from `NT_AMDGPU_METADATA` and checked before loading (`src/resources.rs:63-81`). Device limits are `sharedMemPerBlock`, `maxThreadsPerBlock` and `warpSize`; because `regsPerBlock` is always 0, as the reference warns, register limits are AMDGPUUsage's per architecture (`crates/rustinfer-core/src/config/constants.rs:400-418`). Six tests in `tests/resources.rs` (`Verifies RI-ROC-004`). #59: `lds_at_limit_launches` at 163840 and `lds_over_limit_is_refused` at 163844. The register limits are not exercised on hardware |
| H8 error codes | **conforms** | `Error::Hip { operation, code, message }`, "HIP {operation} failed with error {code}: {message}" (`src/error.rs:31-40`), from `hipGetErrorString` (`src/runtime.rs:44-52`). Error code `device` (`tests/error_contract.rs:24`, `Verifies RI-CLI-001`); every bound call family is covered in `tests/errors.rs` (`Verifies RI-ROC-002`). `hipGetErrorName` and `hipGetLastError` are not used; no requirement needs them |
| H9 runtime version | **conforms** for `hipRuntimeGetVersion`; `hipDriverGetVersion` not bound | Major version 7 required at open, another refused naming found, major and required (`src/lib.rs:157-169`); the version is logged as a manifest line (`src/lib.rs:150`). `test_runtime_of_another_major_version_is_refused` (`tests/errors.rs:278`) is tagged `Groundwork for RI-NFR-017`, not `Verifies`, since the clause's first half (an artifact loads on any host of the same major) needs the runtime. The artifact header records no HIP major version; with one accepted major that is implied |
| H10 graph capture binding | **conforms**; verified on gfx950 | `hipStreamBeginCapture` (thread-local mode), `hipStreamEndCapture`, `hipGraphInstantiate`, `hipGraphLaunch`, `hipGraphDestroy`, `hipGraphExecDestroy` (`src/ffi/symbols.rs:91-96`, `src/device/graph.rs`). A failed capture is always ended; an exec is destroyed only after its last use. #59: `graph_capture_replay` (5 graph launches, 0 host syncs), `graph_destroy_while_in_use` |
| H11 graph replay per bucket | **later release** (R2) | RI-ROC-007. The contract takes a bucket (`crates/rustinfer-target/src/target.rs:128`); the per-bucket plan is R2 |
| H12 peer access | **later release** (R2) | RI-PLN-002. `hipDeviceCanAccessPeer` not bound |

**Note on RI-SEC-001.** The bare-name `dlopen` of PR #44's harness, noted in the
first audit, is gone. The binding opens the HIP runtime only by absolute path:
the first of `/opt/rocm/lib`, `/usr/lib/x86_64-linux-gnu`, `/usr/lib64` and
`/usr/lib` that holds `libamdhip64.so.7` (`ROCM_HIP_LIBRARY_PATHS`,
`crates/rustinfer-core/src/config/constants.rs:368-378`; `src/ffi/symbols.rs:122-161`),
so `LD_LIBRARY_PATH` and the working directory cannot substitute it
(`test_with_the_rocm_feature_hip_is_opened_from_system_paths_only`,
`tests/unsupported.rs:49`, `Groundwork for RI-SEC-001`;
`test_hip_library_paths_are_absolute_and_pinned_to_major_7`, `:73`). SRS v0.4.9
added the `RUSTINFER_HIP_LIBRARY` override, which is loaded alone and validated
first: absolute, canonical, a regular `libamdhip64.so.7` file owned by root or
the effective user, writable by neither group nor world, in a directory writable
by neither (`crates/rustinfer-core/src/config/hip_library.rs:52-78`, `:112-123`;
`test_settings_reject_an_invalid_hip_library_override`,
`crates/rustinfer-core/tests/settings.rs:76`, `Verifies RI-SEC-001, SWG-001 §8.7`;
`test_the_override_alone_is_loaded_and_reported`, `tests/hip_override.rs:89`,
`Verifies RI-SEC-001`). The library loaded and the runtime version are manifest
lines. The clause's "code objects load only after RI-ART-003" part waits for the
runtime, which does not call `load` yet.

**Result.** All ten R1 items conform on `main` `81fbcba` (H7 through the code
object's metadata, H9 without `hipDriverGetVersion`), each with host tests over
the mock, and every one but H8 is exercised on gfx950 hardware by #59. The
remaining R1 gap is evidence, not code: no gfx942 device has run the binding
(HIP-13, #61). H11 and H12 are R2. Gaps are on the [tracker](std-hip-tracker.html).
