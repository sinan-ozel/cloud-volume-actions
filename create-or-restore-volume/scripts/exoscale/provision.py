"""Exoscale block storage volume provisioning script.

Creates a new volume or restores from the most recent snapshot.
Reads configuration from environment variables.
"""

import os
import json
from operator import itemgetter
from exoscale.api.v2 import Client
from helpers import wait_until


def main():
    # Load environment variables
    NAME = os.environ["VOLUME_NAME"]
    VOLUME_SIZE = int(os.environ["VOLUME_SIZE"])

    # Hardcoded constants
    ZONE = os.environ.get("EXOSCALE_ZONE", "ch-gva-2")
    LABELS = {"name": NAME}

    # Exoscale client
    exo = Client(
        os.environ["EXOSCALE_API_KEY"], os.environ["EXOSCALE_API_SECRET"], zone=ZONE
    )

    # Main logic
    volume_id = None
    volume = None

    # Try to find existing volume
    volumes_response = exo.list_block_storage_volumes()
    volumes = volumes_response.get("block-storage-volumes", [])
    matching_volumes = [v for v in volumes if v.get("labels") == LABELS]

    if matching_volumes:
        matching_volumes.sort(key=lambda v: v.get("created-at", ""), reverse=True)
        volume = matching_volumes[0]
        volume_id = volume["id"]

        if volume.get("state", "").lower() == "deleting":
            raise RuntimeError("Volume is being deleted. Please wait and try again.")

        print(f"Found existing volume: {volume_id}")
    else:
        # Try to find the most recent snapshot
        snapshots_response = exo.list_block_storage_snapshots()
        snapshots = snapshots_response.get("block-storage-snapshots", [])
        matching_snapshots = [s for s in snapshots if s.get("labels") == LABELS]

        if matching_snapshots:
            matching_snapshots.sort(key=lambda s: s.get("created-at", ""), reverse=True)
            snapshot = matching_snapshots[0]
            snapshot_id = snapshot["id"]
            snapshot_size = snapshot["size"]

            if VOLUME_SIZE < snapshot_size:
                raise ValueError(
                    f"VOLUME_SIZE ({VOLUME_SIZE} GB) is smaller than the snapshot volume size "
                    f"({snapshot_size} GB). Cannot create volume."
                )

            print(f"Creating volume from snapshot: {snapshot_id}")
            operation = exo.create_block_storage_volume(
                name=NAME,
                size=VOLUME_SIZE,
                block_storage_snapshot={"id": snapshot_id},
                labels=LABELS,
            )
            volume_id = operation["reference"]["id"]
        else:
            print("Creating new empty volume")
            operation = exo.create_block_storage_volume(
                name=NAME, size=VOLUME_SIZE, labels=LABELS
            )
            volume_id = operation["reference"]["id"]

        def check_volume():
            v = exo.get_block_storage_volume(id=volume_id)
            state = v.get("state", "").lower()
            return state in ["attached", "detached"]

        wait_until(check=check_volume, kwargs={}, cond=lambda result: result)

    print(f"Provisioned Volume ID: {volume_id}")
    print(f"Zone: {ZONE}")

    with open(f"volume-exoscale-{NAME}.json", "w") as f:
        json.dump(
            {
                "volume_id": volume_id,
                "zone": ZONE,
            },
            f,
        )


if __name__ == "__main__":
    main()
