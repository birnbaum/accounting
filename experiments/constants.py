"""
All toy-cloud constants, with verbatim source citations next to each value.

Source-grounding rule (CLAUDE.md):
    Every estimated number lives here, with a citation. If a number cannot be
    grounded in a primary source in `references/`, it is marked ESTIMATE and
    bounded with a justification.

Edit this file to retune the toy cloud; downstream analysis scripts import
from here.
"""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# DGX systems
# ---------------------------------------------------------------------------
# Embodied carbon for full DGX A100 / DGX H100 systems is not publicly audited.
# NVIDIA publishes only the GPU baseboard PCF (HGX H100, 1,312 kgCO2e cradle-to-gate
# for the 8-GPU baseboard). A full DGX adds 2× CPU, ~2 TB RAM, 8× NVMe, NVLink
# switches, chassis, cooling, PSUs. Industry rule-of-thumb (chassis-and-board
# adds 2-4× bare-board embodied) bounds DGX H100 at 3-5 tCO2e total. We adopt the
# conservative upper end so that our bottom-up Scope-3 number does not understate
# what a real provider would disclose.
#
# Paper boilerplate:
# "Publicly audited cradle-to-gate embodied carbon data for complete DGX-class
#  systems is not available. We therefore use a bounded estimate derived from
#  disclosed GPU baseboard PCFs (NVIDIA HGX H100) and prior literature on
#  accelerator manufacturing impacts (Falk et al. 2025)."


@dataclass(frozen=True)
class System:
    name: str
    n_gpus: int
    prefill_tokens_per_sec_per_gpu: float  # 7-8B model, rough
    peak_power_w: float                    # full-system, all GPUs busy
    idle_power_w: float                    # system idle (CPU + RAM + fans + GPU idle)
    embodied_kgco2e: float                 # full-system cradle-to-gate (ESTIMATE)
    age_years: float                       # since first install
    lifetime_years: float = 6.0            # SCI amortization window


DGX_A100 = System(
    name="DGX A100",
    n_gpus=8,
    # A100 80GB prefill on a 7-8B model: ~8,000 tok/s/GPU. ESTIMATE — bounded from
    # open vLLM benchmark traces \cite{vllm-benchmarks}; closest primary measurement
    # \cite{patel-splitwise-2024} reports OPT-30B / Bloom-176B, not 7-8B directly.
    # Sanity-checked against the published H100/A100 ~2.5x ratio \cite{nvidia-h100-vs-a100-inference}.
    prefill_tokens_per_sec_per_gpu=8_000.0,
    # NVIDIA DGX A100 datasheet, max 6.5 kW \cite{nvidia-dgx-a100-datasheet}.
    peak_power_w=6_500.0,
    # Estimate: idle ≈ 25% of peak for the system (GPU idle + CPU + RAM + fans + PSU loss)
    idle_power_w=1_600.0,
    # ESTIMATE. Bounded between 8 × A100 SXM (8 × 127.6 = 1,021 kgCO2e, Falk 2025
    # cradle-to-gate) and DGX-class chassis/board/CPU/RAM total. 3 tCO2e is the
    # mid-range bounded estimate consistent with smaller die area + older arch
    # versus DGX H100.
    embodied_kgco2e=3_000.0,
    # NVIDIA A100 launched 2020-05-14. Paper submission July 2026.
    # 6+ years → fully past 6 yr SCI amortization window → SCI M-term = 0.
    age_years=6.0,
    lifetime_years=6.0,
)

