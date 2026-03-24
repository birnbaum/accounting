#!/usr/bin/env python3
"""Fetch hourly carbon intensity for the 5 GCP regions from Electricity Maps."""

import argparse
import csv
import json
import os
import sys

import requests

from datetime import datetime, timedelta

API_URL = "https://api.electricitymaps.com/v3/carbon-intensity/past-range"

REGIONS = [
    "us-central1",
    "europe-west1",
    "asia-east1",
    "australia-southeast1",
    "southamerica-east1",
]


ZONE_OVERRIDES = {
    "australia-southeast1": "AU-NSW",
    "southamerica-east1": "BR-CS",
}


def fetch_region(region: str, start: str, end: str, token: str) -> list[dict]:
    if region in ZONE_OVERRIDES:
        params = {"zone": ZONE_OVERRIDES[region], "start": start, "end": end}
    else:
        params = {
            "dataCenterRegion": region,
            "dataCenterProvider": "gcp",
            "start": start,
            "end": end,
        }
    resp = requests.get(API_URL, params=params, headers={"auth-token": token})
    resp.raise_for_status()
    return resp.json()["data"]


def main():
    parser = argparse.ArgumentParser(description="Fetch carbon intensity for GCP regions")
    parser.add_argument("date", help="Date to query (YYYY-MM-DD)")
    args = parser.parse_args()

    # Build time range: date 01:00 UTC to next day 01:00 UTC
    day = datetime.strptime(args.date, "%Y-%m-%d")
    start = f"{day.strftime('%Y-%m-%d')}T01:00:00.000Z"
    next_day = day + timedelta(days=1)
    end = f"{next_day.strftime('%Y-%m-%d')}T01:00:00.000Z"

    token = os.environ.get("ELECTRICITYMAPS_TOKEN")
    if not token:
        print("ERROR: Set ELECTRICITYMAPS_TOKEN environment variable.", file=sys.stderr)
        sys.exit(1)

    # {datetime: {region: intensity}}
    table: dict[str, dict[str, int]] = {}

    for region in REGIONS:
        print(f"Fetching {region}...", file=sys.stderr)
        data = fetch_region(region, start, end, token)

        for entry in data:
            if entry.get("isEstimated", False):
                print(f"ERROR: estimated data for {region} at {entry['datetime']}", file=sys.stderr)
                sys.exit(1)

            dt = entry["datetime"]
            table.setdefault(dt, {})[region] = entry["carbonIntensity"]

    # Write CSV: datetime as rows, regions as columns
    output = os.path.join(os.path.dirname(__file__), f"carbonintensity_{args.date}.csv")
    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["datetime"] + REGIONS)
        for dt in sorted(table):
            writer.writerow([dt] + [table[dt].get(r, "") for r in REGIONS])

    print(f"Wrote {len(table)} rows to {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
