# §4 Experiments: Reference Toy Cloud Design

Working doc, 2026-05-17.
Not authoritative for paper claims — paraphrase into `paper.tex` once design is locked.

## Goal

A single, fully controlled simulated scenario.
We replay one week of real production LLM inference traffic onto a small heterogeneous GPU fleet, then *analyse the per-request attribution* under each metric.
No scheduling, no optimisation: §4 is about metric properties, not scheduler outcomes (if anything, we add scheudling later).
§5 then shows: real providers don't expose this granularity → the same analysis collapses.

## Framing principle

§4 demonstrates **attribution**, not **optimisation**.
We do not need to show that minimising rSCI improves outcomes; we need to show that rSCI assigns the right per-job *value* across heterogeneous server×time placements.
A single trace, three lenses (SCI / oSCI / rSCI), and we read off the properties.

## Proposition (formalised in §4, before experiments)

**Proposition (no sunk-carbon for existing hardware).**
Within a slice $(s,r)$, $\xi_{s,r}$ is workload-agnostic.
Therefore $\text{rSCI}_i = (E_{i,s,r}/R_i)\cdot\xi_{s,r}$ is monotone in $E_{i,s,r}$ at fixed $R_i$.
A scheduler minimising rSCI minimises energy at fixed output and therefore prefers the more efficient existing server.

**Corollary (low-embodied procurement reward).**
$\xi_{s,r}$ is linear in $\Delta^{\text{S3}}_{s,r}$.
Procuring lower-embodied replacement hardware shrinks $\Delta^{\text{S3}}$ and lowers rSCI for every workload in the slice.
This is automatic; no separate weighting is required.

**Remark (peak-shaving requires reweighting).**
Vanilla energy-share allocation of $\Delta^{\text{S3}}$ does not disincentivize peak usage.
Shapley/peak-share allocation (Attribution Refinements, §4) does.
The toy demonstrates both.

**Note (single-slice setup).**
Under the continuous bare-metal reservation, there is only one slice, so "$\xi_{s,r}$ is workload-agnostic within a slice" is *trivially* true.
The pedagogical content is not that fact in isolation but that *within the slice*, per-request $E_{i,s,r}$ varies by an order of magnitude across workloads and GPU types — that is where rSCI's correct gradient is visible.
The multi-slice form of the Proposition (and the case where $\xi$ legitimately differs across $(s,r)$) is what the framework supports in general and what §5 stresses; the toy is a controlled instance, not a general proof.

## Reference setup

A tiny inference provider with a **continuous bare-metal reservation** of two DGX systems, serving production-replayed LLM inference traffic over one real week (extensible to a month by swapping the trace input).
Deliberately small so the top-down report fits on one page; every aggregate line of that report ties to a sum over the bottom-up trace in a single reproducible script (the trace itself is ~44M requests, not line-auditable, but the *reconciliation* is — and that is what §4 is showing).

### Slice structure

The reservation defines a **single** rSCI slice $(s,r)$: $s$ = "the 2-DGX reservation", $r$ = us-central1.
A continuous reservation is the cleanest possible slice — no shared tenancy, no time-varying allocation, no co-tenant attribution.
Scope-1/2/3 land at the slice level as a single decomposed signal, and rSCI reconciles down to per-prefill-token within that slice.
Both Azure services run inside the slice as *labels* on requests, not as separate slices: they share the same $\xi_{s,r}$.
The A100 vs H100 contrast central to §4.1 lives entirely inside per-request $E_{i,s,r}$ (energy-per-request differs by GPU type), not across slices.

### Fleet — two DGX systems

The reservation unit is a full **NVIDIA DGX** system, not an individual card \citep{nvidia-dgx-a100-datasheet,nvidia-dgx-h100-datasheet}.
This matches the way real inference clusters are deployed (DGX SuperPOD, Azure ND-series, AWS P5 instances) and makes idle-power attribution clean — the system is reserved continuously, so the idle baseline is the same whether the workload is busy or quiet, and we apportion it across requests by time × concurrency.

| System | n_gpus | Peak power | Idle power | Embodied (full system) | Age (yr) | SCI lifetime (yr) |
|---|---|---|---|---|---|---|
| `dgx-a100` (old) | 8× A100 80GB | 6.5 kW | ~1.6 kW | **3,000 kgCO₂e (ESTIMATE, bounded)** | 6.2 (May 2020 launch → July 2026 submission) | 6 |
| `dgx-h100` (new) | 8× H100 80GB | 10.2 kW | ~2.5 kW | **4,000 kgCO₂e (ESTIMATE, bounded)** | 0 (fresh install) | 6 |

