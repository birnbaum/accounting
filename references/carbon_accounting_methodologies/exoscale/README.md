# Exoscale (A1 Digital) — CloudAssess-based calculator

**Customer tool:** CloudAssess-based environmental impact calculator (console + API).

## No PDF available in this folder

Exoscale's calculator is built on **CloudAssess**, a third-party LCA engine co-developed with **Resilio** and **Kleis**. The underlying CloudAssess methodology is partner-owned and not fully public.

**Borderline status**: Exoscale-branded surface, but the engine is third-party. Excluded from the main paper's Tier-A landscape table for this reason.

## Provider URLs

- Sustainability hub: https://www.exoscale.com/sustainability/
- INTRO Sustainability academy doc: https://community.exoscale.com/academy/intro_sus/
- Compliance academy doc: https://community.exoscale.com/academy/intro_cpl/

## Methodology summary (verified 2026-05-16)

### Surface
- Console + API; hourly / daily / monthly granularity.
- API-accessible for invoice/dashboard integration.

### Service coverage
- Not enumerated on landing page. Likely covers compute + storage at minimum given the engine.

### Scope coverage
- Not publicly enumerated in Scope 1/2/3 terms.
- "Multicriteria impact analysis" framing — beyond carbon, but specific scope breakdown not published.

### Embodied carbon
- Yes — by virtue of LCA / ISO 14040 alignment via CloudAssess.

### Energy model
- LCA per **ISO 14040 / ISO 14044**.

### Allocation key
- Not publicly disclosed.

### Standards
- ISO 14040 / ISO 14044 (LCA).
- ADEME.
- ISO 50001 EnMS (in implementation; audit targeted).

### Multi-criteria
- Yes — described as "multicriteria impact analysis."
- Water / abiotic not enumerated publicly.

### Energy mix per DC
- Published carbon-intensity figures for 2024 sourced from electricitymaps.com (42 g CO₂e/kWh CH → 126 g AT).

### Assurance
- None disclosed.
- ISO 50001 audit targeted.

### Replicability
- **Low** — calculator is exposed but the engine is third-party (CloudAssess).

### Known gaps for rSCI
- Methodology is partner-owned and not fully public; cannot independently verify the engine.
- Scope coverage not publicly enumerated.
- Allocation key undisclosed.
- This is the structural reason Exoscale sits in the "borderline" category — the surface is Exoscale's, but the methodology is not.
