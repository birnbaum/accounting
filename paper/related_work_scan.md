  # Related-Work Scan for rSCI (SoCC vision-track)

**Purpose.**
Working annotated bibliography for the rSCI vision paper.
Categories A–I follow the original task spec; the front of the document carries new per-paper summaries from the 2026-05-21 PDF read.
Per entry: citation, source location, relevance hook, paper.tex slot.

**Source tags.**
- `[in paper bib]` — already in `paper/references.bib`.
- `[dissertation.bib]` — present in `/Users/philippwiesner/Dev/dissertation/references.bib`; can be lifted verbatim into the paper bib using the bibkey shown.
- `[new — needs adding]` — not in either bib; my best-guess venue/year given and a proposed bibkey.

**Scope reminder.**
Operator/scheduler-facing, residual = design surface, vision contribution.
Three rSCI weight families: energy-share, static-share, peak-attribution (Shapley-over-peak-capacity-game with practical proxies).
Don't over-cite — pick the 1–2 highest-leverage entries per slot.

---

# Per-paper summaries (read 2026-05-21)

Each entry below is a faithful precis of a PDF read this session.
Load-bearing claims that would feed into `paper.tex` are quoted exactly with PDF §/page.

---

### `acun2023carbon_explorer` — Carbon Explorer: A Holistic Framework for Designing Carbon-Aware Datacenters
- **Authors / venue / year**: Bilge Acun, Benjamin Lee, Fiodar Kazhamiaka, Kiwan Maeng, Udit Gupta, Manoj Chakkaravarthy, David Brooks, Carole-Jean Wu. **HPCA 2023** (ASPLOS in `dissertation.bib` is wrong — verify; the arXiv source uses an acmart sigconf class but the abstract and structure match HPCA 2023, doi 10.1145/3575693.3575736 which is ASPLOS 2023 per dissertation. Keep `ASPLOS 2023` per the published record).
- **Source**: `~/Downloads/arXiv-2201.10036v3.tar.gz` (LaTeX source), bibkey `acun2023carbon_explorer` (dissertation.bib).
- **Summary**: Carbon Explorer is a design-space exploration framework that jointly optimises three knobs — investment in renewable generation, investment in battery storage, and demand-response scheduling — for the Meta production fleet across 13 geographic sites, with the explicit goal of moving from annual Net Zero (REC matching) to 24/7 carbon-free operation.
  The paper takes hourly time-series of fleet demand and grid generation as input and outputs a Pareto front trading operational against embodied carbon.
  Key load-bearing finding (1_intro.tex): "Carbon Explorer takes a holistic approach to datacenter design, balancing reductions in operational carbon against increases in embodied carbon incurred when manufacturing servers, batteries, and wind/solar farms… occasionally discovers that embodied carbon costs outweigh operational carbon reductions and identifies a solution that does not achieve 100\% coverage but is carbon-optimal."
  Site-selection finding (1_intro.tex bullets): Iowa, Nebraska, Texas have the shallowest renewable-supply valleys.
  The framework is the canonical "operator must hold operational and embodied carbon in one objective" prior — and crucially does not amortise embodied per-job: it lives in the optimisation, not the per-request metric.
- **Hooks for paper.tex**:
  - §1 motivation (L60–200): cite for the "holistic operational+embodied is what operators already do at infrastructure-planning scale — but the per-workload metric they use to drive engineering decisions doesn't reflect it" framing.
  - §3 non-provider-alternatives (L423–438): Carbon Explorer is the operator-side analogue of what rSCI does on the per-workload metric side; mention as a parallel motivation that the embodied/operational tradeoff is taken seriously in the operator community.
  - §7 future work (L915–984): when introducing "rSCI is signal-agnostic and could extend to peak-shaving / fleet-deferral analyses," Carbon Explorer is the right cite for "operator-side framework that already optimises along this axis."

---

### `HotCarbon2024GameTheoretic` — Towards Game-Theoretic Approaches to Attributing Carbon in Cloud Data Centers
- **Authors / venue / year**: Leo Han, Jash Kakadia, Benjamin C. Lee, Udit Gupta. **HotCarbon 2024** (3rd Workshop on Sustainable Computer Systems), Santa Cruz CA.
- **Source**: `~/Downloads/han24-hotcarbon.pdf`, bibkey `HotCarbon2024GameTheoretic` (dissertation.bib).
- **Summary**: Han et al. present a Shapley-value framework for fairly attributing both operational and embodied carbon within a single cloud server to its colocated workloads.
  They directly motivate the work as a fix for the failure mode rSCI invokes: existing attribution "either lack[s] embodied carbon attribution entirely [40, 41, 44] or attribute[s] simply based on billing cost, energy usage, or resource utilization quantity and time" (§2.2).
  The Shapley value is invoked precisely on the four properties rSCI also invokes: "Null Player… Symmetry… Efficiency… Linearity" (§3.1 — verbatim).
  For operational carbon, $P_i(t) = \varphi_i(p,t)$ via Shapley over the per-time power function (Eq. 2); operational footprint then integrates this against grid CI $c_i(t)$ (Eq. 3).
  For embodied carbon, the paper makes the **central rSCI-relevant move**: "We frame the problem of embodied carbon attribution as the problem of demand-driven supply provisioning for hardware" (§3.4) — i.e., the workload that drives peak demand is responsible for the embodied carbon of the marginal hardware unit.
  Per-component embodied models are given for CPU (linear in core count), DRAM (linear in capacity), mainboard (linear in peak power capacity, Eq. 10), with constants drawn from imec/ACT.
  Case study on a Dell R650 with CloudSuite 4.0 workloads shows "up to a 43% difference in workload carbon attribution compared to a baseline energy-based attribution method" (Abstract, §1).
  Scope: single-node only, with explicit acknowledgement that Shapley computation is exponential and the single-node bound is what keeps it tractable.
- **Hooks for paper.tex**:
  - §4 peak-attribution weight (L626–648): **the** prior to cite. Han et al. originate the "Shapley over peak-capacity game" framing for embodied carbon at the per-node scope; rSCI generalises it to the slice/fleet scope via the top-down residual.
  - §4 four Shapley properties (L639): cite Han et al. as the precedent for invoking the same four properties (efficiency, null-player, symmetry, linearity) on the embodied attribution problem — currently §4 names them with no citation.
  - §4 "best-effort Shapley approximation" (L638): paired cite with `sharma2024accountable_footprint_serverless`.
  - §7 multi-tenant future work (L980–984): Han et al. is explicit that single-node is a deliberate bound; rSCI gives the slice/fleet bound, and the open question is how the two regimes compose.

---

### `basuroy2024-serverless-hidden` *[new — needs adding; verify exact ACM DL key]* — The Hidden Carbon Footprint of Serverless Computing
- **Authors / venue / year**: Rohan Basu Roy, Raghavendra Kanakagiri, Yankai Jiang, Devesh Tiwari. **SoCC 2024**, Nov 20–22, Redmond, WA. doi 10.1145/3698038.3698546.
- **Source**: `~/Downloads/3698038.3698546.pdf`. Proposed bibkey: `basuroy2024hidden_serverless`.
- **Summary**: First paper to systematise carbon accounting for serverless computing.
  The central observation is that the keep-alive period — the time a function is held in server memory to avoid cold starts — incurs **embodied** carbon that conventional per-execution accounting drops on the floor.
  The paper formalises both phases (keep-alive and execution) for both embodied and operational carbon, and demonstrates that the resulting footprint estimate "can vary based on the chosen methodology" (Abstract).
  A particularly load-bearing observation for the rSCI sunk-carbon framing: "older generation hardware has lower embodied carbon and hence, results in a low keep-alive carbon footprint. Due to this, we argue that service providers may [intentionally keep older hardware for serverless]" (§1, end) — exactly the perverse incentive Bashir warns about under SCI's flat amortisation.
  The paper discusses how serverless-specific scheduling (function-to-server placement, keep-alive duration, execution location) interacts with carbon at "odds with serverless performance with respect to function service time" (§1, end).
  Aim is "standardizing methodological choices" — same agenda as rSCI but scoped to serverless.
- **Hooks for paper.tex**:
  - §3 multi-tenant / serverless (L423–438): cite as the missing SoCC 2024 multi-tenant prior INDEX.md flagged.
  - §7 multi-tenant/serverless future-work (L980–984): the canonical reference for "the residual decomposition reshapes in multi-tenant settings."
  - §2 sunk-carbon paragraph (L218–251): paired with Bashir as evidence that the sunk-carbon perverse incentive shows up empirically in serverless deployments.

---