DGX_H100 = System(
    name="DGX H100",
    n_gpus=8,
    # H100 80GB prefill on a 7-8B model: ~20,000 tok/s/GPU. ESTIMATE — bounded from
    # open vLLM benchmark traces \cite{vllm-benchmarks}; sanity-checked against the
    # H100/A100 ~2.5x inference-throughput ratio \cite{nvidia-h100-vs-a100-inference}.
    prefill_tokens_per_sec_per_gpu=20_000.0,
    # NVIDIA DGX H100 datasheet, max 10.2 kW \cite{nvidia-dgx-h100-datasheet}.
    peak_power_w=10_200.0,
    # Estimate: idle ≈ 25% of peak.
    idle_power_w=2_500.0,
    # ESTIMATE. Anchored on NVIDIA HGX H100 PCF Summary: "the carbon footprint
    # from cradle-to-gate for one HGX H100 GPU baseboard is 1,312 kg CO2".
    # Full DGX H100 adds CPU, RAM, NVMe, NVLink switches, chassis, cooling. Industry
    # rule-of-thumb (2-4× bare-board) bounds the system to 3-5 tCO2e. We use 4 tCO2e
    # (multiplier ≈ 3.05×) for internal consistency with DGX A100 estimate (3 tCO2e
    # over 8× A100 SXM cards = 1,021 kgCO2e → multiplier ≈ 2.94×). Both sit at a
    # uniform ~3× chassis-and-board multiplier — mid-range, defensible without
    # asymmetry between systems.
    embodied_kgco2e=4_000.0,
    # NVIDIA H100 GA: late 2022 / early 2023; for the toy we treat as fresh install
    # to maximise the SCI M-term contrast against the fully-amortised DGX A100.
    age_years=0.0,
    lifetime_years=6.0,
)


# ---------------------------------------------------------------------------
# Per-card embodied (for sensitivity / per-card sub-analysis if useful)
# ---------------------------------------------------------------------------
A100_CARD_KGCO2E = 127.6  # \cite{falk-2025-accelerator-lca}, single A100 SXM 40GB cradle-to-gate
HGX_H100_BASEBOARD_KGCO2E = 1_312.0  # \cite{nvidia-hgx-h100-pcf}, 8-GPU baseboard verbatim


# ---------------------------------------------------------------------------
# Region / grid
# ---------------------------------------------------------------------------
# data/carbonintensity_2026-03-23.csv — 24 hourly samples in gCO2/kWh.
# Trace dates (May 10-18, 2024) do not align with this CSV's date (2026-03-23),
# so we anchor trace t=0 to the CSV's first hour and tile the 24h pattern over
# the 7-day trace until the user provides a longer real series.
REGION = "us-central1"
GRID_CSV = "data/carbonintensity_2026-03-23.csv"


# ---------------------------------------------------------------------------
# DC infrastructure
# ---------------------------------------------------------------------------
PUE = 1.15  # Industry-typical hyperscaler; cite GCP/AWS public reporting if needed.


# ---------------------------------------------------------------------------
# Scope-3 categories beyond Cat 2 IT (the DGX embodied above)
# ---------------------------------------------------------------------------
# All ESTIMATE. Bounded values, calibrated against published provider reports
# (AWS S3 ~30-40% of total, GCP similar; cf. cross_provider_synthesis.md).

# Cat 2 - DC infrastructure embodied (building shell + cooling + racks + networking).
# Grounded in two primary sources:
#  - Waterman 2025 \cite{waterman-2025-dc-embodied}: per-MW mid-ranges for the
#    non-server IT support equipment our toy actually uses:
#      Cooling Systems   : 225 tCO2e/MW
#      Networking        : 175 tCO2e/MW
#      Racks & Enclosures:  55 tCO2e/MW
#    Subtotal IT-support: 455 tCO2e/MW.
#    (Storage 100 tCO2e/MW omitted: prefill-only toy doesn't run shared storage arrays.)
#  - ICEF Sustainable Data Centers Roadmap (Sandalow et al. 2025)
#    \cite{sandalow-2025-icef-roadmap}, Box 3.3-1A: 200 MW reference DC = 93k m^2,
#    ~300k m^3 concrete, ~62.5 Mkg steel. Applying typical material factors
#    (concrete ~250 kgCO2e/m^3, structural steel ~1.0 kgCO2e/kg) yields a
#    bounded shell estimate around 500-700 tCO2e/MW. (Material *quantities* are
#    from ICEF; the per-quantity carbon factors are our bounded estimate.)
#
# Combined (IT-support + shell), rounded to a clean defensible mid-range:
DC_INFRA_KGCO2E_PER_W_TOTAL = 1.0  # one-time, ~1000 tCO2e/MW, ADW + ICEF combined

