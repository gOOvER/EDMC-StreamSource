# Contributing to EDMC-StreamSource

Thank you for your interest in contributing to EDMC-StreamSource! This document provides guidelines for contributing to this project.

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Install development dependencies:
   ```bash
   pip install pre-commit flake8 mypy
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

This project follows PEP 8 style guidelines with the following specifics:

- Maximum line length: 120 characters
- Use type hints where possible
- Use f-strings for string formatting
- Maximum cognitive complexity: 15

## Testing

Currently, this project doesn't have automated tests due to its dependency on EDMC's runtime environment. However, you should test your changes by:

1. Installing the plugin in EDMC
2. Running Elite Dangerous or using test data
3. Verifying that output files are generated correctly
4. Checking that streaming software can read the files properly

## Submitting Changes

1. Create a new branch for your feature/fix
2. Make your changes following the code style guidelines
3. Update the CHANGELOG.md if appropriate
4. Ensure pre-commit hooks pass
5. Create a pull request with a clear description of your changes

## Code Review Process

All changes must be reviewed before merging. The review process includes:

- Code style and quality checks
- Functionality verification
- Documentation updates if needed

## Questions?

If you have questions about contributing, please open an issue for discussion.