### `patel-splitwise-2024` — Splitwise: Efficient Generative LLM Inference Using Phase Splitting
- **Authors / venue / year**: Pratyush Patel, Esha Choukse, Chaojie Zhang, Aashaka Shah, Íñigo Goiri, Saeed Maleki, Ricardo Bianchini. **ISCA 2024** (51st Annual Intl. Symposium on Computer Architecture), doi 10.1109/ISCA59077.2024.00019.
- **Source**: `~/Downloads/Patel2024.pdf`. Already in `paper/references.bib` as `patel-splitwise-2024` with `localfile = {MISSING}` — **PDF now exists, fix the bib entry**.
- **Summary**: Splitwise observes that generative LLM inference has two phases with very different hardware-utilisation characteristics: a compute-intensive prompt phase that benefits from H100's TFLOPs, and a memory-bandwidth-bound token-generation phase that runs essentially as well on A100 at lower power and cost.
  The paper proposes splitting the two phases onto separate machines and demonstrates "up to 1.4× higher throughput at 20% lower cost… 2.35× more throughput under the same power and cost budgets" (Abstract).
  Table I quantifies the asymmetry: H100 has 3.43× the TFLOPs of A100, 1.64× the HBM bandwidth, 1.75× the power, and 2.16× the rental cost.
  The relevance for rSCI is **not** the splitting algorithm itself but the **A100-vs-H100 SKU asymmetry**: choosing the right hardware for the phase changes the per-request energy by a large factor, and the per-request M term in SCI/oSCI is computed differently depending on the chosen SKU.
  Splitwise is the empirical hook for the §4 worked example that "A100 vs. H100 prefill under different SCI variants recommends different SKUs from the same trace" (paper.tex L139–143 bullet).
- **Hooks for paper.tex**:
  - §4 toy experiment / LLM trace (L749–784, also §5 if it survives): cite for the prefill/decode asymmetry; the production trace `azure-llm-inference-trace` is the companion data.
  - §1 worked example (L139–143): cite when introducing the A100 vs. H100 demonstration of allocation-variant pathology.
  - §1 motivation: cite to anchor "AI inference is the dominant emerging workload" — a credible production source.

---

### `bhagavathula2024uncertainty` *[new — needs adding]* — Understanding the Implications of Uncertainty in Embodied Carbon Models for Sustainable Computing
- **Authors / venue / year**: Anvita Bhagavathula, Leo Han, Udit Gupta. **HotCarbon 2024**.
- **Source**: `~/Downloads/10585291.pdf`. Proposed bibkey: `bhagavathula2024uncertainty_embodied`.
- **Summary**: Existing embodied-carbon models (ACT, ECO-CHIP, GreenChip, 3D-Carbon) are deterministic but the input parameters — energy-per-area (EPA), gas-per-area (GPA), yield, carbon intensity of fab grid — have substantial uncertainty.
  Figure 1 (left) shows ≥1.5× variation in carbon-per-area between imec 2020 and imec 2023 estimates for some process nodes; Figure 1 (right) shows >4× variation in per-GB SSD embodied factors across 94 LCAs.
  The paper proposes a probabilistic framework that transforms parameters into distributions and produces histogram outputs of embodied carbon, and applies it to a laptop GPU choice case study (NVIDIA RTX A3000 Mobile vs. Intel Arc Pro A60M).
  The result is that the "carbon-optimal" choice flips based on uncertainty quantiles — and the probability of making the correct choice depends on whether the system is embodied- or operational-dominated.
  Relevance to rSCI: this is the **uncertainty floor** under any ε_p model. The per-component bottom-up engine that rSCI assumes (BoaviztAPI/Cinergy/Kepler) inherits this uncertainty; the residual will reflect it on the §6 / §7 confidence-interval discussion.
- **Hooks for paper.tex**:
  - §3 non-provider alternatives (L423–438): cite as an upper bound on ε_p attainable accuracy.
  - §7 future-work bounded-correlation question (L963–970): cite as the empirical uncertainty model that any bounded-correlation claim has to absorb.

---

### `microsoft-s3-2021` — A New Approach for Scope 3 Emissions Transparency (Microsoft Cloud Supply Chain whitepaper)
- **Authors / venue / year**: Microsoft (corporate). **2021** whitepaper, "Microsoft Cloud Supply Chain Sustainability Organization in Azure," authored / signed by Anand Narasimhan (General Manager).
- **Source**: `~/Downloads/Microsoft_Scope_3_Emissions.pdf`. Bibkey already reserved in paper.tex as `microsoft-s3-2021`; resolves the verification-pending TODO at `paper.tex:500`.
- **Summary**: This is the 2021 Microsoft whitepaper introducing the Scope-3 methodology behind what became the Microsoft Emissions Impact Dashboard.
  The document describes an 8-step methodology: (1) cradle-to-gate emissions per hardware component, (2) per-datacenter monthly emissions, (3) per-region emissions, (4–7) Azure customer allocation, (8) data combination.
  **The load-bearing passage for the §3 critique** is footnote 2 on p. 2 (with the same text repeated as footnote 11 on p. 10), verbatim:
  > "Microsoft Cloud is exploring new methods for emissions reporting that Microsoft has not yet adopted in its corporate disclosure. The underlying methodologies and emissions findings generated from the calculator will differ from those reflected in Microsoft's corporate disclosure. Future updates to the methodologies supporting Microsoft's corporate disclosure will be highlighted accordingly and published annually."
  This is an explicit, signed acknowledgement by Microsoft that the customer-tool methodology and the corporate-disclosure methodology are not the same instrument — they differ in inputs, methods, and results — and the customer tool is "explor[atory]" relative to what Microsoft uses to satisfy its own GHG reporting obligations.
  The body of the whitepaper details what the customer tool covers (cradle-to-gate IT hardware, downstream M365/Azure usage allocation) and what it omits (no building embodied, no FERA, no Cat 12 in this edition; Cat 12 was added by 2025/2026 per cross_provider_synthesis.md).
- **Hooks for paper.tex**:
  - §3 internal/external gap paragraph (L496–509): **resolve the TODO footnote at L500**. The TODO text "PDF currently in references/.../azure/ is the 2018/2020 cloud-carbon study" is correct — `microsoft-cloud-carbon-study-2018.txt` is what's there; this 2021 whitepaper needs to be added to `references/carbon_accounting_methodologies/azure/` as `microsoft-scope3-transparency-2021.{pdf,txt}` and the §3 footnote-2 citation in paper.tex updated to the **exact wording above** with §/page = "p. 2, footnote 2 (and identical wording on p. 10, footnote 11)".
  - §4 / §6 — anchor for the "customer surface ≠ corporate disclosure" structural critique. The §6 provider ask "customer-tool methodology must reconcile with corporate disclosure" cites this footnote as the smoking gun that they currently don't.

---

### `wiesner2025qualitytime` — Quality-Time: A Framework for Balancing Service Quality and Carbon Efficiency
- **Authors / venue / year**: Philipp Wiesner, Dennis Grinwald, Philipp Weiß, Patrick Wilhelm, Ramin Khalili, Odej Kao. **e-Energy 2025**, doi 10.1145/3679240.3734614. Already in `dissertation.bib` as `wiesner2025qualitytime`.
- **Source**: `~/Downloads/Carbon_Aware_Quality_Adaptation_for_Energy_Intensive_Services__e_Energy_25_.pdf`.
- **Summary**: Quality-Time is a carbon-aware service-quality-adaptation framework for energy-intensive interactive services (esp. LLM inference) that have no temporal delay-tolerance, so classical time-shifting cannot apply.
  The mechanism is to adjust the fraction of requests served by high vs. low quality-tier responses as a function of grid carbon intensity; the framework formalises this with a forecast-based multi-horizon optimisation that maintains an annual carbon budget.
  Quantified saving: "up to 10%" reduction in emissions for large-scale LLM services estimated at multiple 10,000 tons CO2 annually (Abstract).
  Importantly for the §1 rSCI framing, Quality-Time explicitly "model[s] emissions from the perspective of data center operators and cloud tenants (Scope 2 and 3 reporting) and prove[s] that both models lead to equivalent" outcomes (§1, contributions list).
  But the optimisation target is the bottom-up operational footprint $E \cdot I$ — what rSCI calls $\Delta^{\text{S2}}$-driving energy share. The embodied side is not in the loss function; this is the structural "oSCI is SOTA" pattern.
  The framework is fully implemented and evaluated on real LLM serving traces.
- **Hooks for paper.tex**:
  - §1 motivation that adaptation levers exist beyond time-shifting (L60–200): cite.
  - §1 / §2 "oSCI is the SOTA" framing paragraph (see oSCI-as-SOTA framing section below): **named example, per user**.
  - §7 future work (L946–953): cite when arguing the residual framework extends to adaptation as a lever, not just scheduling.

---

