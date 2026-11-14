---
title: Standards map
navtitle: Standards map
section: Standards
order: 1
summary: Every standard rustinfer must conform to, by area, with how far each one is met today, its open gaps and its four pages; then the other documents the SRS references.
---

# Standards map

rustinfer reads and writes formats it did not invent: safetensors shards, OCP
microscaling blocks, AMD code objects, JSON sections, later an OpenAI-shaped HTTP
API. SRS §1.4 marks each reference it names: **mandatory R<n>** when a requirement
can be met only by conforming to it, from release *n*; *process*, *informative* or
*internal* otherwise. This map shows the mandatory ones, by area. A standard is
never met as a whole: rustinfer conforms to **the parts in its scope**, the scope its
§1.4 row names, and each standard's requirements page lists those parts one by one.

Two separate things are shown for each standard. The colour is its **state**, from
its audit:

- **works**: every in-scope item conforms on `main`; open gaps, if any, are in the
  tests, not the behaviour;
- **partly works**: some in-scope items conform, others are missing or wait in an
  open pull request;
- **missing**: nothing in scope conforms on `main` yet;
- **later release**: the standard is mandatory only from a release after the
  current one, so nothing is due yet; the work is recorded on its tracker.

The **assessed** tag appears when the standard has an audit page, dated, that checks
the implementation item by item against the specification's own text, downloaded
into the site's `specs/` folder (not published). Where the specification is sold
and could not be read (IEEE 754, ISO 8601), the tag adds **secondary**: the
audit used the named public sources its requirements page lists instead.

