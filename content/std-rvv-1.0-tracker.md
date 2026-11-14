---
title: "RISC-V V 1.0 tracker"
navtitle: Tracker
section: Standards
group: "Compiler and code generation / RISC-V V 1.0"
order: 53
summary: The Release 3 work for the RISC-V vector lowering; no open gap, since nothing is due before R3.
---

# RISC-V V 1.0 tracker

From the [audit](std-rvv-1.0-audit.html). No gap is open: every item is
Release 3 work. The rows below list that work so it stays visible; they are
not counted as gaps. No GitHub issue covers them yet
(`gh issue list -R itej89/rustinfer --state all`, 2026-11-13).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| RVV-1 | No `riscv-vector` lowering: no vector-length-agnostic tile mapping, `vsetvli` stripmining or `v0` masking (RV-R1 to RV-R9) | §2, §3.4, §5.3, §6, §6.3, §8, §18.3 | Later release R3 | RI-RV-004, RI-KC-004, through the LLVM RISC-V back end ([LLVM-4](std-llvm-tracker.html)); bring-up order RI-RV-003 |
| RVV-2 | bf16 and fp16 vector arithmetic are not in V 1.0, which has vector FP for EEW 32 and 64 only | §18.3 | Later release R3 | The R1 generator set is bf16 (RI-KC-005). The SRS may want to name the bf16 vector extensions as a reference for RI-RV-004, or state that RVV kernels compute in f32 |
| RVV-3 | Unordered FP reductions are implementation-dependent (RV-R10) | §14.3.2 | Later release R3 | Decide between `vfredosum` and a tolerance in RI-KC-007 that covers `vfredusum` across VLENs |