### `gagnon-mowers-2025-signals` *[new — needs adding]* — Signals for Guiding Electricity Consumption to Minimize Greenhouse Gas Emissions
- **Authors / venue / year**: Pieter Gagnon (Colorado School of Mines), Matthew Mowers (NREL / independent consultant). 2025 preprint, hosted on SSRN as ssrn-5985015. Citation format (numbered superscript references) and reference style strongly suggest **submitted to / under review at Joule**; verify before citing. Treat as 2025 preprint until accepted. Proposed bibkey: `gagnon2025signals`.
- **Source**: `~/Downloads/ssrn-5985015.pdf`.
- **Summary**: The paper asks what signal a flexible-load operator should follow to minimise the GHG emissions induced by their consumption, recognising that a "real-time composite marginal emissions rate" — one that captures both operational and structural (i.e., long-run capital-investment) impacts — does not exist.
  Gagnon & Mowers use the NREL ReEDS capacity-expansion model to evaluate five heuristic signals against the "true" induced emissions over an 8-hour-daily 1%-load-shift: Average Emissions Rate (AER), Clean Energy Fraction (CEF), Curtailment, Short-Run Marginal Emissions Rate (SRMER), and Locational Marginal Price (LMP), against a flat-block reference (Table 1).
  **Headline finding**: "Average emissions rates, clean energy fractions, wind and solar generation, and marginal energy prices all performed well, reducing average induced emission by over half relative to a flat block of unguided electricity consumption — predominately by increasing demand when wind or solar is strong, and thereby allowing the grid to cost-effectively support more clean generation than it otherwise would have" (Abstract).
  Specifically (Fig. 1 / "National Signal Performance"): AER and CEF both reduce induced emissions by ~66 % and 65 % respectively vs. flat (47 and 48 kg/MWh against 140 kg/MWh baseline).
  The paper is explicit (Introduction L39–46) that no real-time composite marginal signal exists, and that the practical alternative is to use heuristics — and that AER does not perform meaningfully worse than SRMER for inducing-emissions reduction at scale.
  This is the **single strongest recent reference** for the "marginal vs. average" methodological discussion the user wants added to the paper.
- **Hooks for paper.tex**:
  - §2 or §4 (new marginal-vs-average paragraph — see new section below): the headline cite.
  - §6 estimation techniques (L897–905): when discussing what bottom-up $I_r$ should look like, Gagnon & Mowers settles a long debate by giving AER and CEF empirical legitimacy.

---

### `enskat-wiesner-2026-gpu-utilization` *[new — needs adding]* — On the Predictive Power of Compute Utilization Metrics for GPU Power Modeling
- **Authors / venue / year**: Niklas Enskat, Philipp Wiesner, Odej Kao. **Euro-Par 2026** (submission / accepted — verify). Proposed bibkey: `enskat2026gpu_utilization`.
- **Source**: `~/Downloads/EuroPar26.pdf`.
- **Summary**: Empirical study of whether Model FLOPS Utilization (MFU) can serve as a portable proxy for GPU power, vs. vendor-defined GPU Utilization counters.
  Across five GPUs and a sweep of model / batch-size / precision configurations, both metrics show "an approximately linear relationship with power" (Abstract).
  GPU Utilization is more robust globally; MFU is more accurate within compute-bound regimes.
  The takeaway is that MFU — being software-defined and computable inside a simulator like Microsoft's Vidur — is a portable predictor where hardware counters are unavailable.
  Validation includes external wall-power measurement on two systems.
  Relevance to rSCI: this is part of the ε_p estimation literature — a candidate input for bottom-up energy modelling of GPU workloads when the operator does not have telemetry. Same group's MASCOTS-2026 paper deepens the same analysis.
- **Hooks for paper.tex**:
  - §3 non-provider alternatives / ε_p engine (L423–438): cite as evidence that workload-agnostic GPU energy proxies are tractable from public metrics — relevant to the AI/GPU-cloud coverage gap (§3 mentions CoreWeave, Lambda, etc., have zero per-customer tools).
  - §4 / §5 LLM toy experiments: cite as the ε_p method for the GPU components.

---

### `enskat-wiesner-2026-mfu-mascots` *[new — needs adding]* — Evaluating MFU as a Portable Proxy for GPU Power in Energy-Aware LLM Simulation
- **Authors / venue / year**: Niklas Enskat, Philipp Wiesner. **MASCOTS 2026** (submission / accepted — verify). Proposed bibkey: `enskat2026mfu_mascots`.
- **Source**: `~/Downloads/MASCOTS2026_paper_15.pdf`.
- **Summary**: Companion to the Euro-Par paper, deeper-and-narrower: ~3000 training runs across six GPUs (incl. AMD MI210 where vendor utilisation is binary), three precisions, seven batch sizes, two context lengths.
  Key result: "A linear MFU-power model fits every GPU we measure, including AMD MI210 where vendor-reported GPU Utilization is a binary activity flag and admits no linear fit at all."
  Per-(GPU, dtype, batch-size) calibration drops MAPE from ~10 % to ~1 %; one-shot per-GPU calibration is enough to support a new accelerator.
  Conclusion: MFU is a portable, software-defined proxy for GPU power under compute-bound LLM training.
- **Hooks for paper.tex**:
  - §3 (alongside the Euro-Par paper) — cite when discussing ε_p estimation for GPU workloads.
  - §4 (LLM toy experiments) — cite as the GPU power model.

---

### `vitali-wiesner-2026-fgcs` *[new — needs adding]* — Adaptive Green Cloud Applications: Balancing Emissions, Revenue, and User Experience Through Approximate Computing
- **Authors / venue / year**: Monica Vitali (Politecnico di Milano), Philipp Wiesner, Kevin Kreutz, Roberto Gandola. **Future Generation Computer Systems** 176 (2026), article 108143. doi 10.1016/j.future.2025.108143. Proposed bibkey: `vitali2026adaptive_green`.
- **Source**: `~/Downloads/1-s2.0-S0167739X25004376-main.pdf`.
- **Summary**: A carbon-budget-constrained adaptive deployment framework for service-oriented cloud applications using approximate computing (AxC).
  The application designer expresses alternative implementations (AxC features) at function level; the runtime adjusts the deployment plan to honour a carbon budget while balancing Quality of Experience and revenue.
  Simulation-based evaluation across multiple regions, carbon budgets, and application setups.
  Relevance for rSCI: another **oSCI / operational-only** carbon-budget optimisation — the budget is over $E \cdot I$, embodied is not in the loss.
  Same Wiesner-circle pattern as Quality-Time but extended to approximate-computing levers and to a broader application-deployment-plan context.
- **Hooks for paper.tex**:
  - §1 / §2 oSCI-as-SOTA framing: another representative example of the dominant pattern.
  - §7 future work: cite as adaptation-side scheduling SOTA when arguing for residual-aware reconciliation of these existing approaches.

---

### `gaffney2025earth_alignment` *[new — needs adding]* — The Earth Alignment Principle for Artificial Intelligence
- **Authors / venue / year**: Owen Gaffney, Amy Luers, Franklin Carrero-Martinez, Berna Oztekin-Gunaydin, Felix Creutzig, Virginia Dignum, Victor Galaz, Naoko Ishii, Francesca Larosa, Maria Leptin, Ken Takahashi Guevara. **Nature Sustainability** 8 (May 2025), 467–469. Comment (editorial / policy piece). doi 10.1038/s41893-025-01536-6. Proposed bibkey: `gaffney2025earth_alignment`.
- **Source**: `~/Downloads/s41893-025-01536-6.pdf`.
- **Summary**: Policy comment proposing an "Earth alignment" principle for AI governance: the development, deployment, and use of AI must promote planetary stability, not just human safety.
  The piece is explicitly grounded in the Jevons paradox argument: "the development and deployment of AI warrant even greater concern than previous technologies affected by the Jevons paradox, requiring new governance approaches to manage this risk."
  Three criteria for strong Earth alignment: sustainable production and consumption, power-and-access equity, and social cohesion.
  On the rSCI-relevant axis: the comment notes that "the environmental impacts of the development and operations of AI models also need to be addressed. Strong Earth alignment must apply to energy and material used for AI infrastructure. AI development should aim for full decarbonization. Data centres must avoid excessive water consumption in water-stressed regions and be built for material circularity and efficiency."
  Useful for §1 framing as a high-profile, top-tier-venue source linking AI growth, rebound/Jevons, and the need for governance-level carbon accountability — the social pressure on which rSCI's argument operates.
- **Hooks for paper.tex**:
  - §1 motivation (L60–200): cite when leading with the AI demand / Jevons / planetary-stability framing. Pairs with `Bashir2024Climate`, `epri2024powering`, `Wu_SustainableAIMLSys_2022`.
  - §8 conclusion: alternative cite for the "accounting is imperfect but the stakes are high" caveat.

---

