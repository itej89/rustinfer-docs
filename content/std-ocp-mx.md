---
title: "OCP MX v1.1.0"
navtitle: Overview
section: Standards
group: "Number formats / OCP MX v1.1.0"
order: 40
summary: MXFP4 (E2M1 elements, UE8M0 scales, blocks of 32) and the §6.3 conversion with Equation 4, as the Model IR and the CPU reference oracle implement them.
---

# OCP MX v1.1.0

**Scope (SRS §1.4, OCP-MX):** MXFP4 only: E2M1 elements, UE8M0 scales, blocks
of 32, the section 6.3 conversion (Equation 4). The requirements that cite it
are RI-MIR-003 (`fp4x2` holds E2M1 values; `ue8m0` is the UE8M0 scale),
RI-MIR-011 (the `mx` encoding: blocks of 32 sharing one `ue8m0` scale) and
RI-MIR-012 (conversion per §6.3, Equation 4, with the CPU reference as the
oracle). RI-KC-003 and RI-KVC-008 apply RI-MIR-012 in kernels.

**Implementation:**

- Model IR: the dtypes `fp4x2` and `ue8m0` (`crates/rustinfer-mir/src/dtype.rs:30-39`,
  storage `:123-152`) and the `mx` encoding check: `fp4x2` data, block size
  32, `ue8m0` scales, an axis that is a static multiple of 32
  (`crates/rustinfer-mir/src/mx.rs:40-86`); the block size is
  `MX_BLOCK_SIZE` (`crates/rustinfer-core/src/config/constants.rs:167`).
- CPU reference, `crates/rustinfer-target/src/reference/mx.rs`: E2M1 decode
  and encode (`:188-221`), UE8M0 decode (`:223-231`), the block conversion of
  §6.3 with Equation 4 (`:233-278`), dequantization (`:297-303`), `fp4x2`
  packing (`:305-339`), tensor quantization and dequantization along an axis
  (`:423-484`) and the `mx` matmul reference (`:486-507`). It also converts with
  E4M3 elements (MXFP8), outside the scope.
- MXFP4 KV storage, CPU reference (PR #48, issue #37): the cache write
  quantizes with `mx_quantize_block` (`crates/rustinfer-target/src/reference/kv.rs:287-298`).
- Pending: build-time quantization (issue #36), checkpoint import (PR #49,
  issue #35), GPU KV kernels, in-kernel dequantization and `--activations`
  quantization on gfx950 and gfx942 (issue #38).

**Conformance:** mandatory from **R1**.

**Source:** `specs/number-formats/ocp-mx-v1.1.0.pdf`, *OCP MicroXcaling (MX)
Specification, Version 1.1*, October 9, 2026, Open Compute Project,
<https://www.opencompute.org/wp-content/uploads/2026/10/OCP_MicroXcaling_Spec_v1.1.0.pdf>.
Downloaded 2026-11-13. Version 1.1 renames E8M0 to UE8M0 and updates the
§6.3 conversion.

| | |
|---|---|
| Pages | [requirements](std-ocp-mx-requirements.html) · [audit](std-ocp-mx-audit.html) · [tracker](std-ocp-mx-tracker.html) |
| Conformance | mandatory R1 (RI-MIR-003, RI-MIR-011, RI-MIR-012) |
| Audited | 2026-11-13, by reading `origin/main` `ccf02b3`, its tests and the golden file against the specification text; re-audited at `b99720a` after PR #48 |
| Result | the Model IR and the CPU reference oracle conform on every in-scope item, checked by an independent integer-only golden generator; the MXFP4 KV CPU reference applies it (PR #48); the build, GPU KV and kernel paths are not on `origin/main` yet |
| Open gaps | 3 |
