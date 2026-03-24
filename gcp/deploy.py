#!/usr/bin/env python3
"""GCP Carbon Footprint Experiment — Deployment Script.

Uses google-cloud-compute Python API. Each VM runs a startup script
(idle or stress), then self-deletes.

Prerequisites:
  - Application Default Credentials (gcloud auth application-default login)
  - Project mapping in gcp/projects.csv

Usage:
  python gcp/deploy.py list                        # list all experiments
  python gcp/deploy.py run <id> [--region R]       # run experiment
  python gcp/deploy.py status [<id>]               # check running instances
  python gcp/deploy.py cleanup [<id>]              # delete instances
  python gcp/deploy.py test [--stress]             # quick 5min test
  python gcp/deploy.py init                        # grant self-delete IAM
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.cloud import compute_v1, resourcemanager_v3, service_usage_v1

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECTS_CSV = SCRIPT_DIR / "projects.csv"
EXPERIMENT_JSON = SCRIPT_DIR / "experiment.json"
SOURCE_IMAGE = "projects/debian-cloud/global/images/family/debian-12"

SELF_DELETE = """\
echo "=== SELF-DELETE ==="
TOKEN=$(curl -sf -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
PROJECT=$(curl -sf -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/project/project-id")
echo "DELETE https://compute.googleapis.com/compute/v1/projects/$PROJECT/zones/$ZONE/instances/$INSTANCE_NAME"
RESP=$(curl -s -w "\\n%{http_code}" -X DELETE -H "Authorization: Bearer $TOKEN" \\
  "https://compute.googleapis.com/compute/v1/projects/$PROJECT/zones/$ZONE/instances/$INSTANCE_NAME")
HTTP_CODE=$(echo "$RESP" | tail -1)
echo "HTTP $HTTP_CODE"
echo "$RESP" | head -5
if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  echo "Self-delete OK"
else
  echo "Self-delete FAILED, shutting down"
  shutdown -h now
fi"""


# ---------- helpers ----------

def log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")


def die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


@dataclass
class Project:
    index: int
    project_id: str
    billing_account: str


def load_projects() -> dict[int, Project]:
    if not PROJECTS_CSV.exists():
        die(f"{PROJECTS_CSV} not found.")
    projects: dict[int, Project] = {}
    with open(PROJECTS_CSV) as f:
        for row in csv.DictReader(f):
            idx = int(row["index"])
            projects[idx] = Project(idx, row["project_id"], row.get("billing_account", ""))
    return projects


def resolve_project(projects: dict[int, Project], project_var: str) -> str:
    idx = int(project_var.removeprefix("PROJECT_"))
    if idx not in projects:
        die(f"PROJECT_{idx} is not set in {PROJECTS_CSV}.")
    return projects[idx].project_id


def load_experiments() -> dict:
    with open(EXPERIMENT_JSON) as f:
        return json.load(f)


def get_experiment(data: dict, exp_id: int) -> dict:
    for exp in data["experiments"]:
        if exp["id"] == exp_id:
            return exp
    die(f"experiment {exp_id} not found.")


def require_project(exp: dict, projects: dict[int, Project]) -> str:
    pvar = exp.get("project", "")
    if not pvar:
        die(f"experiment {exp['id']} has no project assignment.")
    return resolve_project(projects, pvar)


def _iter_projects(data: dict, projects: dict[int, Project], filter_id: int | None):
    """Yield (project_id, label) for status/cleanup commands."""
    if filter_id is not None:
        exp = get_experiment(data, filter_id)
        yield require_project(exp, projects), f"Experiment {filter_id}"
    else:
        for idx, proj in sorted(projects.items()):
            yield proj.project_id, f"PROJECT_{idx}"


# ---------- startup script ----------

def startup_script(workload: str, duration_m: int) -> str:
    duration_s = duration_m * 60
    if workload == "stress":
        work_cmd = textwrap.dedent(f"""\
            apt-get update -qq && apt-get install -y -qq stress-ng
            stress-ng --matrix 0 --timeout {duration_s}""")
    else:
        work_cmd = f"sleep {duration_s}"

    return f"""\
#!/bin/bash
INSTANCE_NAME=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/name)
ZONE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/zone | awk -F/ '{{print $NF}}')
MTYPE=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/machine-type | awk -F/ '{{print $NF}}')

echo "=== EXPERIMENT START ({workload}) ==="
echo "Time: $(date -u --iso-8601=seconds)"
echo "Duration: {duration_m}m ({duration_s}s)"
echo "Instance: $INSTANCE_NAME | Zone: $ZONE | Type: $MTYPE"
echo "========================"

{work_cmd}