### `wiesner2026hotcarbon_curtailment` *[new — needs adding; flag as in-submission]* — Distributed LLM Pretraining During Renewable Curtailment Windows: A Feasibility Study
- **Authors / venue / year**: Anonymous (likely Wiesner et al.; based on Flower-FL + Exalsius mentions and the `wiesner@tu-berlin.de` connection). **HotCarbon 2026** submission (anonymous review). Treat as in-submission. Proposed bibkey: `wiesner2026hotcarbon_curtailment`.
- **Source**: `~/Downloads/HotCarbon26_llm_curtailment.pdf`.
- **Summary**: System / feasibility paper for full-parameter LLM pretraining (561M-param `nanochat`) across three geo-distributed GPU clusters, with cluster availability gated by renewable curtailment windows (from WattTime marginal CI traces).
  The prototype uses Flower (federated learning) and the Exalsius control plane to elastically switch between single-site training, multi-site federated training (periodic model averaging), and pause.
  Preliminary result: "curtailment-aware scheduling preserves training quality while reducing operational emissions to 5–12% of single-site baselines" (Abstract).
  Frames curtailment as a "low-carbon and low-cost" opportunity — California curtailed 3.4 M MWh of wind/solar in 2024.
  Strongly related to FedZero in spirit; the systems contribution is making the elastic + sporadic + uncertain windows work for stateful tightly-coupled training.
- **Hooks for paper.tex**:
  - §1 (lower priority — only if the paper wants a fresh scheduling-frontier cite to demonstrate that operational carbon-aware optimisation has matured well past simple ACI shifting).
  - **Flag**: this is the author's own in-submission work; cite carefully under HotCarbon-26-anonymous-review rules if relevant.
  - §7 future work: example of "scheduling on the trough" — the kind of behaviour peak-attribution weighting in rSCI would reward.

---

### `illusion-of-reduction-2026` *[new — anonymous; possible near-collision with rSCI critique; needs disambiguation]*
- **Authors / venue / year**: Anonymous. **e-Energy 2026 winter cycle** submission, paper 52.
- **Source**: `~/Downloads/eenergy26winter-paper52.pdf`. Proposed bibkey: `anon2026illusion_of_reduction` (placeholder; resolve after de-anonymisation).
- **Summary**: This paper argues that **SCI (and similar metrics combining operational+embodied) systematically mask global system footprints** because the metrics rely on implicit, under-specified assumptions about system boundaries, system context (load, utilisation), workload model (e.g., serverless vs. VM), and elasticity.
  They identify a "set of paradoxes and anomalies spanning both embodied and operational carbon accounting that arise from under-specified system models and attribution mechanisms" (Abstract).
  For embodied carbon, three causes of inconsistency are named: (a) proportional resource-allocation attribution does not conserve carbon in under-/over-committed systems, so server consolidation and right-sizing can _appear_ to reduce carbon without doing so at the system level; (b–c) two more, summarised in their taxonomy.
  Position: not to propose a new metric ("the multitude of anomalies indicates that there is no simple fix") but to call for carbon metrology to explicitly carry system boundary + context + workload + elasticity as metadata.
  Table 1 surveys recent systems-research carbon-accounting work for SCI / non-SCI use, W&T modelling, and unallocated-resource handling — concludes "SCI adoption is not universal."
  **This is a near-collision with the rSCI critique** in spirit (both attack SCI as under-specified), but the proposed remedy is **disjoint**: theirs is metadata + protocols, rSCI's is structural reconciliation to the top-down report.
  The two papers should be cited together: rSCI cites this as parallel SCI-critique work with a different (but compatible) remedy.
- **Hooks for paper.tex**:
  - §2 background (L203–267): cite as parallel SCI critique; clarify that rSCI offers a constructive structural remedy (reconciliation) where this paper offers a remediation of measurement practice (metadata).
  - §7 future work: cite when discussing the "what should standardisation look like" question.
  - **Flag**: anonymous-review; resolve identity at camera-ready and clarify whether it's friend-or-frontier prior. The framing overlap is the most significant thing to surface.

---

### `anon2026llm_inference_sustainability` *[new — anonymous, likely Wiesner-adjacent; flag]*
- **Authors / venue / year**: Anonymous. **e-Energy 2026 winter cycle** submission, paper 258.
- **Source**: `~/Downloads/eenergy26winter-paper258.pdf`. Proposed bibkey: `anon2026llm_inference_sustainability`.
- **Summary**: Empirical energy / latency / accuracy study of 14 open-source LLMs (6B–34B params) on eight benchmark datasets across four task domains (code generation, summarization, math reasoning, QA), measured on an NVIDIA A100 80GB at GPU-level with fine-grained power sampling.
  Headline finding: increasing model size often increases energy without proportional accuracy gain; mid-sized models often Pareto-dominate larger ones on energy-accuracy.
  E.g. "Phi-3-14B achieves about 31% higher accuracy while using approximately 56% less energy than Qwen-2.5-32B" for code generation (Abstract / §1).
  Task type matters: summarisation is most energy-intensive, QA least.
  Relevance to rSCI: this is an inference-side empirical companion to the §4 toy-cloud LLM experiments — useful as a citation for "AI inference energy varies by 10× across model choices" if the paper makes that claim.
- **Hooks for paper.tex**:
  - §4 LLM toy experiment (low priority): cite as evidence that LLM SKU/architecture choice carries large operational-carbon stakes — the same point Splitwise makes but for accuracy vs. energy.
  - **Flag**: anonymous; resolve identity at camera-ready. If author overlap exists with Wiesner (TUB / Khalili / etc.), declare carefully.

---

## Confirmed in paper bib (no new summary needed; PDFs in `~/Downloads/` match the entries):
- `schneider-mattia-2024` ↔ `2406.09645v1.pdf` (Schneider & Mattia GCP).
- `jacquet2025cinergy` ↔ `cinergy.pdf` (Jacquet et al., Cinergy).
- `simon2024boaviztapi` ↔ `BoaviztAPI.pdf` (Simon et al.).
- `falk-2025-accelerator-lca` ↔ `cradle-to-grave-A100.pdf` (Falk et al.).
- `bashir2024` ↔ `arXiv-2410.15087v1.tar.gz` (Bashir sunk-carbon).
- `aws-ccft-model3` ↔ `aws-customer-carbon-footprint-methodology.pdf`.
- `microsoft-chem-2026` (or whatever bibkey is in use) ↔ `Whitepaper_Cloud-hardware-emissions-methodology.pdf`.
- `ovh-eit-2025` ↔ `methodology_-_environmental_impact_tracker.pdf`.

---

## arxiv-2311.08105v3 — identification

This is **DiLoCo: Distributed Low-Communication Training of Language Models** by DeepMind (Arthur Douillard et al., Google DeepMind 2023+).
It is **not** a carbon-accounting paper.
It is the federated-LLM-pretraining algorithm the curtailment-windows paper above builds on (cited as DiLoCo / `[11]` there).
Not relevant for the rSCI bibliography directly — only if the §7 future-work paragraph wants a "distributed-training-during-clean-energy-windows" pointer; in that case, the HotCarbon-26 curtailment paper is the right cite and DiLoCo is its dependency.

---

# New section: Marginal vs. average grid carbon intensity

The user explicitly asked for a brief discussion of the various methodologies for computing grid carbon intensity, especially average (AEF) vs. marginal (MEF), and their suitability for rSCI's $I_r$ term and for carbon-aware optimisation more broadly.
This is a short lit-section ready to lift into §2 background or §4 estimation.

**Proposed paragraph (drop-in for §2 or §4, ~6 sentences).**

