---
title: "HIP and ROCm environment variables 7.2.4 audit"
navtitle: Audit
section: Standards
group: "Runtime / HIP and ROCm environment variables 7.2.4"
order: 20
summary: The 2026-11-15 audit at main 5a6db49 of the version manifest against RI-ROC-015 and the HIP and ROCm 7.2.4 references; none of the 13 variables is recorded or compared with its default (#95), and no code path sets one.
---

# HIP and ROCm environment variables audit

**Audit of 2026-11-15**, against the [requirements](std-hip-env-requirements.html),
on `main` `5a6db49` (PR #74 merged over SRS v0.5, PR #80 at `4ee01b6`). First
audit.

**Method.** Read the HIP and ROCm 7.2.4 references for each of the 13
variables and, for the three they omit and for the runtime's own defaults,
the HIP flag table and ROCr's flag reader at `rocm-7.2.4`. Read on
`5a6db49`: `crates/rustinfer-core/src/manifest.rs`,
`crates/rustinfer-core/src/config/settings.rs`, `crates/rustinfer-cli/src/main.rs`,
`crates/rustinfer-target-rocm/src/lib.rs` and `src/ffi/symbols.rs`; searched
every crate, script and workflow for the 13 names, for `HSA_`, `HIP_`, `GPU_`,
`ROC_` and `AMD_SERIALIZE`, and for `env::set_var`, `remove_var` and
`Command::env` (none in product code). Read the plan of #95 and the diffs of
the open PRs #68, #73, #75, #76 and #77 (none touches the variables). No tests
were run.

| id | requirement | result | evidence |
|---|---|---|---|
| HENV-R1 to HENV-R13 | Each variable recorded, set or unset | **missing** (HENV-1) | The manifest is `fixed_entries` (software, `rustc`, `llvm_version`, `mlir_llvm_version`, `host_triple`) plus the dependency lines (`crates/rustinfer-core/src/manifest.rs:36-88`), the `hip_library` config line (`:109-136`) and the `hip_runtime` line logged at device open (`:103-105`, called from `crates/rustinfer-target-rocm/src/lib.rs:150`); it is logged once at startup (`crates/rustinfer-cli/src/main.rs:46-47`). No environment variable of the list is read anywhere: the only environment reads are `RUSTINFER_*` settings (`crates/rustinfer-core/src/config/settings.rs:128`) and the HIP library override (`crates/rustinfer-target-rocm/src/ffi/symbols.rs:141`) |
| HENV-R14 | Unset recorded as unset | **missing** (HENV-1) | As above |
| HENV-R15 | A non-default value logged at `warn` | **missing** (HENV-2) | No table of runtime defaults exists (`crates/rustinfer-core/src/config/constants.rs` holds none of them), so no comparison is made |
| HENV-R16 | rustinfer sets none | **conforms** | No `std::env::set_var`, `remove_var` or `Command::env` outside tests; the only calls are in `crates/rustinfer-target-rocm/tests/hip_override.rs:94`, `:111` and `:125`, which set and clear rustinfer's own `RUSTINFER_HIP_LIBRARY` for a test. No test asserts the rule yet (RI-ROC-015 is untagged) |

**The defaults to compare with.** Ten of the 13 have a default in the HIP or
ROCm reference; three (`HSA_FORCE_SDMA_SIZE`, `GPU_FORCE_BLIT_COPY_SIZE`,
`ROC_P2P_SDMA_SIZE`) have one only in the source (1048576 bytes, 16 KiB, 1024
KiB). For `HSA_ENABLE_SDMA`, `HSA_ENABLE_PEER_SDMA` and `HSA_XNACK` the
reference gives `1`, `1` and "None", but ROCr reads only `0` and `1` and keeps
"unset" as a third state (`rocm-7.2.4-rocr-flag.h:90-94`, `:210-215`), so a
`warn` that compared with the documented `1` would miss nothing but would
also treat an explicit `HSA_ENABLE_SDMA=1` as the default when the runtime
does not. The comparison #95 writes should take "unset" as the default of
those three and cite the flag reader. **Not verified:** whether
`SDMA_DEFAULT` and `SDMA_ENABLE` behave differently on gfx942 or gfx950 (the
flag reader only records the state; its users were not read).

**Observations, not gaps.** `HIP_LAUNCH_BLOCKING` serialises launches like
`AMD_SERIALIZE_KERNEL=2`, and AMD's acceptance guide calls
`HSA_OVERRIDE_CPU_AFFINITY_DEBUG` critical; neither is in RI-ROC-015's list.
Recording them would be an SRS change, not a fix here.

## Result

The version manifest records none of RI-ROC-015's variables and compares none
with a default; the rule that rustinfer sets none of them holds. **Missing.**
Both gaps are planned in #95 (the ROCm target reads and records them), with
the print on every subcommand's CLI path in #14. Gaps are on the
[tracker](std-hip-env-tracker.html).
