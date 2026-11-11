---
title: Build on first load, and strict mode
navtitle: Artifact as cache, strict mode
section: Runtime
order: 2
summary: ADR-006; the .rie file is a cache of build decisions that run and serve produce on first load and that --require-prebuilt turns back into a requirement for production starts.
---

# Build on first load, and strict mode

Read from ADR-006, RI-CLI-003, RI-CLI-004, RI-PLN-004 and
`docs/uml/sequence-diagram.md` §2 at commit `082df51`. On the scaffold
branch the refusal half of this page is implemented and tested
(`test_run_with_require_prebuilt_refuses_a_directory`); the build half is
issue #11.

## The decision

ADR-006's context: TensorRT-LLM removed its mandatory engine-build step in
version 1.2; vLLM and SGLang compile and capture graphs on first load and
cache the result. The operational reasons were model release velocity, GPU
and driver churn, and multi-hour builds that failed late. What is worth
keeping from the engine model is the artifact's properties (no inference-time
decisions, portable, inspectable), not the obligation to run a command
first.

So the `.rie` artifact is a durable cache of build decisions, reachable two
ways:

| mode | command | what happens |
|---|---|---|
| explicit | `rustinfer build --model <dir> --target <arch> --out <file>` | the artifact is written at `<out>`, for fleets that want reproducible, inspectable artifacts through CI |
| first load | `rustinfer run <dir>` or `rustinfer serve <dir>` | the same artifact is built into `RUSTINFER_CACHE_DIR`, keyed by model hash, target, precision and profile, and reused on later loads (RI-CLI-003) |
| strict | `--require-prebuilt`, or the server key `strict_artifact` | `run` and `serve` refuse a model directory and refuse to build (RI-CLI-004: "a production start never compiles") |

The cache directory defaults to `$XDG_CACHE_HOME/rustinfer`, else
`$HOME/.cache/rustinfer`, from `rustinfer-core::config` (`ENV_CACHE_DIR`,
`DEFAULT_CACHE_DIR_NAME`). `inspect` reports which path produced an
artifact: the `metadata` section records the origin as `build` or first load
(RI-ART-008).

The sequence, from the diagram: `run` computes the key; on a hit it loads
the cached path; on a miss without `--require-prebuilt` it runs the
frontend, the graph compiler and the kernel compiler, writes to a temporary
file in the cache directory, hashes last, `fsync`s and renames; with
`--require-prebuilt` it returns the refusal and exits 1.

## Placement is cached the same way

ADR-006 extends the rule to the planner: placement is computed at load from
the discovered topology, cached beside the artifact keyed by topology hash,
and pinnable for strict fleets; a pinned placement is refused on a differing
topology (RI-PLN-004, R2). The artifact therefore never bakes one node's
topology in, which is why the `topology` and `placement` sections are empty
at build unless pinned ([the planner](planner.html)).

## What it costs

The ADR's own list: a first load may take minutes; the cache directory needs
space and hygiene; and two code paths produce artifacts and must be kept
identical, which RI-GC-009's byte-identical determinism makes checkable.

## What exists today

The constants, the settings and the refusal:

```text
$ rustinfer run ./some-model-dir --require-prebuilt
error=invalid component=cli detail="./some-model-dir is a model directory and --require-prebuilt forbids building"
```

The refusal is reported under the `invalid` code by the CLI; whether it gets
its own code is not decided in the tree. Everything after the refusal, the
cache lookup and the build, is Planned R1 under issue #11.
