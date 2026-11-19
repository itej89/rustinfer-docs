---
title: Profiler (design)
section: Runtime
order: 5
summary: The design under review for the profiler that finds the gaps by itself: one target-neutral timeline, a gap report, host collectors built on the state-of-the-art Rust and CPU tools, and a device backend per target built on that platform's own profiler and hardware counters, at close to zero cost when off.
---

# Profiler (design)

**Status: under review, 2026-11-19.** PR 1,
[#168](https://github.com/itej89/rustinfer/pull/168) (issue #166,
ADR-012), is merged. It contains the timeline, the gap report, the device
track, `profile report`, roctx markers and Tracy (behind a feature). PRs 2
and 3 are still design. The contracts below are the merged code. Overheads
are measured where marked, and the rest are targets.

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
/// What a run measures, one mode at a time. `#[non_exhaustive]`: Counters,
/// PcSampling, ThreadTrace and InKernelStamps are added by PRs 2 and 3.
pub enum ProfileMode { Off, Timing }

/// How a backend times kernels: `HostSpans` (cpu), `EventPairs` (ROCm,
/// PR 1); `Rocprofiler` comes with PR 2.
pub struct ProfileCapabilities { pub timing: TimingMethod }

/// One per target. Every call takes the device it profiles, so a backend
/// built on the `Device` trait holds no reference to it.
pub trait DeviceProfiler {
    fn capabilities(&self) -> ProfileCapabilities;
    /// Creates what the mode needs, sized from the Plan's launch count;
    /// returns the events it made, which the engine destroys.
    fn start(&mut self, device: &dyn Device, mode: &ProfileMode, launches: usize)
        -> Result<Vec<EventId>>;
    /// The anchor that aligns device time to the host clock (this is the
    /// calibration for event pairs; a ClockMap comes with rocprofiler-sdk).
    fn begin_iteration(&mut self, device: &dyn Device, stream: StreamId, clock: &HostClock)
        -> Result<()>;
    /// Either side of a launch: the event fallback records here; a
    /// rocprofiler backend makes `before_launch` a no-op.
    fn before_launch(&mut self, device: &dyn Device, stream: StreamId, id: CorrelationId) -> Result<()>;
    fn after_launch(&mut self, device: &dyn Device, stream: StreamId, id: CorrelationId) -> Result<()>;
    /// After the readback, never during: fills the preallocated `into`
    /// without growing it.
    fn drain(&mut self, device: &dyn Device, into: &mut Vec<DeviceRecord>) -> Result<()>;
}
```

On the host side, the built-in collector is our own span buffer. It is
preallocated and touched at load, and it keeps the first spans rather than
overwriting the oldest, so no iteration is cut in half (ADR-012 §4). The
host clock is `quanta`, which reads the TSC in 32 ns against 66 ns for
`Instant`. roctx ranges and Tracy are crate-private `HostCollector`s. Tracy
gets a GPU-context timeline sent at the end of each iteration, because its
zone guard is not `Send`. Nothing allocates on the hot path.

The device start of a kernel is the later of its start event and the
return of its launch call. On a host-bound stream the start event fires
before the kernel exists, so it cannot be used alone. This can understate a
kernel by about 1 µs. The per-iteration anchor shifts all device times by a
few µs, which cancels in busy time and in gaps (ADR-012).

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
| Off | 0 (tested) | 0 (tested) | none: no branch per launch (tested) |
| Timing, rocprofiler-sdk | 0 | 0 | one span write (< 100 ns) |
| Timing, event pairs (PR 1, `method=events`) | 2 `hipEventRecord`, plus 1 per iteration; 2 `hipEventElapsedTime` after the readback | 0 | 1.13 µs on the in-process test device; the HIP cost is measured by #120 |
| one span | none | 0 | 28.6 ns (measured, release, P-core) |
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
| 1 — **merged** (#168) | Timeline, gap report, summary lines, Perfetto device, gap and idle tracks, `profile report`, the span buffer on `quanta`, Tracy feature, roctx markers, `scripts/profile/record.sh` | #120 step: `run --profile-out` then `profile report` on the bf16 TinyLlama run |
| 2 | ROCm: rocprofiler-sdk buffered dispatch tracing as the timing method, the event-pair fallback, rocprofv3 import into `profile report` | #120: `method=rocprofiler`, and the report matches `rocprofv3 --kernel-trace` within 2% |
| 3 | Hardware: rocprofiler-sdk counters and the roofline verdict, PC sampling, ATT for one kernel, `s.memrealtime` stamps; perf_event counters on the host | one decode GEMM and the sampler under each mode |
| R2+ | the Vulkan, RISC-V vector and RISC-V mesh backends, each with its target | with each target's lowering |

A second change is going on in parallel, without waiting for the profiler.
It cuts the host overhead the code already shows on every eager launch:
one `hipEventRecord` per bound buffer, the launch rebuilt each time, and
blocking input copies. The profiler then measures the result.

## Open questions for review

1. **Tracy (built, off by default):** this needs the Tracy C++ client, built by `tracy-client-sys`
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
