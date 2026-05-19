# Jacquet et al. 2025 — Cinergy

Authoritative short summary of *"Cinergy: Deterministic Power Monitoring for Carbon Accounting in the Cloud"* (IEEE TCC 2025, extended from CCGrid 2025).
PDF: `sources/cinergy-tcc-2025.pdf`.
Bib key: **TODO** (no entry yet in `paper/references.bib`).

## What it is

Framework for per-VM power monitoring that combines top-down isolation-based modelling (WCPC) with bottom-up runtime profiling, producing **deterministic** per-VM power estimates that still capture consolidation gains.
Partnered with **OVHcloud**, evaluated on production traces across 6 server architectures (Intel Broadwell / Cascade Lake / Ice Lake; AMD Zen1 / Zen2 / Zen3).
MAPE 6.6\% across architectures.

## Core construction

- **WCPC** (§III.A): power consumption of a VM in isolation on a dedicated host — the worst case, since shared hosts are more energy-efficient at high utilisation. Polynomial regression (5th order) on CPU usage; eq. 1 distributes static server power proportionally to vCPU allocation.
- **Cinergy ratio** (§III.B, eq. 2): $r_{VM} = \text{bottom-up}_{VM} / \text{top-down}_{VM}$. Captures the consolidation gain: $r=0.4$ means the VM actually consumes 40\% of its isolated power thanks to sharing. Published as a **per-cluster average** to preserve determinism.
- **Bottom-up estimator** (§V.A, eq. 3): $\mathcal{P}^{bottom-up}_{VM} = (CPU^{usage}_{VM} / CPU^{usage}_{total}) \cdot \mathcal{P}_{RAPL}$.

## The empirical finding that matters most for rSCI (§V.C)

Headline claim from abstract / §V: *current carbon-accounting tools can underestimate operational CO2 emissions by up to 3× for certain VM profiles.*

Mechanism (§V.C):
- Provider attribution is typically linear in VM size (proportional to vCPU / instance-hours), which **assumes constant per-vCPU efficiency**.
- Real servers are *logarithmically* less efficient at low load. Linear allocation under-attributes power at moderate-to-high utilisation, because the actual efficiency improvement from consolidation is sublinear and the linear model bakes in the full theoretical efficiency.
- For a 4-core VM on a Xeon E5-2620 v4 in a France datacenter at high utilisation: Cinergy estimate $\approx 11.0$ kgCO2/month vs. $\approx 3.7$ kgCO2/month with the current OVHcloud static estimate — **3×**.

Also documented (§V.B):
- Cinergy ratio averages: 0.81 for OVHcloud *Public Cloud* (guaranteed-resource), 0.44 for *VPS* (oversubscribed). VPS is $\approx 1.85\times$ more energy-efficient per VM.
- Per-cluster Cinergy ratio is stable enough to publish as a deterministic correction factor (Fig. 6).

## Comparison with related provider methodologies (their §II)

- **Azure / GCP** use what GHG-Protocol calls *Single Data Point Power Consumption* — VM-size $\times$ average host power. Suitable only for static workloads; misses dynamic effects.
- **OVHcloud** uses *Dynamic Power Consumption Calculations* — host-level RAPL measurement scaled by VM size and adjusted by PUE + grid intensity. Closer to GHG recommendations, but still ignores actual customer usage.
- **No provider** integrates customer-side resource usage into the carbon estimate.

## Relation to rSCI

- **Same family as SCI / oSCI / tSCI / BoaviztAPI**: bottom-up, no top-down reconciliation → **not reconcilable**. Falls under §2 critique.
- **Strengthens our motivation**: the 3× underestimation finding is a strong empirical hook for the claim that bottom-up models without top-down anchoring (and provider models without customer-side usage) are quantitatively, not just structurally, wrong. Cite in §2 alongside Bashir's sunk-carbon fallacy as a second concrete pathology of un-reconciled metrics.
- **Cinergy ratio is conceptually adjacent to our (currently commented-out) $\mu_{s,r}$ Scope-2 multiplier**: a slow-moving slice-level correction factor. When we refresh real-time estimation under the per-component weight schema, Cinergy is a precedent for publishing per-cluster correction factors.
- **Alternative bottom-up engine for rSCI**: Cinergy's per-VM power estimates can feed $E_{i,s,r}$ in Eq. \ref{eq:bu-energy}, the same way BoaviztAPI can.
- **Honest caveat**: if Cinergy is right that providers under-attribute by 3×, and rSCI reconciles to the provider's top-down report, then rSCI inherits any provider-side under-reporting. This is the *"captures the top-down report, not physical truth"* scoping caveat already flagged in our intro. Cinergy's finding makes that caveat sharper and worth surfacing in §4 as a discussion point: **negative residuals are admissible and signal provider under-counting**.

## Recommendation for `paper/paper.tex`

- **§2 background**: one sentence pairing Cinergy with Bashir 2024 as concrete empirical evidence of bottom-up / provider-attribution failure modes (3× underestimation).
- **§3 SOTA**: brief mention as the most rigorous non-provider per-VM bottom-up tool, with the OVHcloud partnership noted.
- **§4 after Eq. \ref{eq:rsci} or properties paragraph**: add one sentence that residuals may be **negative** when bottom-up exceeds top-down, signalling provider under-counting — Cinergy's 3× finding is the citation.
- **§6 Asks**: corroborates the "report at billing frequency" ask — Cinergy demonstrates this is technically feasible.
- No structural change to the rSCI framework.
