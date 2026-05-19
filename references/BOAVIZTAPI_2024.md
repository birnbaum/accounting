# Simon et al. 2024 — BoaviztAPI

Authoritative short summary of *"BoaviztAPI: A Bottom-Up Model to Assess the Environmental Impacts of Cloud Services"* (HotCarbon '24).
PDF: `sources/boaviztapi-hotcarbon-2024.pdf`.
Bib key: **TODO** (currently only a generic `boavizta-dc-lca` misc entry exists; add an `@inproceedings` entry when we cite).

## What it is

Open-source API + bottom-up methodology (https://github.com/Boavizta/boaviztapi) for assessing per-component, per-server, per-cloud-instance environmental impacts.
Multi-criteria (not just carbon): **GWP** (g CO2e), **ADP** (abiotic resource depletion, kg Sb-eq), **PE** (primary energy, MJ).
Crowd-sourced impact factors for >1750 CPU models (TechPowerUp), SSD densities, RAM densities.

## Methodology in one screen

§3 Server model: embodied impact factor per component, amortised over lifetime $\mathcal{D}$:
- CPU (eq. 1): $\mathcal{F}^e_{cpu} = (\text{die}_{cpu}\cdot\mathcal{F}^{die}_{cpu} + \mathcal{I}^{base}_{cpu})/\mathcal{D}$.
- NAND (eq. 2): same structure for RAM / SSD with density-based scaling.
- Others (eq. 3): motherboard + PSU + assembly + casing, static.

§3.2 Usage model: CPU power as logarithmic regression on TDP ratios at 0/10/50/100% load (eq. 6); RAM power from \cite[33]; PSU/mobo/fan overhead as 20\% factor (eq. 7).

§4 Cloud model: PUE-based scaling for technical/building environment embodied (eq. 8) and usage (eq. 9).
Per-instance allocation by vCPU + GB share (eq. 10).

## Table 1 — their critique of provider methodologies

§1, Table 1 compares Azure / GCP / AWS / Cloud Carbon Footprint on lifecycle phases, included resources, and electricity method.
Findings closely parallel our §3 (`paper/paper.tex`):
- AWS excludes resource extraction and end-of-life.
- GCP excludes end-of-life; uses 4-yr amortisation.
- Azure excludes buildings and FERA.
- Coolant leaks: unknown for AWS and Azure; explicitly excluded by GCP.
- Idle resources: AWS unknown; GCP and Azure include.
- Third-party services (control plane, billing): unknown for AWS; GCP and Azure include.

Useful as a cross-reference / independent corroboration of our Table 2 (`tab:bigthree-s3`).

## §4.3 Limits they acknowledge (directly relevant to rSCI)

- Third-party services not modelled (control plane, billing).
- Non-server IT (network equipment) usage impacts not counted.
- Idle servers not considered (assumes 100\% occupancy).
- Overcommitted resources double-counted.
- vCPU-based allocation for shared resources is "arbitrary" and to be challenged in future work.
- No GPUs / TPUs.

Each of these is a component that lands in rSCI's $\Delta^k$ residual — i.e., BoaviztAPI's *acknowledged blind spots* are precisely the un-modelled overheads that rSCI absorbs via top-down reconciliation.

## Relation to rSCI — summary

- **Same family as SCI / oSCI / tSCI**: bottom-up, no top-down anchor → **not reconcilable**. Falls under our §2 critique.
- **Complementary**: their per-component $\mathcal{F}^e$ and $\mathcal{P}$ factors are exactly the kind of $\varepsilon_p$ that feed our Eq. \ref{eq:bu-energy}. Picking BoaviztAPI as the bottom-up engine of rSCI is the natural composition.
- **Multi-criteria angle (ADP, PE) corroborates §7 future work**: rSCI's residual-bridge framework is signal-agnostic and can extend to water / abiotic / primary energy as long as the provider reports them top-down.
- **Their Table 1 is a useful independent cross-check** of the provider-methodology heterogeneity we document in §3.

## Recommendation for `paper/paper.tex`

- **§3 SOTA**: short mention as the leading open-source provider-agnostic bottom-up alternative; cite their Table 1 as independent corroboration.
- **§4 (after Eq. \ref{eq:bu-energy})**: one-sentence pointer that $\varepsilon_p$ can be sourced from open-data projects like BoaviztAPI.
- **§7 Future Work / multi-criteria extension**: one sentence on signal-agnosticism with BoaviztAPI's ADP / PE coverage as the concrete handle.
- No structural change to the rSCI framework.
