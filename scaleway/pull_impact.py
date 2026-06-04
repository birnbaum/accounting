#!/usr/bin/env python3
"""Pull Scaleway Environmental Footprint data via the API.

The dashboard only renders daily granularity for a single selected month, and the
PDF export is a monthly aggregate. The Environmental Footprint API
(`get_impact_data`) returns one aggregate `Impact` per query window, so we
reconstruct a daily series by querying one day at a time.

Two API quirks handled here:
  - The Go backend wants RFC3339 (`...T..Z`); the SDK serialises `datetime` with a
    space separator and gets rejected. We pass pre-formatted RFC3339 strings.
  - `get_impact_report_availability` and `get_impact_data` both require start/end.

Observed data-quality quirks (2026-06-04), worth knowing before trusting a pull:
  - Spurious non-zero footprint for dates before the resources (or even the
    account) existed; for this experiment only May 27-31 2026 is real.
  - The same single-day query is non-deterministic: a day can return full data on
    one call and an empty `projects` list minutes later (eventual consistency /
    server-side recomputation). We retry empty days; persistent empties are logged
    to stderr rather than silently dropped.
  - Month-level totals are revised retroactively (May total moved 3.11 -> 3.64
    kgCO2e between the 2026-05-31 PDF export and a 2026-06-04 API pull).

Usage:
  uv run python scaleway/pull_impact.py 2026-05-27 2026-06-01 > scaleway/daily_impact_may2026.csv

Prereqs: SCW_* env vars or ~/.config/scw/config.yaml (same as deploy.py).
"""

from __future__ import annotations

import csv
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scaleway import Client
from scaleway.environmental_footprint.v1alpha1 import (
    EnvironmentalFootprintV1Alpha1UserAPI,
)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_CSV = SCRIPT_DIR / "projects.csv"


def rfc3339(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT00:00:00Z")


def project_names() -> dict[str, str]:
    out: dict[str, str] = {}
    if PROJECTS_CSV.exists():
        with open(PROJECTS_CSV) as f:
            for row in csv.DictReader(f):
                out[row["project_id"]] = row["name"]
    return out


def main() -> None:
    start = datetime.fromisoformat(sys.argv[1]).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(sys.argv[2]).replace(tzinfo=timezone.utc)

    api = EnvironmentalFootprintV1Alpha1UserAPI(Client.from_config_file_and_env())
    names = project_names()

    w = csv.writer(sys.stdout)
    w.writerow(["date", "project_id", "project_name", "kg_co2e", "m3_water"])
    d = start
    while d < end:
        nxt = d + timedelta(days=1)
        r = api.get_impact_data(start_date=rfc3339(d), end_date=rfc3339(nxt))
        for _ in range(8):  # see header: single-day queries are non-deterministic
            if r.projects:
                break
            time.sleep(1.5)
            r = api.get_impact_data(start_date=rfc3339(d), end_date=rfc3339(nxt))
        if not r.projects:
            print(f"WARN: no data for {d.date().isoformat()} after retries", file=sys.stderr)
        for p in r.projects:
            imp = p.total_project_impact
            if imp is None:
                continue
            w.writerow([
                d.date().isoformat(),
                p.project_id,
                names.get(p.project_id, ""),
                f"{imp.kg_co2_equivalent:.6f}",
                f"{imp.m3_water_usage:.6f}",
            ])
        d = nxt


if __name__ == "__main__":
    main()