**Embodied-carbon framing** (paper boilerplate):

> *Publicly audited cradle-to-gate embodied carbon data for complete DGX-class systems is not available. We therefore use a bounded estimate derived from disclosed GPU baseboard PCFs (NVIDIA HGX H100: 1,312 kgCO₂e for the 8-GPU baseboard) and prior literature on accelerator manufacturing impacts (Falk et al. 2025: 127.6 kgCO₂e per A100 SXM 40 GB, cradle-to-gate, ISO 14040/44 + EU PEF).*

Anchors:
- **NVIDIA HGX H100 PCF Summary** \citep{nvidia-hgx-h100-pcf} (verbatim): *"the carbon footprint from cradle-to-gate for one HGX H100 GPU baseboard is 1,312 kg CO2"*. The DGX H100 adds 2× CPU, ~2 TB RAM, 8× NVMe, NVLink switches, chassis + cooling + PSUs. Industry rule-of-thumb (chassis-and-board ≈ 2–4× bare-board embodied) → DGX H100 bounded at 3–5 tCO₂e. **We adopt 4 tCO₂e** (multiplier ≈ 3.05×).
- **Falk et al. 2025** \citep{falk-2025-accelerator-lca} (arXiv:2509.00093): 127.6 kgCO₂e per A100 SXM 40 GB. 8 cards = 1,021 kgCO₂e GPU-only. Similar chassis profile → **DGX A100 estimate 3 tCO₂e** (multiplier ≈ 2.94×).

Both systems sit at a **uniform ~3× chassis-and-board multiplier** — internally consistent, mid-range within the 2–4× industry rule-of-thumb, and avoids asymmetric assumptions between the two estimates.

All numbers (including these) live in `experiments/constants.py` with citations. Edit there to retune; downstream scripts import from there.

**Age structure (SCI sunk-carbon contrast — the strongest possible).**
- `dgx-a100`: NVIDIA A100 launched 2020-05-14 \citep{nvidia-a100-launch}. Paper submission July 2026 → 6 yr 2 months past launch. Under the **provider amortisation convention** used in customer carbon tools today (AWS Model 3.0.1: 6 yr \citep{aws-ccft-model3}; Azure CHEM: 6 yr \citep{azure-chem-2026}; GCP: 4 yr — all zero out past EL), the system is fully past amortisation, so SCI's $M$-term collapses to 0 per request.
- `dgx-h100`: fresh install → full 6 yr ahead → SCI loads full embodied per request.

**Note on the M=0 reading.** The SCI specification itself is silent on $\text{TiR} > \text{EL}$: the formula $\text{TS} = \text{TiR}/\text{EL}$ has no corner-case rule, and read literally TS keeps growing past 1 (so $M$ would *increase*, not vanish, past EL). The $M=0$ past-EL reading is therefore a **provider operationalisation**, not an SCI mandate. We adopt it because it is the only operationalised reading in production today, and because it gives Bashir's sunk-carbon fallacy its empirically strongest case. The fallacy itself is a property of *flat amortisation within EL* (the per-unit-work $M$ does not respond to declining efficiency), of which past-EL $M=0$ is the limit.

Both systems host the **same open-weight model** (Llama-3-8B or similar) — isolates the hardware efficiency delta from model-mix confounds.

### Fleet sizing rationale

Trace aggregate (both services combined, 5-day overlap rate-extrapolated to 7-day): ~86.7B context tokens / week ≈ **143,000 tokens/sec average** (verified from the CSVs — see `experiments/prepare_data.py`).

Per-GPU prefill throughput on a 7-8B-class model — **ESTIMATE, bounded**. Direct per-GPU prefill measurements for Llama-3-8B-class models on A100/H100 are not published in the closest primary sources (Splitwise \citep{patel-splitwise-2024} reports prefill latency curves for OPT-30B and Bloom-176B; DynamoLLM \citep{stojkovic-dynamollm-2025} reports cluster-level throughput, not per-GPU prefill rate). The bounded values used here are drawn from open vLLM benchmark traces \citep{vllm-benchmarks} and are sanity-checked against the H100/A100 ~2.5× inference-throughput ratio reported in NVIDIA's published comparisons \citep{nvidia-h100-vs-a100-inference}:

