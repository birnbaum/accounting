# T Cloud Public (formerly Open Telekom Cloud) — Sustainability Dashboard

**Customer tool:** T Cloud Public Sustainability Dashboard (in-tenant console; launched 2026-02-23).

## No PDF available in this folder

T Cloud Public has not published a methodology PDF.
The only first-party methodology description is the dashboard launch blog (URL below).
This folder will be updated when a methodology PDF or technical guide is released.

## Rename history

- **2026-02-02**: rebrand from *Open Telekom Cloud* (OTC) to *T Cloud Public* announced.
- **2026-02-23**: Sustainability Dashboard launched.
- **Operator**: T-Systems / Deutsche Telekom group.
- **Folder note**: per-provider folder created 2026-05; provider previously appeared in `non-customer-tool-providers.md` as "Open Telekom Cloud" (corporate disclosure only).

## Provider URLs

- Landing: https://www.t-cloud-public.com/en
- Sustainability hub: https://www.t-cloud-public.com/en/benefits/sustainability
- Dashboard launch blog (2026-03-24): https://www.t-cloud-public.com/en/blog/product-news/sustainability-dashboard
- Rename blog (2026-02-02): https://public.t-cloud.com/en/blog/product-news/t-cloud-public-new-name-for-open-telekom-cloud
- Legacy domain (still resolves): https://www.open-telekom-cloud.com/en
- Deutsche Telekom Corporate Responsibility report 2024 PDF: https://report.telekom.com/cr-report/2024/_assets/downloads/env-environment-dtag-cr24.pdf

## Methodology summary (verified 2026-05-23)

### Surface
- In-tenant access: dashboard "directly within their existing financial dashboard environment in their tenant" (per-tenant per-account view).
- Launch: 2026-02-23.
- Pricing: not disclosed in the launch blog.

### Service coverage
- Energy attributed to "individual services such as virtual machines, storage, and data traffic." Full enumeration not yet published.

### Temporal granularity
- Not specified in launch blog.

### Scope coverage
- **Scope 1 + Scope 2** included.
- **Scope 3 (incl. embodied infrastructure)** explicitly excluded today, on the roadmap.
- Verbatim: *"Scope 3 emissions, including embedded infrastructure emissions, are not yet included but are part of the roadmap."*

### Embodied carbon
- Not currently included (see Scope 3).

### Energy model
- Bottom-up: "measured infrastructure power consumption at device level, combined with architecture-aware allocation models."
- Long-term measurement base: "long-term infrastructure power measurements collected over more than one year."

### Allocation key
- Utilization-share: "workload-driven share of infrastructure power consumption based on utilization, rather than allocating total installed capacity by default."
- Granular per-resource formula (vCPU-h, byte, GB-month) not yet disclosed.

### Standards referenced
- **GHG Protocol** (Scope 2 market-based approach).
- **ISO 14067** (product carbon footprinting; framework for the planned Scope 3 extension).
- **ESRS** (European Sustainability Reporting Standards).

### Energy mix
- Scope 2 reported on **market-based** approach.
- T-Systems DCs (Biere/Magdeburg DE, Aalsmeer/Almere NL, Bern/Zollikofen CH) sourced 100% renewable electricity since 2021 (per group CR report; verified for legacy OTC era — to recheck post-rename for the CH sites added 2022).
- Region-specific carbon intensity data referenced.

### Multi-criteria
- Not disclosed; carbon only at launch.

### Assurance
- None disclosed.

### Replicability
- **Low** at launch — no methodology PDF, no per-product allocation formula, no reference values published.
- Will move higher if T-Systems ships a methodology document.

### Known gaps for rSCI
- No Scope 3 / embodied — top priority gap.
- No published allocation key — cannot independently recompute customer numbers.
- No methodology PDF — only the launch blog as primary source.
- No third-party assurance.
- Reconcilability with the Deutsche Telekom group CR report not stated.

## Why this changed the survey classification

In the pre-2026-05 inventory, OTC appeared only with a corporate-level Telekom CR report (no customer tool).
The Sustainability Dashboard launch on 2026-02-23 moved it into the per-customer-tool set (per-tenant carbon dashboard exists).
It is the only provider in our survey that crossed this threshold during the survey window itself, which makes T Cloud Public a useful contemporary data point for §3.
