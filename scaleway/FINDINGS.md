# Scaleway experiment — findings, methodology extract, open questions

Status as of **2026-06-05**.
Procedural setup is in `README.md`; this file is the durable record of what the experiment showed.

## TL;DR

The stress load works (CPU-verified), but Scaleway's **daily** Environmental Footprint report is unreliable, and as currently reported idle and stress have **identical** footprints.
Whether that survives consolidation is the one open question (re-pull ~2026-06-06/07).
If the daily report stays unusable, **Scaleway does not serve our purpose** and the paper keeps its current framing (see `project_scaleway_partial_existence_proof` memory).

## What is verified

### 1. The stress load runs (ground truth, independent of the carbon report)

Live CPU via **Scaleway Cockpit metrics** (`rate(instance_server_cpu_seconds_total[5m])` ÷ `instance_server_vcpu_count`), 2026-06-05:

| Server | Region | Workload | CPU |
|---|---|---|---|
| rsci-exp-1-idle | fr-par-1 | idle | 0.1 % |
| rsci-exp-2-stress | fr-par-1 | stress | **100.0 %** (2.0/2 cores) |
| rsci-exp-3-idle | nl-ams-1 | idle | 0.2 % |
| rsci-exp-4-stress | nl-ams-1 | stress | **100.0 %** (2.0/2 cores) |

The two workloads differ by ~1000× in actual compute.
This is measured directly, not derived from the carbon report.
The earlier `stress-ng` confound (silent install failure → stress VM sat idle) is resolved: the `yes`-per-core burner (commit 190b920) is live and pegging both vCPUs.
No SSH was possible (VMs have no public IP; `dynamic_ip_required=False`); the legacy `/instance/v1/.../servers/{id}/metrics` endpoint now 404s — Cockpit is the only live-CPU path.

### 2. The daily footprint report is buggy

Pull saved to `daily_impact_jun2026.csv` (2026-06-05). Three independent defects:

- **Phantom data.** Non-zero emissions reported for **June 1–3** (and the June-4 morning) when **no resources existed** — all four VMs were created **2026-06-04 13:20 UTC** (confirmed via `get_server.creation_date`).
- **Frozen / unstable placeholder.** June values are bit-identical across June 1, 3, 4, 5 (exp-1/2 = `0.007439`, exp-3/4 = `0.035436`), yet June-2 exp-1 reads `0.002387` — a placeholder that isn't even day-stable.
- **Unexplained ~7× drop May→June** across **all 5 resources** uniformly (exp-1 0.0518→0.0074, exp-3 0.263→0.035, volume 0.0185→0.0026). Systematic, not noise — **cause unknown; do not use either May or June magnitudes until explained.**

### 3. idle == stress as currently reported

Within each region the report assigns idle and stress the **same** daily footprint:

| Region | idle | stress | reported kgCO₂e/day |
|---|---|---|---|
| fr-par-1 | exp-1 | exp-2 | both `0.007439` |
| nl-ams-1 | exp-3 | exp-4 | both `0.035436` |

But these are the **placeholder** values (same figures appear on the no-resource days), so this is **not yet** settled evidence — see open questions.

## Methodology extract

Source: `references/carbon_accounting_methodologies/scaleway/scaleway-methodology-docs-2026-05.md`.

- **Energy is not metered — CPU% is a proxy.** Scaleway feeds CPU utilization through **Boavizta non-linear CPU→power consumption profiles** (§5.4). GPU offers use average consumption instead.
- **Two estimation modes** (§5.4, reaffirmed §8 line 370):
  - *Estimation / pre-order mode:* assumes a flat **30 % CPU** theoretical baseline.
  - *Monthly report mode:* uses **actual CPU consumption** "for highest accuracy."
- **Allocation share** `Resources_Used_VM` = weighted sum of vCPU/pCPU + RAM_vm/RAM_host + Storage_vm/Storage_host (§5.2) — the slice of the shared host you are assigned, separate from the CPU→power energy term.
- **Embodied / manufacturing** is genuinely utilization-independent: prorated runtime ÷ lifespan (25-yr datacenter, 6-yr server) × Boavizta LCA × the allocation share (§5.2–5.3).
- **Grid CI is annual.** Operational emission factors are Ember **annual country** values (FR 0.044, NL 0.253 kgCO₂e/kWh); no time-of-day mechanism.
- **Timing:** data is "generated daily and becomes visible the day after product activation" (§7.2).
- **No stated stability / lock date.** The FAQ (§10) explicitly says values "vary over time" — revised for energy-mix changes, PUE adjustments, and methodology enhancements, to "reflect the most accurate and up-to-date information."

**Key tension:** the methodology *claims* a real utilization term (actual CPU via a non-linear curve in monthly mode), so idle ≠ stress *should* appear once consolidated.
It does **not** state whether the **daily** series uses actual CPU or the flat 30 % estimate.
The cleanest explanation of our frozen, utilization-blind, idle==stress daily pull is that the daily numbers are the **30 % placeholder**, with actual CPU folded in only on consolidation.

## Open questions

1. **Does idle ≠ stress survive consolidation?** — the decider.
   Re-pull June 4–5 around **2026-06-06/07** once Scaleway's retroactive revision settles:
   `uv run python scaleway/pull_impact.py 2026-06-04 2026-06-06`
   (Data revises server-side even after VM deletion, so teardown did not forfeit this.)
   - **Settled idle ≠ stress** ⇒ system works as documented; daily series was just the lagged 30 % estimate. Paper point becomes *daily-data latency/instability*, not utilization-blindness.
   - **Settled idle == stress** (with the CPU-verified 1000× load gap) ⇒ genuine **doc-claims-actual-CPU-but-report-ignores-it** gap. Stronger finding.
2. **What is the uniform ~7× May→June magnitude drop?** Affects all 5 resources equally. Until explained, neither month's absolute numbers are trustworthy.
3. **When (if ever) do daily values stop changing?** No documented finalization point; the phantom/frozen/unstable behaviour above suggests daily data should be treated as provisional indefinitely.

## Decision rule

If the re-pull shows the daily report **stays unreliable / idle == stress**, Scaleway is **not usable for our purpose** and the paper **keeps its current framing** (Scaleway as a partial existence proof; compute-efficiency lever unrealized).
A positive result (idle ≠ stress, settled) would instead let us cite Scaleway as a provider whose report reflects utilization — but only after the ~7× magnitude anomaly is understood.
