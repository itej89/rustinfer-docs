---
title: "RCCL ROCm 7.2 tracker"
navtitle: Tracker
section: Standards
group: "Runtime / RCCL ROCm 7.2"
order: 23
summary: The R2 work to use RCCL for rustinfer's collectives; no issue covers it yet.
---

# RCCL ROCm 7.2 tracker

From the [audit](std-rccl-audit.html) of 2026-11-13. Every row is R2 work; no GitHub
issue covers RCCL yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| RCCL-1 | No RCCL binding and no communicator | Communicator functions: `ncclGetUniqueId`, `ncclCommInitRank` | Later release R2 | RI-ROC-006, RI-DIST-001. Load from the system library path only (RI-SEC-001). Depends on HIP-1 |
| RCCL-2 | No all-reduce | `ncclAllReduce` | Later release R2 | RI-ROC-006; the own small-message all-reduce is R3 |
| RCCL-3 | No all-gather | `ncclAllGather` | Later release R2 | RI-ROC-006 |
| RCCL-4 | No reduce-scatter | `ncclReduceScatter` | Later release R2 | RI-ROC-006 |
| RCCL-5 | No all-to-all | `ncclAllToAll` | Later release R2 | RI-ROC-006; send and receive buffers must be distinct |
| RCCL-6 | RCCL result codes not mapped to typed errors | Result codes, `ncclGetErrorString` | Later release R2 | Same shape as RI-ROC-002 for HIP |
