"""Export GCP carbon footprint data from BigQuery carbon_footprint export."""

import json
import logging
from pathlib import Path

from google.cloud import bigquery

# The carbon footprint export table lives in a dataset linked to your billing account.
# Format: <project_id>.<dataset>.carbon_footprint
# Adjust these to match your setup.
PROJECT_ID = "your-project-id"
DATASET = "carbon_footprint"
TABLE = "carbon_footprint"

OUTPUT_DIR = Path("gcp/carbon_export")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def fetch_carbon_data(client: bigquery.Client) -> list[dict]:
    """Query all carbon footprint rows and return as raw dicts."""
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.{TABLE}`
        ORDER BY usage_month DESC
    """
    log.info(f"Running query on {PROJECT_ID}.{DATASET}.{TABLE}")
    result = client.query(query).result()

    rows = []
    for row in result:
        rows.append(dict(row))
    log.info(f"Fetched {len(rows)} rows")
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

    client = bigquery.Client(project=PROJECT_ID)
    rows = fetch_carbon_data(client)

    outfile = OUTPUT_DIR / "raw_export.json"
    with open(outfile, "w") as f:
        json.dump(rows, f, indent=2, default=serialize)
    log.info(f"Wrote {outfile} ({len(rows)} rows)")
