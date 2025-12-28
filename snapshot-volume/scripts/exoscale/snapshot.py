"""Exoscale block storage volume snapshot script.

Creates snapshots of volumes (without destroying them).
Reads configuration from environment variables.
"""

import os
from exoscale.api.v2 import Client
from helpers import wait_until


def main():
    # Load environment variables
    NAME = os.environ["VOLUME_NAME"]

    # Hardcoded constants
    ZONE = os.environ.get("EXOSCALE_ZONE", "ch-gva-2")
    LABELS = {"name": NAME}

    # Exoscale client
    exo = Client(
        os.environ["EXOSCALE_API_KEY"], os.environ["EXOSCALE_API_SECRET"], zone=ZONE
    )

    # Find all volumes matching labels
    volumes_response = exo.list_block_storage_volumes()
    volumes = volumes_response.get("block-storage-volumes", [])
    matching_volumes = [v for v in volumes if v.get("labels") == LABELS]

    if not matching_volumes:
        raise RuntimeError(f"No volumes found matching the labels: {LABELS}")

    volume_ids = [v["id"] for v in matching_volumes]
    snapshot_ids = []

    # Create snapshots for each volume
    for volume in matching_volumes:
        volume_id = volume["id"]
        snapshot_name = f"{NAME}-snapshot-{volume_id[:8]}"

        print(f"Creating snapshot for volume: {volume_id}")
        operation = exo.create_block_storage_snapshot(
            id=volume_id, name=snapshot_name, labels=LABELS
        )
        snapshot_id = operation["reference"]["id"]
        snapshot_ids.append(snapshot_id)
        print(f"Initiated snapshot creation: {snapshot_id}")

        # Wait until this specific snapshot appears in the list
        def check_snapshot_exists():
            try:
                snapshots_response = exo.list_block_storage_snapshots()
                snapshots = snapshots_response.get("block-storage-snapshots", [])
                for s in snapshots:
                    if s.get("id") == snapshot_id:
                        print(
                            f"Snapshot {snapshot_id} found in list with state: {s.get('state')}"
                        )
                        return True
                return False
            except Exception as e:
                print(f"Error checking snapshot: {e}")
                return False

        print(f"Waiting for snapshot {snapshot_id} to appear in list...")
        wait_until(check=check_snapshot_exists, kwargs={}, cond=lambda result: result)

    # Wait for all snapshots to reach final state
    def check_snapshots_ready():
        all_ready = True
        for snapshot_id in snapshot_ids:
            try:
                snapshot = exo.get_block_storage_snapshot(id=snapshot_id)
                state = snapshot.get("state", "").lower()
                print(f"Snapshot {snapshot_id} state: {state}")
                if state not in ["created", "error"]:
                    all_ready = False
            except Exception as e:
                print(f"Error getting snapshot {snapshot_id}: {e}")
                all_ready = False
        return all_ready

    print("Waiting for all snapshots to complete...")
    wait_until(check=check_snapshots_ready, kwargs={}, cond=lambda result: result)
    print("All snapshots completed")

    # Verify all snapshots exist
    print("\nVerifying snapshots:")
    snapshots_response = exo.list_block_storage_snapshots()
    all_snapshots = snapshots_response.get("block-storage-snapshots", [])
    matching_snapshots = [s for s in all_snapshots if s.get("labels") == LABELS]
    print(f"Found {len(matching_snapshots)} snapshots with matching labels:")
    for s in matching_snapshots:
        print(
            f"  - Snapshot ID: {s.get('id')}, State: {s.get('state')}, Name: {s.get('name')}"
        )

    if len(matching_snapshots) == 0:
        raise RuntimeError("No snapshots found!")

    # Write snapshot IDs to file for output
    with open("snapshot-output.txt", "w") as f:
        f.write(",".join(snapshot_ids))

    print(f"\n✅ Successfully created {len(snapshot_ids)} snapshot(s)")


if __name__ == "__main__":
    main()
