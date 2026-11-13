---
title: The topology planner
navtitle: Topology planner
section: Runtime
order: 4
summary: The pass that places weights, KV tiers, phases and serving functions across GPUs, host CPUs, DPUs, DRAM, CXL and NVMe; its interfaces are Release 1, its implementation Release 2.
---

# The topology planner

Read from SRS §3.2.6 (`RI-PLN`), §2.1, ADR-006,
`docs/planning/datacenter-device-inventory.md` §9, `crates/rustinfer-planner/src/`,
`docs/api/topology.md`, SRS v0.3 and ADR-009 at commit `04a2a26`. GitHub PR #20 merged into
`main` as d886a3c on 2026-11-12 and closed issue #15: the crate holds the
R1 interfaces, the topology model and the single-device planner, and
discovery and the cost-model planner answer `not_implemented` until
Release 2. That is the owner's decision, recorded in the SRS changelog:
interfaces in Release 1 and implementation in Release 2, so the R1 types are
shaped by the R2 job.

## The job

Goal 5 of the SRS: a planner that places weights, KV tiers, phases and
serving-stack functions across GPUs, host CPUs, DPUs, DRAM, CXL and NVMe
from a discovered topology. In the Apple analogy of §2.1 it is Core ML's
scheduler across heterogeneous units. The Model IR gives it somewhere to
write: every tensor carries a placement slot and every node a device slot,
empty after the frontend and filled by the planner (RI-MIR-005). Since PR #32
(2026-11-13, ADR-009) a placement slot is a device index, a memory-tier index
and an optional shard spec ([below](#placement-v2)); before it, the slot was
a memory-tier kind.

## The topology model (R1)

RI-PLN-001 names what the model describes, serialisable to and from JSON;
the device inventory's §9 is the longer form. The table is the code's
`Topology` in `topology.rs`, with the SRS's words where they differ.

| element | attributes in the code |
|---|---|
| `Device` | `name`; `architecture`, the target registry's string; `compute_kind` (`simt`, `vector`, `mesh`, `scalar_cores`, `sram_decode`); `matrix_formats`, Model IR dtypes; `phase_affinity` (`prefill`, `decode`, either, both or none); `local_tier`, an index into the memory tiers; `graph_capture`. The SRS also names whether rustinfer generates code for the device or only routes around it; the code does not carry that yet |
| `MemoryTierSpec` | `name`; `kind`, the Model IR placement tier (`hbm`, `dram`, `cxl`, `nvme`); `capacity_bytes`; `read_bandwidth_bytes_per_s` and `write_bandwidth_bytes_per_s`; `latency_ns`; `sharing_scope` (`device`, `socket`, `node`, `rack`, `cluster`); `reachable_from`, the devices that reach it each with a mechanism (`direct`, `peer_to_peer`, `rdma`, `cxl`, `dpu_mediated`) |
| `Link` | two distinct `endpoints`; `bandwidth_bytes_per_s`; `latency_ns`; `adjacency` (`point_to_point`, `switched`, `ring`, `mesh`; the SRS says crossbar, ring, mesh, PCIe tree); `hardware_collectives` |
| `OffloadEngine` | `name`; `device`; `functions` (`ingress`, `tokenization`, `streaming`, `kv_eviction`, `storage_io`) |

In the code a `Topology` goes to and from canonical JSON (sorted keys,
compact, exact integers) under `topology_version` 1, the only version the
reader accepts; the reader is bounded before parsing
(`TOPOLOGY_MAX_DOCUMENT_BYTES`) and every list by a `TOPOLOGY_MAX_*`
constant ([constants](ref-constants.html)); `validate` refuses a fault naming
the field by path (`devices[2].local_tier`), a duplicate name naming the
list, and an unknown, missing or mistyped field as `malformed`. An empty
topology is valid and is what an unpinned artifact carries. The artifact's
`topology` and `placement` sections exist in `rustinfer-artifact` since
Codeberg PR #21 and are empty unless pinned (RI-PLN-005: "format
stability"); the `build` that writes them is #11.

## Placement in the code

A `Placement` is a `Location` (device, tier, shard) per tensor name, a device index per node path
(`outer/part` for the part of a fused node), the `Strategy`
(`single_device` in R1, `null` for the empty section) and a list of
`Decision`s, each a subject, a choice and a reason in words (RI-PLN-003); it
serialises the same way under `placement_version` 2 (PR #32; version 1, a tier kind per tensor, is refused). `Placement::apply`
fills the Model IR's placement and device slots and refuses, naming the
function and the tensor or node, when the placement lacks an entry or names
one the document does not have; `Placement::check_filled` refuses a document
with any slot still empty (RI-MIR-005).

The `Planner` trait is two methods: `name`, the strategy recorded in the log
line, and `plan(document, profile, topology) -> Placement`, which fills
nothing itself. `SingleDevicePlanner::new(index)` (or `for_architecture`,
the first device with that string) puts every tensor on device `n` in tier
`devices[n].local_tier` with no shard, and every node on the device, and refuses with `capacity_exceeded`
naming the device, the tier, the required and the available bytes when the
footprint at the profile's `max` (the weights plus the largest function's
distinct inputs and outputs, each tensor once) exceeds the tier; KV blocks
are not in the footprint, the runtime sizes the pool (RI-KVC-003). `place`
is the one call the rest of R1 makes: validate the document, the profile and
the topology, plan, apply, check that no slot is empty; on a refusal the
document is left as it was. `CostModelPlanner::plan` and `discover()` exist
and answer `not_implemented` naming RI-PLN-003 and RI-PLN-002. Every type
is `Send + Sync`; the PR's tests share one planner and topology across four
threads.

## Placement v2

ADR-009 and SRS v0.3 (PR #28, 2026-11-12) amended the placement contract, and
GitHub PR #32 (merged as 3df8c1b on 2026-11-13, #27) put it in the code. A
tier kind cannot say which device's memory holds a tensor: on an eight-GPU
node every GPU has an `hbm` tier, and a two-socket host has two `dram`
tiers on different NUMA nodes. The topology already names each tier by
index, so the planner was throwing that away. Nor could a slot say that a
tensor is one shard of a tensor-parallel split. The change was made while
every shipped slot is empty, because the graph compiler (#10) and the
executor (#13) are about to start reading slots, and changing them later
would mean migrating every pinned artifact.

| | before PR #32 | in the code at `04a2a26` (RI-MIR-005, RI-PLN-003, RI-PLN-005) |
|---|---|---|
| tensor placement slot | a tier kind (`hbm`, `dram`, `cxl`, `nvme`) | `PlacementSlot.location`: `{"location": null}` or a `Location` of a device index, a memory-tier index and a shard: `null`, `replicated` or `split` (axis, count, index) |
| node device slot | a device index | a device index (unchanged) |
| Model IR version | `ir_version` 1 | `ir_version` 2 (`MODEL_IR_FORMAT_VERSION`, accepted `[1, 2]`); a version 1 document is read as version 2 only when every slot is empty (every frontend output); a filled version 1 slot is refused as `FilledLegacySlot` naming the function and the tensor or node, because a tier kind cannot be mapped to a tier index without a topology |
| `placement` section | a tier kind per tensor, `placement_version` 1 | the `Location` per tensor, `placement_version` 2 (accepted `[2]`); a pinned section is parsed and checked against the pinned topology at the CLI's artifact boundary by `check_pinned` (`error=invalid component=planner`) |
| single-device planner | every tensor in the device's local tier kind | device `n`, tier `devices[n].local_tier`, no shard: R1 behaviour unchanged |
| validation | a placement entry must name a tensor or node of the document | `Placement::check_against(&Topology)`, run by `place` and `check_pinned`: a device or tier index outside the topology is `OutsideTopology`, a tier the device cannot use is `UnreachableTier`, a shard index not below the count or an axis outside the rank is `InvalidPlacement`, each `invalid` and naming the entry (RI-SEC-002, RI-SEC-003) |

**The reachability rule.** The owner clarified RI-MIR-005 and ADR-009 on
2026-11-13: a tier index t is one device d can use when t is
`devices[d].local_tier` or d is listed in `memory_tiers[t].reachable_from`.
`Topology::reaches(device, tier)` implements it. With it checked, every
RI-MIR-005 test is tagged `Verifies`, and RI-MIR-005, RI-PLN-003 and
RI-PLN-005 count as implemented under the tag rule
([requirements](ref-requirements.html)); the R2 part of RI-MIR-005, shard
specs filled by a planner, is later.

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
(RI-PLN-004, specified in the SRS; load-path behaviour, not in the crate).
The unit of placement is a node or a rack; the inventory says the cluster
layer above, a cache-aware router, decides which rack.

## What the planner may see

The devices, in the AMD and RISC-V scope, are on [hardware](hardware.html).
The pattern the R4 row refers to is the one the inventory cites from the
Blink paper: the NIC does ingress, tokenization and streaming and writes
tokens into GPU memory by RDMA, a persistent GPU kernel does batching,
scheduling and KV management, and the host CPU is off the request path. On
AMD the general-purpose cores for that are a Pensando Salina's Arm cores or
a merchant DPU; the Vulcano and Pollara parts are NICs.
