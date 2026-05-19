"""
SCI / oSCI / rSCI — per-request and slice-aggregate.

Definitions per paper/paper.tex and SCI v1.1 spec:
    SCI_i  = (E_i * I + M_i) / R_i        (Bashir 2024; M from SCI v1.1 amortization)
    oSCI_i = (E_i * I) / R_i              (Bashir's operational-only refinement)
    rSCI_i = (E_i^{active} * xi) / R_i    where xi = I + (Delta^S1+Delta^S2+Delta^S3) / E_slice

R_i = ContextTokens_i (prefill-only model, see experiments_design.md §"Unit of work").

`E` definitions differ across metrics, deliberately and faithfully:
- SCI/oSCI: E SHALL include idle machines and SHOULD apply PUE (SCI v1.1 spec,
  references/SCI.md L185-L209). For our continuously-reserved slice this means
  E = (active + idle) * PUE per token. With this faithful E, sum_i oSCI_i*R_i
  recovers all of Scope-2; the structural gap to top-down is Scope-1 + Scope-3.
- rSCI: E is just bottom-up active IT energy (per paper.tex §rSCI). Idle, PUE,
  market-vs-location, and energy-model error are absorbed by Delta^S2.

SCI's M-term (sunk-carbon pathology, the §4.1 headline):
- DGX A100 is past its 6-yr SCI amortization window → M_i = 0 for every new request.
- DGX H100 is fresh → M is amortized over expected lifetime tokens.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from experiments_old.constants import DGX_A100, DGX_H100, PUE, ROUTING_SHARE
from experiments_old.picocloud import (
    GAMMA,
    HOURS_PER_WEEK,
    J_PER_KWH,
    SYSTEMS,
    TopDown,
)


# ---------------------------------------------------------------------------
# SCI M-term: amortize embodied over expected lifetime context-tokens.
# Pathology: DGX A100 past 6-yr window → M = 0.
# ---------------------------------------------------------------------------
def m_per_token_g(name: str, avg_utilization: float = 0.638) -> float:
    """
    SCI v1.1 amortization: M_i = M_system * R_i / R_lifetime.
    Returns gCO2e per ContextToken.

    R_lifetime = throughput * utilization * lifetime (seconds * tok/s).
    avg_utilization defaults to ~64%, matching the trace's fleet-average load.

    DGX A100: age >= lifetime → fully past amortization → 0.
    """
    sys = SYSTEMS[name]
    if sys.age_years >= sys.lifetime_years:
        return 0.0
    throughput_tok_s = sys.prefill_tokens_per_sec
    seconds_in_lifetime = sys.lifetime_years * 365.25 * 24 * 3600
    r_lifetime_tokens = throughput_tok_s * avg_utilization * seconds_in_lifetime
    return sys.embodied_kgco2e * 1000.0 / r_lifetime_tokens  # kg -> g


@dataclass(frozen=True)
class PerTokenIntensity:
    """Intensities a request sees (gCO2e per ContextToken). Per GPU type."""
    sci: float
    osci: float
    rsci: float


def faithful_op_e_per_token_j(name: str, idle_kwh_total: float, total_tokens: float) -> float:
    """
    SCI-spec-faithful operational E per ContextToken: (active + idle-share) * PUE.

    Idle is the slice baseline (both DGXs continuously reserved); allocated
    uniformly per ContextToken so the per-token denominator R partitions cleanly.
    PUE applied to both active and idle per SCI v1.1 spec (references/SCI.md
    "E should take into account ... PUE").
    """
    active_j = GAMMA[name]
    idle_j_per_tok = idle_kwh_total * J_PER_KWH / total_tokens
    return (active_j + idle_j_per_tok) * PUE


def per_token_intensities(
    name: str,
    avg_ci_gco2_per_kwh: float,
    xi_gco2_per_kwh: float,
    idle_kwh_total: float,
    total_tokens: float,
) -> PerTokenIntensity:
    """
    All three metrics for one GPU type, on a per-ContextToken basis.

    SCI/oSCI use the SCI-spec-faithful E (active + idle, with PUE).
    rSCI uses bottom-up active E with xi carrying all the residuals.
    """
    e_op_j = faithful_op_e_per_token_j(name, idle_kwh_total, total_tokens)
    op_g_per_tok = e_op_j * avg_ci_gco2_per_kwh / J_PER_KWH
    m_g_per_tok = m_per_token_g(name)
    rsci_g_per_tok = GAMMA[name] * xi_gco2_per_kwh / J_PER_KWH
    return PerTokenIntensity(
        sci=op_g_per_tok + m_g_per_tok,
        osci=op_g_per_tok,
        rsci=rsci_g_per_tok,
    )


# ---------------------------------------------------------------------------
# rSCI xi: slice-level effective intensity (gCO2e per kWh).
# ---------------------------------------------------------------------------
def xi_gco2_per_kwh(td: TopDown, slice_active_kwh_total: float, grid_ci: float) -> float:
    """
    xi_{s,r} = I_r + (Delta^S1 + Delta^S2 + Delta^S3) / E_{s,r}

    E_{s,r} = slice bottom-up active IT energy (kWh).
    Delta^S2 absorbs PUE + idle + market-vs-location adjustments.
    """
    # Bottom-up O_{s,r} = E_{s,r} * I_r, in kgCO2e
    o_kg = slice_active_kwh_total * grid_ci / 1000.0
    delta_s1 = td.s1
    delta_s2 = td.s2_lbm - o_kg
    delta_s3 = td.s3
    delta_total_g = (delta_s1 + delta_s2 + delta_s3) * 1000.0  # kg -> g
    return grid_ci + delta_total_g / slice_active_kwh_total


# ---------------------------------------------------------------------------
# Aggregate sums (for reconciliation in §4.2)
# ---------------------------------------------------------------------------
def aggregate_attributed_kg(
    total_context_tokens: float, intensities_by_gpu: dict[str, PerTokenIntensity]
) -> dict[str, float]:
    """
    Sum_i metric_i * R_i, decomposed by metric. Uses expected routing shares —
    exact for slice totals at large N.
    """
    out = {"sci": 0.0, "osci": 0.0, "rsci": 0.0}
    for name, intens in intensities_by_gpu.items():
        toks = ROUTING_SHARE[name] * total_context_tokens
        out["sci"] += intens.sci * toks
        out["osci"] += intens.osci * toks
        out["rsci"] += intens.rsci * toks
    return {k: v / 1000.0 for k, v in out.items()}  # g -> kg
