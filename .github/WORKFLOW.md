# GitHub Actions Workflow

## Workflow DAG (Directed Acyclic Graph)

```
┌──────────────┐
│   Trigger    │  Push to any branch or PR to main
│  (on push/PR)│  with changes to code or workflow
└──────┬───────┘
       │
       ├─────────────────────────────────────────┐
       │                                         │
       ▼                                         ▼
┌─────────────┐                       ┌──────────────────┐
│  reformat   │                       │ detect-version-  │
│             │                       │     change       │
│ Runs Black, │                       │                  │
│ isort, etc. │                       │ Checks if version│
│             │                       │ in pyproject.toml│
│ (parallel)  │                       │ was modified     │
└─────────────┘                       └────────┬─────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │   test-actions       │
                                    │                      │
                                    │ Validates action.yml │
                                    │ syntax (if version   │
                                    │ changed)             │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │  integration-test    │
                                    │                      │
                                    │ AWS & Exoscale tests │
                                    │ - Create volume      │
                                    │ - Snapshot/destroy   │
                                    │ - Restore from snap  │
                                    │ (if version changed) │
                                    └──────────┬───────────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │  publish-release     │
                                    │                      │
                                    │ - Create git tag     │
                                    │ - GitHub Release     │
                                    │ - Update major tag   │
                                    │ (if version changed  │
                                    │  & tests pass)       │
                                    └──────────────────────┘
```

## Job Details

### 1. `reformat`
- **Runs:** Always (parallel, independent)
- **Purpose:** Auto-format code with Black, isort, docformatter
- **Auto-commits:** On non-main branches only
- **Dependencies:** None

### 2. `detect-version-change`
- **Runs:** Always (parallel with reformat)
- **Purpose:** Check if version in `pyproject.toml` changed
- **Outputs:**
  - `version-changed`: true/false
  - `new-version`: The version string
- **Dependencies:** None

### 3. `test-actions`
- **Runs:** Only if version changed
- **Purpose:** Validate action.yml syntax
- **Matrix:** 2 providers × 2 actions = 4 jobs
- **Dependencies:** `detect-version-change`

### 4. `integration-test`
- **Runs:** Only if version changed AND test-actions passed
- **Purpose:** Full lifecycle tests against real cloud APIs
- **Matrix:** 2 providers (AWS, Exoscale)
- **Tests:**
  1. Create new volume
  2. Snapshot and destroy volume
  3. Restore from snapshot
  4. Cleanup (always runs)
- **Dependencies:** `detect-version-change`, `test-actions`

### 5. `publish-release`
- **Runs:** Only if version changed AND all tests passed
- **Purpose:** Publish to GitHub Marketplace
- **Actions:**
  1. Create git tag (`vX.Y.Z`)
  2. Create GitHub Release
  3. Update major version tag (`v1`, `v2`, etc.)
- **Dependencies:** `detect-version-change`, `test-actions`, `integration-test`

## Trigger Conditions

### Runs on:
- **Push** to any branch (`*`)
- **Pull Requests** to `main` branch

### Only when these files change:
- `pyproject.toml`
- `create-or-restore-volume/**`
- `snapshot-and-destroy-volume/**`
- `.github/workflows/publish.yml`

## Version Change Behavior

| Version Changed? | Jobs Run |
|-----------------|----------|
| ❌ No | `reformat`, `detect-version-change` only |
| ✅ Yes | All jobs (reformat, detect, test, integration-test, publish) |

## Safety Mechanisms

1. **No publish without version change** - Version must be bumped in `pyproject.toml`
2. **Syntax validation** - Actions must have valid YAML structure
3. **Integration tests** - Full lifecycle tested against real cloud APIs
4. **All tests must pass** - Any failure blocks publishing
5. **Automatic cleanup** - Integration tests clean up resources even on failure
