# Contributing to Cloud Volume Actions

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Clone the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test your changes (see Testing section below)
5. Commit with descriptive messages
6. Push and create a pull request

## Adding Support for New Providers

To add support for a new cloud provider:

1. **Study existing implementations** in the action.yml files to understand the pattern
2. **Add provider-specific inputs** to both action.yml files
3. **Add validation** in the "Validate provider" step
4. **Implement the provider logic** following the same structure:
   - For `create-or-restore-volume`: Check existing → restore from snapshot → create new
   - For `snapshot-and-destroy-volume`: Create snapshot → delete volume
5. **Add provider-specific outputs** as needed
6. **Update README.md** with new provider documentation
7. **Test thoroughly** before submitting PR

## Testing

Since these are composite actions, test by:

1. Creating a test repository
2. Adding the action as a local path reference:
   ```yaml
   - uses: ./path/to/cloud-volume-actions/create-or-restore-volume
   ```
3. Running workflows with actual cloud credentials (use test accounts)
4. Verifying outputs and behavior

## Version Bumping

To release a new version:

1. Update the `version` field in `pyproject.toml` (semver format: X.Y.Z)
2. Update CHANGELOG if you create one
3. Commit and push to main branch
4. The CI/CD pipeline will automatically:
   - Run tests
   - Create a git tag
   - Create a GitHub release
   - Update the major version tag

## Code Style

- Use clear, descriptive variable names
- Add comments for complex logic
- Follow existing patterns in the codebase
- Keep shell scripts POSIX-compatible where possible

## Pull Request Process

1. Update documentation for any changed functionality
2. Ensure your code follows the existing style
3. Add/update tests if applicable
4. Update README.md with any new inputs/outputs
5. Describe your changes clearly in the PR description
6. Reference any related issues

## Reporting Issues

When reporting issues, please include:

- Cloud provider and region/zone
- Action version used
- Relevant workflow YAML
- Error messages or unexpected behavior
- Steps to reproduce

## Questions?

Feel free to open an issue for questions or discussions about the project.
