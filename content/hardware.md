---
title: Hardware
section: Hardware
order: 1
summary: The targets the workspace registers and the AMD and RISC-V device landscape the planner must describe; accelerators, host CPUs, DPUs and NICs, interconnects, memory tiers and rack systems, with vendor figures as of 2026-11.
---

# Hardware

Read from SRS §2.4, §3.2.8 to §3.2.10, ADR-003,
`docs/planning/datacenter-device-inventory.md`, `crates/rustinfer-target/`
and the four backend crates at commit `f039b4d`; the targets table is read
from the code since GitHub PR #21 (2026-11-12, issue #5), its ROCm rows and
the GPU tests below at `81fbcba` (2026-11-14, after PRs #58, #44 and #62), the
device tables from the inventory. The
inventory's scope statement: AMD and the open-standard and RISC-V ecosystem
around it; NVIDIA parts are out of scope and appear only where a design
pattern is cited; figures are vendor numbers from the sources listed in the
file, as of 2026-11; "announced" marks parts not yet shipping. rustinfer has
run on one GPU: the GPU tests #45 and #59 on an MI350X (gfx950); no model has
run on a device yet.

## Targets

| architecture string | hardware | backend crate | state (`cpu` and stubs at `f039b4d`, ROCm at `81fbcba`) | release |
|---|---|---|---|---|
| `cpu` | any host | `rustinfer-target` | `CpuTarget` in the code: every R1 operator as `f32` reference functions, a catalog of one `cpu.<operator>` kernel per compute operator, one device with a 16 GiB default budget, the oracle of every other target (RI-TGT-003) | R1 (operators), R2 (collectives) |
| `gfx942` | MI300X, MI308X, MI325X | `rustinfer-target-rocm`, feature `rocm` | `RocmTarget` over the HIP 7 runtime (PR #58, issue #12): devices, memory, streams, events, modules, launches and graph capture; empty catalog until the autotuner (#9). Code objects from `rustinfer-kc` (PR #44, issue #8). **Not yet run on hardware** (#61) | R1 |
| `gfx950` | MI350X, MI355X | same | the same code; **verified on an MI350X** by #45 (code objects) and #59 (HIP binding), results in #54 | R1; the reference architecture for autotuning and benchmarks (OI-008) |
| CDNA successor (`gfx1250` class, the inventory's guess) | MI450, MI455X in Helios | same, when available | — | not in a release tag |
| `spirv-vulkan` | Imagination BXM-4-64 on the SpacemiT K3 | `rustinfer-target-spirv-vulkan` | `SpirvVulkanTarget` stub | R2 lowering, compile-tested |
| `riscv-vector` | SpacemiT K3 X100 cores (RVA23, RVV 1.0), SpacemiT V100 | `rustinfer-target-riscv-vector` | `RiscvVectorTarget` stub | R3 lowering, compile-tested; first device bring-up R3 |
| `riscv-mesh` | Tenstorrent Blackhole (120 Tensix cores plus 16 RISC-V Linux cores) | `rustinfer-target-riscv-mesh` | `RiscvMeshTarget` stub | R4 |

In the code, a stub implements `Target` with an `EmptyCatalog` and no
device: it compiles on every host, registers its string through one
`entry()`, any kernel request fails with `catalog empty` naming the target
(RI-RV-002) and `device(0)` with `NoDevice`. The command's registry lists
exactly the six strings above and `build` and `tune` resolve `--target`
through it before any component runs (RI-TGT-001, -004); a product name or
an unregistered string is refused listing the registered ones. The two ROCm
targets are no longer stubs (PR #58, merge `53dac5b`): the HIP runtime
`libamdhip64.so.7` is opened with `dlopen` from the system library
directories, or exactly the file `RUSTINFER_HIP_LIBRARY` names once it is
checked (RI-SEC-001), through one FFI module; every HIP error is
`Error::Hip { operation, code, message }`; the architecture is read from
`gcnArchName`, and a target, kernel binary or code object for another one is
refused naming both; each code object's LDS and register needs, read from its
metadata note, are checked against the device before it is loaded
(RI-ROC-001 to -005); device buffers, streams and graphs are freed only after
their last-use events (per-resource lifetimes). Support is stated by **HIP
runtime major version 7**, checked at startup (`hipRuntimeGetVersion` /
10000000 must be 7; RI-NFR-017, SRS v0.4.10), documented against ROCm 7.2.4
and **tested under ROCm 10.1 (10.1.0-3)**, which ships a HIP 7.x runtime.
RISC-V targets go through their vendor runtime: TT-Metal for Tensix, the host
OS for vector cores, Vulkan for SPIR-V devices.

## GPU tests

GitHub's runners have no AMD GPU, so the owner runs the hardware tests by
hand, from the queue in issue #54 (process: `docs/gpu-testing.md`).

| test | what it proves | gfx950 (MI350X) | gfx942 (MI300X) |
|---|---|---|---|
| [#45](https://github.com/itej89/rustinfer/issues/45) | the AMD code objects of PR #44: the matrix op on MFMA (bf16, OCP fp8 E4M3 and E5M2 on gfx950), masked buffer loads and stores, the zero read past a bound, the LDS round trip across a barrier | **passed** at `821a57e` (PR #44 before its rebase): 4 passed, all 24 result lines `max_abs_err=0`, among them 18 matrix-op lines | not yet run ([#61](https://github.com/itej89/rustinfer/issues/61)) |
| [#59](https://github.com/itej89/rustinfer/issues/59) | the HIP binding of PR #58: memory round trip, module load and launch, stream and event ordering, graph capture and replay, waits on free and graph destroy, architecture refusals, the LDS limit | **passed** at `bb0ce2f` (the merged head): 11 passed, LDS 163840 bytes, 163844 refused | not yet run ([#61](https://github.com/itej89/rustinfer/issues/61)); expects LDS 65536 |

Both gfx950 runs used `rocm/dev-ubuntu-24.04:latest` with ROCm 10.1
(10.1.0-3), Rust 1.100.0 and, for #45, LLVM 23.1.6; the full output is on
#54. #61 also asks for a gfx950 re-run of #45 on `main`, since PR #44 was
rebased onto the ROCm target after its run.

## Accelerators

| class | parts | memory per device | compute | the door rustinfer uses |
|---|---|---|---|---|
| AMD Instinct, CDNA3 | MI300X (192 GB HBM3, 5.3 TB/s, 304 CU), MI308X (binned), MI325X (256 GB HBM3E, 6 TB/s) | 192 to 256 GB | ~1.3 PF FP16 dense; FNUZ fp8, no fp4 | HIP runtime; MLIR to ROCDL, `gfx942` |
| AMD Instinct, CDNA4 | MI350X, MI355X (288 GB HBM3E, 8 TB/s, 256 CU) | 288 GB | 2.3 PF FP16; fp4 and fp6 matrix cores; OCP fp8 | `gfx950` |
| AMD Instinct, next (announced) | MI450, MI455X (432 GB HBM4) in Helios | 432 GB | 40 PF FP4 | the CDNA successor |
| RISC-V core arrays and meshes | Tenstorrent Blackhole (GDDR6, Ethernet scale-out on chip; p150 card, Galaxy racks of 32 chips shipping 2026-04); Vortex (research RISC-V GPGPU, OpenCL via PoCL) | GDDR6 | 23 PF Block FP8 per Galaxy | TT-MLIR for Tensix; LLVM RISC-V for the control cores and for Vortex. The inventory calls these the only RISC-V accelerators with an MLIR or LLVM door |
| RISC-V vector CPUs as accelerators | SpacemiT K3 X100 cores, SpacemiT V100 (46 cores, server) | DDR | tens of TOPS; the K3's 60 TOPS INT4 NPU is closed | LLVM RISC-V with RVV; the matrix extensions (IME, AME) not yet usable through LLVM intrinsics |
| Vulkan-class GPU on a RISC-V SoC | Imagination BXM-4-64 on the K3 | shared LPDDR | ~1 TOPS class | SPIR-V through Vulkan or OpenCL |
| decode-oriented accelerators, pattern only | d-Matrix Corsair, Cerebras WSE-3 | SRAM plus DRAM | decode-bound | not targets; they establish prefill on one device class and decode on another |

## Host CPUs

| part | cores | memory | I/O |
|---|---|---|---|
| AMD EPYC Turin (9005) | up to 192 Zen 5c | 12-channel DDR5-6000, 614 GB/s | 128 PCIe Gen5 lanes, CXL 1.1; eight GPUs per socket |
| AMD EPYC Venice (2026, Zen 6) | up to 256 | 1.6 TB/s; twice Turin's CPU-to-GPU bandwidth | the Helios host, one per four MI455X |
| SpacemiT V100 | 46 RISC-V cores | DDR | a RISC-V host for RISC-V accelerators |

What runs on the host today, per the inventory: request ingress,
tokenization, detokenization, scheduling, sampling post-processing, KV block
management, logging. The host is also the first offload target of the
planner.

## DPUs and NICs

| part | compute | network | what it can own |
|---|---|---|---|
| AMD Pensando Salina 400 DPU | 16 Arm Neoverse N1 plus 232 P4 packet engines | 400G, PCIe Gen5 | inline network processing, storage offload, telemetry; the Arm cores are general compute, the P4 engines are not |
| AMD Pensando Pollara 400 AI NIC | | 400G, Ultra Ethernet and RoCEv2 | scale-out RDMA for GPUs |
| AMD Pensando Vulcano AI NIC (Helios) | | 800G, three per GPU, 2.4 Tb/s per GPU, UEC | scale-out RDMA; a NIC, not a general DPU |
| Marvell OCTEON 10 | 8 to 36 Arm Neoverse N2 (up to 128) | 400G class | general DPU compute; a merchant option on AMD hosts |
| Broadcom Thor Ultra | | 800G, first UEC-compliant 800G NIC | packet multipathing, out-of-order placement, hardware SACK retransmit |
| Intel IPU E2200 | | 800G | hyperscale infrastructure offload |

## Interconnects

| fabric | bandwidth | domain |
|---|---|---|
| AMD Infinity Fabric (XGMI) | ~1 TB/s class aggregate per GPU across an 8-GPU node | node of 8 (MI300X, MI355X) |
| UALink 1.0 (2025-04), 2.0 (2026-04) | 200 Gb/s per lane | rack; open, with AMD, Broadcom, Intel, Meta, Microsoft among the members |
| UALink over Ethernet in Helios | 260 TB/s bidirectional per rack of 72 MI455X | rack |
| PCIe Gen5 x16, Gen6 x16 | 128 GB/s, 256 GB/s | host to device |
| Broadcom Tomahawk 6, co-packaged optics | 102.4 Tb/s per chip | scale-out Ethernet, UEC fabrics |

On today's AMD nodes the collective path the inventory describes is an IPC
all-reduce for small messages and RCCL over XGMI otherwise; on Helios, RCCL
over UALoE. No in-network reduction exists on the open Ethernet side yet.

## Memory tiers beyond HBM

| tier | capacity | bandwidth | latency | role |
|---|---|---|---|---|
| HBM on the accelerator | 192 to 432 GB | 5.3 to 8 TB/s today, HBM4 next | ~500 ns | weights, hot KV, activations |
| CPU DRAM | 1 to 6 TB per socket | 0.6 to 1.6 TB/s | ~100 ns | warm KV, adapter cache, weight streaming source |
| CXL memory, Type 3 expanders and pooled racks | 512 GB per device; appliances to 11 TB | 50 to 64 GB/s per device | 150 to 400 ns | a KV tier between DRAM and NVMe |
| local NVMe | tens of TB | 7 to 14 GB/s per drive | ~13 µs | cold KV, prefix stores |
| remote storage over RDMA | PB | hundreds of GB/s aggregate | tens of µs | shared KV stores; the inventory cites a 9x TTFT improvement reported by VAST and AMD with KV offload |

## Rack-scale systems

| system | accelerators | hosts | scale-up | scale-out |
|---|---|---|---|---|
| AMD MI300X / MI355X node | 8 GPUs | 2 EPYC | Infinity Fabric | Pollara 400 |
| AMD Helios (announced) | 72 MI455X | 18 EPYC Venice | UALink over Ethernet, 260 TB/s | Pensando Vulcano, 43 TB/s |
| Tenstorrent Galaxy Blackhole | 32 Blackhole | RISC-V on chip | Ethernet mesh | Ethernet |
| SpacemiT K3 board | 1 SoC: X100 cores, BXM GPU, NPU | the SoC | | edge, 30B-parameter class on device |

## What is not on the bench

OI-003 records that no RISC-V accelerator is available and the lowering
paths are chosen from documentation, with the resolution to acquire a
Tenstorrent p150 and a SpacemiT K3 board before R3. OI-008 records that
autotuning and the performance baselines need a gfx950 host with vLLM and
AITER. OI-010 defers the DPU agent until a DPU is on the bench.
