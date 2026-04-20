# Vision Paper Framing Note

Working title candidates: *Reconcilable Carbon Accounting for Cloud Software* / *Closing the Reconcilability Gap: From SCI to rSCI*.
Target venue: **HotCarbon** (primary — forgiving of lighter empirical section, 6 pages) or **SoCC vision track** (secondary).

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
*   **Thesis:** carbon metrics for software must be *reconcilable by design*. Reconcilability forces any bottom-up metric to carry a residual term. We propose **rSCI** as the first worked-out metric in this class — solving the framework (reconciliation + sunk carbon) while instantiating one concrete parameterization that the community can refine.

**Contributions (to finalize):**
1.  Argument that reconcilability is a first-class requirement for software carbon metrics, not a separate concern from real-time action.
2.  Survey of the cloud carbon accounting landscape (27 providers evaluated; only Y report customer-level carbon; coarse, delayed, fallback-dominated) exposed through a reconcilability lens.
3.  **rSCI**: an extension of the SCI → oSCI → tSCI taxonomy that fixes the sunk carbon fallacy *and* reconciles with top-down provider reports via residual bridges.
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

### 5. Making rSCI Computable: Asks on the Provider Contract
Reframed from earlier "implications" list. We acknowledge up front: **rSCI is currently not fully computable** on any major provider, because of exactly the failures documented in §3 — the "Other" bucket swallows the signal, Azure's Scope 2 = 0 breaks location-based reconciliation, and fallback allocations are revenue/cost-driven rather than physical.

*   **Ask 1 — Granular reporting with fewer fallbacks:** allocate the "Other" bucket via physical telemetry (power, utilization) rather than revenue. Report at finer granularity (per resource, per hour where feasible).
*   **Ask 2 — Methodological fidelity:** exports must match published methodology. Azure's documented location-based Scope 2 should actually appear in the exported data.
*   **Ask 3 — Transparency on embodied and overhead allocation:** providers should make the decomposition visible enough that $\Delta^{S2}$ and $\Delta^{S3}$ can be estimated, not just the top-line number.
*   These are the minimum conditions under which rSCI becomes a live, auditable metric. Without them, it remains a theoretical construct — and every other per-workload carbon metric remains disconnected from the corporate report.
*   This is our honest evaluation story: not "we measured rSCI on real workloads," but "rSCI is currently blocked by specific, nameable provider methodology failures — and those failures are themselves the evidence that reconcilability is the right requirement."

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
    *   What is the right cadence for residual updates — monthly (matching top-down reports) or finer?
    *   How should $\mu$ and $\rho$ be audited?
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
