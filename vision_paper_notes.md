# Reconcilable Software Carbon Intensity: Bridging Cloud Carbon Accounting and Actionable Metrics

Target venue: **SoCC vision track** (6 pages).

## Framing decision: "solves the framework, instantiates the parameterization"

Reconcilability forces a residual-based structure on any bottom-up metric: if the bottom-up signal must sum to the top-down total, a residual term is mathematically unavoidable.
**rSCI solves the framework problem** — it is the first worked-out metric that (a) closes the reconciliation gap by construction and (b) dodges the sunk carbon fallacy by allocating embodied carbon per-unit-energy rather than per-unit-work.
**rSCI instantiates one concrete parameterization** of that framework — the split between $\mu$ and $\rho$, the choice to allocate $\Delta$ per-unit-energy at service level, the monthly residual cadence, are design decisions, not theorems.
The community's job is to refine the parameterization and pressure providers to make it computable.

This framing is reflected in §1 (thesis), §4 (math-forward, claims the theorem-level contributions), §5 (honest about computability), and §7 (invites alternatives to the specific parameterization, not to the requirement).

## Proposed structure

### 1. Provocation
*   Sustainability-aware and carbon-aware scheduling, placement, and architectural decisions need **actionable, understandable, real-time** carbon metrics.
*   The ISO-adopted **Software Carbon Intensity (SCI)** standard (GSF, now ISO/IEC 21031) is the industry's answer for per-workload carbon.
*   Known flaws have been pointed out — most notably the **sunk carbon fallacy** (Bashir et al., SoCC 2024), where embodied-carbon accounting rewards running on old inefficient hardware.
*   More fundamentally: SCI numbers **do not reconcile** with the organization's corporate carbon report.
    *   When reporting and action diverge, engineers produce *Invisible Efficiency* (saved MWh that never appear in the ESG report) and firms produce *Carbon Washing* (accounting shifts that look like physical ones).
    *   The Green Software Foundation explicitly frames "measuring for reporting" and "measuring for action" as separate concerns; we argue this dichotomy is a failure mode, not a design principle.
    *   An optimization signal that doesn't land in the corporate footprint will not be funded, audited, or sustained at scale.
*   **Thesis:** carbon metrics for software must be *reconcilable by design*. Reconcilability forces any bottom-up metric to carry a residual term. We propose **rSCI** as the first worked-out metric in this class — **solving the framework** (it closes the reconciliation gap by construction *and* dodges the sunk carbon fallacy) while **instantiating one concrete parameterization** that the community can refine. The parameterization is not rigid: rSCI's precision scales along three axes — bottom-up model quality, top-down reporting granularity, and unit-of-work definition — with the residual $\Delta$ shrinking as each improves.

**Contributions (to finalize):**
1.  Argument that reconcilability is a first-class requirement for software carbon metrics, not a separate concern from real-time action.
2.  Survey of the cloud carbon accounting landscape (27 providers evaluated; only Y report customer-level carbon; coarse, delayed, fallback-dominated) exposed through a reconcilability lens.
3.  **rSCI**: an extension of the SCI → oSCI → tSCI taxonomy that fixes the sunk carbon fallacy *and* reconciles with top-down provider reports via residual bridges. Precision scales with infrastructure observability and reporting granularity.
4.  Concrete asks on cloud providers — identified from rSCI's computability requirements — that would make reconcilable per-workload carbon feasible.
5.  Demonstration that a bottom-up reconcilable signal exposes *upstream* methodology flaws: the lever × provider matrix showing which optimization actions actually move the reported number today, and where providers (notably Azure) break the contract.

### 2. The SCI Taxonomy and the Sunk Carbon Fallacy
*   Define SCI (GSF / ISO): carbon per unit of work, covering operational *and* embodied carbon.
*   Bashir et al.'s taxonomy refinement:
    *   **SCI** — includes embodied carbon; vulnerable to sunk carbon fallacy.
    *   **oSCI** — operational only; sensitive and real-time, but blind to facility overhead, idle capacity, and embodied share.
    *   **tSCI** — total; folds embodied carbon back in; re-inherits the sunk carbon behavior.
*   Explain the sunk carbon fallacy in detail: amortized embodied carbon shrinks on older hardware, so the per-unit-work number *drops* as the machine ages and gets less efficient — rewarding exactly the wrong placement decision.
*   None of SCI/oSCI/tSCI was designed with reconciliation to top-down reports in mind. That is the opening we fill.
*   (No GHG Protocol scopes or provider-reported numbers introduced yet — those arrive in §3.)

