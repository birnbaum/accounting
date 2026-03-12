# The Sunk Carbon Fallacy: Rethinking Carbon Footprint Metrics for Effective Carbon-Aware Scheduling

- **Authors:** Noman Bashir, Varun Gohil, Supreeth Belavadi, Mohammad Shahrad, David Irwin, Elsa Olivetti, Christina Delimitrou
- **Year:** 2024
- **URL:** https://arxiv.org/abs/2410.15087

## Key Contributions

1. **Sunk carbon fallacy:** Demonstrates that including embodied carbon in the optimization metric (standard SCI) can lead to perverse scheduling outcomes — carbon-aware schedulers may route work to older, less efficient servers because their per-hour amortized embodied cost is lower, increasing total datacenter emissions.

2. **SCI variant taxonomy:**
   - **oSCI** = `(E · I) / R` — operational carbon only, excludes embodied carbon entirely.
   - **SCI** = `((E · I) + M) / R` — the GSF standard; includes the active server's amortized embodied carbon.
   - **tSCI** = `(tO + tM) / R` — distributes the *entire infrastructure's* operational and embodied carbon proportionally across jobs, rather than only the active server's share.

3. **Scheduling analysis:** Shows that oSCI and tSCI avoid the sunk carbon fallacy because neither metric makes per-job decisions based on the already-committed embodied carbon of the specific server assigned to it.

## Relevance to This Framework

- Directly motivates the rSCI design: the action layer uses oSCI (operational only) to avoid the sunk carbon fallacy. Embodied carbon enters only through the learned residual bridge, where it is part of the reconciliation accounting but cannot distort scheduling decisions.
- rSCI = oSCI · k (uniform rescaling), so it always preserves oSCI ordering while giving each workload its fair share of the full reported footprint.
- tSCI is the closest ancestor to rSCI — both allocate total infrastructure carbon back to individual jobs. rSCI trades the need for full bottom-up datacenter knowledge (tSCI) for a reconciliation target (the provider-reported total) and learns the gap over time.
- Supports treating PUE as a learnable parameter in the action metric rather than a fixed constant, since PUE mismatch is one source of the residual bridge.