The grid carbon intensity $I_r$ that rSCI multiplies against bottom-up energy is itself a methodological choice, not a measurement.
The two dominant families are **average emissions rates** (AEF, sometimes also AER — average gCO2 per kWh across all generation in a balancing region) and **short-run marginal emissions rates** (MEF / SRMER — the rate of the generator that responds to an incremental MW of demand) [@maji2022carboncast, @gagnon2025signals].
The intuition that MEF is "more accurate for decisions" — because it reflects the counterfactual of an incremental load — has driven much carbon-aware scheduling literature (WattTime-style signals, ElectricityMaps' MEF feed), but recent empirical and modelling work shows the picture is more nuanced.
Sukprasert et al. (2024) on average-vs-marginal carbon-aware optimisations [@sukprasert2024average_vs_marginal] find that the choice flips the recommended schedule in many regimes; Wiesner & Kao (2025) [@wiesner2025marginal] argue that MEF is a poor metric for both accounting and grid-flexibility purposes — accounting because it does not sum to the grid's actual emissions (so a fleet of MEF-optimisers does not collectively account for fleet emissions), and flexibility because MEF reflects an instantaneous-marginal signal that does not capture structural / long-run capacity-expansion impacts.
Gagnon & Mowers (2025) [@gagnon2025signals] settle a long-standing debate by running a capacity-expansion model (NREL ReEDS) under five candidate signals (AER, CEF, curtailment, LMP, SRMER) and finding that AER and CEF both reduce induced emissions by ≈66 % and 65 % vs. flat-block — essentially indistinguishable from SRMER for inducing emissions reductions at scale, with the structural-impact piece of marginal emissions remaining ill-defined in real-time.
For rSCI, this matters because the Scope-2 anchor $C_{s,r}^{\downarrow \text{S2}}$ is reported by providers under **location-based** (LBM, average) and **market-based** (MBM, contract-specific) conventions: the rSCI residual is defined against whichever the provider publishes, and operators choosing a real-time signal $I_r$ for the bottom-up term should match the provider's convention (AEF for LBM-reconciled rSCI) to keep the residual interpretable.

**Cite list for this section** (in priority order):
1. `gagnon2025signals` — `[new — needs adding]`. Primary new source (above).
2. `wiesner2025marginal` — `[dissertation.bib]`. User-required cite.
3. `sukprasert2024average_vs_marginal` — `[dissertation.bib]`. Companion empirical study.
4. `maji2022carboncast` — `[dissertation.bib]`. CarbonCast / forecast literature; cite for the AEF forecast modelling that underpins WattTime / ElectricityMaps signals.
5. **Optional**: WattTime / ElectricityMaps reference (institutional / web; cite as `[new — needs adding]` if any concrete claim is sourced from them).

---

# New section: oSCI-as-SOTA framing

The user asked for a paragraph + cite list making the point that **almost all carbon-aware-scheduling literature optimises a metric in the oSCI class** (operational only — energy × grid CI), and that this is the current SOTA position the rSCI vision argues against.

**Proposed paragraph (drop-in for §1 or §2, ~5–6 sentences).**

Despite a decade of progress in carbon-aware computing, virtually all systems-side optimisation literature operates on a metric structurally equivalent to oSCI: the per-workload operational footprint $E \cdot I$, with embodied carbon either dropped, fixed-as-amortised, or relegated to the design-time tradeoff.
This includes temporal-shifting work for batch and ML training [@wiesner2021letswaitawhile, @Wiesner_Cucumber_2022, @wiesner2024fedzero, @hanafy2024asplos, @sukprasert2024eurosys, @lechowicz2023online, @lechowicz2024carbonclipper], spatial-shifting and CDN work [@Radovanovic_Google_2022, @gsteiger2024caribou, @murillo2024cdn_shifter, @souza2023casper], scaling and right-sizing approaches [@carbonscaler2024sigmetrics], adaptation-side work that trades quality for emissions [@wiesner2025qualitytime, @vitali2026adaptive_green], and virtualisation-layer designs [@Souza_Ecovisor_2023].
The few that take embodied carbon seriously do so at the operator-infrastructure-planning level — Carbon Explorer [@acun2023carbon_explorer] balances renewable / storage / scheduling investments against embodied — and not as a per-workload signal that can be reconciled against the provider's GHG report.
This is the failure mode the rSCI vision treats as structural: **the metric an engineer optimises is decoupled from the metric the organisation is judged on**, because no one in the operational scheduling stack carries the top-down anchor.
The community has converged on oSCI not because operational carbon is what matters but because it is what is computable from publicly-available signals — a measurement constraint that rSCI's residual decomposition is designed to relax.

**Per-cite, ≤1 sentence each:**
- `wiesner2025qualitytime` — explicit operational-only objective ("Quality-Time"); the user's named example.
- `Wiesner_Cucumber_2022` — opportunistic excess-renewable scheduling; operational metric.
- `wiesner2021letswaitawhile` — temporal shifting for delay-tolerant batch; operational ACI-weighted scheduling.
- `wiesner2024fedzero` — federated learning on excess renewable energy; operational only.
- `vitali2026adaptive_green` (Vitali/Wiesner FGCS) — carbon budget over operational footprint via approximate computing.
- `acun2023carbon_explorer` — operator-level operational + embodied; explicitly NOT per-workload; cite as the rare exception with embodied awareness.
- `Radovanovic_Google_2022` — Google CICS; production temporal-shifting; ACI-weighted operational only.
- `hanafy2024asplos` (GAIA) — operational batch SOTA.
- `carbonscaler2024sigmetrics` — dynamic scaling by grid CI; operational only.
- `sukprasert2024eurosys` — limits of spatio-temporal shifting; operational target.
- `souza2023casper` — interactive carbon-aware web; operational only.
- `Souza_Ecovisor_2023` — virtual energy system; targets operational allocation visibility.
- `gsteiger2024caribou` — geo-shifting serverless; operational only.
- `murillo2024cdn_shifter` — CDN shifting; operational only.
- `lechowicz2023online`, `lechowicz2024carbonclipper` — online algorithms for operational carbon-aware shifting; operational only.

---

# Categories A–I (updated annotated bibliography)

Updated per the new-summaries above plus the user's explicit B-list edits (drop Cucumber from must-add, add wiesner2025marginal to must-add).

## A. Embodied LCA (academic / open-data)

### A1. Gupta et al. 2021 — *Chasing Carbon* (HPCA 2021)
- `[dissertation.bib]` `gupta2021chasing`. §1, §2 sunk-carbon motivation. **High priority** (unchanged).

### A2. Gupta et al. 2022 — *ACT* (HPCA 2022)
- `[new — needs adding]`. Origin of the SCI $M$ formula. **High priority** — cite at §2 L209.

### A3. Lin, Bunger, Avelar 2023 — Scope-3 GHG of DCs (Schneider Electric report)
- `[dissertation.bib]` `lin2023scope3`. §3.

### A4. Bardon / imec — sustainable logic technologies (IEDM 2022 / imec Future Summit 2023)
- `[new — needs adding]`. Foundational fab embodied factors. Optional §3 footnote.

### A5. Falk et al. 2025 — Cradle-to-gate LCA NVIDIA A100
- `[in paper bib]` `falk-2025-accelerator-lca`. Already cited.

### A6. Switzer et al. 2023 — Junkyard Computing (ASPLOS 2023)
- `[dissertation.bib]` `switzer2023junkyard`. §2 sunk-carbon framing; §7.

### A7. Whitehead / Malmodin — early DC-LCA priors
- `[dissertation.bib]` `Whitehead2015LCA`, `Malmodin2014LCA`. Optional §3 footnote.

### A8. **NEW** Bhagavathula, Han, Gupta 2024 — *Uncertainty in Embodied Carbon Models* (HotCarbon 2024)
- `[new — needs adding]` `bhagavathula2024uncertainty_embodied`. §3 caveat on ε_p accuracy; §7 bounded-correlation discussion. See per-paper summary above.

### A9. Tannu & Nair on SSD embodied carbon variability
- `[new — needs adding]`. Cited inside Bhagavathula 2024 Fig. 1 (right) — shows 4× variation across 94 SSD LCAs. Optional depth-cite for §3.

---

## B. Carbon-aware scheduling (Wiesner self-cites + frontier)

### B1. Wiesner et al. 2021 — Let's Wait Awhile (Middleware 2021)
- `[dissertation.bib]` `wiesner2021letswaitawhile`. §1 temporal-lever motivation.

### B2. Wiesner et al. 2022 — Cucumber (Euro-Par 2022)
- `[dissertation.bib]` `Wiesner_Cucumber_2022`. **Demoted: no longer must-add** per user feedback. Still a B-category entry; cite at §1 / §7 if space permits.

### B3. Wiesner et al. 2025 — Quality-Time (e-Energy 2025)
- `[dissertation.bib]` `wiesner2025qualitytime`. §1 contributions; §1 oSCI-SOTA framing (named example per user).

### B4. Wiesner et al. 2024 — FedZero (e-Energy 2024)
- `[dissertation.bib]` `wiesner2024fedzero`. §1 / §7 (lower priority).

### B5. Wiesner & Kao 2025 — Moving Beyond Marginal Carbon Intensity (CarbonMetrics @ SIGMETRICS 2025)
- `[dissertation.bib]` `wiesner2025marginal`. **PROMOTED to must-add** per user. §2 marginal-vs-average paragraph; §6 estimation-techniques discussion.

### B6. Radovanović et al. 2022 — Google Carbon-Intelligent Computing System (IEEE TPS 2022)
- `[dissertation.bib]` `Radovanovic_Google_2022`. §1 motivation; §6.

### B7. Acun et al. 2023 — Carbon Explorer (ASPLOS 2023)
- `[dissertation.bib]` `acun2023carbon_explorer`. **High priority** (now with per-paper summary). §1, §3, §7.

### B8. Hanafy et al. 2024 — GAIA (ASPLOS 2024)
- `[dissertation.bib]` `hanafy2024asplos`. §1 batch-scheduling SOTA.

### B9. Hanafy et al. 2024 — CarbonScaler (SIGMETRICS 2024)
- `[dissertation.bib]` `carbonscaler2024sigmetrics`. §1 / §5.

### B10. Sukprasert et al. 2024 — Limitations of Carbon-Aware Spatio-Temporal Shifting (EuroSys 2024)
- `[dissertation.bib]` `sukprasert2024eurosys`. §1.

### B11. Souza et al. 2023 — CASPER (IGSC 2023)
- `[dissertation.bib]` `souza2023casper`. §1.

### B12. Souza et al. 2023 — Ecovisor (ASPLOS 2023)
- `[dissertation.bib]` `Souza_Ecovisor_2023`. §6.

### B13. Gsteiger et al. 2024 — Caribou (SOSP 2024)
- `[dissertation.bib]` `gsteiger2024caribou`. §1.

### B14. Lechowicz et al. 2023 — Online Pause and Resume (POMACS / SIGMETRICS 2023)
- `[dissertation.bib]` `lechowicz2023online`. §1 (lower priority).

### B15. Lechowicz et al. 2024 — CarbonClipper
- `[dissertation.bib]` `lechowicz2024carbonclipper`. §1 (lower priority; pick GAIA or CarbonClipper, not both).

### B16. Murillo et al. 2024 — CDN-Shifter (SoCC 2024)
- `[dissertation.bib]` `murillo2024cdn_shifter`. §1 (lower priority).

### B17. Hanafy et al. 2023 — The War of the Efficiencies (HotCarbon 2023)
- `[dissertation.bib]` `hanafy2023war_of_efficiencies`. §1 or §4.

### B18. Sukprasert et al. 2024 — On the Implications of AER vs MER (e-Energy 2024)
- `[dissertation.bib]` `sukprasert2024average_vs_marginal`. **NEW priority** for the marginal-vs-average paragraph.

### B19. **NEW** Vitali, Wiesner, Kreutz, Gandola 2026 — Adaptive Green Cloud Applications (FGCS 2026)
- `[new — needs adding]` `vitali2026adaptive_green`. §1 oSCI-SOTA framing; §7. See per-paper summary above.

### B20. **NEW (in-submission)** Wiesner et al. 2026 — HotCarbon 2026 LLM Curtailment Pretraining
- `[new — needs adding; in submission]` `wiesner2026hotcarbon_curtailment`. §1 / §7 if a fresh scheduling-frontier cite is wanted. Flag anonymous-review.

### B21. Sukprasert et al. 2024 / Bashir et al. — average-vs-marginal discussion
- Pair `B18` with `B5` (`wiesner2025marginal`).

---

## C. GHG accounting critique / RECs / 24-7 / market-based

### C1. Bjørn et al. 2022 — RECs Threaten Targets (Nature Climate Change)
- `[dissertation.bib]` `Bjorn_RECThreatenTargetsNature_2022`. **High priority**. §8 TODO at L992.

### C2. Bashir et al. 2023 — Sustainable Computing Without the Hot Air (SIGENERGY Energy Informatics Review)
- `[dissertation.bib]` `bashir2023hotair`. §8.

### C3. Holzapfel, Bach, Finkbeiner 2023 — Electricity accounting in LCA / double counting (IntJ LCA)
- `[dissertation.bib]` `Holzapfel2023`. §8.

### C4. Riepin & Brown — 24/7 carbon-free energy hourly matching
- `[new — needs adding]`. Best candidate: Riepin & Brown, *Joule* 2024 (verify exact title; "Mean-field market modelling of 24/7 carbon-free electricity procurement," arXiv 2403.xxxxx) — verify before citing.

### C5. Haugen et al. 2024 — Power market models for the clean-energy transition (Applied Energy)
- `[dissertation.bib]` `haugen2024powermarketmodels`. §8 depth-cite.

### C6. Brander — Market-based vs. location-based critique (Energy Policy 2018 + follow-ups)
- `[new — needs adding]`. Foundational MBM critique; pairs with Bjørn.

### C7. Ma et al. 2024 — Double-counting in carbon accounting
- `[dissertation.bib]` `ma2024Double`. §8.

### C8. Schneider 2019 — Double-counting in scope-2
- `[dissertation.bib]` `Schneider2019Double`. §8.

### C9. **NEW** Microsoft 2021 — A New Approach for Scope 3 Emissions Transparency (whitepaper)
- `[new — needs adding]` `microsoft-s3-2021`. **Highest priority for §3 internal/external gap paragraph** — resolves the TODO at paper.tex L500. See per-paper summary above. The exact footnote-2 quotation should be cited.

### C10. **NEW** Gagnon & Mowers 2025 — Signals for Guiding Electricity Consumption
- `[new — needs adding]` `gagnon2025signals`. **Highest priority for the marginal-vs-average paragraph**. See per-paper summary above.

### C11. Items flagged for user disambiguation (carried over):
- "Miller et al." — multiple candidates; please specify.
- "Xu et al." — cannot pin down; please specify.

---

## D. Per-VM / per-workload power attribution (deeper than Cinergy/Boavizta)

(User note: skip Zeus.)

### D1. Amaral et al. 2023 — Kepler (IEEE CLOUD 2023)
- `[dissertation.bib]` `Amaral2023Kepler`. **High priority**. §3, §4.

### D2. Choochotkaew et al. 2023 — Container Power Model Training (MASCOTS 2023)
- `[dissertation.bib]` `Choochotkaew2023CloudSustainability`. §3 supporting cite for Kepler.

### D3. He, Friedman, Rekatsinas 2023 — EnergAt (HotCarbon 2023)
- `[dissertation.bib]` `He2023EnergAt`. **High priority** for multi-tenant attribution discussion. §3 / §7.

### D4. Guan et al. 2024 — WattScope (SIGMETRICS PER)
- `[dissertation.bib]` `Guan2024WattScope`. §3 alternative ε_p engine.

### D5. Schmidt et al. 2023 — carbond (HotCarbon 2023)
- `[dissertation.bib]` `Schmidt2023carbond`. §3 / §6.

### D6. Westerhof, Atherton, Andrikopoulos 2023 — Allocation Model for Multi-Tenant DCs
- `[dissertation.bib]` `Westerhof2023AllocationModel`. §4.

### D7. Han, Kakadia, Lee, Gupta 2024 — Game-Theoretic Attribution (HotCarbon 2024)
- `[dissertation.bib]` `HotCarbon2024GameTheoretic`. **Top must-add** — closest prior to rSCI's peak-attribution weight. See per-paper summary above. §4.

### D8. PowerAPI / SmartWatts
- `[new — needs adding]`. Colmant et al. EuroSys 2015 + Fieni et al. CCGrid 2020.

### D9. CodeCarbon (Lacoste et al. 2019)
- `[new — needs adding]`. arXiv:1910.09700.

### D10. Henderson et al. 2020 — experiment-impact-tracker (JMLR 21, 2020)
- `[new — needs adding]`.

### D11. Jay et al. 2023 — Experimental Comparison of Software-Based Power Meters (CCGrid 2023)
- `[new — needs adding]`. **High priority** — sharpens the ε_p caveat by showing accuracy varies by an order of magnitude across CodeCarbon / Kepler / Scaphandre / PowerAPI / SmartWatts.

### D12. Scaphandre — `[new]` repo cite; pair with Jay 2023.

### D13. **NEW** Enskat & Wiesner 2026 — Predictive Power of Compute Utilization Metrics for GPU Power (Euro-Par 2026)
- `[new — needs adding]` `enskat2026gpu_utilization`. **High priority for GPU ε_p discussion.** See summary.

### D14. **NEW** Enskat & Wiesner 2026 — MFU as Portable Proxy for GPU Power (MASCOTS 2026)
- `[new — needs adding]` `enskat2026mfu_mascots`. Companion to D13.

---

## E. DC energy at scale (motivation numbers)

### E1. Masanet et al. 2020 — Recalibrating Global DC Energy-Use Estimates (Science)
- `[dissertation.bib]` `Masanet_RecalibratingGlobalDCEnergyEstimates_2020`. **Must-have** §1.

### E2. Shehabi LBNL US DC reports
- `[new — needs adding]`. Shehabi et al. 2016 LBNL-1005775 + 2024 update. **Top must-add** §1.

### E3. EPRI 2024 — Powering Intelligence
- `[dissertation.bib]` `epri2024powering`. §1.

### E4. Koomey on PUE
- `[new — needs adding]`. Koomey & Masanet, Joule 2021 "Does not compute" — high-leverage critique cite.

### E5. Uptime Institute Annual Survey
- `[dissertation.bib]` `uptimeinstitute2023`. §2.

### E6. IEA Electricity 2024 — Data Centres outlook
- `[new — needs adding]`. §1 alternative.

### E7. Bashir et al. 2024 — Climate and Sustainability Implications of Generative AI (MIT Exploration)
- `[dissertation.bib]` `Bashir2024Climate`. §1.

### E8. **NEW** Gaffney et al. 2025 — Earth Alignment Principle for AI (Nature Sustainability comment)
- `[new — needs adding]` `gaffney2025earth_alignment`. §1 Jevons + AI motivation. See summary.

---

## F. AI / LLM carbon

### F1. Patterson et al. 2021 — Carbon Emissions and Large NN Training (arXiv 2104.10350).
- `[dissertation.bib]` `patterson2021carbon_large_nn`. §1.

### F2. Patterson et al. 2022 — Carbon Footprint of ML Training Will Plateau, Then Shrink (IEEE Computer)
- `[dissertation.bib]` `Google_CarbonFootprintMLShrink_2022`. §1 counter-narrative.

### F3. Strubell, Ganesh, McCallum 2019 (AAAI 2019/2020)
- `[dissertation.bib]` `Strubell_EnergyConsiderationsDLResearch_2020`. §1.

### F4. Wu et al. 2022 — Sustainable AI (MLSys 2022)
- `[dissertation.bib]` `Wu_SustainableAIMLSys_2022`. §1 (bridges A + F).

### F5. Luccioni, Viguier, Ligozat 2024 — BLOOM (JMLR)
- `[dissertation.bib]` `luccioni2024estimating_bloom`. §1.

### F6. Luccioni, Jernite, Strubell 2024 — Power Hungry Processing (FAccT 2024)
- `[new — needs adding]`. Inference-not-just-training framing. §1 / §3.

### F7. Li, Yang et al. 2025 — Making AI Less Thirsty (CACM 2025)
- `[new — needs adding]`. §7 water signal.

### F8. Stojkovic et al. 2025 — DynamoLLM (HPCA 2025)
- `[in paper bib]` `stojkovic-dynamollm-2025`. §4 / §5 trace source.

### F9. Chien et al. 2023 — Reducing Carbon Impact of Generative AI Inference (HotCarbon 2023)
- `[dissertation.bib]` `chien2023carbonimpact_AI_inference`. §1.

### F10. Li, Samsi, Gadepally, Tiwari 2023 — Clover (SC 2023)
- `[dissertation.bib]` `li2023clover`. §1.

### F11. Faiz et al. 2024 — LLMCarbon (ICLR 2024)
- `[dissertation.bib]` `faiz2024llmcarbon`. §1.

### F12. Samsi et al. 2023 — From Words to Watts (HPEC 2023)
- `[dissertation.bib]` `Samsi2023FromWT`. §4.

### F13. Li et al. 2024 — Uncertainty-Aware Decarbonization for DCs (HotCarbon 2024)
- `[dissertation.bib]` `li2024uncertaintyAwareCarbonDatacenters`. §6 / §7.

### F14. Sandalow et al. 2025 — Sustainable DC Roadmap (ICEF)
- `[in paper bib]` `sandalow-2025-icef-roadmap`. Already cited.

### F15. **NEW** Patel et al. 2024 — Splitwise (ISCA 2024)
- `[in paper bib]` `patel-splitwise-2024` (fix `localfile = MISSING`). §1 worked-example + §4 trace.

### F16. **NEW** anon e-Energy 2026 #258 — LLM Inference Sustainability
- `[new; anonymous]` `anon2026llm_inference_sustainability`. §4 (lower priority). Flag.

---

## G. Multi-tenant / serverless carbon

### G1. **NEW** Basu Roy, Kanakagiri, Jiang, Tiwari 2024 — Hidden Carbon Footprint of Serverless (SoCC 2024)
- `[new — needs adding]` `basuroy2024hidden_serverless`. **Top must-add** — closest SoCC prior. See per-paper summary. §3 / §7.

### G2. Sharma & Fuerst 2024 — Accountable Carbon for Serverless (SoCC 2024)
- `[in paper bib]` `sharma2024accountable_footprint_serverless`. Core cite.

### G3. He, Friedman, Rekatsinas 2023 — EnergAt. See D3.

### G4. Westerhof et al. 2023 — Allocation Model. See D6.

### G5. Han, Kakadia, Lee, Gupta 2024 — Game-Theoretic. See D7.

### G6. Shahrad et al. 2020 — Serverless in the Wild
- `[dissertation.bib]` `Shahrad_CharacterizingServerless_2020`. §7.

---

## H. Reporting standards beyond GHGP

### H1. SBTi 2024 — Corporate Net-Zero Standard v1.2
- `[dissertation.bib]` `stbi2024`. §6.

### H2. EU CSRD — Directive 2022/2464
- `[dissertation.bib]` `eu2022csrd`. §6.

### H3. SEC Climate Disclosure Rule analysis — Deloitte 2024
- `[dissertation.bib]` `deloitte2024SEC_analysis`. §6.

### H4. CDP cloud category
- `[dissertation.bib]` `cdp2024`. §6.

### H5. ESRS E1
- `[new — needs adding]`. §6 footnote alt.

### H6. **NEW** Microsoft 2021 Scope-3 Whitepaper
- See C9 above. Cite in §3, not §6.

---

## I. Cooperative-game-theory / cost-sharing

### I1. Shapley 1953 — A Value for n-Person Games (Contributions to the Theory of Games II)
- `[new — needs adding]`. **Must-cite at L632 / L638.**

### I2. Tijs & Driessen 1986 — Game theory and cost allocation (Management Science 32(8))
- `[new — needs adding]`. Optional depth-cite §4.

### I3. Sharma & Fuerst 2024 — Shapley in FaaS. See G2 (paper bib).

### I4. Han, Kakadia, Lee, Gupta 2024 — Game-theoretic attribution. See D7.

### I5. Castro, Gómez, Tejada 2009 — Sampled-Permutation Shapley (Computers & OR 36(5))
- `[new — needs adding]`. Cite at L646 (sampled-permutation proxy).

### I6. Optional: Maleki, Tran-Thanh, Hines, Rahwan, Rogers — Bounding the Shapley value approximation error (sampling-based)
- `[new — needs adding]`. Would underpin a future-work bounded-correlation guarantee (paper.tex L963–970).

---

## Dissertation prose worth lifting (line refs) — unchanged from prior

Liftable from `/Users/philippwiesner/Dev/dissertation/`:
- **1-intro.tex L5–11**: opening hyperscaler energy growth bullets — drop-in §1 opening.
- **1-intro.tex L14–18**: end-of-Moore framing — useful §1 backdrop.
- **1-intro.tex L20–25**: Jevons / rebound.
- **1-intro.tex L33–35**: CSRD / SEC / SECR / Japan / carbon pricing — §6 standards backdrop.
- **2-background.tex L36–47**: embodied definition with ISO 14040, Lin 2023, Junkyard, Wu — §2 background.
- **2-background.tex L86–96**: REC-as-greenwashing critique (Bjørn + Holzapfel + bashir2023hotair) — drop-in for §8 TODO at L992.
- **2-background.tex L114–118**: operator-vs-tenant reporting split with `[HotCarbon2024GameTheoretic, Amaral2023Kepler, He2023EnergAt, ...]` — perfectly aligned with §7 Scope-3 Cat-1 framing.
- **3-related.tex L13–20**: temporal-shifting paragraph for §1 lever-exists backdrop.
- **4-problem.tex L297–299**: clean-grid → demand-side flexibility argument — §1.
- **8-conclusion.tex L29–33**: structural / policy barriers + rebound caveat — §8.

---

# Top must-add list (expanded; ranked)

No 10-item cap. Format: rank — bibkey — 1-line rationale — slot.

1. **`HotCarbon2024GameTheoretic`** (Han, Kakadia, Lee, Gupta 2024) — closest prior to rSCI's peak-attribution weight; cites the four Shapley properties verbatim. §4 peak-attribution paragraph. `[dissertation.bib]`.
2. **`microsoft-s3-2021`** (NEW summary above) — resolves the §3 L500 TODO; exact footnote-2 quotation available. §3 internal/external gap. `[new — needs adding]`.
3. **`Bjorn_RECThreatenTargetsNature_2022`** — Nature CC critique of RECs; §8 TODO L992. `[dissertation.bib]`.
4. **`acun2023carbon_explorer`** — canonical embodied+operational holistic prior. §1 / §3 / §7. `[dissertation.bib]`.
5. **`gagnon2025signals`** (NEW summary above) — primary new source for the marginal-vs-average paragraph. §2 / §4. `[new — needs adding]`.
6. **`wiesner2025marginal`** — user-required; consistency of position with rSCI critique. §2 / §6. `[dissertation.bib]`.
7. **`basuroy2024hidden_serverless`** (NEW summary above) — closest SoCC prior; multi-tenant SoCC 2024 entry INDEX.md flagged. §3 / §7. `[new — needs adding]`.
8. **`patel-splitwise-2024`** — already in paper bib (with `localfile = MISSING`); now PDF available; fix the bib entry and cite at §1 worked example + §4 LLM trace. `[in paper bib; fix localfile]`.
9. **ACT (Gupta et al. HPCA 2022)** — origin of SCI's $M$ formula; currently uncredited at paper.tex L209. §2. `[new — needs adding]`.
10. **`Amaral2023Kepler`** — deployed industry attribution stack; §3 alongside BoaviztAPI/Cinergy. `[dissertation.bib]`.
11. **Shapley 1953 + Castro/Gómez/Tejada 2009** — foundational refs for §4 Shapley + sampled-permutation proxy. `[new — needs adding]`.
12. **Shehabi LBNL 2024 US DC report** — strongest single quantitative motivation cite if §1 leads with demand growth. `[new — needs adding]`.
13. **Jay et al. 2023 — Experimental Comparison of Software-Based Power Meters (CCGrid 2023)** — sharpens §3 ε_p caveat by showing across-tool variance. `[new — needs adding]`.
14. **`bhagavathula2024uncertainty_embodied`** (NEW summary) — uncertainty in embodied carbon estimates; §3 caveat; §7 bounded-correlation discussion. `[new — needs adding]`.
15. **`He2023EnergAt`** — multi-tenant attribution on one host; pairs with G1. §3 / §7. `[dissertation.bib]`.
16. **`gaffney2025earth_alignment`** (NEW summary) — Nature Sustainability comment; §1 Jevons / AI motivation. `[new — needs adding]`.
17. **Luccioni 2024 — Power Hungry Processing (FAccT)** — inference-not-just-training. §1 / §3. `[new — needs adding]`.
18. **`Westerhof2023AllocationModel`** — multi-tenant DC allocation rules. §4. `[dissertation.bib]`.
19. **`vitali2026adaptive_green`** (NEW summary) — oSCI-as-SOTA example; §1 / §2 framing paragraph. `[new — needs adding]`.
20. **`enskat2026gpu_utilization` + `enskat2026mfu_mascots`** (NEW summaries) — GPU ε_p engines for §3 / §4 LLM toy experiment. `[new — needs adding]`.
21. **`anon2026illusion_of_reduction`** (NEW summary; anonymous) — parallel SCI critique. §2 background / §7. `[new — needs adding; resolve anon]`. **Flag near-collision in framing.**
22. **`sukprasert2024average_vs_marginal`** — companion to wiesner2025marginal for §2 average-vs-marginal paragraph. `[dissertation.bib]`.
23. **`wiesner2025qualitytime`** — explicit oSCI-SOTA named example (per user). §1 framing. `[dissertation.bib]`.
24. **`Wu_SustainableAIMLSys_2022`** — bridges A + F; §1. `[dissertation.bib]`.
25. **`carbonscaler2024sigmetrics`** — the rare lever (right-sizing) that already moves provider-reported carbon. §1 / §5. `[dissertation.bib]`.
26. **`hanafy2024asplos` (GAIA)** — single representative scheduling SOTA cite for §1. `[dissertation.bib]`.
27. **`Wiesner_Cucumber_2022`** — DEMOTED to non-must-add per user; keep as B-category entry only.

---

# Ambiguous / anonymous downloads (user decision needed)

- `eenergy26winter-paper52.pdf` — **The Illusion of Reduction: How Software Carbon Metrics Mask Global Footprints** (anonymous). Parallel SCI critique with disjoint remedy (metadata, not reconciliation). **Strongly recommend citing**, ideally after de-anonymisation. My read: friend-or-frontier prior; the two papers can co-exist on the same SoCC programme.
- `eenergy26winter-paper258.pdf` — **Assessing the Sustainability of LLM Inference through Energy–Accuracy Analysis** (anonymous). Empirical inference-energy study. Possibly relevant to §4 LLM toy experiments. Lower-priority cite; defer until de-anonymised.
- `HotCarbon26_llm_curtailment.pdf` — likely Wiesner et al.; **in submission**. Cite carefully under HotCarbon-26 review rules; only if §1 / §7 needs a fresh scheduling-frontier example.
- `EuroPar26.pdf` / `MASCOTS2026_paper_15.pdf` — Enskat & Wiesner. Citing self-cites at submission stage is fine but flag both at camera-ready depending on acceptance status.

---

# What else might be missing — proposals for the user

Based on reading the priority PDFs, the following sources are likely worth adding to `references/` but were not in `~/Downloads/`:

1. **Bjørn 2024 follow-up** — A. Bjørn, S. Lloyd, M. Brander, H. M. Matthews, "Climate response of REC-bundled vs. additional clean-energy procurement," — likely 2024 follow-up to the 2022 *Nature Climate Change* paper. Verify.
2. **Tannu & Nair — *Toward a Sustainable Future for SSDs*** (specific paper that contributed the 94-SSD-LCA dataset cited in Bhagavathula 2024 Fig. 1, right). Likely ASPLOS or HPCA 2022/2023.
3. **Gupta et al. — ACT** (HPCA 2022) — confirm full bib entry. Should be added regardless.
4. **NREL ReEDS documentation** (cited by Gagnon & Mowers) — Standard Scenarios 2024 report, Annual Technology Baseline 2024. Reference these as datasets in §2/§6 grid-CI discussion.
5. **ElectricityMaps API methodology** — institutional cite for AEF/MEF data sources rSCI's $I_r$ depends on.
6. **Google Cloud — *Carbon footprint methodology for AI Inference workloads*** — Feb 2026 update (the source for the §3 footnote-c "GCP attributes AI-inference emissions directly to associated services at the SKU level since Feb 2026" claim). Should already be in `references/carbon_accounting_methodologies/gcp/`; verify.
7. **Open Compute Project Sustainability Working Group** — published per-component LCA factors that align with BoaviztAPI / Falk; cite as standards backdrop in §6.
8. **EnergyStar Server program v4.0** — references baseline server-efficiency methodology relevant to PUE / idle-baseline discussion in §2.
9. **IEA 2024 — Electricity 2024 outlook** (Data Centres section, January 2024). Verify; should be in `references/sources/`.
10. **Riepin & Brown 2024 (Joule)** — 24/7 carbon-free electricity mean-field modelling. Confirm exact title and venue.
11. **Lin Liuzixuan et al. — Exploding AI Power Use** — already in dissertation.bib as `lin2024exploding_ai_power`; could be promoted to §1 if AI Jevons framing is centred.
12. **Patterson et al. 2024 — Energy and Carbon of Training Frontier Models** — Google 2024 follow-up; likely separate from F1/F2 above. Verify; possibly important.
13. **Aslan et al. 2018 — Electricity Intensity of Internet Data Transmission** — under-cited but useful for the "what part of electricity is computing" tally in §1.
14. **Anders et al. 2024 — How Cloud Providers Decarbonise: A Comparative Study** — sometimes-cited industry survey; verify if it exists in a peer-reviewed venue.
15. **Bashir, Irwin, Shenoy 2025 — *Carbon Containers* or related follow-up to Sunk Carbon Fallacy** — verify whether Bashir has a 2025 follow-up the rSCI paper should cite.

---

# Notes on overlaps with existing paper bib

Entries already in `paper/references.bib` that don't need re-adding (carry over):
- `bashir2024`, `schneider-mattia-2024`, `greensku-2024`, `sharma2024accountable_footprint_serverless`, `simon2024boaviztapi`, `jacquet2025cinergy`, `stojkovic-dynamollm-2025`, `falk-2025-accelerator-lca`, `sandalow-2025-icef-roadmap`, `patel-splitwise-2024` (fix localfile), `aws-ccft-model3`, `microsoft-chem-2026`.

---

# Items still flagged for user disambiguation (carried + new)

- "Miller et al." (C7 in prior scan) — multiple candidates; please specify.
- "Xu et al." (C8 in prior scan) — cannot pin down; please specify.
- "Lin et al." — Liuzixuan Lin (Chien co-author, `lin2024exploding_ai_power`) vs. Pengfei Li (`li2024equitable_ai_geographic`); please specify.
- "Maji" — `maji2022carboncast` (CarbonCast) confirmed; if a different Maji is intended, please specify.
- "Bostandoost" — `hanafy2023war_of_efficiencies` co-author; if a separate paper, please specify.
- Acun et al. *Carbon Explorer* venue — dissertation.bib says ASPLOS 2023, arXiv source uses acmart sigconf — confirm against ACM DL before camera-ready.
- All three anonymous e-Energy 2026 / HotCarbon 2026 submissions (`paper52`, `paper258`, `llm_curtailment`) — resolve anon status before citing.
