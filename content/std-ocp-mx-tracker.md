---
title: "OCP MX v1.1.0 tracker"
navtitle: Tracker
section: Standards
group: "Number formats / OCP MX v1.1.0"
order: 43
summary: Gaps between rustinfer's MXFP4 implementation and OCP MX v1.1.
---

# OCP MX v1.1.0 tracker

Gaps found by the [audit](std-ocp-mx-audit.html) of 2026-11-13, re-audited
against `origin/main` `b99720a` the same day after PR #48 merged, and on
2026-11-14 against `8c7d47e` after PRs #55, #53 and #49. PR #49 (checkpoint
MXFP4 import, checkpoint fp8 KV scales) closes no MX gap and opens none: it
imports stored MXFP4 bytes and does not convert, and its KV scales are fp8
scales, not MX. None is a
wrong value: the CPU reference conforms. Each is an R1 path that must apply
the reference's rule and is not fully on `origin/main` yet.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| MX-1 | Build-time MXFP4 quantization (`build --precision mxfp4`) is not implemented | §6.3, Equation 4; SRS RI-GC-004, RI-CLI-002, RI-MIR-012 | Open ([#36](https://github.com/itej89/rustinfer/issues/36)) | Must call the CPU reference conversion or match it bit for bit. Landing it, with #38, turns the `Groundwork for RI-MIR-012` tags into `Verifies` |
| MX-2 | MXFP4 KV storage: the cache write computing each block's UE8M0 scale | §6.3; SRS RI-KVC-008, RI-MIR-012 | Open ([#38](https://github.com/itej89/rustinfer/issues/38)) for the GPU kernels; CPU reference merged 2026-11-13 e218b8a | The CPU reference landed with PR #48 (issue #37, merge `e218b8a`): the cache write quantizes each 32-value block along `head_dim` with `mx_quantize_block` and E2M1 elements (`crates/rustinfer-target/src/reference/kv.rs:287-298`), and `test_cached_k_and_v_equal_the_oracle_conversion_bit_exactly` (`crates/rustinfer-target/tests/kv.rs:212`, `Groundwork for RI-KVC-008, RI-MIR-012`) checks packed values and UE8M0 scales bit for bit; the Model IR refuses an MXFP4 KV group whose `head_dim` is not a multiple of 32 (`crates/rustinfer-mir/src/kv.rs:147-150`, `crates/rustinfer-mir/tests/kv_dtypes.rs:122`). Open: the GPU cache-write kernels (#38), which must match it bit for bit |
| MX-3 | In-kernel MXFP4 dequantization on gfx950 and gfx942, and in-kernel `mxfp4` activation quantization on gfx950 | §5.1 (X·P_i), §6.3; SRS RI-KC-003, RI-MIR-011, RI-MIR-012 | Open ([#38](https://github.com/itej89/rustinfer/issues/38)), blocked by [#8](https://github.com/itej89/rustinfer/issues/8) (PR #44) | gfx950 uses the `v_cvt_scalef32_pk_bf16_fp4` conversions and the scaled MFMA; gfx942 dequantizes by integer and bf16 arithmetic. Both are validated against the CPU reference |