### 3. How Cloud Carbon Accounting Actually Works
The survey/methodology chapter. Structured as a reconcilability lens on existing accounting practice, not as a general survey.

*   **Landscape** (from our provider review): **27 cloud providers** evaluated; only **Y** offer any form of customer-facing carbon accounting. Of those, most report monthly, with weeks of delay, at service-level granularity, and only a handful offer raw exports (BigQuery, CCFT CSV, Azure Emissions Impact Dashboard).
*   **Methodologies in detail** (draw from `HYPERSCALER_CARBON_ACCOUNTING.md`):
    *   **AWS CCFT** — quarterly, service-level; uses revenue-based allocation for non-foundational services ("Other" bucket).
    *   **GCP Carbon Footprint** — monthly, service/region level; Schneider & Mattia 2024 methodology; cost-based fallback when usage allocation unavailable.
    *   **Azure Emissions Impact Dashboard** — monthly; methodology claims location+market-based Scope 2, exports contain only market-based.
    *   Cross-cutting: hardware amortization choices (GCP 4yr vs. AWS 6yr) and usage-vs-telemetry allocation create "greener" clouds by accounting alone.
*   **Why this is considered useless for optimization today:**
    *   Delay (weeks to quarter).
    *   Granularity (service × region × month; no per-workload, per-hour, per-request signal).
    *   Fallback allocations (revenue, cost) that are insensitive to engineering action.
*   **Vignette 1 — AWS "Other" = 70%:** in our two AWS use cases, ~70% of reported emissions fall into "Other" (revenue-allocated), only ~30% in "Compute." No amount of Lambda/DynamoDB optimization moves the reported footprint unless the bill moves.
*   **Vignette 2 — Azure Scope 2 = 0:** Azure's methodology documents both allocation types, but the exported data contains only market-based Scope 2; location-based is effectively 0, erasing grid-intensity-driven optimization signals.
*   **Takeaway for §4:** this is why SCI-style bottom-up metrics *have* to exist — but also why any bottom-up metric that ignores reconciliation is destined to stay a hobby.

### 4. rSCI: Reconciling Bottom-Up and Top-Down
Mathematically precise. The theory is the contribution, since experiments are limited.

*   **Setup:** For workload $i$ on service $s$, region $r$, a provider reports top-down $C^{top}_{s,r}$ (monthly, coarse). A bottom-up usage model gives $E_{i,s,r} = \sum_p q_p \cdot \varepsilon_p$ energy and a naive operational footprint $C^{op}_{i,s,r} = E_{i,s,r} \cdot I_r$ where $I_r$ is grid intensity.
*   **Residual bridges:** Define $\Delta^{S1}$, $\Delta^{S2}$, $\Delta^{S3}$ such that the per-workload rSCI sums, across all workloads on the service, equal the reported $C^{top}_{s,r}$.
    *   $\Delta^{S2}$ absorbs PUE, idle capacity, market-vs-location adjustments.
    *   $\Delta^{S3}$ absorbs embodied and provider-side supply-chain carbon.
    *   $\Delta^{S1}$ absorbs on-site fuel combustion (usually small).
*   **Effective intensity:** $\xi_{s,r} = I_r + \Delta/E_{s,r}$, or in real-time decomposition form $\xi = \mu \cdot I_r + \rho$ (Scope 2 multiplier + non-electricity intensity).
*   **Why this solves the sunk carbon fallacy:** embodied carbon lives in $\Delta^{S3}$, allocated per-unit-energy at the service level. Older, less efficient hardware *increases* energy per unit work, so the per-workload rSCI *rises* — the opposite of SCI/tSCI behavior. Routing to legacy hardware stops looking green.
*   **Why this solves reconciliation:** by construction, $\sum_i rSCI_i \cdot w_i = C^{top}_{s,r}$. The bottom-up signal is *defined* as consistent with the top-down report.
*   **What it preserves:** the oSCI real-time sensitivity. The $I_r$ term still moves with grid intensity and workload energy; the $\Delta$ term is the audited anchor.
*   Connect each property back explicitly to §2 (sunk carbon) and §3 (fallback allocations, delay, granularity).

### 5. Making rSCI Computable: The "Billing Frequency" Contract
Reframed from earlier "implications" list. We acknowledge up front: **rSCI is currently not fully computable in real-time** on any major provider, because of the failures documented in §3 — notably the delay and low frequency of top-down reporting (monthly).

However, we argue that the solution is not for providers to expose proprietary datacenter telemetry. Instead, the fix requires aligning carbon reporting with financial billing.

