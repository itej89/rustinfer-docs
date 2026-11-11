---
title: Hardware
section: Hardware
order: 1
summary: The targets the workspace registers and the AMD and RISC-V device landscape the planner must describe; accelerators, host CPUs, DPUs and NICs, interconnects, memory tiers and rack systems, with vendor figures as of 2026-11.
---

# Hardware

Read from SRS §2.4, §3.2.8 to §3.2.10, ADR-003 and
`docs/planning/datacenter-device-inventory.md` at commit `e91e002`. The
inventory's scope statement: AMD and the open-standard and RISC-V ecosystem
around it; NVIDIA parts are out of scope and appear only where a design
pattern is cited; figures are vendor numbers from the sources listed in the
file, as of 2026-11; "announced" marks parts not yet shipping. No device has
run rustinfer.

## Targets

| architecture string | hardware | backend crate | state at `e91e002` | release |
|---|---|---|---|---|
| `cpu` | any host | `rustinfer-target` | error type only; issue #5 | R1 (operators), R2 (collectives) |
| `gfx942` | MI300X, MI308X, MI325X | `rustinfer-target-rocm`, feature `rocm` | error type only; issue #12 | R1 |
| `gfx950` | MI350X, MI355X | same | same | R1; the reference architecture for autotuning and benchmarks (OI-008) |
| CDNA successor (`gfx1250` class, the inventory's guess) | MI450, MI455X in Helios | same, when available | — | not in a release tag |
| `spirv-vulkan` | Imagination BXM-4-64 on the SpacemiT K3 | `rustinfer-target-spirv-vulkan` | stub | R2 lowering, compile-tested |
| `riscv-vector` | SpacemiT K3 X100 cores (RVA23, RVV 1.0), SpacemiT V100 | `rustinfer-target-riscv-vector` | stub | R3 lowering, compile-tested; first device bring-up R3 |
| `riscv-mesh` | Tenstorrent Blackhole (120 Tensix cores plus 16 RISC-V Linux cores) | `rustinfer-target-riscv-mesh` | stub | R4 |

A stub compiles on every host, registers its string, and makes a build fail
at kernel selection with `catalog empty` (RI-RV-002). The ROCm runtime is
`libamdhip64` through one FFI module, with every HIP error carried as a
typed error, the architecture read from `gcnArchName` and a mismatched
artifact refused, code objects loaded only after the artifact check with
each kernel's LDS and register needs checked against the device before its
first launch (RI-ROC-001 to -004). ROCm 7.0 to 7.2 is the stated range.
RISC-V targets go through their vendor runtime: TT-Metal for Tensix, the host
OS for vector cores, Vulkan for SPIR-V devices.

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
