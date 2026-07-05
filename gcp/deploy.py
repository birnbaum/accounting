#!/usr/bin/env python3
"""GCP Carbon Footprint Experiment — Deployment Script.

Uses google-cloud-compute Python API. Each VM runs a startup script
(idle or stress), then self-deletes.

Prerequisites:
  - Application Default Credentials (gcloud auth application-default login)
  - Project mapping in gcp/projects.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
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


def load_experiments() -> list[dict]:
    with open(EXPERIMENT_JSON) as f:
        return json.load(f)


def get_experiments(data: list[dict], ids: list[int]) -> list[dict]:
    by_id = {exp["id"]: exp for exp in data}
    missing = [i for i in ids if i not in by_id]
    if missing:
        die(f"experiment(s) not found: {missing}")
    return [by_id[i] for i in ids]


def parse_ids(raw: str) -> list[int]:
    return [int(x) for x in raw.split(",")]


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


def create_instances_parallel(tasks: list[tuple[str, str, str, str, str]]) -> None:
    if not tasks:
        return
    log(f"Launching {len(tasks)} VMs in parallel...")
    with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
        futures = {pool.submit(create_instance, *t): t[2] for t in tasks}
    for fut, name in futures.items():
        try:
            fut.result()
        except Exception as e:
            log(f"  UNEXPECTED ERROR for {name}: {e}")


def exp_to_task(exp: dict) -> tuple[str, str, str, str, str]:
    mtype = f"{exp['family']}-standard-{exp['size']}"
    zone = f"{exp['region']}-{exp['zone']}"
    name = f"{mtype}-{exp['workload']}-{exp['duration_h']}h-{zone}"
    script = startup_script(exp["workload"], exp["duration_h"] * 60)
    return (exp["project"], zone, name, mtype, script)


def cmd_run(data: list[dict], ids: list[int]) -> None:
    exps = get_experiments(data, ids)
    log(f"=== Running {len(exps)} experiment(s): {ids} ===")
    for e in exps:
        log(f"  #{e['id']}: {e['family']}-standard-{e['size']} {e['workload']} {e['duration_h']}h in {e['region']}-{e['zone']} ({e['project']})")
    create_instances_parallel([exp_to_task(e) for e in exps])
    log("=== Deployment complete ===")


def _unique_projects(data: list[dict], ids: list[int] | None, projects: dict[int, Project]) -> list[str]:
    if ids:
        return sorted({e["project"] for e in get_experiments(data, ids)})
    return sorted({p.project_id for p in projects.values() if p.billing_account})


def cmd_status(data: list[dict], projects: dict[int, Project], ids: list[int] | None = None) -> None:
    client = compute_v1.InstancesClient()
    for project_id in _unique_projects(data, ids, projects):
        print(f"--- {project_id} ---")
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


def cmd_cleanup(data: list[dict], projects: dict[int, Project], ids: list[int] | None = None) -> None:
    client = compute_v1.InstancesClient()
    for project_id in _unique_projects(data, ids, projects):
        log(f"Cleaning up {project_id}")
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
    tasks = []
    for idx in range(1, 6):
        wl = workloads[idx]
        project_id = resolve_project(projects, f"PROJECT_{idx}")
        script = startup_script(wl, 10)
        log(f"  PROJECT_{idx} ({project_id}) — {wl}")
        tasks.append((project_id, zone, f"test2-{idx}-{wl}", "e2-standard-2", script))
    create_instances_parallel(tasks)
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


def main() -> None:
    parser = argparse.ArgumentParser(description="GCP Carbon Footprint Experiment — Deployment")
    parser.add_argument("command", choices=["run", "status", "cleanup", "test", "test2", "init", "help"])
    parser.add_argument("ids", nargs="?", help="Comma-separated experiment ids (e.g. 1,2,3)")
    parser.add_argument("--stress", action="store_true", help="Use stress workload (for test)")
    args = parser.parse_args()

    if args.command == "help":
        parser.print_help(); return

    data = load_experiments()
    projects = load_projects()
    ids = parse_ids(args.ids) if args.ids else None
    match args.command:
        case "run":
            if not ids: parser.error("run requires experiment ids (e.g. run 1,2,3)")
            cmd_run(data, ids)
        case "status":  cmd_status(data, projects, ids)
        case "cleanup": cmd_cleanup(data, projects, ids)
        case "test":    cmd_test(projects, args.stress)
        case "test2":   cmd_test2(projects)
        case "init":    cmd_init(projects)


if __name__ == "__main__":
    main()
