"""Export AWS Customer Carbon Footprint Tool data via Cost Explorer API."""

import json
import logging
from datetime import date
from pathlib import Path

from dateutil.relativedelta import relativedelta
import boto3

OUTPUT_DIR = Path("aws/carbon_export")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def generate_months(start: date, end: date) -> list[tuple[str, str]]:
    """Generate (start, end) ISO date pairs for each month in range."""
    months = []
    current = start
    while current <= end:
        next_month = current + relativedelta(months=1)
        months.append((current.isoformat(), next_month.isoformat()))
        current = next_month
    return months


def fetch_carbon_data(ce_client, start: str, end: str) -> dict:
    """Fetch carbon emissions for a given time period."""
    response = ce_client.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        Filter={
            "Dimensions": {
                "Key": "RECORD_TYPE",
                "Values": ["Credit"],
            }
        },
    )
    return response


def fetch_carbon_footprint(client) -> list[dict]:
    """Query the AWS Customer Carbon Footprint Tool API."""
    paginator = client.get_paginator("list_carbon_footprint_summaries")
    rows = []
    for page in paginator.paginate():
        for summary in page.get("CarbonFootprintSummaries", []):
            rows.append(summary)
    log.info(f"Fetched {len(rows)} carbon footprint summaries")
    return rows


def serialize(obj):
    """JSON serializer for types not serializable by default."""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # The Carbon Footprint Tool data is available via the
    # AWS Billing and Cost Management console export, or via the
    # sustainability.us-east-1 endpoint.
    client = boto3.client("sustainability", region_name="us-east-1")

    rows = fetch_carbon_footprint(client)

    outfile = OUTPUT_DIR / "raw_export.json"
    with open(outfile, "w") as f:
        json.dump(rows, f, indent=2, default=serialize)
    log.info(f"Wrote {outfile} ({len(rows)} rows)")
