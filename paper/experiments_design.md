# §5 Controlled Demonstration — design

Working doc. Updated 2026-06-06 — see [[project-rsci-dominates-osci-framing]], [[project-experiment2-spine-vision-first]].
Not authoritative for paper claims — paraphrase into `paper.tex` once locked.
Implementation: the live marimo notebook `experiments/trace_analysis.py` (edit via the marimo session — see [[feedback-marimo-notebook-style]]).

## What we demonstrate: three benefits of rSCI

We drive the workload of a well-known carbon-aware LLM-serving paper (DynamoLLM / the Azure 2024 inference trace \citep{stojkovic-dynamollm-2025}) through SCI, oSCI, and rSCI on one heterogeneous GPU slice, and read off three benefits.
The arc is **why you need a residual (1) → adding it back is safe (2) → and it buys something new (3)**.
Benefit 3 is the vision contribution; 1 and 2 clear the ground for it.

| # | Benefit | Claim | Vehicle | Reader takeaway |
|---|---|---|---|---|
| 1 | **Completeness** | rSCI is the only per-workload metric that sums to the provider's audited total | Fig 1 — reconciliation bar | bottom-up metrics aren't imprecise, they are *structurally incomplete*; the residual is the missing mass |
| 2 | **Safety** | rSCI makes the *same* placement choice as oSCI → cannot commit Bashir's sunk-carbon fallacy | Prop 1 + worked 2-server table + Fig 2 | adding embodied back does **not** reintroduce the fallacy — provably, not by tuning |
| 3 | **Capability** | rSCI expresses a peak-deferral incentive oSCI structurally cannot | Prop 2 + Fig 3 | the residual is a *design surface*: shift off-peak → pay less → defer the next embodied-heavy server |

This is **attribution**, not **optimisation**: we never simulate a scheduler.
Claims 1 and the two propositions are *proved*; the figures show the proven properties on the real request mix.
We are not contradicting Bashir — we are *implementing* his scheduling/procurement separation inside a single metric.

**Honesty (non-negotiable).** The residual magnitude `Δ` and any multiple derived from it (the peak/quiet ratio, the reconciliation gap %) are **knobs** — report *direction and ordering*, never headline magnitudes.
The only *measured* quantities are two real **shapes**, both on the conv trace + CAISO over 2024-05-10–19, raw hourly min/max over the week: the **load swing ≈ 3.4×** and the **grid-CI swing ≈ 5.3×**.
Both series are **UTC by design** — keep UTC; relabelling to datacenter-local smuggles in a load-timezone assumption (the trace location is undisclosed — [[reference-azure-llm-trace-2024]]).

## Formal results (state in §4, before the figures)

**Setup (one slice).**
A service occupies one slice $(s,r)$: heterogeneous servers $g\in\mathcal G$ under one grid intensity $I$ and one Scope-3 residual pool $\Delta\equiv\Delta^{\text S3}_{s,r}$.
Job $i$ carries work $R_i$ (prefill tokens) and draws energy $E_i^g=\gamma_g R_i$ on server $g$, where $\gamma_g$ is per-token energy ($\gamma$ smaller $=$ more efficient).
Per-token metrics for running $i$ on $g$:
$$\text{oSCI}(i,g)=\gamma_g I,\qquad \text{SCI}(i,g)=\gamma_g I+m_g,\qquad \text{rSCI}(i,g)=\gamma_g I+\tfrac{w_i^g}{R_i}\,\Delta,$$
where $m_g=M_g/R_g^{\text{life}}$ is server $g$'s **additive, $\gamma$-independent** amortised embodied per token, and $w_i^g$ is the residual weight ($\sum_i w_i^g=1$).
Energy-share allocation: $w_i^g=E_i^g/E_{\text{slice}}\Rightarrow \tfrac{w_i^g}{R_i}\Delta=\tfrac{\gamma_g}{E_{\text{slice}}}\Delta$.

**Proposition 1 (placement-equivalence $\Rightarrow$ fallacy-free).**
Fix job $i$ and the energy $E_{\text{rest}}$ of all *other* jobs (server-independent).
Placing $i$ on $g$ gives $E_{\text{slice}}=E_{\text{rest}}+\gamma_g R_i$, so
$$\text{rSCI}(i,g)=\gamma_g I+\frac{\gamma_g\,\Delta}{E_{\text{rest}}+\gamma_g R_i}.$$
Both terms are strictly increasing in $\gamma_g$ (the second has derivative $\Delta\,E_{\text{rest}}/(E_{\text{rest}}+\gamma_g R_i)^2>0$), hence
$$\arg\min_g\ \text{rSCI}(i,g)=\arg\min_g\ \gamma_g=\arg\min_g\ \text{oSCI}(i,g).$$
rSCI always places on the most efficient available server; it can never trade efficiency for a smaller embodied charge — the move that *defines* the fallacy. $\square$