- A100 80 GB: ~8,000 tok/s/GPU × 8 GPUs = **~64k tok/s per DGX A100**
- H100 80 GB: ~20,000 tok/s/GPU × 8 GPUs = **~160k tok/s per DGX H100**

Combined fleet capacity: ~224k tok/s vs ~143k tok/s average load → **64% average utilisation**.

**Routing: throughput-weighted, not round-robin.** Round-robin pinned the A100 above its capacity (110%) and left the H100 at 45% — not a defensible operating point for a real provider, and an artefact of the routing rule rather than the metric. Under throughput-weighted routing,

$$\Pr[\text{H100}] = \frac{160}{64+160} = 71.4\%, \quad \Pr[\text{A100}] = \frac{64}{64+160} = 28.6\%,$$

both DGXs run at the same 64% utilisation. Attribution-only analysis is now downstream of a physically sane fleet steady-state. The A100/H100 efficiency delta still shows up in Analysis 1 because per-request *energy* differs by GPU type, independent of routing share.

**Sensitivity to throughput estimates.** The exact values of $T_{A100}$ and $T_{H100}$ enter §4 only through (i) the routing weights, (ii) per-request $\gamma_g$, and (iii) idle-share denominator. The ratio $T_{H100}/T_{A100}$ matters more than the absolute values; the ratio is the well-established part. We treat the absolute values as estimates to refine when published per-GPU prefill numbers for 7-8B-class models are added to `references/sources/`.

**One DGX of each type. Two systems total.** Clean.

### Region

One region (**us-central1**). Hourly grid CI from `data/carbonintensity_2026-03-23.csv` — 24 samples averaging **299 gCO₂/kWh** (modest-CI grid, mostly natural gas + some renewables).

Trace dates (May 10–18, 2024) don't align with the CI CSV's date (2026-03-23). We anchor trace t=0 to the CI CSV's first hour and **tile the 24h CI pattern over the 7-day trace**. Placeholder until a longer real series replaces it; structurally what changes is just the time series, not the math.

**Region as a future axis.** §4 takes us-central1 as the single reference. The framework is region-agnostic; switching region (or running multiple regions in parallel) is a 1-line change once we have the data. We note in §6 (Future Work) that the operational/embodied ratio is a strong function of grid CI — see "Operational-dominance finding" below — and evaluating across regions is a natural extension.

PUE = 1.15 constant (industry-typical hyperscaler).

### Operational-dominance finding (preserve in paper)

At GPU-class compute density in a moderate-CI grid like us-central1, operational emissions dominate the reported total by an order of magnitude:

- Weekly IT energy: 2 DGXs × ~5 kW average × 168 h ≈ **1,680 kWh/week**
- S2 ≈ 1,680 × 0.30 ≈ **500 kgCO₂e/week**
- DGX embodied amortized weekly (6 yr lifetime): (3,000 + 4,000) / (6 × 52) ≈ **22 kgCO₂e/week** — about **4–5% of S2**

This is a real characteristic of GPU inference clouds, not a bug of the toy. **Implication for the paper:** SCI's wrong gradient on the embodied piece has *bounded* practical impact in operational-dominated regimes, but the *direction* is wrong, which is what disqualifies it as a metric. rSCI is *especially* clean for inference because the dominant operational signal already drives correct decisions, and the small embodied correction at least *aligns* with rather than fighting it. Worth one paragraph in §4.

**Note on the building-embodied line.** The SCI spec/Guidance is silent on the IT-hardware-vs-DC-building split (the $M$ page discusses only "hardware components"). Including building embodied in $\Delta^{\text{S3}}$ is therefore *additional* to what SCI literally requires, consistent with the GHG-Protocol Cat 2 perimeter that AWS and GCP report (Azure excludes it — see paper Table 2).

We can re-evaluate later in a cleaner-grid region (europe-west1, low-CI hours of CAISO, or a fully-renewable PPA region) where the operational/embodied ratio inverts and the sunk-carbon pathology bites harder.

### Two workloads from the real Azure 2024 traces

