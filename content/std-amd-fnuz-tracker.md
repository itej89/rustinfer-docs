---
title: "AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025) tracker"
navtitle: Tracker
section: Standards
group: "Number formats / AMD FP8 FNUZ (CDNA3 ISA, 5 August 2025)"
order: 33
summary: Gaps between rustinfer's FP8 E4M3 FNUZ handling and the CDNA3 ISA guide.
---

# AMD FP8 FNUZ tracker

Gaps found by the [audit](std-amd-fnuz-audit.html).

| id | gap | required by | status | notes |
|---|---|---|---|---|
| FNUZ-1 | The Kernel IR `max` identity for `f8E4M3FNUZ`, 0xFF (−240), has no test | ISA §7.2 Table 30 (max 240) | Open | Test gap only; the value is right. Assert it in a kc test against `fp8_to_f32(0xFF, E4m3Fnuz)` or a literal −240. OFP8-2 records the same for 0xFE |
| FNUZ-2 | The R1 gfx942 users of FNUZ are not on `origin/main`: the FNUZ fp8 MFMA and fp8 KV storage | ISA §7.2 Table 30 for every value they read or write; SRS RI-KC-003, RI-KVC-008 | In PR #44 (MFMA, [#8](https://github.com/itej89/rustinfer/issues/8)), In PR #48 (KV, CPU reference, [#37](https://github.com/itej89/rustinfer/issues/37)); Open ([#38](https://github.com/itej89/rustinfer/issues/38), GPU KV kernels) | The cache-write kernel must saturate like the CPU reference (FP16_OVFL = 1 or a clamp to ±240) to meet RI-KVC-008's bit-exact acceptance; see the audit's conversion note |
