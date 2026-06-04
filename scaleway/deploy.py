#!/usr/bin/env python3
"""Scaleway carbon-reporting experiment — init / run / status / cleanup.

Spins up 4 VMs (one SKU, two regions, idle vs stress) + 1 block volume
across 5 Scaleway Projects, so the Environmental Footprint dashboard
filters cleanly per cell. Cleanup is manual (no self-delete).

Prereqs:
  uv add scaleway
  Set SCW_ACCESS_KEY / SCW_SECRET_KEY / SCW_DEFAULT_ORGANIZATION_ID
  (or have ~/.config/scw/config.yaml configured).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scaleway import Client
from scaleway.account.v3 import AccountV3ProjectAPI
from scaleway.block.v1 import BlockV1API, CreateVolumeRequestFromEmpty
from scaleway.instance.v1.custom_api import InstanceUtilsV1API as InstanceV1API

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_CSV = SCRIPT_DIR / "projects.csv"
EXPERIMENT_JSON = SCRIPT_DIR / "experiment.json"

PROJECT_PREFIX = "rsci-exp"
IMAGE_LABEL = "ubuntu_jammy"
ZONES = ["fr-par-1", "nl-ams-1"]


def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")


def die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def user_data(workload: str) -> bytes:
    if workload == "stress":
        # Network-independent CPU burner: one `yes` per core, no apt/no egress.
        # (The earlier apt-get install stress-ng silently failed on instances
        # without a public IP / Public Gateway, leaving "stress" VMs idle.)
        body = "for i in $(seq $(nproc)); do yes > /dev/null & done\nwait"
    else:
        body = "sleep infinity"
    return f"#!/bin/bash\necho '=== rsci-exp start (workload={workload}) at '$(date -u --iso-8601=seconds) ===\n{body}\n".encode()


def load_projects() -> dict[int, str]:
    if not PROJECTS_CSV.exists():
        die(f"{PROJECTS_CSV} not found; run `init` first.")
    out: dict[int, str] = {}
    with open(PROJECTS_CSV) as f:
        for row in csv.DictReader(f):
            out[int(row["index"])] = row["project_id"]
    return out


def load_experiments() -> list[dict]:
    return json.loads(EXPERIMENT_JSON.read_text())


def cmd_init(client: Client) -> None:
    if PROJECTS_CSV.exists():
        log(f"{PROJECTS_CSV} already exists; not re-creating projects. Delete the file and re-run if you want fresh ones.")
        return
    api = AccountV3ProjectAPI(client)
    rows = []
    for i in range(1, 6):
        name = f"{PROJECT_PREFIX}-{i}"
        log(f"Creating project {name}")
        p = api.create_project(name=name, description="rSCI carbon experiment")
        rows.append({"index": i, "project_id": p.id, "name": name})
    with open(PROJECTS_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["index", "project_id", "name"])
        w.writeheader()
        w.writerows(rows)
    log(f"Wrote {PROJECTS_CSV}")


def cmd_run(client: Client) -> None:
    exps = load_experiments()
    projects = load_projects()
    instance_api = InstanceV1API(client)
    block_api = BlockV1API(client)

    for e in exps:
        pid = projects[e["project_index"]]
        zone = e["zone"]

        if e["kind"] == "block_volume":
            name = f"rsci-exp-vol-{e['id']}"
            log(f"Cell {e['id']}: creating {e['size_gb']} GB block volume {name} in {zone} (project {pid})")
            block_api.create_volume(
                name=name,
                project_id=pid,
                zone=zone,
                perf_iops=5000,
                from_empty=CreateVolumeRequestFromEmpty(size=e["size_gb"] * 1024 * 1024 * 1024),
            )
            continue

        name = f"rsci-exp-{e['id']}-{e['workload']}"
        log(f"Cell {e['id']}: creating {e['commercial_type']} {name} in {zone} (workload={e['workload']}, project {pid})")
        res = instance_api.create_server(
            zone=zone,
            commercial_type=e["commercial_type"],
            name=name,
            project=pid,
            image=IMAGE_LABEL,
            volumes={},
            dynamic_ip_required=False,
            protected=False,
        )
        srv = res.server
        if srv is None:
            log(f"  ERROR: server creation returned no server")
            continue
        log(f"  -> {srv.id}, waiting for stable state…")
        instance_api.wait_instance_server(server_id=srv.id, zone=zone)
        instance_api.set_server_user_data(
            server_id=srv.id, zone=zone, key="cloud-init", content=user_data(e["workload"])
        )
        instance_api.server_action(server_id=srv.id, zone=zone, action="poweron")
        log(f"  -> powered on")


def _iter_all(instance_api, block_api, projects):
    for idx, pid in projects.items():
        for zone in ZONES:
            try:
                servers = instance_api.list_servers(zone=zone, project=pid).servers
            except Exception as ex:
                servers = []
            try:
                vols = block_api.list_volumes(zone=zone, project_id=pid, include_deleted=False).volumes
            except Exception:
                vols = []
            yield idx, pid, zone, servers, vols


def cmd_status(client: Client) -> None:
    projects = load_projects()
    instance_api = InstanceV1API(client)
    block_api = BlockV1API(client)
    for idx, pid, zone, servers, vols in _iter_all(instance_api, block_api, projects):
        if not servers and not vols:
            continue
        print(f"--- Project {idx} ({pid}) zone {zone} ---")
        for s in servers:
            print(f"  server {s.name} {s.commercial_type} {s.state}")
        for v in vols:
            gb = (v.size or 0) // (1024 ** 3)
            print(f"  volume {v.name} {gb}GB {v.status}")


def cmd_cleanup(client: Client) -> None:
    projects = load_projects()
    instance_api = InstanceV1API(client)
    block_api = BlockV1API(client)
    for idx, pid, zone, servers, vols in _iter_all(instance_api, block_api, projects):
        for s in servers:
            if s.id is None:
                continue
            log(f"Project {idx} {zone}: deleting server {s.name} ({s.state})")
            try:
                if s.state != "stopped":
                    instance_api.server_action(server_id=s.id, zone=zone, action="poweroff")
                    instance_api.wait_instance_server(server_id=s.id, zone=zone)
                instance_api.delete_server(server_id=s.id, zone=zone)
            except Exception as ex:
                log(f"  WARNING: {ex}")
            # Also delete the auto-created root volume if it still exists.
            try:
                for v in instance_api.list_volumes(zone=zone, project=pid).volumes:
                    if v.server is None and v.name.startswith("rsci-exp-"):
                        log(f"  deleting orphan instance volume {v.name}")
                        instance_api.delete_volume(volume_id=v.id, zone=zone)
            except Exception:
                pass
        for v in vols:
            if v.id is None:
                continue
            log(f"Project {idx} {zone}: deleting block volume {v.name}")
            try:
                block_api.delete_volume(volume_id=v.id, zone=zone)
            except Exception as ex:
                log(f"  WARNING: {ex}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["init", "run", "status", "cleanup"])
    args = p.parse_args()
    client = Client.from_config_file_and_env()
    {"init": cmd_init, "run": cmd_run, "status": cmd_status, "cleanup": cmd_cleanup}[args.command](client)


if __name__ == "__main__":
    main()
