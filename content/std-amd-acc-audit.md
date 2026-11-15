---
title: "AMD Instinct system acceptance (accessed 2026-11-15) audit"
navtitle: Audit
section: Standards
group: "Runtime / AMD Instinct system acceptance (accessed 2026-11-15)"
order: 30
summary: The 2026-11-15 audit at main 5a6db49 of rustinfer's tune and GPU test records against the host settings of AMD's Instinct acceptance guides; neither NUMA balancing nor the IOMMU mode is read or recorded (#97), and nothing changes them.
---

# AMD Instinct system acceptance audit

**Audit of 2026-11-15**, against the [requirements](std-amd-acc-requirements.html),
on `main` `5a6db49` (PR #74 merged over SRS v0.5, PR #80 at `4ee01b6`). First
audit.

**Method.** Read the guides' *OS Tuning*, *Kernel Parameters*, *BIOS
Settings*, *Interpreting GPU fabric topology*, MI300X and MI350X pages as
served on 2026-11-15. Read on `5a6db49`: `crates/rustinfer-cli/src/`,
`crates/rustinfer-core/src/manifest.rs`, `.github/ISSUE_TEMPLATE/gpu-test.md`
and `docs/gpu-testing.md`; searched every crate, script and workflow for
`numa_balancing`, `/proc/sys`, `/proc/cmdline`, `iommu`, `cpupower`,
`max_cstate` and `sysctl` (none). Read the plan of #97 and the diff of the
open PR #68. No tests were run.

| id | requirement | result | evidence |
|---|---|---|---|
| ACC-R1 | NUMA balancing read from `/proc/sys/kernel/numa_balancing` and recorded | **missing** (ACC-1) | Not read anywhere. There is no record to hold it: `rustinfer tune` is `NotImplemented` (`crates/rustinfer-cli/src/commands.rs:100-108`), the version manifest holds no host setting beyond `host_triple` (`crates/rustinfer-core/src/manifest.rs:42-61`), and the GPU test template asks only for `rocminfo` and `rocm-smi --showproductname` (`.github/ISSUE_TEMPLATE/gpu-test.md:42-48`) |
| ACC-R2 | IOMMU mode read from the kernel command line and recorded | **missing** (ACC-1) | As ACC-R1; `/proc/cmdline` is not read |
| ACC-R3 | Read only | **conforms** | No code path writes a `/proc` or `/sys` file, runs `sysctl`, `cpupower` or `grubby`, or needs root; nothing tests the rule yet (RI-OBS-005 is untagged) |

**What "IOMMU mode" means to a reader.** The guides check the mode on the
kernel command line (`iommu=pt`) and in the kernel log; neither says what an
unprivileged process should read when the parameter is absent (the kernel's
default then depends on the build and the BIOS). A record that holds the
command line's `iommu=` and `intel_iommu=` values, or says they are absent,
is what the guides support; anything more is **not verified** from a primary
source here.

**Observations, not gaps.** The guides also name C-states, `pci=realloc=off`,
`pci=bfsort`, BIOS settings and two environment variables (see the
[requirements](std-amd-acc-requirements.html)); RI-OBS-005 names only NUMA
balancing and the IOMMU mode. Whether the others belong in the record is an
SRS question for the owner.

## Result

Neither host setting is read or recorded on `5a6db49`, and no record format
exists for them; nothing changes them. **Missing.** ACC-1 is an open R1 gap,
planned in #97; ACC-2, the same fields in `bench` records, is R2. Gaps are on
the [tracker](std-amd-acc-tracker.html).
