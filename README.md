# Cloud Volume Actions

GitHub Actions for managing persistent cloud volumes with automatic snapshot-based restore capabilities.

It restores a block storage if the snapshot exists, or a brand new one.
When destroying, it snapshots it first.
The purpose is to give data science and development teams _temporary-but-persistent_ environments.

See the usage example here: https://github.com/sinan-ozel/iac/blob/main/.github/workflows/volume.yaml

## ☁️ Supported Providers

| Provider | Create or Restore | Snapshot | Snapshot and Destroy |
|----------|-------------------|----------|----------------------|
| AWS (EBS) | ✅ | N/A | ✅ |
| Exoscale (Block Storage) | ✅ | ✅ | ❌ Not allowed* |
| Oracle Cloud | 🔜 Planned | 🔜 Planned | 🔜 Planned |
| Google Cloud | 🤔 Under Consideration | 🤔 Under Consideration | 🤔 Under Consideration |
| Azure | 🤔 Under Consideration | 🤔 Under Consideration | 🤔 Under Consideration |


*Exoscale snapshots are automatically deleted when volumes are deleted, preventing reliable backup/restore. Use the `snapshot-volume` action instead.



## Actions

### 🔄 `create-or-restore-volume`

Creates a new volume or restores from the most recent snapshot if available.

**Features:**
- Checks for existing volume with matching tags/labels
- Automatically restores from most recent snapshot if volume doesn't exist
- Creates new empty volume if no snapshot exists
- Validates volume size against snapshot size
- Waits for volume to be available before completing

**Usage:**

```yaml
- name: Create or Restore Volume
  uses: sinan-ozel/cloud-volume-actions/create-or-restore-volume@v0.1.0
  with:
    provider: 'aws'  # or 'exoscale'
    volume-name: 'my-data-volume'
    volume-size: '100'  # Size in GB

    # AWS-specific (required if provider=aws)
    aws-region: 'us-east-1'
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

    # Exoscale-specific (required if provider=exoscale)
    exoscale-zone: 'ch-gva-2'
    exoscale-api-key: ${{ secrets.EXOSCALE_API_KEY }}
    exoscale-api-secret: ${{ secrets.EXOSCALE_API_SECRET }}
```

**Outputs:**
- `volume-id`: The ID of the created or existing volume
- `availability-zone` (AWS only): The availability zone of the volume
- `zone` (Exoscale only): The zone of the volume

### 📸 `snapshot-and-destroy-volume`

Creates snapshots of volumes and then destroys them.

**Features:**
- Creates snapshots with matching tags/labels for backup
- Deletes all volumes matching the specified name/tags
- Waits for complete deletion before completing
- Preserves data via snapshots for future restoration

**Usage:**

```yaml
- name: Snapshot and Destroy Volume
  uses: sinan-ozel/cloud-volume-actions/snapshot-and-destroy-volume@v0.1.0
  with:
    provider: 'aws'  # or 'exoscale'
    volume-name: 'my-data-volume'

    # AWS-specific (required if provider=aws)
    aws-region: 'us-east-1'
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

    # Exoscale-specific (required if provider=exoscale)
    exoscale-zone: 'ch-gva-2'
    exoscale-api-key: ${{ secrets.EXOSCALE_API_KEY }}
    exoscale-api-secret: ${{ secrets.EXOSCALE_API_SECRET }}
```

**Outputs:**
- `snapshot-id`: The ID of the created snapshot (AWS)
- `snapshot-ids`: Comma-separated IDs of created snapshots (Exoscale, if multiple volumes)

> **⚠️ Important for Exoscale:** This action is **disabled for Exoscale** because Exoscale automatically deletes snapshots when their source volumes are deleted, making backup/restore impossible. Use the `snapshot-volume` action instead to create snapshots without deletion.

### 📸 `snapshot-volume` (Exoscale Only)

Creates snapshots of Exoscale block storage volumes without deleting them.