*   **Ask 1 — Carbon at Billing Frequency:** Financial billing (e.g., AWS CUR) provides hourly, resource-level granularity. Top-down carbon reporting must match this frequency. Monthly sampling is fundamentally incompatible with the rate of application churn, preventing real-time state estimation.
*   **Ask 2 — Granular reporting with fewer fallbacks:** allocate the "Other" bucket via physical telemetry (power, utilization) rather than revenue. Report at finer granularity (per resource, per hour where feasible).
*   **Ask 3 — Methodological fidelity:** exports must match published methodology. Azure's documented location-based Scope 2 should actually appear in the exported data.

If providers fulfill Ask 1 (hourly/daily top-down reporting), rSCI becomes computable without requiring providers to expose their internal PUE or embodied carbon metrics. High-frequency reporting unlocks the use of standard state-estimation techniques (like Kalman filters) to derive these values dynamically (see §7).

This is our honest evaluation story: not "we measured rSCI on real workloads," but "rSCI is currently blocked by specific, nameable provider methodology failures — and those failures are themselves the evidence that reconcilability is the right requirement."

### 6. Upstream Effects: A Reconcilable Bottom-Up Signal Exposes Provider Flaws
The lever × provider matrix as the centerpiece of this section. The point: a reconcilable metric makes provider methodology choices *visible and challengeable* in a way that top-down-only reporting never did.

*   **The lever × provider matrix:**
    *   Rows: optimization levers — compute efficiency, temporal shifting, spatial shifting, right-sizing, architecture choice.
    *   Columns: AWS, GCP, Azure.
    *   Cells: `direct` / `approximate` / `structural_mismatch`.
    *   Punchline: **compute efficiency reconciles nowhere.** The signal engineers care about most is invisible in every provider's report.
*   **Azure critique:** Azure's Scope 2 = 0 export breaks spatial shifting and grid-intensity optimization entirely; its methodology/export mismatch is a concrete case of a provider *choosing* to be unreconciled.
*   **AWS critique:** revenue-based allocation for the "Other" bucket turns code-level optimization into bill-level optimization, which collapses carbon accounting into price accounting.
*   **GCP:** most methodologically honest of the three; still uses cost-based fallbacks where usage data is missing.
*   Broader claim: without a bottom-up reconcilable framework like rSCI, these provider-side methodology choices are invisible to the customer. rSCI doesn't just serve engineers — it gives the rest of the accounting ecosystem a lens to push back on providers.

### 7. Discussion / Call to Action (short)
*   Reconcilability is a *requirement*, not a feature. The residual-bridge structure is forced by it; rSCI is the first worked-out metric carrying that structure.
*   What is open (and what we invite the community to take up): the *parameterization* of the framework.
    *   Is per-unit-energy the right $\Delta$ allocation, or should it follow $vCPU \cdot h$ or other physical proxies?
    *   What is the right cadence for residual updates — monthly (matching current top-down reports) or billing-frequency (hourly)?
    *   **Cross-tenant pooling & state estimation.** If providers adopt billing-frequency carbon reporting, the sampling rate outpaces workload churn. This unlocks Kalman filters or distributed Bayesian state estimation over pooled cross-tenant $(E_{\text{bottom-up}}, C_{\text{top-down}})$ tuples to reverse-engineer region-level $\mu$ and $\rho$ without providers exposing proprietary infrastructure. **TODO:** synthetic / toy convergence experiment to show the estimator behaves under realistic sampling rates and churn — reviewers will ask.
    *   **Auditability of $\varepsilon_p$.** How do we standardize the energy coefficients used in the bottom-up model so rSCI is comparable across organizations?
    *   How do multi-tenant and serverless settings reshape the decomposition? (Hook to Basu Roy et al.)
    *   Who owns the resulting standard — GSF, GHG Protocol, a joint effort?
*   The requirement is non-negotiable; the metric is a first draft.

## Data story (internal — do not write in paper)

*   Two AWS use cases → vignette 1 in §3 and ammunition for §6 AWS critique.
*   Azure export data showing Scope 2 = 0 → vignette 2 in §3 and ammunition for §6 Azure critique.
*   27-provider review + populated `SCHEMA.md` profiles → §3 landscape and §6 lever-matrix.
*   No multi-partner dataset. Framed as vision; data limitation must not appear as a caveat — the contribution is conceptual (taxonomy extension + reconcilability requirement) supported by targeted evidence and the "rSCI not yet computable" honest-limitation framing in §5.

## Relationship to prior work