echo "=== EXPERIMENT END ==="
echo "Time: $(date -u --iso-8601=seconds)"
echo "Self-deleting $INSTANCE_NAME in $ZONE..."
{SELF_DELETE}
"""


# ---------- instance creation ----------

def create_instance(project_id: str, zone: str, instance_name: str,
                    machine_type: str, script: str) -> bool:
    log(f"  Creating {instance_name} ({machine_type}) in {zone}")
    instance = compute_v1.Instance(
        name=instance_name,
        machine_type=f"zones/{zone}/machineTypes/{machine_type}",
        disks=[compute_v1.AttachedDisk(
            boot=True, auto_delete=True,
            initialize_params=compute_v1.AttachedDiskInitializeParams(
                source_image=SOURCE_IMAGE, disk_size_gb=10),
        )],
        network_interfaces=[compute_v1.NetworkInterface(
            network="global/networks/default",
            access_configs=[compute_v1.AccessConfig(name="External NAT", type_="ONE_TO_ONE_NAT")],
        )],
        service_accounts=[compute_v1.ServiceAccount(
            scopes=["https://www.googleapis.com/auth/compute"])],
        scheduling=compute_v1.Scheduling(automatic_restart=False),
        metadata=compute_v1.Metadata(items=[compute_v1.Items(key="startup-script", value=script)]),
    )
    try:
        compute_v1.InstancesClient().insert(
            project=project_id, zone=zone, instance_resource=instance).result()
        return True
    except GoogleAPICallError as e:
        log(f"  WARNING: Failed to create {instance_name}: {e.message}, skipping")
        return False


def deploy_region(project_id: str, family: str, size: int, workload: str,
                  duration_h: int, region: str, zones: list[str] | None = None) -> None:
    mtype = f"{family}-standard-{size}"
    name = f"{mtype}-{workload}-{duration_h}h"
    script = startup_script(workload, duration_h * 60)
    if zones:
        for suffix in zones:
            create_instance(project_id, f"{region}-{suffix}", f"{name}-{region}-{suffix}", mtype, script)
    else:
        create_instance(project_id, f"{region}-b", f"{name}-{region}", mtype, script)


# ---------- commands ----------

def cmd_list(data: dict) -> None:
    print("=== GCP Carbon Footprint Experiments ===\n")
    for exp in data["experiments"]:
        eid, etype = exp["id"], exp["type"]
        print(f"--- Experiment {eid} ({etype}) ---")
        print(f"  {exp['description']}")
        if p := exp.get("project"):
            print(f"  Project: {p}")

        if etype == "controlled":
            print(f"  Config: {exp['family']}-standard-{exp['size']}, {exp['workload']}, "
                  f"{exp['duration_h']}h, start {exp['start_utc']} UTC")
            print(f"  Regions: {', '.join(data['controlled_regions'])}")
            print("  Instances: 5")
        else:
            print("  Per-region config:")
            n_inst = 0
            for region, rc in exp["regions"].items():
                z = rc.get("zones")
                z_info = f" zones:{','.join(z)}" if z else ""
                n_info = f" ({rc['notes']})" if rc.get("notes") else ""
                n_inst += len(z) if z else 1
                print(f"    {region:<24s} {rc['family']}-standard-{rc['size']:<2} "
                      f"{rc['workload']:<6s} {rc['duration_h']}h {rc['start_utc']} UTC{z_info}{n_info}")
            print(f"  Instances: {n_inst}")
        print()
    print("Total: 15 controlled + 3 zone + 23 factorial = 41 data points")


def cmd_run(data: dict, projects: dict[int, Project], exp_id: int, filter_region: str = "") -> None:
    exp = get_experiment(data, exp_id)
    project_id = require_project(exp, projects)
    log(f"=== Running experiment {exp_id} ({exp['type']}) in project {project_id} ===")

    if exp["type"] == "controlled":
        regions = [filter_region] if filter_region else data["controlled_regions"]
        for r in regions:
            deploy_region(project_id, exp["family"], exp["size"], exp["workload"], exp["duration_h"], r)
    else:
        regions_to_run = [filter_region] if filter_region else list(exp["regions"].keys())
        for r in regions_to_run:
            if (rc := exp["regions"].get(r)) is None:
                log(f"  WARNING: region {r} not found, skipping")
                continue
            deploy_region(project_id, rc["family"], rc["size"], rc["workload"], rc["duration_h"], r, rc.get("zones"))

    log(f"=== Experiment {exp_id} deployment complete ===")


def cmd_status(data: dict, projects: dict[int, Project], filter_id: int | None = None) -> None:
    client = compute_v1.InstancesClient()
    for project_id, label in _iter_projects(data, projects, filter_id):
        print(f"--- {label} ({project_id}) ---")
        try:
            found = False
            for _, scoped in client.aggregated_list(project=project_id):
                for inst in (scoped.instances or []):
                    if not found:
                        print(f"  {'NAME':<30s} {'ZONE':<25s} {'MACHINE_TYPE':<20s} STATUS")
                        found = True
                    print(f"  {inst.name:<30s} {inst.zone.rsplit('/', 1)[-1]:<25s} "
                          f"{inst.machine_type.rsplit('/', 1)[-1]:<20s} {inst.status}")
            if not found:
                print("  (no instances)")
        except GoogleAPICallError:
            print("  (project not accessible)")
        print()


def cmd_cleanup(data: dict, projects: dict[int, Project], filter_id: int | None = None) -> None:
    client = compute_v1.InstancesClient()
    for project_id, label in _iter_projects(data, projects, filter_id):
        log(f"Cleaning up {label} ({project_id})")
        try:
            found = False
            for _, scoped in client.aggregated_list(project=project_id):
                for inst in (scoped.instances or []):
                    found = True
                    zone = inst.zone.rsplit("/", 1)[-1]
                    log(f"  Deleting {inst.name} in {zone}")
                    try:
                        client.delete(project=project_id, zone=zone, instance=inst.name).result()
                    except GoogleAPICallError as e:
                        log(f"  WARNING: {e.message}")
            if not found:
                log("  No instances found")
        except GoogleAPICallError:
            log("  Project not accessible")
    log("Cleanup complete")


def cmd_test(projects: dict[int, Project], stress: bool = False) -> None:
    project_id = resolve_project(projects, "PROJECT_0")
    zone, workload = "europe-west1-b", "stress" if stress else "idle"
    log(f"=== Test: e2-standard-2, {workload}, 5min in {zone} ===")
    script = startup_script(workload, 5)
    if create_instance(project_id, zone, "test", "e2-standard-2", script):
        log("Instance created. It will self-delete after 5 minutes.")
    else:
        log("Test failed — instance was not created.")


def cmd_test2(projects: dict[int, Project]) -> None:
    zone = "us-east1-c"
    workloads = {1: "idle", 2: "idle", 3: "idle", 4: "stress", 5: "stress"}
    log(f"=== Test2: e2-standard-2, 10min in {zone} across projects 1-5 ===")
    for idx in range(1, 6):
        wl = workloads[idx]
        project_id = resolve_project(projects, f"PROJECT_{idx}")
        script = startup_script(wl, 10)
        log(f"  PROJECT_{idx} ({project_id}) — {wl}")
        create_instance(project_id, zone, f"{idx}-{wl}", "e2-standard-2", script)
    log("All test instances launched. They will self-delete after 10 minutes.")


def cmd_init(projects: dict[int, Project]) -> None:
    log("Granting compute.instanceAdmin.v1 to default compute SA on all projects")
    su_client = service_usage_v1.ServiceUsageClient()
    rm_client = resourcemanager_v3.ProjectsClient()

    for idx in range(20):
        if (proj := projects.get(idx)) is None:
            continue
        project_id = proj.project_id
        log(f"  PROJECT_{idx} ({project_id})")
        try:
            su_client.enable_service(request=service_usage_v1.EnableServiceRequest(
                name=f"projects/{project_id}/services/compute.googleapis.com")).result()
        except GoogleAPICallError:
            log("    Skipping (billing/API error)"); continue

        try:
            proj = rm_client.get_project(request=resourcemanager_v3.GetProjectRequest(
                name=f"projects/{project_id}"))
        except (GoogleAPICallError, NotFound):
            log("    Skipping (project not found)"); continue

        sa = f"{proj.name.rsplit('/', 1)[-1]}-compute@developer.gserviceaccount.com"
        log(f"    SA: {sa}")
        try:
            policy = rm_client.get_iam_policy(request={"resource": f"projects/{project_id}"})
            policy.bindings.append(resourcemanager_v3.types.Binding(
                role="roles/compute.instanceAdmin.v1", members=[f"serviceAccount:{sa}"]))
            rm_client.set_iam_policy(request={"resource": f"projects/{project_id}", "policy": policy})
        except GoogleAPICallError as e:
            log(f"    WARNING: IAM binding failed: {e.message}")
    log("Done. VMs can now self-delete.")


# ---------- main ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="GCP Carbon Footprint Experiment — Deployment")
    parser.add_argument("command", choices=["list", "run", "status", "cleanup", "test", "test2", "init", "help"])
    parser.add_argument("id", nargs="?", type=int, help="Experiment id")
    parser.add_argument("--region", help="Run in one region only")
    parser.add_argument("--stress", action="store_true", help="Use stress workload (for test)")
    args = parser.parse_args()

    if args.command == "help":
        parser.print_help(); return

    data = load_experiments()
    if args.command == "list":
        cmd_list(data); return

    projects = load_projects()
    match args.command:
        case "run":
            if args.id is None: parser.error("run requires an experiment id")
            cmd_run(data, projects, args.id, args.region or "")
        case "status":  cmd_status(data, projects, args.id)
        case "cleanup": cmd_cleanup(data, projects, args.id)
        case "test":    cmd_test(projects, args.stress)
        case "test2":   cmd_test2(projects)
        case "init":    cmd_init(projects)


if __name__ == "__main__":
    main()
