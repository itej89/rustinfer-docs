---
title: Architecture diagram
section: Design
order: 2
summary: rustinfer in the C4 model, from its context down to its code, with the layer stack, the standards, the build-then-run sequence and the one-node deployment; every status chip derived from the tracker.
---

# Architecture diagram

Three rules decide the shape.

**A checkpoint is compiled once, ahead of time.** Nothing that runs a model
reads a Model IR document or plans a kernel. The build writes one artifact
for one target and one checkpoint; every load after that verifies it and
streams the weights.

**Every kernel is generated.** Kernel IR, built by Rust generators, lowers
in process through the pinned LLVM 23. No vendor kernel library is linked,
and no kernel exists as text.

**A backend is a crate and one registry line.** The graph compiler, the
planner and the runtime see only the `Target` traits; adding hardware
changes nothing above them (RI-TGT-004).

The diagrams follow Simon Brown's [C4 model](https://c4model.com): the
system in its context, its containers, their components, and their code,
each level a zoom into the one before. Beside them are the supplementary
views C4 allows: the layers in the Matins form, read from the bottom; the
mandatory standards on the element each applies to; the build-then-run
sequence; and the one-node deployment of Release 1. A tab switches the
level, and each has its own link. **Show standards** puts each element's
standards on the first three levels.

The boxes, their relations and the issues behind them are data, in
`data/c4/*.json`; the dependency bands and the public items are read from
the tree's `Cargo.toml` files and `lib.rs`; the standards come from
`data/standards/` through `data/standards-placement.json`. No chip is typed:
each is derived from the issue tracker's last fetch. The shape is the
design; the chips are the truth as of {{c4-date}}.

<!-- c4 -->
