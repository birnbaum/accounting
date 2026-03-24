#!/usr/bin/env python3
"""Crawl VM start/stop times from Cloud Audit Logs across all billed projects.

Reads projects.csv, queries audit logs for instance insert/delete operations,
and writes results to gcp/vm_times.csv.

Usage:
  python gcp/crawl_vm_times.py [--since 2026-03-22] [--output gcp/vm_times.csv]
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path

from google.cloud import logging_v2

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_CSV = SCRIPT_DIR / "projects.csv"
DEFAULT_OUTPUT = SCRIPT_DIR / "vm_times.csv"
QUOTA_PROJECT = "fabled-decker-146511"


def load_billed_projects() -> list[dict]:
    projects = []
    with open(PROJECTS_CSV) as f:
        for row in csv.DictReader(f):
            if row.get("billing_account", "").strip():
                projects.append(row)
    return projects


def query_vm_events(project_id: str, since: str) -> list[dict]:
    """Query audit logs for VM insert/delete completion events."""
    client = logging_v2.Client(project=project_id, client_options={"quota_project_id": QUOTA_PROJECT})
    filter_str = (
        'resource.type="gce_instance" AND '
        '(protoPayload.methodName="v1.compute.instances.insert" OR '
        ' protoPayload.methodName="v1.compute.instances.delete") AND '
        'operation.last="true" AND '
        f'timestamp>="{since}"'
    )
    entries = []
    for entry in client.list_entries(filter_=filter_str, order_by="timestamp asc"):
        payload = entry.to_api_repr().get("protoPayload", {})
        resource_name = payload.get("resourceName", "")
        method = payload.get("methodName", "")

        parts = resource_name.split("/")
        instance_name = parts[-1] if len(parts) >= 2 else ""
        zone = parts[parts.index("zones") + 1] if "zones" in parts else ""

        entries.append({
            "timestamp": entry.timestamp.isoformat(),
            "method": method,
            "instance": instance_name,
            "zone": zone,
            "project_id": project_id,
        })
    return entries


def pair_events(events: list[dict]) -> list[dict]:
    """Match insert/delete events by instance name into start/stop pairs."""
    starts: dict[str, dict] = {}
    rows = []
    for ev in events:
        key = f"{ev['project_id']}/{ev['zone']}/{ev['instance']}"
        if "insert" in ev["method"]:
            starts[key] = ev
        elif "delete" in ev["method"]:
            start = starts.pop(key, None)
            start_time = start["timestamp"] if start else ""
            stop_time = ev["timestamp"]
            duration_s = ""
            if start_time and stop_time:
                t0 = datetime.fromisoformat(start_time)
                t1 = datetime.fromisoformat(stop_time)
                duration_s = str(int((t1 - t0).total_seconds()))
            rows.append({
                "project_id": ev["project_id"],
                "instance": ev["instance"],
                "zone": ev["zone"],
                "start_time": start_time,
                "stop_time": stop_time,
                "duration_s": duration_s,
            })
    # Instances that started but never stopped
    for key, ev in starts.items():
        rows.append({
            "project_id": ev["project_id"],
            "instance": ev["instance"],
            "zone": ev["zone"],
            "start_time": ev["timestamp"],
            "stop_time": "",
            "duration_s": "",
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="Crawl VM start/stop times from audit logs")
    default_since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    parser.add_argument("--since", default=default_since, help=f"Start date (default: {default_since})")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output CSV path")
    args = parser.parse_args()

    projects = load_billed_projects()
    print(f"Querying {len(projects)} projects with billing accounts (since {args.since})...")

    all_events = []
    for proj in projects:
        pid = proj["project_id"]
        print(f"  {pid}...", end=" ", flush=True)
        try:
            events = query_vm_events(pid, args.since)
            print(f"{len(events)} events")
            all_events.extend(events)
        except Exception as e:
            print(f"ERROR: {e}")

    rows = pair_events(all_events)
    rows.sort(key=lambda r: r["start_time"] or r["stop_time"])

    output = Path(args.output)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["project_id", "instance", "zone", "start_time", "stop_time", "duration_s"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} VM records to {output}")


if __name__ == "__main__":
    main()
