# Discussion sketch: rSCI as a class of metrics

Working note, 2026-05-21.
Drafted from the §4 experiment discussion; rework into paper voice when §X discussion section is written.

## Paragraph 1 — rSCI is a class, not a single metric.

rSCI is parameterised by a choice of weight family per residual component, and the choice is editorial — operators reveal what they want to incentivise by selecting one.
Under energy-share weighting, the Scope-3 residual is allocated proportionally to operational kWh, which charges a constant per-kWh fee that does not differentiate when or where the work runs.
Under peak-attribution weighting (Eq. peak-share in §4), the same residual concentrates on tokens that contribute to fleet peak, charging them a multiple of what the same token would carry at trough.
The experiment in §X shows this concretely: under rSCI[peak 10%] a token landing in the busiest 20% of hours is charged ~8× more than the same token at trough; under oSCI or SCI the same token sees ~1.2× variation (essentially just grid CI).
The peak-disincentive property is therefore not intrinsic to rSCI — it is the *consequence* of choosing peak-share weights, which the framework supports but does not mandate.

## Paragraph 2 — the metric varies with system behaviour, by design.

rSCI is sensitive to the system it measures.
Two operators with identical fleets but different workload shapes will compute different per-request rSCI values for an otherwise-identical request, because the residual is allocated against the slice's actual load distribution.
A request that lands in a slice with a flat load profile carries a smaller peak-share residual than the same request landing in a slice with a sharp diurnal peak.
This is the right behaviour: the metric is grounded in the operator's actual physical reality, not in a calibration table.
It also means that comparing rSCI numbers across operators without comparing their slice contexts is meaningless — but the same is already true of any allocation-based metric, and rSCI at least makes the slice context explicit (the reconciliation identity in Eq. reconcile is the audit trail).

## Paragraph 3 — the sunk-carbon fallacy as a routing decision, not just an attribution artifact.

Bashir et al.'s sunk-carbon critique of SCI is usually read as an attribution problem (the per-job number is wrong), but a metric that biases attribution biases the scheduler that optimises it.
We drove a placement scheduler with each metric on a real CAISO-region trace, with a 6-yr-old DGX A100 (past EL, M=0) alongside a fresh DGX H100.
The SCI scheduler routes to the A100 first whenever grid CI drops below ~78 gCO2/kWh — i.e. precisely the clean-grid hours where solar dominates CAISO's supply.
Over the trace this happens 35.7% of the time, and the resulting placement burns 6% more energy and 3% more operational carbon than the oSCI or rSCI placements, all three of which prefer the H100 throughout.
The sunk-carbon fallacy is therefore not a bookkeeping curiosity that goes away when the operator is honest about hardware age; it is a real lever that produces real waste when a real scheduler optimises it.

## Notes on shape

- Each paragraph anchored to one defensible number (8×, slice-dependence, 35.7% / 6% / 3%).
- P3 is the strongest empirical finding. Consider leading with it — doubles as concrete restatement of §2's critique on a production trace.
- "rSCI is a class" framing in P1 consistent with §3's three weight families subsection.
- Nothing here requires temporal scheduling, user-facing role, or customer Scope-3 role. Those stay in Future Work.
- P3 currently depends on the spatial-routing scheduler experiment having been run; the experiment cells were removed from the notebook on 2026-05-21 (the headline numbers are quoted from the last run). Re-derive if calibration changes.
