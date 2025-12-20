"""AWS EBS volume teardown script.

Creates snapshots of EBS volumes and then deletes them.
Reads configuration from environment variables.
"""

import os
import boto3
from helpers import wait_until


def main():
    # Load environment variables
    NAME = os.environ["VOLUME_NAME"]

    # Hardcoded constants
    REGION = os.environ.get("AWS_REGION", "ca-central-1")
    TAGS = {"name": NAME}
    FILTERS = [{"Name": f"tag:{k}", "Values": [v]} for k, v in TAGS.items()]

    # Boto3 session
    session = boto3.Session(region_name=REGION)
    ec2_client = session.client("ec2")

    response = ec2_client.describe_volumes(Filters=FILTERS)
    volumes = response.get("Volumes", [])
    if not volumes:
        raise RuntimeError(f"No volumes found matching the filter: {FILTERS}")
    volume_ids = [volume["VolumeId"] for volume in volumes]

    snapshot_id = None
    for volume_id in volume_ids:
        response = ec2_client.create_snapshot(
            VolumeId=volume_id,
            Description=f"Snapshot For: {volume_id}. Tags: {TAGS}",
            TagSpecifications=[
                {
                    "ResourceType": "snapshot",
                    "Tags": [{"Key": k, "Value": TAGS[k]} for k in TAGS],
                }
            ],
        )
        snapshot_id = response["SnapshotId"]
        print(f"Created snapshot: {snapshot_id}")

    for volume_id in volume_ids:
        ec2_client.delete_volume(VolumeId=volume_id)
        print(f"Deleted volume: {volume_id}")

    wait_until(
        ec2_client.describe_volumes,
        {"Filters": FILTERS},
        lambda x: len(x["Volumes"]) == 0,
    )

    # Write snapshot ID to file for output
    with open("snapshot-output.txt", "w") as f:
        f.write(snapshot_id if snapshot_id else "")


if __name__ == "__main__":
    main()
