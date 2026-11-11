---
title: The topology planner
navtitle: Topology planner
section: Runtime
order: 3
summary: The pass that places weights, KV tiers, phases and serving functions across GPUs, host CPUs, DPUs, DRAM, CXL and NVMe; its interfaces are Release 1, its implementation Release 2.
---

# The topology planner

Read from SRS §3.2.6 (`RI-PLN`), §2.1, ADR-006 and
`docs/planning/datacenter-device-inventory.md` §9 at commit `082df51`. The
`rustinfer-planner` crate is an error type; issue #15 implements the R1
interfaces (the types and a single-device planner). The owner's decision,
recorded in the SRS changelog, is interfaces in Release 1 and implementation
in Release 2, so the R1 types are shaped by the R2 job.

## The job

Goal 5 of the SRS: a planner that places weights, KV tiers, phases and
serving-stack functions across GPUs, host CPUs, DPUs, DRAM, CXL and NVMe
from a discovered topology. In the Apple analogy of §2.1 it is Core ML's
scheduler across heterogeneous units. The Model IR gives it somewhere to
write: every tensor carries a placement slot (memory tier) and every node a
device slot, empty after the frontend and filled by the planner (RI-MIR-005).

## The topology model (R1)

RI-PLN-001 names what the model describes, serialisable to and from JSON;
the device inventory's §9 is the longer form.

| element | attributes |
|---|---|
| device | architecture id; compute kind (simt, vector, mesh, scalar cores, sram-decode); matrix formats; phase affinity (prefill, decode, both); local memory tier; graph capture; whether rustinfer generates code for it or only routes around it |
| memory tier | capacity; read and write bandwidth; latency; sharing scope (device, socket, node, rack, cluster); the set of units that reach it and by what mechanism (direct, RDMA, peer-to-peer, CXL, DPU-mediated) |
| link | endpoints; bandwidth; latency; adjacency pattern (crossbar, ring, mesh, PCIe tree); hardware collective support |
| offload engine | a device that can run serving-stack functions (DPU cores, a persistent GPU kernel) and which functions: ingress, tokenization, streaming, KV eviction, storage I/O |

The artifact reserves `topology` and `placement` sections from R1, empty at
build unless pinned (RI-PLN-005: "format stability").

## Discovery and placement (R2 and beyond)

Discovery populates the model from the node: HIP devices and peer access,
PCIe and NUMA topology, DRAM, CXL devices, NVMe devices, RDMA-capable NICs,
DPUs; what cannot be probed is absent, never guessed (RI-PLN-002). The
planner then fills the slots from a cost model and explains each decision in
the placement section (RI-PLN-003):

| placement | release |
|---|---|
| weight residency per tensor; KV tier policy per layer; prefill and decode device sets; serving-stack function placement; collective-to-link mapping; transfer path per cross-device edge, over GPU, host CPU, DRAM, NVMe and RDMA | R2 |
| CXL tiers; expert placement | R3 |
| serving functions on a DPU with general-purpose cores, running a rustinfer agent built for that ISA, with tokens delivered to device memory by RDMA | R4 (RI-PLN-006; the ISA and deployment are open issue OI-010) |

Placement is computed at load, cached beside the artifact keyed by topology
hash, and pinnable; a pinned placement is refused on a differing topology
(RI-PLN-004). The unit of placement is a node or a rack; the inventory says
the cluster layer above, a cache-aware router, decides which rack.

## What the planner may see

The devices, in the AMD and RISC-V scope, are on [hardware](hardware.html).
The pattern the R4 row refers to is the one the inventory cites from the
Blink paper: the NIC does ingress, tokenization and streaming and writes
tokens into GPU memory by RDMA, a persistent GPU kernel does batching,
scheduling and KV management, and the host CPU is off the request path. On
AMD the general-purpose cores for that are a Pensando Salina's Arm cores or
a merchant DPU; the Vulcano and Pollara parts are NICs.
