# Writing Plan: rSCI SoCC Vision Paper

**Status as of 2026-05-21.**
§1 prose drafted; §3 SOTA is the strongest existing section; §4 math committed;
§2 / §5 / §6 / §7 / §8 still need work.
This file is the **ordered queue** for the next sessions; update line refs and check items off as you go.

---

## Locked framing (do not relitigate without a memory write)

- Audience: operator- and scheduler-facing, not customer-facing.
- Headline critique: reconcilability. Sunk-carbon is one symptom.
- Vision contribution: the residual is a design surface for sustainable-behavior incentives.
- Worked demo: SCI's M is time-invariant per request → peak-attribution rSCI fixes this. A100/H100 routing is secondary, not the lead.
- v1 experiment plan drops scheduling; we report signal variation under fixed workload.

---

## §1 Introduction — DONE (`paper.tex:201–294`)

Prose drafted 2026-05-21. Comment scaffolding kept above the prose for reference.
**Open items**: replace `\todo` placeholders if any (none currently); revisit after §5 results to retune contribution emphasis.

---

## §2 Background — NEEDS REFRAMING (`paper.tex:296–360` post-§1-insert; verify offsets after compile)

**Currently leads with**: sunk-carbon fallacy as the structural flaw of SCI.
**Should lead with**: reconcilability as the primary critique; sunk-carbon as one symptom (per the comment TODO at the old L184–189).