We use the **Azure LLM Inference Dataset 2024** \citep{stojkovic-dynamollm-2025} (HPCA 2025, arXiv:2408.00741).
Collected May 10–19, 2024 from "multiple LLM inference services in Azure" (model and hardware unspecified by the authors).
Schema: `TIMESTAMP, ContextTokens, GeneratedTokens`.

Files in `./data/`:
- `AzureLLMInferenceTrace_code_1week.csv` (~16.8M requests, May 10–16) — coding-assistant workload `code-svc`
- `AzureLLMInferenceTrace_conv_1week.csv` (~27.3M requests, May 12–18) — conversational workload `conv-svc`

Both run **inside the single slice** (the continuous 2-DGX reservation) — they are *labels* on requests, not distinct slices, and share one $\xi_{s,r}$. They differ in:
- prompt/generation size distributions (code = long prompts, short generations; conv = shorter prompts, longer generations) — widens per-request scatter in Analysis 1
- arrival-rate diurnal patterns — gives Analysis 3 a richer peak/trough structure than a single workload would
- §5 gains an extra collapse knob (per-workload labels degrade to a bucket alongside the time/resource degradations)

**No synthesis required.** The 1-week real trace already provides realistic diurnal and weekday/weekend variation. Earlier plan to envelope-synthesize from 1-hour traces is obsolete.

Alignment window for joint analysis: 5 days where both traces overlap (May 12–16, 2024). Full 7-day per-workload windows used where the analysis doesn't need joint alignment. **Month-extension path**: replace the 1-week CSVs with a tiled or re-collected 4-week trace; nothing in the slice math depends on window length.

### Routing

Routing rule fixed (not optimised) — we are analyzing attribution, not scheduling.
Default: **throughput-weighted random assignment** — Pr[H100]=71.4%, Pr[A100]=28.6%, derived in "Fleet sizing rationale" above so both DGXs share the same utilisation.
Both DGXs run continuously (continuous bare-metal reservation) — idle power is amortized across requests by time × concurrency, against the slice idle baseline.
Analysis 1's per-request scatter still separates cleanly by GPU type: per-request energy differs by $\gamma_g$ regardless of how requests are split.

### Unit of work and per-request energy: prefill-only

**Architectural framing.** We model the cluster as a **prefill-only** inference service. Following Splitwise \citep{patel-splitwise-2024} and subsequent disaggregated-serving work (DistServe \citep{zhong-distserve-2024}, Sarathi-Serve \citep{agrawal-sarathi-2024}), prefill and decode are routed to separate hardware pools. The toy is the prefill pool — the compute-bound, context-token-processing tier. This sidesteps having to model decode autoregression, KV-cache eviction, and generated-length-dependent latency — none of which we have ground truth for.

**Unit of work $R_i$ = ContextTokens$_i$** (prefill tokens processed per request).
Aggregates to "total tokens prefilled" per slice — well-defined LLM-serving denominator.

**Energy model.**
$E_i = \gamma_g \cdot \text{ContextTokens}_i + P^{\text{idle}}_g \cdot \frac{\Delta t_i}{N(t)}$
where $\gamma_g$ is per-prefill-token energy on GPU $g$, $P^{\text{idle}}_g$ is the GPU's static draw, $\Delta t_i$ is prefill duration, and $N(t)$ is concurrent in-flight requests.
Prefill is compute-bound (dense matmul), so per-token energy is GPU-throughput-dominated and well-behaved — defensible without per-request profiling. This is also where the A100 vs H100 efficiency delta is most pronounced, giving Analysis 1 its strongest signal.

**GeneratedTokens drops out of the headline.** It's a property of the decode tier we don't model. The trace exposes ContextTokens directly, no estimation needed.

**Why prefill (not decode) for the toy.** ContextTokens in the Azure trace spans roughly three orders of magnitude (~10 to ~10k+). That wide variance produces a per-request scatter that visually separates the SCI / oSCI / rSCI lines cleanly across the energy axis — pedagogically valuable for Analysis 1. Decode-only would compress the variance and weaken the figure.

