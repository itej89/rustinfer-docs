---
title: "AMD Instinct system acceptance (accessed 2026-11-15) requirements"
navtitle: Requirements
section: Standards
group: "Runtime / AMD Instinct system acceptance (accessed 2026-11-15)"
order: 29
summary: The host settings AMD's Instinct acceptance guides name and how they are read back, NUMA balancing and the IOMMU mode first, with the other settings the guides list that RI-OBS-005 does not name.
---

# AMD Instinct system acceptance requirements

Sources, as accessed 2026-11-15, in `specs/observability/`: *OS Tuning*
(`amd-acc-os-tuning.txt`, **[OS]**), *Kernel Parameters*
(`amd-acc-kernel-parameters.txt`, **[KP]**), the MI350X page
(`amd-acc-mi350x.txt`, **[MI350X]**) and *Interpreting GPU fabric topology*
(`amd-acc-xgmi-topology.txt`, **[XGMI]**), cited by section and line. The
requirement on rustinfer is RI-OBS-005's: record what the host is set to,
read only.

## The two settings RI-OBS-005 names

| id | requirement | source |
|---|---|---|
| ACC-R1 | NUMA balancing: the guides set `numa_balancing=disable` on the kernel command line ("disables NUMA page migration which can cause overhead during GPU operations"; *Kernel Parameters* lists it as "Optional") and read it back from `/proc/sys/kernel/numa_balancing`, "0: Disabled (recommended)", "1: Enabled"; "Kernel updates can re-enable NUMA balancing", so the value is read at run time, not assumed from the command line | [OS] *NUMA Configuration*, lines 125 to 162; [KP] *Required Kernel Parameters*, lines 154 to 157 |
| ACC-R2 | IOMMU mode: `iommu=pt` "Enables IOMMU pass-through mode, which allows the adapter to bypass DMA translation to memory, thereby improving performance" (with `intel_iommu=on` on Intel hosts); verified from the kernel command line (`cat /proc/cmdline`) and `dmesg | grep iommu`; on hosts of 256 or more logical CPUs the IOMMU must be enabled in the BIOS, or the kernel "falls back to the Advanced Programmable Interrupt Controller (APIC), which can only enumerate a maximum of 255 logical cores" | [KP] lines 142 to 151; [OS] *IOMMU Configuration for Large Systems*, lines 190 to 216, *Common Commands for Verification* |
| ACC-R3 | Read only: the guides change these with GRUB, `sysctl` and `cpupower` as root; rustinfer reads the files and changes nothing | SRS RI-OBS-005 ("rustinfer SHALL NOT change any of them"); [OS] lines 99 to 160 |

## Named by the guides, not by RI-OBS-005

RI-OBS-005 says "the host settings AMD's acceptance guides name (NUMA
balancing, IOMMU mode)". The guides name more; whether the parenthesis is
the whole list or two examples is not settled by the SRS. Listed so the
owner can decide; the audit does not count them as gaps.

- CPU C-states: disable C2 with `cpupower idle-set -d 2`, or
  `processor.max_cstate=0` on the command line ([OS] *C-states
  Configuration*, lines 86 to 123; *CPU Power Management*, lines 218 to 223).
- The other required kernel parameters, `pci=realloc=off` and `pci=bfsort`,
  and the optional `modprobe.blacklist=amdgpu` ([KP] lines 121 to 170;
  [MI350X] line 168, the acceptance checklist's "Pass: Shows all required
  params").
- The environment variables `HIP_FORCE_DEV_KERNARG=1` and
  `HSA_OVERRIDE_CPU_AFFINITY_DEBUG=0` ([OS] *Environment Variables*, lines
  168 to 188); the first is one of RI-ROC-015's 13, the second is not (see
  [HIP-ENV](std-hip-env-requirements.html)).
- BIOS settings (IOMMU, PCIe, xGMI, DF C-states), not readable from Linux in
  general ([MI350X] line 162; `amd-acc-bios-settings.txt`).
- The xGMI topology, `amd-smi topology` hops and link types ([XGMI]), which
  belongs to the planner's device fields (RI-PLN-001, #92) rather than a
  record of host settings.
