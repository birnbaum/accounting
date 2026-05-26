# Scaleway carbon-reporting experiment

Small toy: 4 × `BASIC3-X2C-4G` VMs (idle/stress × fr-par-1/nl-ams-1) + one 10 GB SBS-5K block volume in fr-par-1.
One Scaleway Project per cell so the **Environmental Footprint** dashboard filters cleanly per condition.

## Prereqs

API credentials in env or `~/.config/scw/config.yaml`:

```sh
export SCW_ACCESS_KEY=SCW...
export SCW_SECRET_KEY=...
export SCW_DEFAULT_ORGANIZATION_ID=...
```

The `scaleway` SDK is in `pyproject.toml`; `uv sync` installs it.

## Sequence

```sh
uv run python scaleway/deploy.py init      # create 5 Projects, write projects.csv
uv run python scaleway/deploy.py run       # create 4 VMs + 1 block volume
uv run python scaleway/deploy.py status    # list everything

# ... wait 2-3 days ...

uv run python scaleway/deploy.py cleanup   # delete servers + volumes (Projects stay)
```

Carbon data is visible the day after activation in the dashboard:
https://console.scaleway.com/cost-impact-management/environmental-footprint

Filter by **Project** → see per-cell daily kgCO₂e.
Single-month selection triggers the daily view (per Scaleway docs §7.2).

## What to look at after 2–3 days

- idle vs stress at the same region — does the daily report differ? (Tests Scaleway's "actual CPU consumption" claim.)
- fr-par-1 vs nl-ams-1 — France/NL grid CI ratio is ~6× per Scaleway's reference values; how does the dashboard show it?
- 10 GB unattached volume — is the embodied (prorated by storage share) visible day-by-day?

## Cost

~€3-5 total for 3 days. Cleanup is manual — don't forget.

## Files

- `experiment.json` — cell definitions
- `projects.csv` — written by `init`, lists the 5 created Project IDs
- `deploy.py` — init/run/status/cleanup