**Calibration source for $\gamma_g$.** Currently bounded estimates derived from datasheet GPU TDP / per-GPU throughput: $\gamma_{A100} \approx 400\text{W} / 8000\text{tok/s} = 50$ mJ/token, $\gamma_{H100} \approx 700\text{W} / 20000\text{tok/s} = 35$ mJ/token (see `experiments/constants.py`). To refine, in order of preference:
- Splitwise \citep{patel-splitwise-2024} reports prefill phase power and latency curves — derivable per-token energy for the model classes they measure (OPT-30B, Bloom-176B). Closest fit to our architecture.
- DynamoLLM \citep{stojkovic-dynamollm-2025} reports cluster-level energy — useful as an aggregate sanity check rather than per-GPU calibration.
- vLLM benchmark suite \citep{vllm-benchmarks} — per-token prefill measurements on a range of model sizes (open source, reproducible).
None of these directly publish $\gamma$ for a 7-8B model on A100/H100; we'll either (a) re-derive from Splitwise's reported power × latency for the closest model class and adjust by parameter-count scaling, or (b) measure on vLLM ourselves and cite. **PDFs needed in `references/sources/`**: Patel-Splitwise-ISCA-2024, Stojkovic-DynamoLLM-HPCA-2025.

### Constructed top-down carbon report

We publish, at hourly slice resolution per service, decomposed into the categories below.
This is the "ideal" provider report that §4 attributes against, and that §5 will show is unobtainable in practice.

**Scope-1.** Diesel testing + refrigerant leakage for a small DC fraction. **~5–10 kgCO₂e/week** (fixed; whole slice — no allocation needed in the single-slice setup). Cite GHG Protocol Corporate Standard \citep{ghg-protocol-corp}.

**Scope-2.** $\sum_t \text{IT}_t \cdot \text{PUE} \cdot I_r(t)$. Both LBM (location-based, residual grid factor) and MBM (market-based with PPA) variants \citep{ghg-protocol-scope2} — gives us the §3 "Frankfurt LBM=0" critique a foothold in §5.

**Scope-3 (categories — needed for §4.2 to demonstrate what SCI/oSCI miss):**

| GHG Cat | Source | Estimation approach |
|---|---|---|
| Cat 2 — IT hardware embodied | GPU + (CPU + RAM + SSD + chassis if we go full-server) | Per-card kgCO₂e × cards × (1/lifetime) × (week/year) |
| Cat 2 — Building embodied | DC shell, racks, cooling infrastructure | Allocate small slice of a published DC LCA (Boavizta / Scaleway / OVHcloud factors — already in `references/`) |
| Cat 3 — FERA (upstream fuel + T&D losses) | Grid losses upstream of S2 | ~8–15% of S2 (standard; \citep{ghg-protocol-scope3}) |
| Cat 4 — Upstream transport | Shipping GPUs/chassis from manufacturer | Small fixed (cite shipping LCA factors) |
| Cat 12 — End-of-life treatment | Disposal/recycling of hardware | Small fixed; Azure includes this, AWS/GCP don't (cf. Table 2 in paper) |

