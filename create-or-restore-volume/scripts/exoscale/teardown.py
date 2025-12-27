"""Exoscale block storage volume teardown script.

Creates snapshots of volumes and then deletes them.
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
        print(f"Created snapshot: {snapshot_id}")

    # Wait for all snapshots to complete
    def check_snapshots_ready():
        for snapshot_id in snapshot_ids:
            snapshot = exo.get_block_storage_snapshot(id=snapshot_id)
            state = snapshot.get("state", "").lower()
            if state not in ["created", "error"]:
                return False
        return True

    print("Waiting for snapshots to complete...")
    wait_until(check=check_snapshots_ready, kwargs={}, cond=lambda result: result)
    print("All snapshots completed")

    # Delete all matching volumes
    for volume_id in volume_ids:
        print(f"Deleting volume: {volume_id}")
        exo.delete_block_storage_volume(id=volume_id)

    # Wait until all volumes are deleted
    def check_volumes_deleted():
        volumes_response = exo.list_block_storage_volumes()
        volumes = volumes_response.get("block-storage-volumes", [])
        remaining = [v for v in volumes if v.get("labels") == LABELS]
        return len(remaining) == 0

    wait_until(check=check_volumes_deleted, kwargs={}, cond=lambda result: result)
    print("All volumes deleted successfully")

    # Write snapshot IDs to file for output
    with open("snapshot-output.txt", "w") as f:
        f.write(",".join(snapshot_ids))


if __name__ == "__main__":
    main()