**Features:**
- Creates snapshots with matching labels for identification
- Preserves volumes after snapshot creation
- Waits for snapshots to complete before finishing
- Exoscale-specific action for safe snapshot management

**Usage:**

```yaml
- name: Snapshot Volume
  uses: sinan-ozel/cloud-volume-actions/snapshot-volume@v0.1.0
  with:
    volume-name: 'my-data-volume'
    exoscale-zone: 'ch-gva-2'
    exoscale-api-key: ${{ secrets.EXOSCALE_API_KEY }}
    exoscale-api-secret: ${{ secrets.EXOSCALE_API_SECRET }}
```

**Outputs:**
- `snapshot-ids`: Comma-separated IDs of created snapshots

## Inputs

### Common Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `provider` | Cloud provider (`aws` or `exoscale`) | Yes | - |
| `volume-name` | Name/label for the volume | Yes | - |
| `volume-size` | Size in GB (create-or-restore only) | Conditional | - |

### AWS Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `aws-region` | AWS region | Yes (for AWS) | `ca-central-1` |
| `aws-access-key-id` | AWS access key | Yes (for AWS) | - |
| `aws-secret-access-key` | AWS secret key | Yes (for AWS) | - |

### Exoscale Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `exoscale-zone` | Exoscale zone | Yes (for Exoscale) | `ch-gva-2` |
| `exoscale-api-key` | Exoscale API key | Yes (for Exoscale) | - |
| `exoscale-api-secret` | Exoscale API secret | Yes (for Exoscale) | - |

## Example Workflow

```yaml
name: Volume Lifecycle

on:
  workflow_dispatch:
    inputs:
      action:
        type: choice
        options: [create, destroy]

jobs:
  manage-volume:
    runs-on: ubuntu-latest
    steps:
      - name: Create or Restore Volume
        if: github.event.inputs.action == 'create'
        uses: your-org/cloud-volume-actions/create-or-restore-volume@v0.1.0
        with:
          provider: aws
          volume-name: my-persistent-data
          volume-size: '500'
          aws-region: us-west-2
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Snapshot and Destroy Volume
        if: github.event.inputs.action == 'destroy'
        uses: your-org/cloud-volume-actions/snapshot-and-destroy-volume@v0.1.0
        with:
          provider: aws
          volume-name: my-persistent-data
          aws-region: us-west-2
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## How It Works

### Volume Lifecycle

1. **Creation/Restoration:**
   - Searches for existing volume with matching name/tags
   - If not found, looks for most recent snapshot
   - Restores from snapshot OR creates new empty volume
   - Ensures volume is in available state

2. **Snapshot & Destroy:**
   - **AWS:** Creates snapshot(s) of all matching volumes, then deletes volumes after successful snapshot
   - **Exoscale:** Not supported - snapshots are deleted with volumes. Use `snapshot-volume` action instead
   - Preserves snapshots for future restoration (AWS only)

3. **Snapshot Only (Exoscale):**
   - Creates snapshot(s) without deleting volumes
   - Safe way to backup Exoscale volumes
   - Volumes remain active after snapshot creation

### Snapshot Management

Snapshots are automatically tagged/labeled with the same name as the volume, enabling automatic restore on next creation.

## Requirements

- Python 3.11+
- boto3 (AWS)
- python-exoscale (Exoscale)

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.

### Development Requirements

**You only need 🐳 [Docker](https://www.docker.com/)** - no Python installation required! All development happens in containers.

### Code Formatting

Before submitting a PR, format your code using Docker Compose:

```bash
docker compose -f reformat/docker-compose.yml up --build --abort-on-container-exit
```

Or use the VS Code task: `Cmd+Shift+P` → "Tasks: Run Task" → "Reformat Code"

This will automatically run:
- **Black** - Code formatter
- **isort** - Import sorter
- **docformatter** - Docstring formatter

The same formatting script runs in CI/CD, ensuring consistency across all contributions.