*   **Bashir et al. 2024 (SoCC vision):** established SCI/oSCI/tSCI and the sunk carbon fallacy. rSCI extends their taxonomy; we credit them explicitly.
*   **Basu Roy et al. 2024 (SoCC, "Hidden Carbon Footprint of Serverless"):** pointer for hidden carbon patterns and for the multi-tenant / serverless open question in §7.
*   **Schneider & Mattia 2024 (Google):** official GCP top-down methodology. We *consume* their output to build Δ; not competing.
*   **GSF "reporting vs. action" post:** foil in §1.

## Risks / open tensions

*   Reviewers may ask for evaluation we don't have. Our answer: §5 reframes the lack of evaluation as itself the evidence — rSCI is blocked by the exact failures that motivate the paper.
*   Tone risk: the "solves the framework, instantiates the parameterization" split must be held consistently — drift toward pure "solves" overclaims deployability, drift toward pure "instantiates" gives up the theorem-level wins.
*   Vendor-naming: Azure S2=0 and AWS "Other"=70% both name providers. Frame as *structural failure classes* any provider could exhibit, using AWS/Azure as instances.

## Findings and ideas to POTENTIALLY integrate (from May 2026 discussion)

Recorded here so they survive the next round of restructuring; existing §1–§7 structure preserved for now.

**Empirical findings from the AWS Frankfurt case study (9 months, single customer):**
- Of total reported emissions: **30.1%** attributable to EC2 (the only telemetry-modelable service), **69.9%** to "Other" (revenue-allocated).
- Within reported emissions: **64.4%** is Scope 2 LBM (the only slice grid-intensity optimization can touch); **35.6%** is Scope 1 + Scope 3 (S1 tiny, S3 ≈ 35%).
- Three-tier reachability decomposition: **19.8% addressable** (EC2 S2 LBM) / **10.3% visible but electricity-inelastic** (EC2 S1+S3) / **69.9% invisible** (Other, all scopes). Figure exists: `paper/figures/reachability_bound.pdf`.
- **$\xi_{s,r}$ stability**: addressable share ranges 61.3–67.5% across 9 months despite ~10× variation in absolute emissions (0.005 → 0.058 mt). Cheap positive empirical hook supporting the real-time-estimation claim in README §"Real-time Estimation".
- Illustrative-but-not-yet-derived: realistic temporal-shifting ceiling ≈ 2% of reported footprint (needs intra-day Frankfurt grid-intensity variance); spatial shifting FRA→ARN ceiling ≈ 17% (needs FRA vs ARN LBM factor differential). TODO substantiate before claiming in paper.

**Sharper thesis candidate (alt-framing, not yet committed):**
"Carbon-aware computing optimizes for grid intensity, but provider methodologies can only resolve a small fraction of customer emissions at that granularity, so the field is structurally capped on its effect on the *reported* footprint." rSCI demotes from "the contribution" to "the diagnostic framework that exposes the ceiling and concretizes the asks." Foil shifts from GSF "reporting vs. action" to the carbon-aware computing literature itself (Wiesner, Radovanović, Acun, Lin et al.). Provisional title: *"The 20% Ceiling: Why Carbon-Aware Computing Cannot Move the Numbers Its Cloud Provider Reports."*

**Three-stakeholder agenda (alt to current §7 framing):**
Each stakeholder controls one missing piece. (1) Carbon-aware computing research: broaden beyond $E \cdot I$ to actions that target provider-resolvable terms — embodied amortization via right-sizing/longevity, idle-capacity reduction, hardware-aware placement; validate gains against reconcilable metrics. (2) Providers: billing-frequency reporting; eliminate revenue allocation in favor of physical telemetry; publish methodology at reconciliation granularity. (3) GHG reporting standards: close LBM/MBM gap without erasing the grid-intensity signal carbon-aware computing depends on. Goal: metrics whose improvement provably contributes to grid decarbonization and renewable-heavy grid stability — a property no current carbon-aware metric has.

**Data story updates:**
- Add GCP case study (best-in-production contrast to AWS's worst-case). Without it, reviewers will say AWS is an outlier.
- The 19.8% / 69.9% numbers are N=1. Defense options: (a) frame the *decomposition* as universal even if the *number* is case-specific; (b) GCP case to bound the spectrum; (c) cite any provider-published aggregate statistics on "Other"-share if they exist.

**New risk:**
- Single-customer generalization. Reviewers will hammer this. The decomposition framework (addressable / visible-inelastic / invisible) is universal; the percentages are not. Hold this distinction explicitly.

**GHG-reporting critique (to draft as §7 sketch, do not formalize):**
Brief paragraph: LBM vs MBM divergence, contractual instruments (PPAs, EACs) decoupled from physical generation, hourly matching debates. Cite RW. Mark as future work, not contribution.

