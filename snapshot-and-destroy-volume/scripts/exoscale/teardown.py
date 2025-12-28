"""Exoscale block storage volume teardown script.

DISABLED: Automatic deletion is not allowed for Exoscale volumes.
Exoscale snapshots are deleted when volumes are deleted, providing no backup.
"""


def main():
    raise RuntimeError(
        "Automatic volume deletion is not allowed for Exoscale. "
        "Exoscale snapshots are automatically deleted when their source volumes are deleted, "
        "which means there is no way to backup and restore data. "
        "Use the 'snapshot-volume' action instead to create snapshots without deletion, "
        "or manually delete volumes through the Exoscale console after verifying snapshots persist."
    )


if __name__ == "__main__":
    main()