*General form.* Holds for any allocation with $w_i^g$ non-decreasing in $\gamma_g$ (energy-share, peak-share, Shapley-over-energy).
The fallacy needs an embodied term flat or *decreasing* in $\gamma_g$ (SCI's additive $m_g$); rSCI's is strictly *increasing* — the inefficient server gets a **larger** embodied charge, not a smaller one.

**Contrast (why SCI fails).**
$\arg\min_g\text{SCI}(i,g)=\arg\min_g(\gamma_g I+m_g)$.
$m_g$ is additive and uncorrelated with — for old-vs-new, *anti*-correlated with — $\gamma_g$ (worn server: large $\gamma$, small/zero $m$), so the minimiser can be the high-$\gamma$ server. Bashir's fallacy.
Prop 1 makes the rSCI result **analytical**: we never need SCI's ranking to actually flip on the GPU fleet (under operational dominance it does not — see below), so the result is immune to the embodied/operational ratio.

**Proposition 2 (temporal dominance).**
For the *timing* of a shiftable job on a fixed server $g$ — fleet peak hour $t^\ast$ vs trough $t^\circ$ — under a load-shape-sensitive (peak-share) allocation,
$$\text{[rSCI embodied]}(t^\ast)>0=\text{[rSCI embodied]}(t^\circ),$$
strictly penalising peak placement.
oSCI's charge $\gamma_g I(t)$ tracks only the grid and is invariant to the load-shape dimension (equal at $t^\ast,t^\circ$ when $I(t^\ast)=I(t^\circ)$; orthogonal to fleet-peak in general).
So rSCI expresses a **peak-deferral incentive** — fewer peak hours $\Rightarrow$ smaller required fleet $\Rightarrow$ smaller future $\Delta$ — that oSCI structurally cannot. $\square$
This is the procurement axis Bashir holds separate from scheduling (§3.3): rSCI keeps embodied *off* placement (Prop 1) and *on* capacity (Prop 2), in one metric.

**Corollary (low-embodied procurement reward).**
$\Delta$ is linear in each machine's embodied carbon.
Procuring lower-embodied replacement hardware shrinks $\Delta$ and lowers rSCI for every job in the slice — automatic, no separate weighting.
Distinct from Prop 1: that is *which existing server to place on* (embodied sunk); this is *which server to buy* (embodied live) — exactly Bashir's scheduling/procurement split.

## Benefit 1 — Completeness (Fig 1: reconciliation)

Sum the attributed footprint across all requests under each metric and compare to the constructed top-down report (decomposed S1 / S2-grid / S2-PUE / S3-embodied / S3-FERA / S3-building).
- $\sum_i\text{oSCI}_i R_i$ — visibly omits S1 + PUE overhead + all of S3.
- $\sum_i\text{SCI}_i R_i$ — adds only IT-embodied (and only when $M\neq0$); still omits S1, FERA, building, PUE overhead. Show two SCI bars under different $M$-amortisation choices to make $M$-sensitivity visible.
- $\sum_i\text{rSCI}_i R_i$ — matches the top-down total by construction.

**Reader takeaway:** the gap oSCI/SCI leave is not noise to be reduced — it is *whole categories omitted by construction* (S1, FERA, building, PUE overhead), which no parameter choice closes.
**Honesty:** reconciliation is a mathematical identity; the empirical content is *which categories* are structurally missing, not the gap's size (that scales with `Δ`, a knob). Do **not** headline a "% gap closed" number.

## Benefit 2 — Safety (Prop 1 + Fig 2)

The figure: per-token **embodied** charge by SKU across the real request mix.
- SCI on the worn `dgx-a100`: $m_g=0$ under the provider convention (past EL) → embodied charge **zero**; the worn, less-efficient server looks *cleanest* on the embodied axis.
- rSCI on the same A100: embodied charge is *higher* than the H100's (co-monotone with energy via energy-share) — the correct direction.
- oSCI: no embodied axis at all (reference line).

**Worked 2-server table** (under Prop 1, hand-computable): one job, servers {A100-old, H100-new}, show `oSCI`, `SCI`, `rSCI` per token.
Direction claim only — **SCI charges the worn server zero embodied, rSCI charges it more.**
Do **not** claim "SCI picks the A100" in this toy: at moderate CAISO intensity the operational term dominates, so SCI/oSCI/rSCI *all* rank the H100 first — the fallacy is **latent, not active**.
An active ranking flip needs a low-CI regime (Bashir forces this with $I\approx10$ gCO₂/kWh so embodied is 20% of lifecycle, §3.3); note this in the caption and that the *direction* of SCI's embodied gradient is wrong regardless of whether it flips the rank here.

**Reader takeaway:** you might fear that putting embodied back into the metric reintroduces Bashir's fallacy. Prop 1 proves it cannot — rSCI ranks hardware identically to oSCI, always.

## Benefit 3 — Capability (Prop 2 + Fig 3)

The figure (the spine): per-token carbon vs **fleet utilisation**, one line per metric.
- oSCI, SCI: flat in utilisation — charge the same per token whether the fleet is idle or maxed.
- rSCI[peak-share]: rises with utilisation — a busy fleet costs more per token, because peak load is what forces the next server purchase.

**Hold grid-CI flat (synthetic) for this figure.** The phase check (2026-06-06) found load-peak and CAISO are nearly orthogonal (Pearson +0.245; trace load peaks ~14:00 UTC, CAISO cleanest ~18–20:00 UTC).
With real CI, the oSCI line would wobble with the grid and muddy the load-shape signal. Flat CI isolates the capacity axis cleanly: oSCI flat, rSCI[peak-share] rising — unambiguously the load-shape dimension.

**Reader takeaway:** the residual is a *design surface*. Peak-share allocation turns it into a peak-deferral incentive — shift off the peak, pay less, defer the embodied-heavy next purchase — an incentive oSCI structurally cannot express.

§6 then reports the *real* CAISO phase as a bonus: oSCI follows the grid, peak-share rSCI follows the load, and on real data the two are nearly independent — so rSCI's signal is **not redundant** with oSCI's grid-following.
Sampled-Shapley and the bounded-correlation argument move to §8 Future Work; peak-hour-share is the concrete trough-rewarding allocation here.

## Setup details

**Slice.** One rSCI slice $(s,r)$: $s$ = a continuous bare-metal reservation of two DGX systems, $r$ = the reference region.
A continuous reservation is the cleanest slice — no shared tenancy, no time-varying allocation.
Both Azure services (conv, code) run *inside* the slice as request *labels*, sharing one $\Delta$; the A100/H100 contrast lives in per-request energy $E_i^g$, not across slices.

**Fleet — two DGX systems** \citep{nvidia-dgx-a100-datasheet,nvidia-dgx-h100-datasheet}. Reservation unit is a full DGX (matches DGX SuperPOD / Azure ND / AWS P5), so idle power is amortised across requests by time × concurrency against a fixed slice baseline.

| System | GPUs | Peak / Idle power | Embodied (system) | Age | SCI lifetime |
|---|---|---|---|---|---|
| `dgx-a100` (old) | 8× A100 80GB | 6.5 / 1.6 kW | 3,000 kgCO₂e (est.) | 6.2 yr (May-2020 launch → submission) | 6 yr |
| `dgx-h100` (new) | 8× H100 80GB | 10.2 / 2.5 kW | 4,000 kgCO₂e (est.) | 0 (fresh) | 6 yr |

*Both host the same open-weight model (e.g. Llama-3-8B) to isolate the hardware-efficiency delta from model-mix confounds.*

**Embodied-carbon provenance** (audit trail — no `constants.py` exists yet; numbers are hardcoded in the notebook `NODES` dict):

> *Publicly audited cradle-to-gate embodied data for complete DGX-class systems is not available. We use a bounded estimate from disclosed GPU baseboard PCFs and prior LCA literature.*

- **NVIDIA HGX H100 PCF Summary** \citep{nvidia-hgx-h100-pcf} (verbatim): *"the carbon footprint from cradle-to-gate for one HGX H100 GPU baseboard is 1,312 kg CO2"*. DGX adds CPUs, RAM, NVMe, NVLink, chassis, cooling, PSUs. Chassis-and-board rule-of-thumb ≈ 2–4× bare-board → DGX H100 bounded 3–5 tCO₂e.
- **Falk et al. 2025** \citep{falk-2025-accelerator-lca} (arXiv:2509.00093): 127.6 kgCO₂e per A100 SXM 40 GB (ISO 14040/44 + EU PEF). 8 cards = 1,021 kgCO₂e GPU-only → DGX A100 ≈ 3 tCO₂e at the same ~3× multiplier.

A uniform ~3× multiplier avoids asymmetric assumptions. **Open: pin the DGX H100 number** — this table says 4 t, the notebook `NODES` uses 5 t.

**M=0 provider convention** (the source of the worn-A100 zero-embodied case). Customer carbon tools zero embodied past end-of-life: AWS Model 3.0.1 \citep{aws-ccft-model3} and Azure CHEM \citep{azure-chem-2026} amortise over 6 yr, GCP over 4 yr — all collapse $M\to0$ afterwards.
The A100 (launched 2020-05-14 \citep{nvidia-a100-launch}) is past 6 yr at submission, so its $M$-term is 0.
*Caveat:* SCI's spec is silent on $\text{TiR}>\text{EL}$ ($\text{TS}=\text{TiR}/\text{EL}$ read literally would *grow* past 1, not vanish), so $M=0$ is a provider operationalisation, not an SCI mandate — flag in the figure caption.

**Operational dominance** (why the fallacy is latent here). At GPU density in a moderate-CI grid, operational ≫ embodied: ~1,680 kWh/week IT → S2 ≈ 500 kgCO₂e/week vs DGX embodied amortised ≈ 22 kgCO₂e/week (~4–5% of S2).
SCI's wrong embodied *gradient* therefore has bounded practical impact here, but the *direction* is wrong — which is what disqualifies it. The pathology bites harder in a cleaner-grid region (a §6/Future-Work axis).

**Unit of work & energy — prefill-only.** Model the slice as the prefill pool (Splitwise-style disaggregation \citep{patel-splitwise-2024,zhong-distserve-2024,agrawal-sarathi-2024}).
$R_i=\text{ContextTokens}_i$; $E_i=\gamma_g\,\text{ContextTokens}_i + P^{\text{idle}}_g\,\Delta t_i/N(t)$.
Prefill is compute-bound, so per-token energy is throughput-dominated and well-behaved without per-request profiling; ContextTokens spans ~3 orders of magnitude, giving Fig 2 its scatter. GeneratedTokens (decode tier) drops out.
$\gamma$ values (datasheet TDP / throughput, in the notebook): $\gamma_{A100}\approx50$, $\gamma_{H100}\approx35$ mJ/token — **estimates**; refine against Splitwise / vLLM published numbers.

**Data.** Azure LLM Inference Dataset 2024 \citep{stojkovic-dynamollm-2025} (schema `TIMESTAMP, ContextTokens, GeneratedTokens`):
`AzureLLMInferenceTrace_conv_1week.csv` (~27.3M req, May 12–18, `conv-svc`) and `..._code_1week.csv` (~16.8M req, May 10–16, `code-svc`).
Joint-analysis window = the 5-day overlap (May 12–16); per-service analyses use the full 7 days. Grid CI: `data/carbon_intensity_2024-05_azure_trace.csv` (CAISO anchor, UTC, aligned by weekday×hour). Month extension = trace-input swap.

**Constructed top-down report** (the ground truth Fig 1 reconciles against), hourly per service:
- **S1** ~5–10 kgCO₂e/week (diesel + refrigerant; whole-slice) \citep{ghg-protocol-corp}.
- **S2** $\sum_t \text{IT}_t\cdot\text{PUE}\cdot I_r(t)$, PUE = 1.15; LBM + MBM variants \citep{ghg-protocol-scope2} (feeds the §6 Frankfurt LBM≈0 critique).
- **S3** Cat 2 IT-embodied + Cat 2 building-embodied + Cat 3 FERA (~8–15% of S2) + small Cat 4 transport + Cat 12 EoL \citep{ghg-protocol-scope3}. Asymmetric provider coverage (Table 2) is a §6 hook.

Every line is reproducible from fleet + grid + trace + energy model.

## §6 reality check (not a re-run of §5)

§6 does **not** degrade this toy and re-run it. It makes the can't-compute case from real provider evidence:
- **Vignettes:** AWS Frankfurt — ~70% of reported emissions in the revenue-allocated "Other" bucket; Azure Frankfurt — location-based Scope-2 ≈ 0.
- **Lever diagnostic:** the lever-by-provider matrix — compute-efficiency structurally invisible across the Big-3.
- **Scaleway partial-existence-proof** (re-run pending): daily granularity *exists* but the daily number is flat under load and idle≈stress is confounded → the union needed to recover the signal is unrealised. *Do not write numbers until re-derived* — [[project-scaleway-partial-existence-proof]].
- **Phase nugget:** on real CAISO, oSCI (grid-following) and peak-share rSCI (load-following) are nearly orthogonal — the rSCI signal is not redundant.

Takeaway: the residual `Δ` and per-workload attribution §5 assumes as ground truth are exactly what no provider report supplies today.

## Open items

1. **Pin DGX H100 embodied** — table 4 t vs notebook 5 t. Decide and make consistent.
2. **Create `experiments/constants.py`** — the doc still references it but it does not exist; numbers currently hardcoded in the notebook `NODES`. Either build it (with citeps) or update all references to point at the notebook.
3. **Per-token energy $\gamma$** — calibrate $\gamma_{A100}/\gamma_{H100}$ against Splitwise / vLLM; add those PDFs to `references/sources/`.
4. **Building / FERA factors** — pull specific numbers from Boavizta / Scaleway / OVHcloud (in `references/`).
