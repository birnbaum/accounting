"""Export per-resource Azure carbon emission data (all scopes, per month)."""

import json
import logging
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.mgmt.carbonoptimization import CarbonOptimizationMgmtClient
from azure.mgmt.carbonoptimization.models import (
    CategoryTypeEnum,
    SortDirectionEnum,
    OrderByColumnEnum,
    EmissionScopeEnum,
    DateRange,
    ItemDetailsQueryFilter,
)
from azure.core.exceptions import HttpResponseError

SUBSCRIPTION_IDS = ["3b7f0d07-2848-4c7c-87d3-074743ad0131"]

OUTPUT_DIR = Path("carbon_export")
PAGE_SIZE = 5000

SCOPES = [EmissionScopeEnum.SCOPE1, EmissionScopeEnum.SCOPE2, EmissionScopeEnum.SCOPE3]

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def safe_request(func, *args, **kwargs):
    for attempt in range(10):
        try:
            return func(*args, **kwargs)
        except HttpResponseError as e:
            if e.status_code == 429:
                wait = 2 ** attempt
                log.warning(f"Rate limited. Waiting {wait}s (attempt {attempt+1}/10)")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Failed after 10 retries due to rate limiting.")


def generate_months(start_date: str, end_date: str) -> list[date]:
    months = []
    current = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    while current <= end:
        months.append(current)
        current += relativedelta(months=1)
    return months


def paginate_query(carbon, query_filter):
    """Paginate through all results for a given query filter."""
    items = []
    while True:
        result = safe_request(carbon.query_carbon_emission_reports, query_filter)
        if result.value:
            items.extend(result.value)
        if not result.skip_token:
            break
        query_filter.skip_token = result.skip_token
    return items


def export_emissions(carbon, available_range):
    """Query resource-level emissions per month, merge scopes, write one JSON per month."""
    months = generate_months(available_range.start_date, available_range.end_date)

    for month in months:
        month_key = month.strftime("%Y-%m")
        outfile = OUTPUT_DIR / f"{month_key}.json"
        if outfile.exists():
            log.info(f"Skipping {month_key} (already exists)")
            continue

        resources = {}  # resourceId -> record dict
        for scope in SCOPES:
            scope_field = scope.value.lower()  # "scope1", "scope2", "scope3"
            log.info(f"{month_key} | {scope.value}")

            query_filter = ItemDetailsQueryFilter(
                date_range=DateRange(start=month, end=month),
                subscription_list=SUBSCRIPTION_IDS,
                carbon_scope_list=[scope],
                category_type=CategoryTypeEnum.RESOURCE,
                order_by=OrderByColumnEnum.LATEST_MONTH_EMISSIONS,
                sort_direction=SortDirectionEnum.DESC,
                page_size=PAGE_SIZE,
            )

            items = paginate_query(carbon, query_filter)
            for item in items:
                rid = item.resource_id
                if rid not in resources:
                    resources[rid] = {
                        "resourceId": rid,
                        "resourceGroup": item.resource_group,
                        "resourceType": item.resource_type,
                        "location": item.location,
                        "resourceName": item.item_name,
                    }
                resources[rid][scope_field] = item.latest_month_emissions

            log.info(f"  -> {len(items)} items")

        with open(outfile, "w") as f:
            json.dump(list(resources.values()), f, indent=2)
        log.info(f"Wrote {outfile} ({len(resources)} resources)")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    credential = DefaultAzureCredential()
    client = CarbonOptimizationMgmtClient(credential=credential)
    carbon = client.carbon_service

    available_range = safe_request(carbon.query_carbon_emission_data_available_date_range)
    log.info(f"Date range: {available_range.start_date} -> {available_range.end_date}")

    export_emissions(carbon, available_range)
