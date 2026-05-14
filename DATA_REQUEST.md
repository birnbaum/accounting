# Measuring Software Carbon Intensity — Data Collaboration Request

## Background

Cloud providers like Google Cloud report carbon footprint numbers that customers can use for GHG/Scope 3 reporting.
These numbers are auditable and comprehensive, but they are coarse (one number per service per region per month), delayed (available weeks after month-end), and do not tell individual teams what to optimize.

The Green Software Foundation's [Software Carbon Intensity (SCI)](https://sci.greensoftware.foundation/) standard addresses this by defining an actionable metric: carbon per unit of work (e.g., per request, per job, per GB processed).
However, current SCI implementations have known limitations — they miss facility overhead, idle capacity, and provider-specific allocation effects, and they do not connect back to the provider-reported number.
If the two signals diverge without explanation, teams lose trust in both.

We are developing an improved metric that fully reconciles with the provider-reported carbon numbers.
The goal: give teams an optimization signal they can act on, with confidence that improvements actually show up in their organization's official carbon reporting.

## What you would gain

- **Per-workload carbon metrics** tailored to your infrastructure, mapped to units your teams understand (e.g., carbon per request, per training job, per GB processed).
- **Visibility into your carbon number** — what drives your provider-reported footprint and which optimization levers actually move it (and which don't).
- **Early access** to a framework that connects day-to-day engineering decisions to corporate sustainability reporting.

## What we need from you

### 1. GCP Carbon Footprint Export

Google Cloud can export your project's carbon footprint data to BigQuery.
This is the provider-reported carbon data broken down by project, service, region, and month — the top-down number we reconcile against.

**How to set it up:**

1. Enable the Carbon Footprint export to BigQuery in the Google Cloud Console.
   See [Google's documentation](https://cloud.google.com/carbon-footprint/docs/export) for step-by-step instructions.
2. The export is linked to your billing account and creates a dataset with a `carbon_footprint` table.

**Required permissions:**

- To **set up** the export: `Billing Account Administrator` role on the billing account.
- To **read** the exported data: `BigQuery Data Viewer` role on the export dataset is sufficient.

We provide a script that queries the exported table and extracts the relevant fields — no manual data wrangling needed.

### 2. A Conversation About Your Workloads

We do **not** need you to write anything or fill out a questionnaire.

We would like a short meeting (30-60 min) to understand:
- What GCP services and resources your project uses (Compute Engine, Cloud Storage, BigQuery, etc.).
- What your workloads do at a high level (web serving, batch processing, ML training, data pipelines, etc.).
- What a meaningful "unit of work" looks like for each workload — something your teams already think about.

Together, we define carbon-per-unit-of-work metrics that map to business value your teams can understand and optimize for.
We will also discuss practical ways to provide us with workload-level usage data (job counts, request volumes, resource utilization) without exposing sensitive internal information.

## Data handling

All data stays within the research project.
We can anonymize project names, workload details, and organizational information if needed.
