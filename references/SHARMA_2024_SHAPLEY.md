# Sharma & Fuerst 2024 — Shapley-based fair attribution for FaaS

Authoritative short summary of *"Accountable Carbon Footprints and Energy Profiling For Serverless Functions"* (SoCC '24).
PDF: `sources/accountable-carbon-footprints-serverless.pdf`.
Cite as `sharma2024accountable_footprint_serverless`.

## Scope and method

FaaS / serverless per-invocation **energy and carbon** footprints, computed in-situ and online.
Three building blocks: statistical power disaggregation (§4.1), Kalman-filter online updates (§4.2), and Shapley-based fair attribution (§5).
Implemented in the Iluvatar control plane.

## Statistical disaggregation (§4.1)

Contributions matrix $C$ has $M$ columns (functions) and $N$ rows (time intervals); $C[i][j]$ is the time function $j$ was running during interval $i$.
Per-function power $X$ solved by linear regression:
$X_{\text{Full}} = \min_X |CX - W|$ … (their eq.\ 1), with $W$ the system-wide power measurement.

Control plane normalised by system-wide CPU share (their eq.\ 2): $c_{cp} = \frac{\text{control plane CPU\%}}{\text{system-wide CPU\%}} \cdot \delta$.

## Kalman filter online updates (§4.2)

Their eq.\ 3: $\hat X_i = \alpha \hat X_{i-1} + \beta U_i + K Z_i$, with $\alpha$ memory, $\beta$ innovation weight, $\gamma$ latency-variance weight; $K$ is the Kalman gain.
Used to track drift across reconciled time windows without offline pre-training.

## Shapley fair attribution (§5) — the part that matters most for rSCI

**Exact Shapley is infeasible online.** §5 verbatim: *"computing Shapley values requires sampling an exponential number of energy readings ... Exact Shapley values are thus infeasible and impractical, especially considering measurement noise and under an online setting. Instead, we approximate the Shapley values by satisfying its four properties in a best-effort manner."*

The four Shapley properties they approximate (citing Winter [110] for theory):
1. **Efficiency** — per-function footprints sum to total system energy (minimised via the Kalman filter).
2. **Null-player** — non-executing functions get $0$ energy (by construction of $C$).
3. **Symmetry** — identical functions get identical footprints.
4. **Linearity** — total shared-resource energy attributed = sum of individual shared-resource energies.

### Three allocation rules for three classes of shared cost (§5)

Their eq.\ 4: $J_{\text{Shap}} = J_{\text{Indiv}} + \phi_{cp} + \phi_{\text{idle}}$.

| Shared cost | Rule | Their justification |
|---|---|---|
| Function's own energy $J_{\text{Indiv}}$ | direct attribution from disaggregation | the workload caused it |
| Control plane $\phi_{cp}$ | proportional to invocation frequency $A_i/\sum A$ | "dynamic" shared resource; cost scales with how many calls |
| Idle power $\phi_{\text{idle}}$ | even share, $J_{\text{idle}}/M$ over $M$ active functions | "static" shared resource; cite Islam & Ren [66] for datacenter-power Shapley |

Their eq.\ 5 (carbon): $C_{\text{Shap}} = k \cdot J_{\text{Shap}} + e/M$, with embodied rate $e = \mathcal{E}\cdot N/\mathcal{L}$ (server lifetime embodied $\mathcal{E}$, lifetime $\mathcal{L}$, interval $N$).
**Embodied is divided evenly among $M$ active functions, irrespective of how much of the server they use.**

### Explicit position on embodied vs.\ SCI (§5, "Comparison with SCI")

Verbatim: *"the main difference in the SCI metric is that it considers embodied emissions as a usage-based cost, whereas we believe that embodied emissions are more appropriately viewed as static sunk costs."*
Their formulation: $C_{\text{SCI}} \approx J_{\text{Server}}(k + e) \cdot r$ where $r = A_i \tau_i / \sum_{i \in M} A_i \tau_i$ is the function's usage fraction.

Stated incentive consequences of static-cost framing:
- **Favours locality** — co-locating functions on the same server spreads embodied, reduces cold-start cost.
- **Popular functions naturally amortise embodied** anyway via high invocation frequency, so the embodied tax does not over-penalise them.
- **Splitting a function into two doubles the dynamic control-plane cost and the per-invocation embodied "tax"** — incentivises consolidation rather than micro-splitting.

### Validation framing (§6.1)

Primary external validation metric is **marginal energy** as ground truth: $\mathcal{M}_f = (\mathcal{J}(\mathcal{T}(\mathcal{S})) - \mathcal{J}(\mathcal{T}(\mathcal{S}-f)))/\text{invocations}$ (their eq.\ 7).
Primary internal validation metric is **cosine similarity** between predicted and ground-truth footprint vectors; total-error (sum-of-footprints vs.\ measured total) is secondary.

## What rSCI inherits from this

1. The **vocabulary of three cost classes** — usage-proportional, frequency-proportional, static-shared — is exactly the per-residual-component schema rSCI needs in §4.
2. The **"approximate Shapley by satisfying its four properties"** pattern is the precedent for declaring rSCI's residual-allocation weights as a Shapley approximation rather than promising an exact game-theoretic computation.
3. The **embodied-as-static-cost** position (with named incentive consequences) is a directly citable prior for rSCI's argument that energy-share is the wrong default for $\Delta^{\text{S3-embodied}}$.

## What rSCI does *not* inherit

- Sharma's even-share embodied allocation makes sense in a single-server / single-slice FaaS context where peak-driving is not the question. It does **not** encode the peak-vs-trough gradient that rSCI's vision contribution needs.
  rSCI uses Sharma's static-cost framing for $\Delta^{\text{S1}}$ and the non-IT Scope-3 residuals (building, freight, EoL), but uses a **peak-share / Shapley-over-peak-capacity-game** weight for $\Delta^{\text{S3-embodied-IT}}$ to expose the temporal incentive.
- Sharma operates strictly bottom-up (no reconciliation against a top-down provider report). rSCI's residual bridge is orthogonal to their framework, not derived from it.

## Limitations Sharma flag explicitly (§5.1, §6)

- Focus on individual functions; multi-function applications approximated as sum of components (no joint attribution).
- Networking and storage not yet covered (server-level only); these will need additional fair-division work.
- Power models are deliberately simple/linear for generalisability — better fidelity needs deep CPU models, not in scope.
- "Fairness issues" in carbon accounting (who pays for past embodied) flagged as outside scope (§5).