# ICEF uses a 15-yr "whole DC" lifecycle (includes IT replacement during life).
# Cleaner than the AWS 50-yr shell-only / 6-yr IT split since we lumped the
# components into a single line.
DC_INFRA_LIFETIME_YEARS = 15.0

# Cat 3 - FERA (Fuel- and Energy-Related Activities; upstream fuel + T&D losses).
# GHG Protocol Scope-3 Standard \cite{ghg-protocol-scope3} defines Cat 3
# qualitatively but does not publish a global percentage; real implementers
# apply published emission factors from external databases:
#   - UK DEFRA / BEIS Conversion Factors workbook (annual, splits WTT and T&D)
#   - US EPA eGRID grid factors + WTT factors
#   - IEA World Energy Statistics (grid T&D losses by country)
# Rough magnitudes from those sources put combined FERA at order ~10% of LBM
# Scope-2 for typical OECD grids (T&D losses ~5-8%, WTT ~5-10% of combustion).
# We use 10% as a defensible round midpoint; ESTIMATE pending a DEFRA/EPA/IEA
# PDF in references/sources/ that we can cite for the specific factor.
FERA_FRACTION_OF_S2 = 0.10  # ESTIMATE, no primary-source factor in references/ yet

# Cat 4 - Upstream transport (shipping DGX from manufacturer to DC).
# Small fixed addend. ESTIMATE.
TRANSPORT_KGCO2E_PER_SYSTEM = 50.0  # one-time, amortized over lifetime

# Cat 12 - End-of-life treatment.
# Omitted: no Big-3 provider currently exposes EOL in their methodology,
# so including it in the toy's top-down report would diverge from realistic
# provider disclosures. (Earlier ref to Table 2 saying Azure includes EOL
# is the only counter-example, but on re-check it's not actually exposed in
# the customer-facing report.)


# ---------------------------------------------------------------------------
# Scope-1
# ---------------------------------------------------------------------------
# Diesel generator testing + refrigerant leakage for a 2-DGX-sized DC slice.
# ESTIMATE.
S1_KGCO2E_PER_WEEK = 5.0


# ---------------------------------------------------------------------------
# Routing: throughput-weighted random assignment.
# Computed from per-system prefill capacity above; both DGXs land at the same
# utilization fraction under the trace's average load. See §"Routing" in
# paper/experiments_design.md.
# ---------------------------------------------------------------------------
def _routing_share() -> dict[str, float]:
    cap_a100 = DGX_A100.n_gpus * DGX_A100.prefill_tokens_per_sec_per_gpu
    cap_h100 = DGX_H100.n_gpus * DGX_H100.prefill_tokens_per_sec_per_gpu
    total = cap_a100 + cap_h100
    return {DGX_A100.name: cap_a100 / total, DGX_H100.name: cap_h100 / total}


ROUTING_SHARE = _routing_share()  # {'DGX A100': 0.2857, 'DGX H100': 0.7143}


# ---------------------------------------------------------------------------
# Energy model per request (prefill-only)
# ---------------------------------------------------------------------------
# E_i = gamma_g * ContextTokens_i + idle_share
# gamma values are the *active* per-prefill-token energy on each GPU type.
# ESTIMATE — bounded; calibrate from Splitwise \cite{patel-splitwise-2024}
# (power-latency curves) or vLLM \cite{vllm-benchmarks} per-token measurements
# once PDFs / scripts land in references/.

# At ~8000 tok/s and ~400W per A100 card busy: 400W / 8000 tok/s = 50 mJ/token.
GAMMA_A100_J_PER_TOKEN = 0.050

# At ~20000 tok/s and ~700W per H100 card busy ≈ 35 mJ/token.
GAMMA_H100_J_PER_TOKEN = 0.035
