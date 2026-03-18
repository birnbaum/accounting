"""Export per-resource Azure carbon emission data (all scopes, categories, months)."""

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
CATEGORY_TYPES = [
    CategoryTypeEnum.RESOURCE,
    CategoryTypeEnum.RESOURCE_GROUP,
    CategoryTypeEnum.RESOURCE_TYPE,
    CategoryTypeEnum.LOCATION,
    CategoryTypeEnum.SUBSCRIPTION,
]

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


def export_item_details(carbon, available_range):
    """Query ItemDetailsReport per month × scope × category with full pagination."""
    months = generate_months(available_range.start_date, available_range.end_date)

    for scope in SCOPES:
        for category in CATEGORY_TYPES:
            cat_name = category.value.lower()
            for month in months:
                outfile = OUTPUT_DIR / f"item_details_{cat_name}_{scope.value}_{month.isoformat()}.jsonl"
                log.info(f"ItemDetails | {scope.value} | {cat_name} | {month}")

                query_filter = ItemDetailsQueryFilter(
                    date_range=DateRange(start=month, end=month),
                    subscription_list=SUBSCRIPTION_IDS,
                    carbon_scope_list=[scope],
                    category_type=category,
                    order_by=OrderByColumnEnum.LATEST_MONTH_EMISSIONS,
                    sort_direction=SortDirectionEnum.DESC,
                    page_size=PAGE_SIZE,
                )

                total = 0
                while True:
                    result = safe_request(carbon.query_carbon_emission_reports, query_filter)
                    if result.value:
                        with open(outfile, "a") as f:
                            for item in result.value:
                                f.write(json.dumps(item.as_dict(), default=str) + "\n")
                        total += len(result.value)
                    if not result.skip_token:
                        break
                    query_filter.skip_token = result.skip_token

                log.info(f"  -> {total} items")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    credential = DefaultAzureCredential()
    client = CarbonOptimizationMgmtClient(credential=credential)
    carbon = client.carbon_service

    available_range = safe_request(carbon.query_carbon_emission_data_available_date_range)
    log.info(f"Date range: {available_range.start_date} -> {available_range.end_date}")

    export_item_details(carbon, available_range)
