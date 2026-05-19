"""
Toy-cloud primitives: fleet, routing, energy model, top-down report.

Single rSCI slice (s, r) = (the 2-DGX continuous bare-metal reservation, us-central1).
Both Azure workloads (conv, code) live inside this slice as labels on requests.

See paper/experiments_design.md.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

import numpy as np
import pandas as pd

from experiments_old.constants import (
    DC_INFRA_KGCO2E_PER_W_TOTAL,
    DC_INFRA_LIFETIME_YEARS,
    DGX_A100,
    DGX_H100,
    FERA_FRACTION_OF_S2,
    GRID_CSV,
    PUE,
    REGION,
    ROUTING_SHARE,
    S1_KGCO2E_PER_WEEK,
    TRANSPORT_KGCO2E_PER_SYSTEM,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]

SYSTEMS = {DGX_A100.name: DGX_A100, DGX_H100.name: DGX_H100}
GAMMA = {name: sys.gamma_j_per_token for name, sys in SYSTEMS.items()}

J_PER_KWH = 3_600_000.0
HOURS_PER_WEEK = 168.0
WEEKS_PER_YEAR = 52.1775


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
def assign_gpu(n: int, seed: int = 42) -> np.ndarray:
    """Throughput-weighted random GPU assignment for n requests."""
    rng = np.random.default_rng(seed)
    names = np.array(list(ROUTING_SHARE.keys()))
    probs = np.array(list(ROUTING_SHARE.values()))
    return rng.choice(names, size=n, p=probs)


# ---------------------------------------------------------------------------
# Energy model
# ---------------------------------------------------------------------------
# Per the paper, bottom-up E_i is *active IT energy only*; PUE and idle capacity
# end up in Delta^{S2} via the residual bridge. This keeps the bottom-up model
# clean and pushes everything bottom-up can't see into the residuals where it
# belongs (per paper.tex §rSCI).

def per_request_active_energy_j(
    context_tokens: np.ndarray, gpu: np.ndarray
) -> np.ndarray:
    """gamma_g * ContextTokens_i — marginal active energy above idle."""
    return np.where(
        gpu == DGX_A100.name,
        DGX_A100.gamma_j_per_token * context_tokens,
        DGX_H100.gamma_j_per_token * context_tokens,
    )


def slice_active_energy_kwh(total_context_tokens: float) -> dict[str, float]:
    """Slice active energy, partitioned by GPU via throughput-weighted routing."""
    e = {}
    for name, sys in SYSTEMS.items():
        toks = ROUTING_SHARE[name] * total_context_tokens
        e[name] = GAMMA[name] * toks / J_PER_KWH
    e["total"] = sum(v for k, v in e.items() if k != "total")
    return e


def slice_idle_energy_kwh(hours: float) -> dict[str, float]:
    """Idle baseline for the slice — both DGXs run continuously."""
    e = {name: sys.idle_power_w * hours / 1000.0 for name, sys in SYSTEMS.items()}
    e["total"] = sum(e.values())
    return e


# ---------------------------------------------------------------------------
# Grid intensity
# ---------------------------------------------------------------------------
def load_grid_intensity() -> pd.DataFrame:
    """24-h CI pattern for the reference region; tiled by callers if needed."""
    df = pd.read_csv(ROOT / GRID_CSV, parse_dates=["datetime"])
    return df[["datetime", REGION]].rename(columns={REGION: "gco2_per_kwh"})


def avg_grid_intensity_gco2_per_kwh() -> float:
    return float(load_grid_intensity()["gco2_per_kwh"].mean())


# ---------------------------------------------------------------------------
# Top-down constructed report (week)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TopDown:
    """Weekly constructed top-down report for the single slice. All kgCO2e."""

    s1: float
    s2_lbm: float
    s3_it_embodied: float
    s3_dc_infra: float
    s3_fera: float
    s3_transport: float

    @property
    def s3(self) -> float:
        return (
            self.s3_it_embodied
            + self.s3_dc_infra
            + self.s3_fera
            + self.s3_transport
        )

    @property
    def total(self) -> float:
        return self.s1 + self.s2_lbm + self.s3


def build_topdown(
    total_context_tokens: float,
    hours: float = HOURS_PER_WEEK,
    s2_lbm_override_kg: float | None = None,
) -> TopDown:
    """
    Construct the weekly top-down report from the bottom-up model + fixed factors.

    If `s2_lbm_override_kg` is given, use it directly for Scope-2 (e.g. the
    time-integrated S2 from the per-minute trace, which is the only value that
    reconciles exactly when grid CI varies over time). Otherwise compute S2
    from the weekly-average CI — a coarse approximation, used for the no-trace
    sanity case in a0_sanity.

    This is the *constructed ground truth* against which rSCI reconciles by
    construction. S2 includes idle and PUE.
    """
    active = slice_active_energy_kwh(total_context_tokens)
    idle = slice_idle_energy_kwh(hours)
    it_kwh = active["total"] + idle["total"]
    total_kwh_with_pue = it_kwh * PUE

    if s2_lbm_override_kg is not None:
        s2 = s2_lbm_override_kg
    else:
        ci = avg_grid_intensity_gco2_per_kwh()
        s2 = total_kwh_with_pue * ci / 1000.0  # gCO2 -> kgCO2

    # IT embodied: amortize each DGX over its lifetime, take this week's share.
    week_frac = (hours / HOURS_PER_WEEK) / WEEKS_PER_YEAR
    s3_it = sum(
        sys.embodied_kgco2e / sys.lifetime_years * week_frac for sys in SYSTEMS.values()
    )

    # DC infrastructure embodied (shell + cooling + racks + networking).
    # Allocate by peak IT capacity; the toy is the sole tenant of its slice.
    peak_w = sum(sys.peak_power_w for sys in SYSTEMS.values())
    s3_infra = (
        DC_INFRA_KGCO2E_PER_W_TOTAL * peak_w / DC_INFRA_LIFETIME_YEARS * week_frac
    )

    s3_fera = FERA_FRACTION_OF_S2 * s2

    n_systems = len(SYSTEMS)
    s3_transport = (
        TRANSPORT_KGCO2E_PER_SYSTEM * n_systems / DGX_A100.lifetime_years * week_frac
    )

    return TopDown(
        s1=S1_KGCO2E_PER_WEEK * (hours / HOURS_PER_WEEK),
        s2_lbm=s2,
        s3_it_embodied=s3_it,
        s3_dc_infra=s3_infra,
        s3_fera=s3_fera,
        s3_transport=s3_transport,
    )
