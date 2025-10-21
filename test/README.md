# Test Suite for EDMC-StreamSource Plugin

This directory contains comprehensive tests for the EDMC-StreamSource plugin.

## Test Structure

```
test/
├── __init__.py           # Test package initialization
├── mock_utils.py         # Mock utilities for EDMC environment
├── test_functional.py    # Functional tests
├── test_performance.py   # Performance and stress tests
├── run_tests.py         # Main test runner
└── test_runner.py       # Development test commands
```

## Running Tests

### Quick Test Commands

```bash
# Run all tests
cd test
python run_tests.py

# Development commands
python test_runner.py all           # All tests
python test_runner.py functional    # Functional tests only
python test_runner.py performance   # Performance tests only
python test_runner.py lint          # Code quality checks
python test_runner.py quick         # Quick smoke test
python test_runner.py clean         # Clean test artifacts
```

### Individual Test Files

```bash
# Functional tests
python test_functional.py

# Performance tests
python test_performance.py
```

## Test Categories

### Functional Tests (`test_functional.py`)
- **Plugin Initialization**: Tests plugin startup and file creation
- **Journal Events**: Tests processing of Elite Dangerous journal events
- **Dashboard Events**: Tests Status.json data processing
- **Error Handling**: Tests behavior with invalid configurations
- **Edge Cases**: Tests with None values, empty strings, extreme coordinates

### Performance Tests (`test_performance.py`)
- **Rapid Updates**: 1000+ rapid journal entries (target: <5 seconds)
- **Stress Scenarios**: Extreme coordinates, Unicode characters, long names
- **Memory Usage**: Memory growth monitoring (target: <10MB growth)
- **File I/O Performance**: 500+ file writes (target: <1 second)

## Mock Environment

The test suite uses comprehensive mocks to simulate EDMC environment:

- **MockConfig**: Simulates EDMC configuration system
- **MockLocale**: Provides number formatting functionality  
- **Mock Ship Map**: Contains Elite Dangerous ship name mappings
- **Mock Modules**: Replaces `config`, `edmc_data`, and `l10n` imports

## Test Results

All tests should pass with these performance targets:

| Test Category | Target | Current Performance |
|---------------|--------|-------------------|
| Rapid Updates | <5 seconds for 1000 entries | ~2.2 seconds |
| File I/O | <1 second for 500 writes | ~0.18 seconds |
| Memory Growth | <10MB for extended session | <1MB |
| Success Rate | 100% | 100% |

## Continuous Integration

Tests are automatically run in GitHub Actions:

- **CI Workflow**: Runs on every push/PR
- **Release Workflow**: Runs before creating releases
- **Multi-Python**: Tests on Python 3.9, 3.10, 3.11, 3.12

## Adding New Tests

### Adding Functional Tests

1. Add test functions to `test_functional.py`
2. Follow naming convention: `test_*`
3. Use mock utilities from `mock_utils.py`
4. Add assertions to verify expected behavior

### Adding Performance Tests

1. Add test functions to `test_performance.py`
2. Include performance targets and measurements
3. Use `time.time()` for duration measurement
4. Print clear results with PASS/FAIL status

### Test Utilities

Use the provided utilities for consistent testing:

```python
from mock_utils import (
    setup_mock_environment,
    add_project_to_path,
    create_test_journal_entry,
    create_test_state
)

# Setup mocks
add_project_to_path()
config, edmc_data, l10n = setup_mock_environment()

# Create test data
entry = create_test_journal_entry('FSDJump', StarSystem='Sol')
state = create_test_state(ShipType='sidewinder', ShipName='Test Ship')
```

## Requirements

- Python 3.9+
- No external dependencies required for basic tests
- Optional: `psutil` for detailed memory monitoring

## Troubleshooting

### Common Issues

1. **Module Import Errors**: Ensure you're running from the `test/` directory
2. **File Permission Errors**: Check that test directories are writable
3. **Unicode Errors**: Tests use ASCII-safe output for Windows compatibility
4. **Performance Failures**: May indicate system resource constraints

### Debug Mode

For detailed debugging, modify test files to include more verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Development

The test suite integrates with development workflows:

- **Pre-commit**: Run `python test_runner.py lint` before commits
- **Release Preparation**: Run `python run_tests.py` before releases  
- **Performance Monitoring**: Use performance tests to detect regressions
- **Code Quality**: Tests enforce type safety and error handling

## Future Enhancements

Planned improvements:

- [ ] Integration tests with real EDMC environment
- [ ] Automated performance benchmarking
- [ ] Test coverage reporting
- [ ] Parallel test execution
- [ ] Browser-based test reporting