Definitions still needed:
- `M` formula: now credits Gupta et al. ACT~\cite{gupta2022act} (done in this pass).
- Add 1–2 sentences citing parallel SCI critiques: `anon2026illusion` (e-Energy 2026 submission #52 — flagged friend-or-frontier), `wiesner2025marginal` (parallel critique of MCI).
- Mini-paragraph on **marginal vs. average grid CI** (4–6 sentences from `related_work_scan.md`'s drop-in paragraph). Cite `gagnon2025signals`, `wiesner2025marginal`, `sukprasert2024aermer`, `maji2023carboncast`. Decide: §2 here or §4 (recommend §2 since $I_r$ is introduced in §4 but the *concept* is methodological background).
- One sentence acknowledging the **oSCI-as-SOTA pattern** (most carbon-aware-computing optimises operational only): cite `wiesner2025qualitytime` as named example + 4–5 others (Cucumber, FedZero, CarbonScaler, Caribou, CASPER, GAIA, Ecovisor, CarbonClipper, Vitali 2026). Forward-reference §4 for why this matters.
- Cite parallel game-theoretic / Shapley attribution within a server: `han2024gametheoretic` (already cited in §4; consider a forward mention here).

**Effort**: ~1–2 hours of editing.

---

## §3 State of the Art — MINOR UPDATES (`paper.tex:360–610` approx)

The two big tables are the strongest content in the paper. Already lifts.

- **Resolve `paper.tex:500`** — DONE 2026-05-21.
- **Add Kepler, EnergAt, WattScope, Westerhof** to the non-provider-alternatives paragraph (L423–438 of pre-§1-insert; verify after re-compile). Currently mentions Boavizta + Cinergy; should also flag the per-VM attribution landscape: `amaral2023kepler`, `he2023energat`, `guan2024wattscope`, `westerhof2023allocation`.
- **Add Carbon Explorer** as the operator-side analogue of holistic operational+embodied — useful in the non-provider-alternatives paragraph: `acun2023carbon_explorer`.
- **Cite Bhagavathula et al.** when discussing $\varepsilon_p$ uncertainty (single sentence): `bhagavathula2024uncertainty`.
- **Optional**: Jay et al. CCGrid 2023 on software power-meter accuracy — adds ~1 sentence to the BoaviztAPI/Cinergy paragraph. `[new — needs adding]`.

**Effort**: ~1 hour.

---

## §4 \RSCI — CITATIONS ADDED, OPEN ITEMS REMAIN (`paper.tex:660–900` approx)

- ✅ ACT cited at M formula (done).
- ✅ Shapley 1953 + Castro 2009 + Han 2024 cited in peak-attribution paragraph (done).
- Open: the **Real-time estimation block** (paper.tex commented out around the old L716–737) needs to be rewritten or dropped. The old block assumed energy-share allocation for ALL residuals, which the new schema invalidates. **Decision needed**: rewrite under per-component schema or drop entirely and discuss only retrospectively in §4 + push real-time estimation to §6/§7. Recommend: drop from §4, recover in §6.
- Open: cite `westerhof2023allocation` and `sharma2024accountable_footprint_serverless` together in the weight-families intro as parallel allocation-rules-for-multi-tenant-DC prior.
- Open: ensure the negative-residual paragraph cites Cinergy explicitly with the 3× under-attribution figure: already done at L699–701.

**Effort**: ~2 hours (mostly the real-time-estimation decision).

---

## §5 \RSCI in Practice — NEEDS EXPERIMENTS BEFORE PROSE (`paper.tex:899–1025` approx)

This section is the empirical backbone. The two planned experiments per `paper.tex:762–812`:

1. **Synthetic toy-cloud cadence/granularity collapse** — least urgent. The §3 tables already show the structural failures; this experiment is confirmatory. Could be dropped to 1 paragraph + figure if space pressures bite.
2. **Shapley/peak-share worked example with one batch job at 12:00 vs 03:00** — **the figure that sells the vision contribution**. 50 workloads, 7 days hourly, real DE / Electricity Maps trace, three allocations (energy-share, peak-hour-share, sampled Shapley), 2×3 bar chart + total-fleet-vs-shift-fraction plot.

**Action items**:
- Implement experiment 2 first; produce the figure.
- Decide whether experiment 1 stays or compresses to a paragraph.
- The lever-vs-provider matrix (Table~\ref{tab:levers}) decision in `paper.tex:830–844` to promote to a named subsection — defer until §5 stabilises.
- Cite `sukprasert2024limits` (cadence/granularity literature) in §5 prose.
- Cite `gagnon2025signals` for the average-vs-marginal $I_r$ choice in the toy experiment setup.

**Effort**: large — experiments + figures + ~1 page of prose.

---

## §6 Closing the Gap (`paper.tex:1026–1064` approx)

Three buckets currently: provider asks, estimation techniques, standards/policy.

Open items:
- **Provider asks**: cite Microsoft S3 whitepaper for the customer-tool / corporate-disclosure non-reconciliation (already cited; add the explicit quote if space allows).
- **Estimation techniques**: cite `wiesner2025marginal`, `gagnon2025signals` for $I_r$ choice; `souza2023ecovisor` for the virtualisation-layer approach; `he2023energat` and `amaral2023kepler` for per-tenant attribution.
- **Standards and policy**: cite SBTi~\cite{sbti2024netzero}, CSRD~\cite{eu2022csrd}; add ESRS E1 if available. Add Bjørn et al. on REC integrity~\cite{bjorn2022recs} when discussing market-based-method gaps.
- One sentence on what's been resolved by 24/7 hourly matching efforts (Riepin & Brown — `[needs adding]`).

**Effort**: ~1 hour.

---

## §7 Future Work (`paper.tex:1065–1135` approx)

Currently covers: signals beyond carbon; user reporting / Scope-3 Cat-1; attribution refinements; \TSCI parallel; multi-tenant; energy-coefficient standardisation.

Open items:
- Cite `basuroy2024hidden` as the canonical multi-tenant/serverless prior the residual decomposition reshapes (paper.tex multi-tenant paragraph).
- Cite `bhagavathula2024uncertainty` in the bounded-correlation open question (already flagged in the existing `\todo`).
- Cite `gaffney2025earth` for the AI / Jevons backdrop in the signal-agnostic water/abiotic-resources discussion.
- Decide whether to keep the user-facing routing-invariance paragraph (L924–940). Memory says framing is scheduler-facing; this paragraph hedges. **Recommend**: keep as one sentence, drop the elaboration. (User explicitly pulled back from customer-facing reframing 2026-05-18.)

**Effort**: ~30 min.

---

## §8 Conclusion (`paper.tex:1136–1153` approx) + Abstract + Title — WRITTEN LAST

- §8 currently a placeholder + the GHG-Protocol-critique TODO at the old L992. **Resolve TODO**: cite `bjorn2022recs`, `holzapfel2023double`, `ma2024doublecount`, `schneider2019double`, `bashir2023hotair`, `haugen2024powermarkets` in 2–3 sentences acknowledging the underlying accounting framework's limits.
- Add `gaffney2025earth` as the "stakes are high, governance is moving" anchor.
- Then write 1 paragraph: theory closes the gap, practice does not yet, here is what to do about it.
- **Abstract**: write after §5 lands. Lead with the vision (residual-as-design-surface) per memory, then the critique, then rSCI as concrete instance.
- **Title**: pick from the commented candidates at `paper.tex:38–44`. Recommended: *"Reconcilable \SCI: Connecting Bottom-Up Sustainability Metrics with Cloud Carbon Accounting"* — front-loads the metric name, signals SoCC audience.

**Effort**: ~1 hour combined.

---

## Cross-cutting cleanups (pick up any time)

- Remove `[disable]` toggle for `todonotes` before camera-ready (`paper.tex:12`).
- Re-verify all `localfile = MISSING` notes in `references.bib` after experiments lock — pull missing PDFs from Downloads / ACM DL.
- Update `references/INDEX.md` "Missing" table — Microsoft 2021 S3 now resolved; remove from the list.
- Update `references/terminology.md` — add row for AER vs MEF vs CEF if not present.
- Update `paper/SECTIONS.md` line ranges after §1 lands and section offsets shift.

---

## Reviewer-proofing pass (last 48h before submission)

- Did we cite Han et al. 2024 next to every Shapley mention? ✅ (in §4 now)
- Did we credit ACT for the M formula? ✅
- Did we resolve the L500 TODO footnote? ✅
- Did §2 lead with reconcilability? **NO** — see §2 above. Do this before submission.
- Did we frame oSCI as SOTA explicitly and cite Quality-Time as the example? **NO** — see §2 above.
- Is the marginal-vs-average grid CI methodology discussion present? **NO** — see §2.
- Are negative residuals discussed? ✅ (L699–710)
- Does §5 have at least one figure? **NO** — implement Shapley/peak-share worked example.
- Is the abstract written? **NO** — last.
- Is the title chosen? **NO** — last.

---

## Recommended next session order

1. **Write §2 reframe** (1–2h) — invert critique order, add marginal-vs-average paragraph, add oSCI-as-SOTA paragraph. All citations are now in the bib.
2. **Run §5 Shapley/peak-share experiment + figure** (large, multi-session) — this is what sells the vision contribution.
3. **Tighten §3 + §6 + §7** with the new citations (~2h total).
4. **Write §8 conclusion + abstract + pick title** (1h).
5. **Reviewer-proofing pass**.

After step 1, the paper reads end-to-end for the first time. That's the right moment to call advisor.
