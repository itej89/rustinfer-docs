---
title: "OCP MX v1.1.0 tracker"
navtitle: Tracker
section: Standards
group: "Number formats / OCP MX v1.1.0"
order: 43
summary: Gaps between rustinfer's MXFP4 implementation and OCP MX v1.1.
---

# OCP MX v1.1.0 tracker

Gaps found by the [audit](std-ocp-mx-audit.html). None is a wrong value: the
CPU reference conforms. Each is an R1 path that must apply the reference's
rule and is not on `origin/main` yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| MX-1 | Build-time MXFP4 quantization (`build --precision mxfp4`) is not implemented | §6.3, Equation 4; SRS RI-GC-004, RI-CLI-002, RI-MIR-012 | Open ([#36](https://github.com/itej89/rustinfer/issues/36)) | Must call the CPU reference conversion or match it bit for bit. Landing it, with #38, turns the `Groundwork for RI-MIR-012` tags into `Verifies` |
| MX-2 | MXFP4 KV storage: the cache write computing each block's UE8M0 scale | §6.3; SRS RI-KVC-008, RI-MIR-012 | In PR #48 ([#37](https://github.com/itej89/rustinfer/issues/37)) for the CPU reference; Open ([#38](https://github.com/itej89/rustinfer/issues/38)) for the GPU kernels | The PR's CPU path calls `mx_quantize_block`; its acceptance is bit-exact equality with the reference conversion |
| MX-3 | In-kernel MXFP4 dequantization on gfx950 and gfx942, and in-kernel `mxfp4` activation quantization on gfx950 | §5.1 (X·P_i), §6.3; SRS RI-KC-003, RI-MIR-011, RI-MIR-012 | Open ([#38](https://github.com/itej89/rustinfer/issues/38)), blocked by [#8](https://github.com/itej89/rustinfer/issues/8) (PR #44) | gfx950 uses the `v_cvt_scalef32_pk_bf16_fp4` conversions and the scaled MFMA; gfx942 dequantizes by integer and bf16 arithmetic. Both are validated against the CPU reference |
