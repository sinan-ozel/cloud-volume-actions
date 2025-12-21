# Required GitHub Secrets

To enable the full CI/CD pipeline, including integration tests, you need to configure the following secrets in your GitHub repository.

## How to Add Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed below

## Required Secrets

### AWS Testing Credentials

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `TEST_AWS_REGION` | AWS region for integration tests | `us-east-1` or `ca-central-1` |
| `TEST_AWS_ACCESS_KEY_ID` | AWS access key ID for test account | `AKIAIOSFODNN7EXAMPLE` |
| `TEST_AWS_SECRET_ACCESS_KEY` | AWS secret access key for test account | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |

### Exoscale Testing Credentials

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `TEST_EXOSCALE_ZONE` | Exoscale zone for integration tests | `ch-gva-2` or `at-vie-1` |
| `TEST_EXOSCALE_API_KEY` | Exoscale API key for test account | `EXOxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TEST_EXOSCALE_API_SECRET` | Exoscale API secret for test account | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

## Security Best Practices

### For AWS
1. **Create a dedicated IAM user** for CI/CD testing (don't use root credentials)
2. **Attach minimal permissions policy**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ec2:CreateVolume",
           "ec2:DeleteVolume",
           "ec2:DescribeVolumes",
           "ec2:CreateSnapshot",
           "ec2:DeleteSnapshot",
           "ec2:DescribeSnapshots",
           "ec2:DescribeAvailabilityZones",
           "ec2:CreateTags"
         ],
         "Resource": "*"
       }
     ]
   }
   ```
3. **Add resource tags** to easily identify test resources
4. **Set up billing alerts** to catch any runaway costs
5. **Use a separate AWS account** for testing if possible

### For Exoscale
1. **Create a dedicated API key** for CI/CD testing
2. **Use organization roles** to limit permissions to Block Storage only
3. **Enable audit logging** to track API usage
4. **Set up billing alerts** for the test account

## Cost Considerations

Integration tests create and destroy small volumes (10 GB) on each version change:
- **AWS:** ~$0.10 per test run (2 volumes created/destroyed)
- **Exoscale:** ~$0.20 per test run (2 volumes created/destroyed)

Tests include automatic cleanup, so volumes don't persist between runs.

## Testing the Setup

After adding secrets, you can test by:

1. Make a change to any action file
2. Bump the version in `pyproject.toml`
3. Push to a feature branch
4. Watch the workflow run in the **Actions** tab

The integration tests should run and validate your credentials are working correctly.

## Troubleshooting

### "Error: Secrets not found"
- Verify secret names match exactly (case-sensitive)
- Ensure secrets are set at the repository level, not organization level (unless inherited)

### "Integration tests failed"
- Check the Actions logs for specific error messages
- Verify credentials have the correct permissions
- Ensure the region/zone is valid and available
- Check for quota limits in your cloud account

### "Cleanup failed"
- Manual cleanup may be needed in your cloud console
- Look for resources tagged with `gha-test-*` pattern
- Delete any orphaned volumes or snapshots manually
