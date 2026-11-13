---
title: Standards
navtitle: Overview
section: Standards
order: 1
summary: What it means for rustinfer to implement a standard, where the state comes from, how a standard is added to the SRS, and how a candidate becomes tracked.
---

# Standards

rustinfer reads and writes formats it did not invent: safetensors shards, OCP
microscaling blocks, AMD code objects, JSON sections, later an OpenAI-shaped HTTP API.
The [standards tracker](ref-standards.html) lists each one the SRS references, with the
requirements that cite it and how far those requirements are implemented. This page
says what that state means and how the list changes.

## What "implemented" means for a standard

A standard is never implemented as a whole. rustinfer implements **the parts in its
scope**: the parts the SRS says it uses, stated in the requirement clauses that cite the
standard (for OCP MX, for example, only MXFP4: E2M1 elements in blocks of 32 with a
UE8M0 scale, converted per §6.3 of v1.1). Anything outside that scope is out of the
claim, implemented or not.

The state of a standard is not judged by hand. It comes from the requirements that cite
it, and the state of each requirement comes from the tags its tests carry, under the
rule of the rustinfer repository's `docs/testing.md` (the same rule the
[requirements page](ref-requirements.html) uses):

- a requirement is *implemented* when a test says `Verifies` it and none says
  `Groundwork for` it, *partial* when any test says `Groundwork for` it, *reserved only*
  when tests only assert its later-release refusal (`Reserved`), and *planned* otherwise;
- a standard is <span class="state-ok">implemented</span> in its R1 scope when every
  citing R1 requirement is implemented, <span class="state-part">in part</span> when some
  citing requirement is implemented or partial, and <span class="state-no">not
  implemented</span> otherwise. A reference no requirement cites is listed as *not cited*.

A later-release requirement does not hold back the R1 state; it is counted beside it so
the remaining work stays visible.

## How to add a standard

A standard is tracked when the SRS says two things about it:

1. **A row in SRS §1.4 References**: an ID, the exact title, the pinned version and its
   date. The version is the one the code is written against; a moving target ("latest")
   is not a pin.
2. **A citing clause**: at least one requirement whose clause, `Rationale` or
   `Acceptance` text names the ID (or an unambiguous name of the standard), and states
   which parts are in scope. If the standard pins an external interface, the §3.1.3
   table should name it too.

Both go through an SRS amendment (a change request, a changelog row, the version
bump). Then regenerate the tracker with
`.venv/bin/python scripts/reference/gen_standards.py`; if the standard is known by a
name other than its ID, add the name to `ALIASES` in that script, and its scope to
`SCOPE`.

## Candidates

The second table of the tracker, *Required, not yet in the SRS*, lists standards the
code or the plan already depends on that §1.4 does not reference: the IEEE 754 and OCP
fp8 formats the CPU reference converts, the safetensors header the frontend and Sluice
parse, the SHA-256 of the artifact, the LLVM 23 pin of ADR-007, and others. Each names
the requirements that should cite it, the release, and the lines of the tree that show
the dependency. They come from `data/standards-candidates.json`, curated by reading the
tree, and the generator refuses an evidence line that does not exist in the checkout.

A candidate is a proposal, not a tracked standard: it has no state until an SRS
amendment adds its §1.4 row and a requirement cites it. After that amendment, remove it
from the candidates file; the generator then finds it in §1.4 like any other reference.
