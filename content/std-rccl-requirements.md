---
title: "RCCL ROCm 7.2 requirements"
navtitle: Requirements
section: Standards
group: "Runtime / RCCL ROCm 7.2"
order: 21
summary: What the RCCL library specification requires of a caller of all-reduce, all-gather, reduce-scatter and all-to-all, and of the communicator they run on.
---

# RCCL ROCm 7.2 requirements

Source: `specs/runtime/rccl-7.2.4-library-specification.html` (AMD, *RCCL library
specification*, RCCL 2.27.7 documentation for ROCm 7.2.4). The document is an API
reference without numbered clauses; items are cited by its section and function.
Scope from SRS §1.4: all-reduce, all-gather, reduce-scatter, all-to-all. Every item
is needed from R2 (RI-ROC-006, RI-DIST-001); none in R1.

| id | item (section, function) | what the specification says |
|---|---|---|
| C1 | Communicator functions: `ncclGetUniqueId` | "should be called once by a single rank and the ID should be distributed to all ranks in the communicator before using it as a parameter for ncclCommInitRank." |
| C2 | Communicator functions: `ncclCommInitRank` | "Rank must be between 0 and nranks-1 and unique within a communicator clique. Each rank is associated to a CUDA device, which has to be set before calling ncclCommInitRank." It "implicitly syncronizes with other ranks, so it must be called by different threads/processes or use ncclGroupStart/ncclGroupEnd." |
| C3 | Collective communication: `ncclAllReduce` | "Reduces data arrays of length count in sendbuff using op operation, and leaves identical copies of result on each recvbuff. In-place operation will happen if sendbuff == recvbuff." Runs on the HIP stream given. |
| C4 | Collective communication: `ncclAllGather` | "Each device gathers sendcount values from other GPUs into recvbuff, receiving data from rank i at offset i*sendcount"; "recvbuff should have a size of at least nranks*sendcount elements." |
| C5 | Collective communication: `ncclReduceScatter` | "recvbuff on rank i will contain the i-th block of the result"; "sendbuff should have a size of at least nranks*recvcount elements." |
| C6 | Collective communication: `ncclAllToAll` | "Each block for sending/receiving has count elements, which means that recvbuff and sendbuff should have a size of nranks*count elements. In-place operation is NOT supported. It is the user's responsibility to ensure that sendbuff and recvbuff are distinct." |
| C7 | Result codes and `ncclGetErrorString` | Every call returns an `ncclResult_t`; `ncclGetErrorString` "Returns a human-readable string describing the given result code." |

Data types the collectives take include `ncclBfloat16`, `ncclFloat8e4m3` and
`ncclFloat8e5m2` (section *Data types*); which ones rustinfer passes is set with the
R2 design. Group semantics (`ncclGroupStart`, `ncclGroupEnd`) apply when one thread
drives several ranks; RI-DIST-001 runs one process per rank, so only C2's
cross-process form is needed. Point-to-point, broadcast, gather and scatter are out of
scope.
