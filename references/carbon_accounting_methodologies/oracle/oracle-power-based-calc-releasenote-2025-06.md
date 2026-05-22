# Oracle OCI Carbon Emissions Analysis — Power-Based Calculation Support

**Source URL:** https://docs.oracle.com/en-us/iaas/releasenotes/governance/carbon-analysis-powercalculation.htm
**Original URL (redirects):** https://docs.public.content.oci.oraclecloud.com/en-us/iaas/releasenotes/governance/carbon-analysis-powercalculation.htm
**Fetch date:** 2026-05-22
**Page release date:** June 30, 2025

---

## Overview

The Carbon Emissions Analysis page in Emissions Management allows customers to track estimated carbon emissions footprints while using OCI services.
Provides visualization tools to generate charts, data tables, and CSVs based on customizable parameters.

## Calculation Methodologies

### Power-Based

OCI leverages GHG Protocol guidance to automate carbon emissions calculations using **power-based** calculations, which:

- Track the amount of power consumed (in kWh) by service workloads
- Align with GHG Protocol guidelines and EU/UK regulations
- Allocate energy consumption from OCI data center hardware (both dedicated and shared) to resource workloads
- Multiply consumption by a regional carbon emissions factor based on the power grid mix of renewable and non-renewable energy

### Spend-Based (fallback)

- Calculate emissions by multiplying a customer's service spend (pre-discount) by a regional carbon emissions factor
- Based on the Oracle Clean Cloud OCI Data Sheet
- Used for services **not** supported by power-based calculations

## Emission Factor Types

**Power-based calculations support two types:**

1. **Location-based emissions** — reflects the region's power grid emissions (partially to 100% renewable depending on region)
2. **Market-based emissions** — includes Oracle's renewable energy certificates and grid purchases to offset emissions; results in **zero carbon emission factors in European regions** (due to Oracle's PPA contracts)

**Spend-based calculations** support only market-based emissions factors.

## Provider Caveat (verbatim)

> "Carbon Emissions Analysis isn't a developer tool for reducing emissions. All data provided is an estimate."

---

## Delta vs. existing oracle-technical-carbon-guidance.pdf (Feb 2023, v1.0)

The 2023 PDF covers **only spend/revenue-based methodology**:
- Formula: customer revenue × regional emission intensity factor = estimated Scope 3 emissions
- No power tracking, no per-service kWh metering
- No LBM/MBM distinction
- Third-party assurance (ISO 14064-3) for Oracle's corporate inventory only, not the customer tool

The June 2025 release note adds:
- Power-based calculation mode (kWh-based, LBM + MBM)
- Explicit LBM / MBM distinction for power-based
- EU/UK regulatory alignment stated
- Zero-MBM in European regions explicitly documented
- Spend-based remains for services without power coverage (specific service list not enumerated)

**What's still missing from public docs:**
- Which specific OCI services are covered by power-based vs spend-based (no enumerated list)
- Per-service energy intensity values or formulas
- CSRD / SB-253 regulatory alignment is not named; only "EU/UK regulations" stated
- Service coverage scope (Compute only? Storage? Database? All?)