Categories deliberately omitted from the toy: Cat 1 (purchased goods/services — material for a real provider, not for a 2-server toy); Cat 6/7 (travel/commute — irrelevant at this scale, but noting this is exactly what GCP includes and others don't); Cat 5 (operations waste — negligible). The asymmetric coverage by real providers (Table 2) becomes a §5 critique we can point at.

**Total expected Scope-3 share:** 30–60% of total reported emissions over the week — comparable to real provider reports, large enough that oSCI's exclusion of S3 leaves a visible gap.

Every line is reproducible from fleet + grid trace + Azure trace + energy model. Numbers committed once we pick the energy-calibration source.

### Internal representation vs plot resolution

Internally: per-request data (the basis of $w_i$ and the rSCI math).
For all time-series plots: bin to minutely or 5-minutely.
Per-request only used in Analysis 1's scatter (subsample to ~10k points for rendering).

## Analysis 1 — Sunk-carbon (existing hardware)

**Setup.** Take all requests over the week. Partition by DGX system (dgx-a100 vs dgx-h100).
For each request, compute SCI$_i$, oSCI$_i$, rSCI$_i$ (vanilla energy-share).
$R_i$ = ContextTokens (prefill-only model).

**Outputs.**
(a) Per-request scatter: request energy $E_i$ on x-axis, attributed footprint per generated token on y-axis, three series (SCI / oSCI / rSCI), points colored by GPU type. Probably faceted by service (conv vs code).
(b) Boxplot: distribution of attributed-footprint-per-token, faceted by metric × GPU type.

**Expected result.**
- SCI on dgx-a100: under the provider convention ($M=0$ past EL), every request gets $M=0$ — the strongest empirical realisation of Bashir's sunk-carbon fallacy.
Under a literal SCI reading with $\text{TiR}/\text{EL} > 1$, $M$ would grow rather than vanish; we flag this asymmetry in the figure caption so the A100 case is not read as a literal SCI claim.
The fallacy's *structural* form (flat amortisation within EL → $M$/unit-work insensitive to declining efficiency) is also visible on the H100 within its lifetime.
- SCI on dgx-h100 (fresh): full $M$ amortized over short cumulative tokens served → high per-token values.
- oSCI: monotone in energy, indifferent to system embodied profile.
- rSCI: monotone in energy AND higher on the A100 (more energy per token → larger $w_i$ → larger $\Delta^{\text{S3}}$ share). Correct gradient.

**Headline.** Identical inference requests receive *systematically wrong* SCI attributions on aged hardware; rSCI gives the right ordering and oSCI is silent on the embodied axis.
The Proposition guarantees this in general; the trace illustrates it numerically on production-realistic request mixes.

## Analysis 2 — Reconciliation

**Setup.** Same trace. Sum attributed footprints across all requests under each metric.
Compare to the toy cloud's constructed monthly top-down report.
Show per-slice breakdown (conv vs code) and the fleet total.

**Outputs.**
Stacked-bar comparison:
- Top-down report (ground truth, decomposed: S1 / S2-grid / S2-PUE / S3-embodied / S3-FERA / S3-buildings)
- $\sum_i \text{SCI}_i R_i$ — residual depends on $M$-amortization choice; show two SCI bars under different amortization assumptions to make $M$-sensitivity visible
- $\sum_i \text{oSCI}_i R_i$ — visibly missing S1 + S3 + PUE overhead. Quantify ("oSCI captures X% of reported emissions")
- $\sum_i \text{rSCI}_i R_i$ — matches top-down exactly (by construction)

**Headline.** rSCI closes a ~40–60% gap between the bottom-up operational signal and the audited top-down number; oSCI structurally cannot.
**Caveat to state in prose:** reconciliation is a mathematical identity, not an empirical finding. The empirical content is the *size* of the residual the other metrics leave unaccounted in a realistic month.

## Analysis 3 — Peak-shaving (new-hardware procurement)

**Setup.** Same trace. Partition requests by *time-of-execution* (peak vs trough hours, defined by the fleet aggregate load curve — the real Azure trace contains genuine diurnal and weekday/weekend structure).
Compute per-request rSCI under three weightings of $\Delta^{\text{S3}}$:
- vanilla energy-share $w_i = E_i / E_{s,r}$
- peak-hour-share $w_i^{\text{S3}} = E_i(t^\ast) / E_{s,r}(t^\ast)$ where $t^\ast$ is the slice peak hour
- sampled Shapley over a few hundred coalition orderings of the peak-capacity game

**Outputs.**
(a) Per-job scatter: job timing (peak/mid/trough) on x-axis, attributed rSCI on y-axis, three series (one per weighting). Possibly faceted by job type.
(b) Aggregate by job-type × weighting: how much embodied is loaded onto peak-driving jobs vs trough jobs.

**Expected result.**
- Energy-share: embodied component independent of time placement; only operational moves by grid-CI delta.
- Peak-share / Shapley: peak-running jobs carry markedly more embodied; trough jobs carry near-zero embodied.
- oSCI: silent on embodied entirely (reference line).

**Headline.** Vanilla rSCI is bookkeeping-fair but not incentive-aligned for procurement deferral; the same residual decomposition under peak-share/Shapley weighting attributes the cost of "forcing the next server purchase" to the jobs that actually drive peak.
This honest qualification of vanilla rSCI sets up §6 "Future Work" on bounded-correlation guarantees.

## Figures plan

Four figures, tight:
- Fig. 1 — the toy cloud schematic + month-long load/grid-CI strip plot (one shared context figure)
- Fig. 2 — Analysis 1 per-job scatter (or boxplot), three metrics × server-generation
- Fig. 3 — Analysis 2 reconciliation stacked bar (top-down + metric sums)
- Fig. 4 — Analysis 3 per-job attribution by time-of-execution × weighting

## §5 flip

§5 reuses the same the toy cloud trace but degrades the *report* to what real providers expose:
- Monthly aggregation only (no hourly slice → no $E_{s,r}(t)$)
- Per-service-only granularity (collapses all jobs into one bucket → no per-resource $\xi_{s,r}$)
- Revenue-allocated S3 (kills the embodied gradient: the per-job $w_i \Delta^{\text{S3}}$ signal disappears)

Re-run Analyses 1–3 on the degraded report.
Expected: all three rSCI properties collapse — Analysis 1's old-vs-new gradient flattens; Analysis 2 still reconciles in aggregate but per-job attribution is uniform; Analysis 3's peak signal vanishes.
$\widehat{\text{rSCI}}_i$ degenerates toward oSCI.

Frankfurt vignettes (existing in §5) become the empirical anchor: "this is not hypothetical — here's AWS-Frankfurt with 70% revenue-allocated 'Other'."

## Open questions before implementation

All numbers (verified and estimated) live in `experiments/constants.py` with citations.

1. **A100 card-level embodied: 127.6 kgCO₂e** (Falk et al., arXiv:2509.00093) — verified. Add PDF to `references/sources/`.
2. **HGX H100 baseboard: 1,312 kgCO₂e** (NVIDIA PCF Summary, verbatim) — verified. Add PDF to `references/sources/`.
3. **DGX A100 / DGX H100 system embodied: 3,000 / 5,000 kgCO₂e** — ESTIMATE, bounded. Anchored on (1) and (2). Adopt paper boilerplate framing (see fleet section).
4. **Per-prefill-token energy** — currently $\gamma_{A100}=50$ mJ/token, $\gamma_{H100}=35$ mJ/token in `constants.py`, derived from datasheet TDP / throughput. Calibrate against Splitwise / DynamoLLM published per-request energy.
5. **Building / DC infrastructure embodied** — currently 1.0 kgCO₂e/W IT capacity/year (Boavizta mid-range). Pull a more specific number from Boavizta / Scaleway / OVHcloud (all in `references/carbon_accounting_methodologies/`).
6. **Grid CI trace** — currently `data/carbonintensity_2026-03-23.csv` (24 h, us-central1, tiled). User will replace with a longer / different-region series later.
7. **Shapley sample budget** for Analysis 3 — 100 / 500 / 1000 orderings? With only 2 systems the system-coalition game is trivial; the interesting Shapley game is over *requests* (or request-cohorts) in the peak-capacity game. Decide based on convergence plot.
8. **Analysis window** — full 7-day week per workload; for §4.2's combined report use the 5-day overlap (May 12–16, 2024). Month extension is a trace-input swap, deferred.
9. **Region sweep** — defer to §6 (Future Work). One reference region for §4; mention region-CI sensitivity in the operational-dominance paragraph.

## What lives where

- `paper/paper.tex` — final prose + final figures. Update §4 to add Proposition + three subsections. Update §5 to reference the same setup.
- `paper/figures/` — final PDFs.
- `data/` — Azure LLM inference traces (already present: `AzureLLMInferenceTrace_conv.csv`, `AzureLLMInferenceTrace_code.csv`).
- New: `experiments/` (proposed) — plain Python scripts (not notebooks). One driver per Analysis (`a1_sunk_carbon.py`, `a2_reconciliation.py`, `a3_peak_shaving.py`), plus shared library (`picocloud.py` for fleet/trace synthesis/energy model/metric definitions). Each driver writes a PDF directly to `paper/figures/`. Reproducibility via `uv run python experiments/a1_sunk_carbon.py` etc.
- Living: this file — design notes; deprecate once experiments land.

## Implementation skeleton (proposed)

```
experiments/
  picocloud.py         # Fleet, Service, Request, energy model, metric definitions
  trace_synthesis.py   # Diurnal-envelope + Poisson + size-sampling from Azure CSVs
  metrics.py           # sci(), osci(), rsci() — per-request and aggregate
  topdown.py           # Build the constructed monthly report
  a1_sunk_carbon.py    # Analysis 1 driver → figures/a1.pdf
  a2_reconciliation.py # Analysis 2 driver → figures/a2.pdf
  a3_peak_shaving.py   # Analysis 3 driver → figures/a3.pdf
```

Why scripts not notebooks: deterministic, version-controllable, debuggable with a real debugger, reruns are `uv run` away. Notebooks only for one-off exploration (in a `notebooks/` folder, untracked) if needed.