Each standard has four pages: the **overview** (what it is, its scope and how far
rustinfer meets it), the **requirements** (what the specification asks, in scope),
the **audit** (each requirement against the code, with the evidence and its date)
and the **tracker** (the gaps). A gap is **open** when its status is *Open* or
*In PR #N*; a *Later release R<n>* gap is recorded but not counted as open; an
*Out of scope* gap, one the owner removed from the §1.4 scope (OCP OFP8's
non-saturating mode, PR #50), is kept for the record and counted nowhere. The
same counts feed the [issue tracker](issues.html#standards) and the
[progress](progress.html#standards) page.

<div class="std-legend" aria-hidden="true">
  <span class="std-key std-ok">works</span>
  <span class="std-key std-part">partly works</span>
  <span class="std-key std-gap">missing</span>
  <span class="std-key std-later">later release</span>
  <span class="std-tag">assessed</span>
</div>

<!-- begin generated map: scripts/reference/gen_standards.py from data/standards/*.json and the std-* pages; do not edit by hand -->
<div class="std-map" role="list" aria-label="Areas and the mandatory standards in each">

<section class="std-card" role="listitem">
  <h3 class="std-sys">Number formats</h3>
  <ul>
    <li class="std-ok"><span class="std-name"><a href="std-ieee-754.html">IEEE 754</a></span><span class="std-scope">754-2019</span><span class="std-scope">mandatory R1 · 0 open gaps</span><span class="std-pages"><a href="std-ieee-754.html">overview</a> · <a href="std-ieee-754-requirements.html">requirements</a> · <a href="std-ieee-754-audit.html">audit</a> · <a href="std-ieee-754-tracker.html">tracker</a></span><a class="std-tag" href="std-ieee-754-audit.html" title="audited 2026-11-13 against secondary sources: the specification is not freely available">assessed · secondary</a></li>
    <li class="std-part"><span class="std-name"><a href="std-ocp-ofp8.html">OCP OFP8</a></span><span class="std-scope">Revision 1.1</span><span class="std-scope">mandatory R1 · 1 open gap</span><span class="std-pages"><a href="std-ocp-ofp8.html">overview</a> · <a href="std-ocp-ofp8-requirements.html">requirements</a> · <a href="std-ocp-ofp8-audit.html">audit</a> · <a href="std-ocp-ofp8-tracker.html">tracker</a></span><a class="std-tag" href="std-ocp-ofp8-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-part"><span class="std-name"><a href="std-amd-fnuz.html">AMD FP8 FNUZ</a></span><span class="std-scope">CDNA3 ISA guide of 2025-08-05</span><span class="std-scope">mandatory R1 · 1 open gap</span><span class="std-pages"><a href="std-amd-fnuz.html">overview</a> · <a href="std-amd-fnuz-requirements.html">requirements</a> · <a href="std-amd-fnuz-audit.html">audit</a> · <a href="std-amd-fnuz-tracker.html">tracker</a></span><a class="std-tag" href="std-amd-fnuz-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-part"><span class="std-name"><a href="std-ocp-mx.html">OCP MX</a></span><span class="std-scope">v1.1.0</span><span class="std-scope">mandatory R1 · 3 open gaps</span><span class="std-pages"><a href="std-ocp-mx.html">overview</a> · <a href="std-ocp-mx-requirements.html">requirements</a> · <a href="std-ocp-mx-audit.html">audit</a> · <a href="std-ocp-mx-tracker.html">tracker</a></span><a class="std-tag" href="std-ocp-mx-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
  </ul>
</section>

<section class="std-card" role="listitem">
  <h3 class="std-sys">Model formats</h3>
  <ul>
    <li class="std-part"><span class="std-name"><a href="std-safetensors.html">safetensors</a></span><span class="std-scope">v0.8.0</span><span class="std-scope">mandatory R1 · 3 open gaps</span><span class="std-pages"><a href="std-safetensors.html">overview</a> · <a href="std-safetensors-requirements.html">requirements</a> · <a href="std-safetensors-audit.html">audit</a> · <a href="std-safetensors-tracker.html">tracker</a></span><a class="std-tag" href="std-safetensors-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-part"><span class="std-name"><a href="std-hf-config.html">Transformers config</a></span><span class="std-scope">v5.23.0</span><span class="std-scope">mandatory R1 · 3 open gaps, 1 later</span><span class="std-pages"><a href="std-hf-config.html">overview</a> · <a href="std-hf-config-requirements.html">requirements</a> · <a href="std-hf-config-audit.html">audit</a> · <a href="std-hf-config-tracker.html">tracker</a></span><a class="std-tag" href="std-hf-config-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-hf-tokenizer.html">Tokenizers</a></span><span class="std-scope">v0.23.3</span><span class="std-scope">mandatory R2 · 0 open gaps, 2 later</span><span class="std-pages"><a href="std-hf-tokenizer.html">overview</a> · <a href="std-hf-tokenizer-requirements.html">requirements</a> · <a href="std-hf-tokenizer-audit.html">audit</a> · <a href="std-hf-tokenizer-tracker.html">tracker</a></span><a class="std-tag" href="std-hf-tokenizer-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-gap"><span class="std-name"><a href="std-quark.html">AMD Quark MXFP4 export</a></span><span class="std-scope">as surveyed (313cb0b)</span><span class="std-scope">mandatory R1 · 3 open gaps</span><span class="std-pages"><a href="std-quark.html">overview</a> · <a href="std-quark-requirements.html">requirements</a> · <a href="std-quark-audit.html">audit</a> · <a href="std-quark-tracker.html">tracker</a></span><a class="std-tag" href="std-quark-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-gap"><span class="std-name"><a href="std-ct.html">compressed-tensors</a></span><span class="std-scope">0.13.0</span><span class="std-scope">mandatory R1 · 2 open gaps</span><span class="std-pages"><a href="std-ct.html">overview</a> · <a href="std-ct-requirements.html">requirements</a> · <a href="std-ct-audit.html">audit</a> · <a href="std-ct-tracker.html">tracker</a></span><a class="std-tag" href="std-ct-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-peft.html">PEFT</a></span><span class="std-scope">v0.21.3</span><span class="std-scope">mandatory R3 · 0 open gaps, 1 later</span><span class="std-pages"><a href="std-peft.html">overview</a> · <a href="std-peft-requirements.html">requirements</a> · <a href="std-peft-audit.html">audit</a> · <a href="std-peft-tracker.html">tracker</a></span><a class="std-tag" href="std-peft-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
  </ul>
</section>

<section class="std-card" role="listitem">
  <h3 class="std-sys">Compiler and code generation</h3>
  <ul>
    <li class="std-part"><span class="std-name"><a href="std-llvm.html">LLVM</a></span><span class="std-scope">23.1.x</span><span class="std-scope">mandatory R1 · 2 open gaps, 2 later</span><span class="std-pages"><a href="std-llvm.html">overview</a> · <a href="std-llvm-requirements.html">requirements</a> · <a href="std-llvm-audit.html">audit</a> · <a href="std-llvm-tracker.html">tracker</a></span><a class="std-tag" href="std-llvm-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-part"><span class="std-name"><a href="std-mlir.html">MLIR</a></span><span class="std-scope">LLVM 23 (23.1.x)</span><span class="std-scope">mandatory R1 · 3 open gaps, 1 later</span><span class="std-pages"><a href="std-mlir.html">overview</a> · <a href="std-mlir-requirements.html">requirements</a> · <a href="std-mlir-audit.html">audit</a> · <a href="std-mlir-tracker.html">tracker</a></span><a class="std-tag" href="std-mlir-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-gap"><span class="std-name"><a href="std-amdgpu-abi.html">AMDGPU code object V5 (AMDGPUUsage)</a></span><span class="std-scope">code object V5, LLVM 23.1.0 text</span><span class="std-scope">mandatory R1 · 4 open gaps</span><span class="std-pages"><a href="std-amdgpu-abi.html">overview</a> · <a href="std-amdgpu-abi-requirements.html">requirements</a> · <a href="std-amdgpu-abi-audit.html">audit</a> · <a href="std-amdgpu-abi-tracker.html">tracker</a></span><a class="std-tag" href="std-amdgpu-abi-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-spir-v.html">SPIR-V</a></span><span class="std-scope">1.6 Revision 8</span><span class="std-scope">mandatory R2 · 0 open gaps, 3 later</span><span class="std-pages"><a href="std-spir-v.html">overview</a> · <a href="std-spir-v-requirements.html">requirements</a> · <a href="std-spir-v-audit.html">audit</a> · <a href="std-spir-v-tracker.html">tracker</a></span><a class="std-tag" href="std-spir-v-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-rvv-1.0.html">RISC-V V vector extension</a></span><span class="std-scope">1.0</span><span class="std-scope">mandatory R3 · 0 open gaps, 3 later</span><span class="std-pages"><a href="std-rvv-1.0.html">overview</a> · <a href="std-rvv-1.0-requirements.html">requirements</a> · <a href="std-rvv-1.0-audit.html">audit</a> · <a href="std-rvv-1.0-tracker.html">tracker</a></span><a class="std-tag" href="std-rvv-1.0-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
  </ul>
</section>

<section class="std-card" role="listitem">
  <h3 class="std-sys">Runtime</h3>
  <ul>
    <li class="std-gap"><span class="std-name"><a href="std-hip.html">HIP runtime API</a></span><span class="std-scope">ROCm 7.0 to 7.2 (7.2.4 reference)</span><span class="std-scope">mandatory R1 · 10 open gaps, 2 later</span><span class="std-pages"><a href="std-hip.html">overview</a> · <a href="std-hip-requirements.html">requirements</a> · <a href="std-hip-audit.html">audit</a> · <a href="std-hip-tracker.html">tracker</a></span><a class="std-tag" href="std-hip-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-rccl.html">RCCL</a></span><span class="std-scope">ROCm 7.0 to 7.2 (RCCL 2.27.7 reference)</span><span class="std-scope">mandatory R2 · 0 open gaps, 6 later</span><span class="std-pages"><a href="std-rccl.html">overview</a> · <a href="std-rccl-requirements.html">requirements</a> · <a href="std-rccl-audit.html">audit</a> · <a href="std-rccl-tracker.html">tracker</a></span><a class="std-tag" href="std-rccl-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-vulkan.html">Vulkan</a></span><span class="std-scope">1.4.368 text; no minimum core version (OI-016)</span><span class="std-scope">mandatory R2 · 1 open gap, 4 later</span><span class="std-pages"><a href="std-vulkan.html">overview</a> · <a href="std-vulkan-requirements.html">requirements</a> · <a href="std-vulkan-audit.html">audit</a> · <a href="std-vulkan-tracker.html">tracker</a></span><a class="std-tag" href="std-vulkan-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
  </ul>
</section>

<section class="std-card" role="listitem">
  <h3 class="std-sys">Data and integrity</h3>
  <ul>
    <li class="std-ok"><span class="std-name"><a href="std-fips-180-4.html">FIPS PUB 180-4 Secure Hash Standard (SHA-256)</a></span><span class="std-scope">180-4</span><span class="std-scope">mandatory R1 · 0 open gaps</span><span class="std-pages"><a href="std-fips-180-4.html">overview</a> · <a href="std-fips-180-4-requirements.html">requirements</a> · <a href="std-fips-180-4-audit.html">audit</a> · <a href="std-fips-180-4-tracker.html">tracker</a></span><a class="std-tag" href="std-fips-180-4-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-ok"><span class="std-name"><a href="std-rfc-8259.html">RFC 8259 JSON</a></span><span class="std-scope">RFC 8259 (STD 90)</span><span class="std-scope">mandatory R1 · 0 open gaps</span><span class="std-pages"><a href="std-rfc-8259.html">overview</a> · <a href="std-rfc-8259-requirements.html">requirements</a> · <a href="std-rfc-8259-audit.html">audit</a> · <a href="std-rfc-8259-tracker.html">tracker</a></span><a class="std-tag" href="std-rfc-8259-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-ok"><span class="std-name"><a href="std-iso-8601.html">ISO 8601-1 Date and time (RFC 3339 profile)</a></span><span class="std-scope">ISO 8601-1:2019 with Amd 1:2022</span><span class="std-scope">mandatory R1 · 2 open gaps</span><span class="std-pages"><a href="std-iso-8601.html">overview</a> · <a href="std-iso-8601-requirements.html">requirements</a> · <a href="std-iso-8601-audit.html">audit</a> · <a href="std-iso-8601-tracker.html">tracker</a></span><a class="std-tag" href="std-iso-8601-audit.html" title="audited 2026-11-13 against secondary sources: the specification is not freely available">assessed · secondary</a></li>
  </ul>
</section>

<section class="std-card" role="listitem">
  <h3 class="std-sys">Serving</h3>
  <ul>
    <li class="std-later"><span class="std-name"><a href="std-openai-api.html">OpenAI API</a></span><span class="std-scope">2.3.0</span><span class="std-scope">mandatory R3 · 0 open gaps, 5 later</span><span class="std-pages"><a href="std-openai-api.html">overview</a> · <a href="std-openai-api-requirements.html">requirements</a> · <a href="std-openai-api-audit.html">audit</a> · <a href="std-openai-api-tracker.html">tracker</a></span><a class="std-tag" href="std-openai-api-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-rfc-9110.html">HTTP RFC 9110 and RFC 9112</a></span><span class="std-scope">RFC 9110, RFC 9112</span><span class="std-scope">mandatory R3 · 0 open gaps, 4 later</span><span class="std-pages"><a href="std-rfc-9110.html">overview</a> · <a href="std-rfc-9110-requirements.html">requirements</a> · <a href="std-rfc-9110-audit.html">audit</a> · <a href="std-rfc-9110-tracker.html">tracker</a></span><a class="std-tag" href="std-rfc-9110-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-sse.html">Server-sent events</a></span><span class="std-scope">WHATWG 2026-11-13</span><span class="std-scope">mandatory R3 · 0 open gaps, 3 later</span><span class="std-pages"><a href="std-sse.html">overview</a> · <a href="std-sse-requirements.html">requirements</a> · <a href="std-sse-audit.html">audit</a> · <a href="std-sse-tracker.html">tracker</a></span><a class="std-tag" href="std-sse-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
    <li class="std-later"><span class="std-name"><a href="std-prom-text.html">Prometheus text format</a></span><span class="std-scope">0.0.4</span><span class="std-scope">mandatory R3 · 0 open gaps, 3 later</span><span class="std-pages"><a href="std-prom-text.html">overview</a> · <a href="std-prom-text-requirements.html">requirements</a> · <a href="std-prom-text-audit.html">audit</a> · <a href="std-prom-text-tracker.html">tracker</a></span><a class="std-tag" href="std-prom-text-audit.html" title="audited 2026-11-13 against the downloaded specification">assessed</a></li>
  </ul>
</section>

</div>
<!-- end generated map -->

## Other referenced documents

SRS §1.4 also names documents that are not standards rustinfer must conform to:
*process* (how the project is developed), *informative* (background, method,
evidence) and *internal* (the project's own decisions, on the
[decisions](decisions.html) page). None has a tracker.

<!-- begin generated references: scripts/reference/gen_standards.py from SRS §1.4; do not edit by hand -->

Read from the Conformance column of SRS §1.4 at `origin/main`.

| ID | Document | Conformance | Purpose |
|---|---|---|---|
| SWG-001 | Software Development Guidelines | process | The engineering standard the project is developed under: requirement format, reviews, logging, tests; adapted by ADR-001, ADR-004 and ADR-008. |
| AITER-DOCS | AITER read from the tree (`../aiter-docs`): the reference for tuned kernels on gfx942 and gfx950 and the benchmark baseline | informative | The kernels rustinfer's generated kernels are compared with, never linked: the GEMM baseline of RI-NFR-006. |
| DEV | `docs/planning/datacenter-device-inventory.md` | informative | The datacenter GPUs and accelerators the targets are chosen from. |
| IEEE-29148 | ISO/IEC/IEEE 29148-2018 | informative | The requirements-engineering standard that succeeds IEEE 830; the SRS follows both. |
| IEEE-830 | IEEE Std 830-1998 | informative | The structure of the SRS and the qualities a requirement must have. |
| INV | `docs/planning/trt-llm-feature-inventory.md` | informative | The TensorRT-LLM feature inventory the scope of each release was drawn from. |
| MXFP4-RTN | arXiv 2509.23202: weight-only MXFP4 RTN recovers about 95.6 percent on Llama-3.1-8B | informative | Evidence that weight-only MXFP4 round-to-nearest keeps about 95.6 percent of Llama-3.1-8B's accuracy, behind MXFP4 in Release 1. |
| NV-KV | NVIDIA, "Optimizing Inference for Long Context and Large Batch Sizes with NVFP4 KV Cache" | informative | Background for a low-precision KV cache (NVFP4 KV cache, long context and large batches). |
| UC | `docs/planning/use-cases.md` | informative | The use cases the requirements trace back to. |
| ADR-001 to ADR-006 | `docs/adr/` | internal | The founding decisions: Rust under SWG-001, the artifact format, the target abstraction, Codeberg rules, the three representations, the artifact as a cache. |
| ADR-007 | `docs/adr/ADR-007-pinned-llvm-and-mlir-link.md` | internal | The pinned LLVM 23 and the in-process MLIR link. |
| ADR-008 | `docs/adr/ADR-008-hosting-on-github.md` | internal | The move of the project to GitHub. |
| ADR-009 | `docs/adr/ADR-009-placement-names-devices-and-tiers.md` | internal | Placement names devices and tiers. |
| ADR-010 | `docs/adr/ADR-010-mxfp4-in-release-1.md` | internal | MXFP4 in Release 1. |

<!-- end generated references -->

## How a standard is added

1. **A row in SRS §1.4** through an SRS amendment: the ID, the exact title, the
   pinned version and its date, the scope, and the conformance `mandatory R<n>`. The
   version is the one the code is written against; "latest" is not a pin.
2. **Its four pages**, `content/std-<id>.md`, `-requirements`, `-audit` and
   `-tracker`, with `section: Standards`, `group: "<Area> / <Name> <version>"` and
   four consecutive orders; the specification downloaded into `specs/`.
3. **Its record**, `data/standards/<id>.json`: name, version, area, conformance,
   state, whether it is assessed, the audit date and the source of the
   specification (`downloaded` or `secondary`).
4. `.venv/bin/python scripts/reference/gen_standards.py`, which checks the pages
   against the record and the SRS, recomputes the gap counts from the tracker and
   rewrites the map above.
