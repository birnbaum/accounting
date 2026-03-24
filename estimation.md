## Estimation

**Goal:** estimate the residual bridge at the reporting slice before provider actuals arrive.

### Residual Bridge

Each per-slice residual bridge $`\Delta_s`$ is a fitted scalar that captures everything the action metric does not within that slice: embodied carbon (hardware and buildings), facility overhead (PUE), idle/shared capacity, non-energy overhead (Scope 1 diesel/refrigerants, other Scope 3 categories), and allocation artifacts from provider methodology. Embodied carbon is deliberately excluded from the action layer to avoid the sunk carbon fallacy (Bashir et al., 2024) — it enters only through the residual. With monthly slice-level data, these components are not individually identifiable — the total bridge is constrained, but the breakdown is not. We therefore treat $`\Delta_s`$ as one quantity per slice fitted from historical pairs rather than pretending the components can be separated.

| Parameter | Meaning | Units / Role | Prior | Sensitivity |
|---|---|---|---|---|
| $`\Delta_s`$ | Residual bridge for slice $`s`$ | tCO₂e; fitted from historical slice pairs $`(O_s, \tilde{C}_s)`$ | Provider profile-driven | High |

### Bayesian Framing

$$
\tilde{C}_s \sim \mathcal{N}\big(O_s + \Delta_s,\;\sigma^2_s\big)
$$

- Monthly data strongly constrains the **per-slice bridge**.
- Side information (provider profiles, methodology changes) sets the prior on $`\Delta_s`$.

### Output Format

```text
Workload: web-api / region=europe-west4 / month=2026-02

Slices touched:
  Compute (n2-standard-16):  O = 6.2 tCO2e  |  Δ = 2.1 tCO2e  |  C̃ = 10.8 tCO2e
  Networking (vpc-egress):   O = 0.4 tCO2e  |  Δ = 0.2 tCO2e  |  C̃ = 1.3 tCO2e

Per workload:
  web-api (interactive):  oSCI = 0.042 kgCO2e/req   |  rSCI = 0.058 kgCO2e/req
  ml-training (batch):    oSCI = 8.7 kgCO2e/job      |  rSCI = 12.1 kgCO2e/job

Reconciliation check (per slice):
  Compute:    Σ rSCI_compute · R = 10.8 tCO2e = C̃,compute    ✓
  Networking: Σ rSCI_network · R =  1.3 tCO2e = C̃,networking  ✓

Model maturity: 8 months
Last residual error: Compute +0.3 tCO2e (2.4%), Networking +0.05 tCO2e (3.8%)
```