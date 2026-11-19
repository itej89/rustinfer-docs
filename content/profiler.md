---
title: Profiler (design)
section: Runtime
order: 5
summary: The design under review for the profiler that finds the gaps by itself: one target-neutral timeline, a gap report, host collectors built on the state-of-the-art Rust and CPU tools, and a device backend per target built on that platform's own profiler and hardware counters, at close to zero cost when off.
---

# Profiler (design)

**Status: design for review, 2026-11-19.** It is not built yet beyond the R1
profiler of #127 (RI-OBS-007) and `run --profile-out` (#165). This page
describes what the profiler PRs will build, and the order they build it in.
Every overhead figure below is a target until a PR measures it.

## Why

GPU test [#120](https://github.com/itej89/rustinfer/issues/120) measured
TinyLlama-1.1B bf16 decode on an MI350X at **29.77 tokens/s**, which is
33.6 ms per token. Reading the 2.2 GB of weights at HBM bandwidth takes about
0.3–0.5 ms, so the GPU was idle most of the time. The profiler today can
write a trace, but someone still has to read it to find out why. The owner's
direction:

- show the gap, automatically, with no manual trace reading;
- use the state-of-the-art profilers for Rust on the CPU and combine them
  with each platform's own GPU profiler;
- use the hardware features;
- keep the overhead close to zero.

rustinfer has five targets, so the design keeps everything that is not
specific to a device in one core. Each target adds only what its platform
offers.

| target | crate | release |
|---|---|---|
| CPU reference | `rustinfer-target` (cpu) | R1 |
| AMD Instinct gfx942, gfx950 (ROCm/HIP) | `rustinfer-target-rocm` | R1 |
| SPIR-V on Vulkan | `rustinfer-target-spirv-vulkan` | R2 |
| RISC-V vector CPUs | `rustinfer-target-riscv-vector` | R3 |
| RISC-V meshes (Tenstorrent, Vortex) | `rustinfer-target-riscv-mesh` | R4 |

## The layers

Read the stack from the bottom up. Each band is a layer, and the strip
between two bands is the contract that layer offers the one above it.

<div class="stack" role="img" aria-label="From the hardware upward: device backends per target, the host collectors, the timeline, and the gap report.">
<div class="layer layer-3"><div class="layer-head"><span class="layer-no">4</span><span class="layer-name">Report</span><span class="chip chip-later">to build</span></div><p class="layer-note">The gap analysis, which needs nobody to read the trace. It prints one summary line per phase, the largest idle gaps, the slowest kernels and each kernel's bound (memory, compute or latency). It writes a Perfetto trace with host and device tracks on one timeline. <code>rustinfer profile report &lt;file&gt;</code> prints the same report from any saved trace, ours or rocprofv3's.</p><ul class="parts"><li class="part-chip-later">summary lines (key=value)</li><li class="part-chip-later">top-N gaps and kernels</li><li class="part-chip-later">roofline verdict per kernel</li><li class="part-chip-later">Perfetto trace</li><li class="part-chip-later">profile report CLI</li></ul></div>
<div class="bound"><span class="bound-rule"></span><span class="bound-label">the Timeline: host spans and device records on one clock, joined by a correlation id per launch</span></div>
<div class="layer layer-2"><div class="layer-head"><span class="layer-no">3</span><span class="layer-name">Timeline</span><span class="chip chip-later">to build</span></div><p class="layer-note">A target-neutral model of what happened: iterations, phases, launches, copies, syncs and readbacks on the host; kernels, copies and counters on each device. Every record carries the launch's correlation id. Device timestamps are aligned to the host clock by the backend's calibration.</p><ul class="parts"><li class="part-chip-later">correlation id per launch</li><li class="part-chip-later">clock calibration</li><li class="part-chip-later">per-device tracks</li></ul></div>
<div class="bound"><span class="bound-rule"></span><span class="bound-label">two collector contracts: HostCollector (spans, CPU counters) and DeviceProfiler (one implementation per target)</span></div>
<div class="layer layer-1"><div class="layer-head"><span class="layer-no">2</span><span class="layer-name">Host collectors</span><span class="chip chip-part">partly built</span></div><p class="layer-note">These cover every target, because the host issues all work. Span timestamps come from the invariant TSC and are written to a ring buffer preallocated at load, with no allocation and no lock. Optional sources: hardware counters per span through perf_event_open, read with rdpmc; Tracy for a live view; samply or perf for sampling, using AMD IBS or Intel PEBS.</p><ul class="parts"><li class="part-chip-part">spans (#127, to move to the TSC ring)</li><li class="part-chip-later">perf_event counters</li><li class="part-chip-later">Tracy (feature)</li><li class="part-chip-later">samply / perf wrapper</li></ul></div>
<div class="bound"><span class="bound-rule"></span><span class="bound-label">each platform's own profiler, loaded with dlopen like the driver, so a build without the platform still compiles and runs</span></div>
<div class="layer layer-0"><div class="layer-head"><span class="layer-no">1</span><span class="layer-name">Device backends</span><span class="chip chip-part">ROCm in part</span></div><p class="layer-note">One DeviceProfiler per target, built on that platform's tools and hardware features. ROCm uses rocprofiler-sdk for dispatch timestamps, counters, PC sampling and thread trace, and roctx markers for rocprofv3. Vulkan uses timestamp queries, performance queries and calibrated timestamps. RISC-V uses the Zicntr counters and Sscofpmf sampling. Meshes use the vendor's device counters.</p><ul class="parts"><li class="part-chip-ok">CPU (host spans)</li><li class="part-chip-part">ROCm: event pairs today</li><li class="part-chip-later">ROCm: rocprofiler-sdk</li><li class="part-chip-later">Vulkan · R2</li><li class="part-chip-later">RISC-V vector · R3</li><li class="part-chip-later">RISC-V mesh · R4</li></ul></div>
</div>

## The contracts

The runtime never names a target. Each target's `Device` hands out a
`DeviceProfiler`, and the runtime asks it for one mode at a time. The sketch
below shows the shape for review. The PRs will fix the names.

```rust
/// What a run measures. Only one mode at a time: counters and thread trace
/// serialise dispatches, so mixing them with timing would distort it.
pub enum ProfileMode {
    Off,           // zero cost: one predictable branch per launch
    Timing,        // device start/end per launch, host spans
    Counters(CounterSet),   // hardware counters per launch
    PcSampling,    // hot instructions per kernel
    ThreadTrace(KernelId),  // instruction timing for one kernel
    InKernelStamps,         // phase timestamps the kernel writes
}

/// One per target. Each method is a no-op on a target that lacks the mode;
/// `capabilities` says which modes it offers.
pub trait DeviceProfiler {
    fn capabilities(&self) -> ProfileCapabilities;
    fn start(&mut self, mode: &ProfileMode) -> Result<()>;
    /// Called at launch time with the launch's correlation id; the backend
    /// adds no driver call when its platform tags dispatches itself.
    fn on_launch(&mut self, id: CorrelationId);
    /// Drain buffered device records after the iteration (never during).
    fn drain(&mut self, into: &mut Vec<DeviceRecord>) -> Result<()>;
    /// Host-to-device clock offset and drift, measured at start and drain.
    fn calibrate(&mut self) -> Result<ClockMap>;
}
```

`HostCollector` works the same way for the host side: spans, plus optional
counters per span. Neither contract allocates on the hot path. Buffers are
sized at load from the Plan's launch count and `RUNTIME_PROFILE_MAX_SPANS`.

## What each target uses

| | CPU (R1) | ROCm gfx942, gfx950 (R1) | Vulkan (R2) | RISC-V vector (R3) | RISC-V mesh (R4) |
|---|---|---|---|---|---|
| kernel timing | TSC spans around the launch | rocprofiler-sdk buffered kernel-dispatch trace (start/end from the hardware); fallback: hipEvent pair per launch | `vkCmdWriteTimestamp2` query pools | TSC spans, `rdcycle` / `rdtime` (Zicntr) | vendor device cycle counters |
| hardware counters | perf_event_open: cycles, instructions, cache and branch misses (rdpmc) | rocprofiler-sdk counters: SQ_WAVES, SQ_BUSY_CYCLES, VALU and MFMA utilisation, FETCH_SIZE / WRITE_SIZE, L2 and MALL hits, LDS bank conflicts | `VK_KHR_performance_query` | perf with Sscofpmf, the `hpmcounter`s | vendor counters |
| sampling | samply / perf, AMD IBS or Intel PEBS | rocprofiler-sdk PC sampling (host-trap or stochastic; which one gfx950 offers under ROCm 7 is to verify) | none | perf (Sscofpmf overflow) | none planned |
| instruction trace | none | ATT / SQTT thread trace, one kernel per run | RGP (external) | none | vendor |
| in-kernel stamps | none | `s.memrealtime` intrinsic through ROCDL (not assembly) | `OpReadClockKHR` (`VK_KHR_shader_clock`) | `rdcycle` in generated code | vendor |
| markers for external tools | Tracy zones | roctx ranges, so rocprofv3 lines up with ours | `VK_EXT_debug_utils` labels for RGP and RenderDoc | Tracy zones | Tracy (tt-metal uses Tracy) |
| clock alignment | same clock | rocprofiler-sdk timestamps against `CLOCK_MONOTONIC` (to verify) | `VK_KHR_calibrated_timestamps` | same clock | vendor sync |

## How the gap is found

For each iteration, the report splits the wall time into categories. It
then names the worst offenders. The calculation is the same on every
target, because it reads only the Timeline.

| category | from | means |
|---|---|---|
| device busy | Σ (kernel end − kernel start) | the kernels themselves |
| idle, host issue | gap before a launch whose host launch call had not returned yet | the host is slower than the kernels: per-launch cost, locks, allocation, bookkeeping |
| idle, copy | gap spanned by an input upload or readback | blocking or badly ordered copies |
| idle, sync | gap spanned by a host synchronisation | a sync the Plan did not need |
| host other | wall time with neither the host nor the device in the categories above | scheduling, sampling on the host, logging |

The summary line, one per phase (prefill, decode):

```
stage=profile phase=decode iterations=16 wall_ms_per_iter=33.6
  device_busy_ms=… idle_issue_ms=… idle_copy_ms=… idle_sync_ms=…
  idle_pct=… launches_per_iter=… host_launch_us_mean=… method=rocprofiler
```

After it come the top gaps, each with the launch it follows, the kernel and
Plan node, and its category. Then the slowest kernels, by device time and by
share of the iteration. In counters mode, each kernel also gets achieved
GB/s and FLOP/s against the measured peaks, and a verdict: memory-bound,
compute-bound or latency/occupancy-bound.

## Overhead budget

These are targets. Each PR measures its own mode and records the number
here.

| mode | added driver calls per launch | allocations per launch | added host time per launch (target) |
|---|---|---|---|
| Off | 0 | 0 | one branch (< 1 ns) |
| Timing, rocprofiler-sdk | 0 | 0 | one span write (< 100 ns) |
| Timing, event fallback | 2 `hipEventRecord` | 0 | a few µs; logged as `method=events` |
| Counters, PC sampling, thread trace | per the platform | 0 | the run is serialised: use it for diagnosis, never for timing |
| Tracy, perf_event | 0 | 0 | tens of ns per span |

The tests check three things on the mock device:

- with profiling off, the HIP call count and the allocation count are
  exactly those of an unprofiled run;
- with the timing mode on rocprofiler-sdk, no HIP calls are added;
- the gap arithmetic gives the exact values on synthetic timelines.

## Delivery

| PR | content | GPU check |
|---|---|---|
| 1 | Timeline, gap report, summary lines, Perfetto device tracks, `profile report`, TSC ring buffer, Tracy feature, roctx markers, the samply/perf wrapper | #120 step: `run --profile-out` then `profile report` on the bf16 TinyLlama run |
| 2 | ROCm: rocprofiler-sdk buffered dispatch tracing as the timing method, the event-pair fallback, rocprofv3 import into `profile report` | #120: `method=rocprofiler`, and the report matches `rocprofv3 --kernel-trace` within 2% |
| 3 | Hardware: rocprofiler-sdk counters and the roofline verdict, PC sampling, ATT for one kernel, `s.memrealtime` stamps; perf_event counters on the host | one decode GEMM and the sampler under each mode |
| R2+ | the Vulkan, RISC-V vector and RISC-V mesh backends, each with its target | with each target's lowering |

A second change is going on in parallel, without waiting for the profiler.
It cuts the host overhead the code already shows on every eager launch:
one `hipEventRecord` per bound buffer, the launch rebuilt each time, and
blocking input copies. The profiler then measures the result.

## Open questions for review

1. **Tracy:** this needs the Tracy C++ client, built by `tracy-client-sys`
   through `cc`. That is a C++ dependency behind a feature, off by default.
   Is it acceptable, or should the live view stay Perfetto-only?
2. **Counter permissions:** in the GPU test container, are counters and PC
   sampling allowed (`/dev/kfd` profiling access, `perf_event_paranoid`)?
   If not, mode 3 falls back to timing only and says so.
3. **Default for `bench`:** with rocprofiler-sdk, timing mode adds no driver
   calls. Should `bench` turn it on by default?
4. **In-kernel stamps:** these change the code of the kernel they
   instrument, so the stamped build is a separate pass-pipeline variant
   that is never tuned. Is that acceptable?
